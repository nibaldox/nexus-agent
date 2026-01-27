from agno.team import Team
from agents.provider import get_openrouter_model
from agno.db.sqlite import SqliteDb
from tools.workspace_file_tools import FileTools
from skills.visualization_skills import VisualizationSkills
from skills.docs_skills import DocsSkills
from skills.research_skills import ResearchSkills
from skills.quality_skills import QualitySkills
from skills.triage_skills import TriageSkills
from skills.source_validation_skills import SourceValidationSkills
from skills.data_normalization_skills import DataNormalizationSkills
from skills.synthesis_skills import SynthesisSkills
from skills.workflow_skills import WorkflowSkills
from skills.risk_skills import RiskSkills
from skills.memory_skills import MemorySkills
from skills.tool_decision_skills import ToolDecisionSkills
from skills.context_compression_skills import ContextCompressionSkills
from skills.decision_log_skills import DecisionLogSkills
from agno.tools.function import Function
from typing import List, Dict, Any
from dotenv import load_dotenv
import json
import re

# Import Squads
from agents.squads.development.squad_leader import dev_squad
from agents.squads.data_intelligence.squad_leader import data_intelligence_squad
from agents.squads.knowledge.squad_leader import knowledge_squad
from agents.squads.knowledge.reviewer import reviewer

load_dotenv()

# Dynamic Agent Creation System
class DynamicAgentFactory:
    """Factory for creating agents dynamically based on requirements."""

    @staticmethod
    def evaluate_agent_needs(task_description: str, available_agents: List[str]) -> List[Dict[str, Any]]:
        """
        Evaluate what agents are needed for a task using LLM analysis.
        Returns list of agent specifications if new agents are required.
        """
        from agno.agent import Agent

        evaluator = Agent(
            name="AgentEvaluator",
            role="Evaluates task requirements and determines needed agent specializations",
            model=get_openrouter_model(max_tokens=2000),
            instructions=[
                "Analiza la tarea y determina si se necesitan agentes especializados adicionales.",
                "Considera los agentes disponibles: " + ", ".join(available_agents),
                "Si falta especialización, especifica: nombre, rol, instrucciones clave, herramientas necesarias.",
                "Responde SOLO con JSON válido: [] si no necesita nuevos agentes, o lista de specs.",
                "Formato ejemplo: [{\"name\": \"CryptoAnalyst\", \"role\": \"Analista de criptomonedas\", \"instructions\": [\"Analizar tendencias crypto\"], \"tools\": [\"YFinance\", \"ResearchSkills\"]}]"
            ]
        )

        response = evaluator.run(f"Evalúa esta tarea y determina agentes necesarios: {task_description}")
        try:
            specs = json.loads(str(response.content).strip())
            return specs if isinstance(specs, list) else []
        except:
            return []

    @staticmethod
    def create_agent_from_spec(spec: Dict[str, Any]) -> Agent:
        """
        Create an agent from a specification dictionary.
        Spec should contain: name, role, instructions, tools, model
        """
        from agno.agent import Agent

        # Extract agent properties
        name = spec.get('name', 'DynamicAgent')
        role = spec.get('role', 'General purpose agent')
        instructions = spec.get('instructions', [])
        tools = spec.get('tools', [])
        model = spec.get('model', get_openrouter_model(max_tokens=5000))

        # Convert tool names to actual tool instances
        actual_tools = []
        tool_registry = {
            'FileTools': FileTools(),
            'ResearchSkills': ResearchSkills(),
            'VisualizationSkills': VisualizationSkills(),
            'QualitySkills': QualitySkills(),
            'DocsSkills': DocsSkills(),
            'TriageSkills': TriageSkills(),
            'SourceValidationSkills': SourceValidationSkills(),
            'DataNormalizationSkills': DataNormalizationSkills(),
            'SynthesisSkills': SynthesisSkills(),
            'WorkflowSkills': WorkflowSkills(),
            'RiskSkills': RiskSkills(),
            'MemorySkills': MemorySkills(),
            'ToolDecisionSkills': ToolDecisionSkills(),
            'ContextCompressionSkills': ContextCompressionSkills(),
            'DecisionLogSkills': DecisionLogSkills(),
        }

        for tool_name in tools:
            if tool_name in tool_registry:
                actual_tools.append(tool_registry[tool_name])

        return Agent(
            name=name,
            role=role,
            model=model,
            tools=actual_tools,
            instructions=instructions,
            markdown=True,
        )

