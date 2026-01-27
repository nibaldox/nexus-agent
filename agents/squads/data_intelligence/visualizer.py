"""
Visualizer Agent - Specialized in creating charts and managing files
"""
from agno.agent import Agent
from agents.provider import get_openrouter_model
from agents.chart_tools import ChartTools
from tools.workspace_file_tools import FileTools
from datetime import datetime
from tools.squad_tools import update_squad_status
from skills.visualization_skills import VisualizationSkills
import os
from dotenv import load_dotenv
load_dotenv()

visualizer = Agent(
    name="Visualizer",
    role="Data Visualization Specialist",
    model=get_openrouter_model(max_tokens=30000),
    tools=[
        ChartTools(),  # Create line, bar, pie, scatter, area, histogram, and box plots
        FileTools(),  # Read and write files
        VisualizationSkills(),
        update_squad_status,
    ],
    description="Your goal is to create beautiful, professional visualizations using ChartTools ONLY. Never create HTML files manually.",
    instructions=[
        "Rol: Visualizador. Usa ChartTools obligatoriamente para crear gráficos.",
        "Prohibido crear HTML/JS manual o usar write_file para gráficos.",
        "Valida datos: x_values y y_values con misma longitud y unidades claras.",
        "Elige el tipo de gráfico adecuado y titula con contexto temporal.",
        "Entrega: gráfico embebido, ruta del archivo y breve interpretación.",
        "Reporta progreso con update_squad_status.",
        "Guarda artefacto en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/visualizer/.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    markdown=True,
)
