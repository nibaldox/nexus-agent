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
from dotenv import load_dotenv
from datetime import datetime

# Import Squads
from agents.squads.development.squad_leader import dev_squad
from agents.squads.data_intelligence.squad_leader import data_intelligence_squad
from agents.squads.knowledge.squad_leader import knowledge_squad
from agents.squads.knowledge.reviewer import reviewer

load_dotenv()

manager = Team(
    name="Nexus Manager",
    members=[data_intelligence_squad, knowledge_squad, dev_squad, reviewer],
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
    ],  # Manager can create/read mission plans
    description="You are Nexus Lead, coordinator of specialized elite squads. You lead the Data Intelligence Squad, the Knowledge Squad, and the Development Squad.",
    instructions=[
        "Rol: Coordinador Nexus. Orquesta equipos con calidad y evidencia.",
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
