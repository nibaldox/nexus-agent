from agno.agent import Agent
from agno.team import Team
from agents.provider import get_openrouter_model
from tools.workspace_file_tools import FileTools
from datetime import datetime
from tools.squad_tools import update_squad_status, get_squad_status, create_shared_variable, get_shared_variable

# Import specialists
from agents.squads.data_intelligence.researcher import researcher
from agents.squads.data_intelligence.analyst import analyst
from agents.squads.data_intelligence.visualizer import visualizer

data_intelligence_squad = Team(
    name="Data Intelligence Squad",
    members=[researcher, analyst, visualizer],
    model=get_openrouter_model(max_tokens=50000),
    instructions=[
        f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}",
        "Eres el líder del escuadrón de Inteligencia de Datos.",
        "Delegas a Researcher (fuentes), Analyst (métricas) y Visualizer (gráficos).",
        "Reglas:",
        "- Define criterios de éxito por tarea.",
        "- Sintetiza resultados y riesgos para el Manager.",
        "- Exige artefactos a cada miembro.",
        "Entrega:",
        "- Reporta progreso con update_squad_status.",
        "- Guarda síntesis en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/data_intelligence_lead/.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    tools=[FileTools(), update_squad_status, get_squad_status, create_shared_variable, get_shared_variable],
    show_members_responses=True,
    markdown=True
)
