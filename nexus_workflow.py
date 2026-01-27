"""
Nexus Workflow Orchestrator
Implements 4-phase workflow: Planning → Execution → Review → Delivery
"""
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from agno.workflow import Workflow, Step, StepOutput, StepInput
from agno.db.sqlite import SqliteDb
from agents.manager import manager
from agents.squads.knowledge.reviewer import reviewer
from config import settings
import logging

logger = logging.getLogger("NexusWorkflow")

class NexusWorkflow:
    """Orchestrates the 4-phase agent workflow using Agno Workflow."""

    def __init__(self, workspace_dir: Optional[str] = None):
        self.workspace = str(Path(workspace_dir) if workspace_dir else settings.workspace_dir)
        self.plans_dir = os.path.join(self.workspace, "mission_plans")
        os.makedirs(self.plans_dir, exist_ok=True)
        self.workflow = Workflow(
            name="Nexus Workflow",
            description="Flujo principal de Nexus basado en Agno",
            db=SqliteDb(db_file="agent.db", session_table="nexus_workflow_sessions"),
            store_events=True,
            steps=[
                Step(
                    name="Planificación",
                    description="Crear plan de misión si aplica",
                    executor=self._plan_step,
                ),
                Step(
                    name="Nexus Manager",
                    description="Orquestación principal del equipo",
                    executor=self._manager_step
                ),
                Step(
                    name="Revisión",
                    description="Validación de calidad y dictamen final",
                    executor=self._review_step
                )
            ],
        )

    def run(self, user_request: str, session_id: Optional[str], stream: bool, stream_events: bool):
        return self.workflow.run(
            input=user_request,
            additional_data={"session_id": session_id},
            session_id=session_id,
            stream=stream,
            stream_events=stream_events
        )

    def _plan_step(self, step_input: StepInput) -> StepOutput:
        user_request = step_input.input or ""
        session_id = None
        if step_input.additional_data:
            session_id = step_input.additional_data.get("session_id")
        session_id = session_id or "default"
        os.environ["NEXUS_SESSION_ID"] = session_id

        if not self.should_create_plan(str(user_request)):
            return StepOutput(content={"created": False, "plan_path": None, "tasks": []})

        tasks = self.extract_tasks_from_manager_response(str(user_request))
        plan_path = self.create_mission_plan(
            user_request=str(user_request),
            session_id=session_id,
            tasks=tasks
        )
        return StepOutput(
            content={
                "created": True,
                "plan_path": plan_path,
                "tasks": tasks
            }
        )

    def _manager_step(self, step_input: StepInput):
        """
        Ejecuta el Manager usando SIEMPRE la solicitud original,
        evitando que el output del paso anterior reemplace el input.
        """
        message = step_input.input
        session_id = None
        if step_input.additional_data:
            session_id = step_input.additional_data.get("session_id")
        if not session_id and step_input.workflow_session:
            session_id = step_input.workflow_session.session_id
        session_id = session_id or "default"
        os.environ["NEXUS_SESSION_ID"] = session_id

        stream = manager.run(
            input=message,
            session_id=session_id,
            stream=True,
            stream_events=True,
            yield_run_output=True
        )
        for chunk in stream:
            yield chunk

    def _review_step(self, step_input: StepInput):
        """
        Ejecuta el Reviewer para validar la respuesta del Manager.
        """
        session_id = None
        if step_input.additional_data:
            session_id = step_input.additional_data.get("session_id")
        session_id = session_id or "default"
        os.environ["NEXUS_SESSION_ID"] = session_id

        # Obtener el prompt original para contexto
        user_request = step_input.input or ""
        
        # --- NUEVA LÓGICA DE OMISIÓN ---
        # Si la solicitud es simple (no requiere plan), omitimos la revisión formal
        if not self.should_create_plan(str(user_request)):
            logger.info(f"Omitiendo fase de revisión para solicitud simple: {user_request}")
            return
        
        # El Reviewer necesita ver la respuesta del Manager.
        session_id = None
        if step_input.additional_data:
            session_id = step_input.additional_data.get("session_id")
        session_id = session_id or "default"
        os.environ["NEXUS_SESSION_ID"] = session_id

        # Obtener el prompt original para contexto
        user_request = step_input.input or ""
        
        # El Reviewer necesita ver la respuesta del Manager.
        # En Agno Workflow, el output del paso anterior está disponible en el historial del workflow.
        # Para simplificar y asegurar que el Reviewer tiene todo, le pasamos la solicitud y el estado de la misión.
        
        review_prompt = (
            f"Solicitud Original del Usuario: {user_request}\n\n"
            "Por favor, revisa la ejecución de la misión hasta ahora. "
            "Valida si se han cumplido los objetivos, si la calidad es óptima y si la respuesta es coherente. "
            "Responde con tu dictamen estructurado en JSON."
        )

        stream = reviewer.run(
            input=review_prompt,
            session_id=session_id,
            stream=True,
            stream_events=True,
            yield_run_output=True
        )
        
        full_reviewer_response = ""
        for chunk in stream:
            # Acumular la respuesta para procesar el dictamen al final
            if hasattr(chunk, "content") and chunk.content:
                full_reviewer_response += chunk.content
            yield chunk
        
        # Procesar el dictamen final para actualizar el estado de la misión (opcional / futuro)
        # dictamen = self.parse_reviewer_response(full_reviewer_response)
        # logger.info(f"Reviewer dictamen: {dictamen['status']}")
    
    def create_mission_plan(
        self, 
        user_request: str, 
        session_id: str,
        tasks: List[Dict[str, str]]
    ) -> str:
        """
        Create a mission plan file.
        
        Args:
            user_request: Original user request
            session_id: Session ID
            tasks: List of tasks with 'description', 'agent', 'objective'
            
        Returns:
            Path to the created plan file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_filename = f"plan_{session_id}_{timestamp}.md"
        plan_path = os.path.join(self.plans_dir, plan_filename)
        
        # Generate plan content
        plan_content = self._generate_plan_template(
            user_request=user_request,
            timestamp=timestamp,
            tasks=tasks
        )
        
        # Write to file
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        # Also save a copy under the session workspace for traceability
        session_plan_dir = os.path.join(self.workspace, "conversations", session_id, "plans")
        os.makedirs(session_plan_dir, exist_ok=True)
        session_plan_path = os.path.join(session_plan_dir, plan_filename)
        try:
            with open(session_plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)
        except Exception as e:
            logger.warning(f"Failed to save plan copy to session dir: {e}")
        
        return plan_path
    
    def _generate_plan_template(
        self, 
        user_request: str, 
        timestamp: str, 
        tasks: List[Dict[str, str]]
    ) -> str:
        """Generate markdown template for mission plan"""
        
        # Create task list markdown
        task_lines = []
        for i, task in enumerate(tasks, 1):
            desc = task.get('description', 'Unnamed task')
            agent = task.get('agent', 'Unknown')
            objective = task.get('objective', '')
            task_lines.append(
                f"{i}. [ ] **{desc}** - Escuadrón: {agent} - Objetivo: {objective}"
            )
        
        tasks_md = "\n".join(task_lines)
        
        plan = f"""# Plan de Misión: {user_request[:50]}{'...' if len(user_request) > 50 else ''}

