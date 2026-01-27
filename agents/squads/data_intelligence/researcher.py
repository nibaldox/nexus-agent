from agno.agent import Agent
from agents.provider import get_openrouter_model
from agno.tools.duckduckgo import DuckDuckGoTools
from tools.workspace_file_tools import FileTools
from agents.serper_tools import SerperTools
from tools.squad_tools import update_squad_status
from skills.research_skills import ResearchSkills
from skills.source_validation_skills import SourceValidationSkills

import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

researcher = Agent(
    name="Researcher",
    role="Web Research Specialist",
    model=get_openrouter_model(max_tokens=50000),  # Research requires large context
    tools=[
        SerperTools(api_key=os.getenv("SERPER_API_KEY")),  # Primary search
        DuckDuckGoTools(),  # Fallback search
        FileTools(),
        ResearchSkills(),
        SourceValidationSkills(),
        update_squad_status,
    ],
    description="Your goal is to find accurate and up-to-date information on the web using Serper as primary search and DuckDuckGo as fallback.",
    instructions=[
        "Rol: Investigador web. Prioriza precisión, fechas y fuentes confiables.",
        "Herramientas: usa SerperTools primero; DuckDuckGo solo como fallback.",
        "Busca 2-4 fuentes relevantes y cruza datos críticos.",
        "Entrega: hallazgos clave, síntesis breve y URLs de fuentes.",
        "Si hay contradicción, reporta ambas fuentes y explica la diferencia.",
        "Si no hay resultados confiables, indícalo explícitamente.",
        "Reporta progreso con update_squad_status.",
        "Guarda artefacto en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/researcher/.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    markdown=True,
)
