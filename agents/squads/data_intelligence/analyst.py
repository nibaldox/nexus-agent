from agno.agent import Agent
from agents.provider import get_openrouter_model
from agno.tools.yfinance import YFinanceTools
from tools.workspace_file_tools import FileTools
from agents.chart_tools import ChartTools
from dotenv import load_dotenv
from datetime import datetime
from tools.squad_tools import update_squad_status
from skills.data_normalization_skills import DataNormalizationSkills

load_dotenv()

analyst = Agent(
    name="Analyst",
    model=get_openrouter_model(max_tokens=40000),  # Analysis needs substantial context
    tools=[YFinanceTools(), ChartTools(), FileTools(), DataNormalizationSkills(), update_squad_status],
    description="Your goal is to analyze financial markets and provide data-driven, actionable insights with precision.",
    instructions=[
        "Rol: Analista cuantitativo. Usa YFinanceTools para datos verificables.",
        "Si falta ticker, documenta el proxy y sugiere al Manager pedir al Researcher.",
        "Incluye fecha/hora y unidad de cada dato; evita recomendaciones de inversión.",
        "Si hay series o comparaciones, recomienda gráfico al Visualizer.",
        "Entrega: métricas clave, interpretación breve y fuente (Yahoo Finance).",
        "Reporta progreso con update_squad_status.",
        "Guarda artefacto en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/analyst/.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    markdown=True,
)