**Fecha Creación**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Solicitud Original**: {user_request}

## Estrategia

El Manager analizó la solicitud y descompuso la misión en {len(tasks)} tareas específicas.
Se delegarán a los escuadrones especializados en orden lógico.

## Tareas

{tasks_md}

## Progreso

_Este plan se actualiza conforme se completan las tareas._

---

### Registro de Ejecución
"""
        return plan
    
    def update_plan_task(
        self, 
        plan_path: str, 
        task_number: int, 
        status: str = "completed",
        result_summary: Optional[str] = None
    ):
        """
        Update a task's status in the plan file.
        
        Args:
            plan_path: Path to the plan file
            task_number: Task number (1-indexed)
            status: 'completed', 'failed', 'in_progress'
            result_summary: Brief summary of the result
        """
        if not os.path.exists(plan_path):
            return
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Mark task as completed/failed
        if status == "completed":
            # Change [ ] to [x] for the specified task
            lines = content.split('\n')
            task_line_found = False
            for i, line in enumerate(lines):
                # Match task number
                if line.strip().startswith(f"{task_number}. [ ]"):
                    lines[i] = line.replace("[ ]", "[x]")
                    task_line_found = True
                    break
            
            if task_line_found:
                content = '\n'.join(lines)
                
                # Append result summary if provided
                if result_summary:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    log_entry = f"\n**[{timestamp}]** Tarea {task_number} completada: {result_summary}\n"
                    content += log_entry
        
        elif status == "in_progress":
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{task_number}. [ ]"):
                    lines[i] = line.replace("[ ]", "[/]")  # Custom notation for in-progress
                    break
            content = '\n'.join(lines)
        
        # Write back
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def parse_reviewer_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Reviewer's JSON response.
        
        Args:
            response_text: Text response from Reviewer
            
        Returns:
            Parsed dict with status, issues, recommendations, etc.
        """
        # Try to extract JSON block from markdown
        json_match = None
        
        # Look for JSON code blocks
        import re
        code_block = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if code_block:
            json_match = code_block.group(1)
        else:
            # Try to find raw JSON object
            json_match = re.search(r'\{[^{}]*"status"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_match = json_match.group(0)
        
        if json_match:
            try:
                return json.loads(json_match)
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to infer from keywords
        status = "APPROVED" if "APPROVED" in response_text else "NEEDS_REVISION"
        
        return {
            "status": status,
            "confidence": "LOW",
            "issues": [],
            "missing_tasks": [],
            "recommendations": [],
            "quality_score": 50,
            "summary": "Could not parse structured response"
        }
    
    def should_create_plan(self, user_request: str) -> bool:
        """
        Determine if a mission plan should be created based on request complexity.
        
        Simple queries (1-2 words) don't need plans.
        Complex requests with multiple parts do.
        """
        text = (user_request or "").strip().lower()
        if not text:
            return False

        simple_ack = {
            "ok", "okei", "listo", "vale", "perfecto", "gracias", "entendido",
            "si", "sí", "no", "bien", "dale", "hecho", "continuar", "continua"
        }
        if text in simple_ack:
            return False

        # Simple status checks
        if re.match(r'^(esta|estan|esta listo|listo|completado|terminado|hecho)\??$', text):
            return False

        # Simple heuristics
        word_count = len(text.split())
        
        # Check for complexity indicators
        complexity_keywords = [
            'analisis', 'analysis', 'completo', 'complete', 
            'comparar', 'compare', 'grafico', 'chart', 'graph',
            'investigar', 'research', 'tendencias', 'trends',
            'distribucion', 'distribution', 'estadistica', 'statistics'
        ]
        
        has_complexity = any(kw in text for kw in complexity_keywords)
        has_multiple_parts = text.count(",") + text.count(";") + text.count(" y ") + text.count(" and ") >= 2
        
        # Create plan if:
        # - More than 10 words
        # - Contains complexity keywords
        # - Contains multiple questions (has '?' or 'y' or 'and')
        
        if word_count > 12 or has_complexity or has_multiple_parts:
            return True
        
        # Check for multiple questions
        if '?' in text and text.count('?') > 0:
            return True
        
        return False
    
    def extract_tasks_from_manager_response(self, manager_initial_response: str) -> List[Dict[str, str]]:
        """
        Extract planned tasks from Manager's initial analysis.
        
        This attempts to parse structured task output from the Manager.
        Falls back to heuristics if no structured response is found.
        """
        manager_response = self._get_manager_task_breakdown(manager_initial_response)
        tasks = self._parse_manager_tasks(manager_response)
        if tasks:
            return tasks
        return self._fallback_heuristic_tasks(manager_initial_response)

    def _get_manager_task_breakdown(self, user_request: str) -> str:
        prompt = (
            "Analiza la solicitud y devuelve SOLO un JSON valido con esta estructura:\n"
            "{\n"
            "  \"tasks\": [\n"
            "    {\n"
            "      \"description\": \"...\",\n"
            "      \"squad\": \"Data Intelligence|Knowledge|Development\",\n"
            "      \"objective\": \"...\",\n"
            "      \"priority\": 1\n"
            "    }\n"
            "  ],\n"
            "  \"requires_review\": true\n"
            "}\n"
            "Solicitud:\n"
            f"{user_request}\n"
        )
        try:
            response = manager.run(prompt, stream=False)
            if isinstance(response, str):
                return response
            return getattr(response, "content", "") or str(response)
        except Exception as e:
            logger.error(f"Error getting task breakdown from Manager: {e}")
            return ""

    def _parse_manager_tasks(self, response_text: str) -> List[Dict[str, str]]:
        if not response_text:
            return []

        json_match = None
        code_block = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if code_block:
            json_match = code_block.group(1)
        else:
            raw_match = re.search(r'\{[\s\S]*\}', response_text, re.DOTALL)
            if raw_match:
                json_match = raw_match.group(0)

        if not json_match:
            return []

        try:
            parsed = json.loads(json_match)
        except Exception as e:
            logger.warning(f"Failed to parse manager response JSON: {e}")
            return []

        tasks = []
        for task in parsed.get("tasks", []) or []:
            squad = self._map_squad_name(task.get("squad", ""))
            tasks.append({
                "description": task.get("description", "Tarea"),
                "agent": squad,
                "objective": task.get("objective", ""),
                "priority": task.get("priority", 5)
            })

        tasks.sort(key=lambda t: t.get("priority", 5))
        for task in tasks:
            task.pop("priority", None)

        if parsed.get("requires_review"):
            tasks.append({
                "description": "Revisión y síntesis final",
                "agent": "Knowledge Squad",
                "objective": "Validar calidad y consolidar respuesta final"
            })

        return tasks

    def _map_squad_name(self, squad_value: str) -> str:
        value = (squad_value or "").lower()
        if "data" in value or "intelligence" in value:
            return "Data Intelligence Squad"
        if "knowledge" in value:
            return "Knowledge Squad"
        if "develop" in value or "dev" in value:
            return "Development Squad"
        return "Knowledge Squad"

    def _fallback_heuristic_tasks(self, request_text: str) -> List[Dict[str, str]]:
        text = (request_text or "").lower()

        def has_any(tokens: List[str]) -> bool:
            return any(tok in text for tok in tokens)

        def has_negation() -> bool:
            return bool(re.search(r'\b(no|sin|evitar|omitir)\b', text))

        tasks: List[Dict[str, str]] = []

        if has_any(["investigar", "research", "búsqueda", "buscar", "noticias", "artículo", "web"]):
            tasks.append({
                "description": "Investigación inicial",
                "agent": "Data Intelligence Squad",
                "objective": "Obtener información relevante y fuentes confiables"
            })

        if has_any(["análisis", "analysis", "financ", "market", "ticker", "precio", "serie", "estadística"]):
            tasks.append({
                "description": "Análisis de datos",
                "agent": "Data Intelligence Squad",
                "objective": "Procesar datos y extraer insights cuantitativos"
            })

        if not has_negation() and has_any(["gráfico", "grafico", "chart", "visual", "visualización", "plot", "tabla"]):
            tasks.append({
                "description": "Visualización de resultados",
                "agent": "Data Intelligence Squad",
                "objective": "Generar gráficos o tablas claras para comunicar hallazgos"
            })

        if has_any(["pdf", "documento", "documentación", "knowledge", "archivo", "base de conocimiento"]):
            tasks.append({
                "description": "Búsqueda en base de conocimiento",
                "agent": "Knowledge Squad",
                "objective": "Encontrar evidencia en documentos locales"
            })

        if not tasks:
            tasks.append({
                "description": "Investigación inicial",
                "agent": "Data Intelligence Squad",
                "objective": "Obtener información relevante"
            })

        tasks.append({
            "description": "Síntesis de resultados",
            "agent": "Knowledge Squad",
            "objective": "Consolidar información y responder al usuario"
        })

        return tasks
    
    def get_plan_path_for_session(self, session_id: str) -> Optional[str]:
        """Get the most recent plan file for a given session"""
        import glob
        
        plans = glob.glob(os.path.join(self.plans_dir, f"plan_{session_id}_*.md"))
        if plans:
            # Return most recent
            plans.sort(reverse=True)
            return plans[0]
        return None
