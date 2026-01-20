from agno.agent import Agent
from agno.team import Team
from agno.models.openrouter import OpenRouter
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
from datetime import datetime

# Import Specialists
from agents.researcher import researcher
from agents.analyst import analyst
from agents.librarian import librarian
from agents.visualizer import visualizer

load_dotenv()

manager = Team(
    name="Nexus Manager",
    members=[researcher, analyst, librarian, visualizer],
    model=OpenRouter(id="nvidia/nemotron-3-nano-30b-a3b:free", max_tokens=200000),
    description="You are Nexus Lead, coordinator of an advanced research team. You have access to a Researcher, an Analyst, a Librarian, and a Visualizer.",
    instructions=[
        "Eres el coordinador del equipo: decide rápidamente qué especialista ejecutar y sintetiza las respuestas en un único resultado claro y accionable.",
        "Antes de delegar, haz 1–2 preguntas rápidas de clarificación si la tarea es ambigua.",
        "Asigna tareas así: Finanzas -> Analyst; Búsqueda web general -> Researcher; Documentos locales -> Librarian; Gráficos/archivos -> Visualizer.",
        "Cuando llames a sub-agentes, solicita salidas estructuradas (json o lista) para facilitar la síntesis.",
        "Recopila las respuestas de los miembros, filtra duplicados, prioriza evidencia con fuentes y devuelve: 1) resumen de 3 viñetas, 2) detalles esenciales y 3) fuentes.",
        "Si los sub-agentes divergen, indica claramente las diferencias y tu recomendación preferida con su justificación breve.",
        "Mantén la síntesis breve por defecto (máx. 250 palabras) y ofrece pasos de seguimiento concretos.",
    ],
    db=SqliteDb(db_file="agent.db", session_table="nexus_team_sessions"),
    add_history_to_context=True,
    markdown=True,
    show_members_responses=True, # Show what sub-agents say (useful for stream)
)
