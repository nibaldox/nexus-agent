"""
Nexus Workflow Orchestrator
Implements 4-phase workflow: Planning → Execution → Review → Delivery
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

class NexusWorkflow:
    """Orchestrates the 4-phase agent workflow"""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace = workspace_dir
        self.plans_dir = os.path.join(workspace_dir, "mission_plans")
        os.makedirs(self.plans_dir, exist_ok=True)
    
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
                f"{i}. [ ] **{desc}** - Asignado: {agent} - Objetivo: {objective}"
            )
        
        tasks_md = "\n".join(task_lines)
        
        plan = f"""# Plan de Misión: {user_request[:50]}{'...' if len(user_request) > 50 else ''}

**Fecha Creación**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Solicitud Original**: {user_request}

## Estrategia

El Manager analizó la solicitud y descompuso la misión en {len(tasks)} tareas específicas.
Se delegarán a los agentes especializados en orden lógico.

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
        # Simple heuristics
        word_count = len(user_request.split())
        
        # Check for complexity indicators
        complexity_keywords = [
            'analisis', 'analysis', 'completo', 'complete', 
            'comparar', 'compare', 'grafico', 'chart', 'graph',
            'investigar', 'research', 'tendencias', 'trends',
            'distribucion', 'distribution', 'estadistica', 'statistics'
        ]
        
        has_complexity = any(kw in user_request.lower() for kw in complexity_keywords)
        
        # Create plan if:
        # - More than 10 words
        # - Contains complexity keywords
        # - Contains multiple questions (has '?' or 'y' or 'and')
        
        if word_count > 10 or has_complexity:
            return True
        
        # Check for multiple questions
        if '?' in user_request and user_request.count('?') > 0:
            return True
        
        return False
    
    def extract_tasks_from_manager_response(self, manager_initial_response: str) -> List[Dict[str, str]]:
        """
        Extract planned tasks from Manager's initial analysis.
        
        This is a helper to parse Manager's thinking if it outlines tasks.
        For now, returns a simple default based on heuristics.
        """
        # TODO: In future, parse Manager's actual output for task breakdown
        # For now, return a default structure
        
        tasks = [
            {
                "description": "Investigación inicial",
                "agent": "Researcher",
                "objective": "Obtener información relevante"
            },
            {
                "description": "Síntesis de resultados",
                "agent": "Manager",
                "objective": "Consolidar información"
            }
        ]
        
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
