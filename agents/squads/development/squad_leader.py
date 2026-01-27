from agno.agent import Agent
from agno.team import Team
from agents.provider import get_openrouter_model
from tools.workspace_file_tools import FileTools
from datetime import datetime
from tools.squad_tools import update_squad_status, get_squad_status, create_shared_variable, get_shared_variable

# Import specialists
from agents.squads.development.frontend import frontend_expert
from agents.squads.development.backend import backend_expert
from agents.squads.development.devops import devops_expert
from agents.squads.development.ml_expert import ml_expert

dev_squad = Team(
    name="Development Squad",
    members=[frontend_expert, backend_expert, devops_expert, ml_expert],
    model=get_openrouter_model(max_tokens=50000),
    tools=[FileTools(), update_squad_status, get_squad_status, create_shared_variable, get_shared_variable],
    instructions=[
        f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}",
        "Eres el líder del escuadrón de Desarrollo.",
        "Delegas a Frontend, Backend, DevOps y ML según necesidad.",
        "Reglas:",
        "- Define arquitectura y puntos de integración.",
        "- Revisa calidad antes de entregar al Manager.",
        "- Exige artefactos a cada miembro.",
        "Entrega:",
        "- Reporta progreso con update_squad_status.",
        "- Guarda síntesis en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/development_lead/.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    show_members_responses=True,
    markdown=True
)
