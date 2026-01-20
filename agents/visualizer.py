"""
Visualizer Agent - Specialized in creating charts and managing files
"""
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agents.chart_tools import ChartTools
from agno.tools.file import FileTools
from agno.tools.local_file_system import LocalFileSystemTools
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

visualizer = Agent(
    name="Visualizer",
    role="Data Visualization Specialist",
    model=OpenRouter(id="nvidia/nemotron-3-nano-30b-a3b:free", max_tokens=8192),
    tools=[
        ChartTools(),  # Create line, bar, pie, scatter, area, histogram, and box plots
        FileTools(),  # Read and write files
        LocalFileSystemTools(),  # Manage local file system
    ],
    description="Your goal is to create beautiful visualizations and manage files.",
    instructions=[
        "Eres un especialista en visualización: crea gráficos claros, etiquetados y listos para presentación.",
        f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}.",
        "Cuando recibas datos, primero valida su formato y rango; si faltan valores, rellena o avisa al usuario.",
        "Devuelve una especificación mínima para `ChartTools`: {type, width, height, x_label, y_label, x_values, y_values, title}.",
        "Guarda la imagen en `frontend/assets/charts/` y devuelve un enlace markdown con alt text y una breve interpretación (1–2 frases).",
        "Prefiere gráficos simples y legibles: evita sobrecargar con demasiadas series en una sola vista.",
        "Si el usuario no indica tipo de gráfico, sugiere la mejor opción (1–2) y pide confirmación si hay ambigüedad.",
    ],
    markdown=True,
)