# Initialize base team
base_members = [data_intelligence_squad, knowledge_squad, dev_squad, reviewer]

# Define dynamic agent functions before creating manager
def create_dynamic_agent(agent_spec: Dict[str, Any]) -> Agent:
    """
    Function to create and add a dynamic agent to the manager team.
    This can be called by the manager during execution.
    """
    new_agent = DynamicAgentFactory.create_agent_from_spec(agent_spec)

    # Add to manager's members list if not already present
    if new_agent not in manager.members:
        manager.members.append(new_agent)
        print(f"✅ Agente dinámico '{new_agent.name}' creado y agregado al equipo")

    return new_agent

def evaluate_and_create_agents(task_description: str) -> List[Agent]:
    """
    Evaluate task requirements and create any needed dynamic agents.
    Returns list of newly created agents.
    """
    available_agent_names = [member.name if hasattr(member, 'name') else str(member) for member in manager.members]

    needed_specs = DynamicAgentFactory.evaluate_agent_needs(task_description, available_agent_names)

    created_agents = []
    for spec in needed_specs:
        try:
            new_agent = create_dynamic_agent(spec)
            created_agents.append(new_agent)
        except Exception as e:
            print(f"❌ Error creando agente dinámico: {e}")

    return created_agents

manager = Team(
    name="Nexus Manager",
    members=base_members,  # Start with base members
    model=get_openrouter_model(max_tokens=10000), # Nemotron via OpenRouter
    tools=[
        FileTools(),
        VisualizationSkills(),
        DocsSkills(),
        ResearchSkills(),
        QualitySkills(),
        TriageSkills(),
        SourceValidationSkills(),
        DataNormalizationSkills(),
        SynthesisSkills(),
        WorkflowSkills(),
        RiskSkills(),
        MemorySkills(),
        ToolDecisionSkills(),
        ContextCompressionSkills(),
        DecisionLogSkills(),
        # Dynamic Agent Creation Tools
        Function(
            name="evaluate_and_create_agents",
            description="Evalúa la tarea y crea agentes dinámicos si son necesarios",
            parameters={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Descripción de la tarea a evaluar"
                    }
                },
                "required": ["task_description"]
            },
            function=evaluate_and_create_agents
        ),
        Function(
            name="create_dynamic_agent",
            description="Crea un agente dinámico con especificaciones dadas",
            parameters={
                "type": "object",
                "properties": {
                    "agent_spec": {
                        "type": "object",
                        "description": "Especificación del agente a crear",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "instructions": {"type": "array", "items": {"type": "string"}},
                            "tools": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "required": ["agent_spec"]
            },
            function=create_dynamic_agent
        ),
    ],  # Manager can create/read mission plans
    description="You are Nexus Lead, coordinator of specialized elite squads. You lead the Data Intelligence Squad, the Knowledge Squad, and the Development Squad.",
    instructions=[
        "Rol: Coordinador Nexus. Orquesta equipos con calidad y evidencia.",
        "EVALUACIÓN DINÁMICA: Al inicio de cada tarea, evalúa si necesitas agentes especializados adicionales usando evaluate_and_create_agents().",
        "CREACIÓN DE AGENTES: Si determinas que necesitas un agente nuevo, proporciona especificaciones JSON claras y llama create_dynamic_agent() con el spec.",
        "Ejemplo de spec: {\"name\": \"CryptoAnalyst\", \"role\": \"Analista de criptomonedas\", \"instructions\": [\"Analizar tendencias crypto\"], \"tools\": [\"YFinance\", \"ResearchSkills\"]}",
        "Planifica si la solicitud es compleja; delega por escuadrón según especialidad.",
        "Reviewer es obligatorio antes de la entrega final.",
        "No inventes datos. Cita fuentes verificables y explicita limitaciones.",
        "Formato de salida: Estado, Resumen, Hallazgos, Recomendaciones, Detalles por escuadrón, Fuentes, Artifacts, Próximos pasos.",
        "Política de archivos: cada tarea genera un artefacto en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/<agente>/.",
        "Usa FileTools para planes en workspace/mission_plans/ y mantén el plan actualizado.",
        "Reporta progreso con update_squad_status y coordina el cierre con Reviewer.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    db=SqliteDb(db_file="agent.db", session_table="nexus_team_sessions"),
    add_history_to_context=True,
    markdown=True,
    show_members_responses=True,  # Show what sub-agents say (useful for stream)
)
