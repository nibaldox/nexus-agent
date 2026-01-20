from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.websearch import WebSearchTools
from agno.tools.website import WebsiteTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.exa import ExaTools
from agno.tools.arxiv import ArxivTools
from agno.tools.newspaper import NewspaperTools
from agents.serper_tools import SerperTools

import os
from dotenv import load_dotenv
load_dotenv()

researcher = Agent(
    name="Researcher",
    role="Web Research Specialist",
    model=OpenRouter(id="nvidia/nemotron-3-nano-30b-a3b:free", max_tokens=8192),
    tools=[
        DuckDuckGoTools(),
        WebSearchTools(backend="auto"),  # Auto-selects best available backend (Google, Bing, Brave, etc.)
        WebsiteTools(),  # Scrape and read website content
        HackerNewsTools(),  # Search Hacker News for tech news
        ExaTools(api_key=os.getenv("EXA_API_KEY")),  # AI-powered search with categories
        ArxivTools(),  # Search scientific papers
        NewspaperTools(),  # Extract articles from news websites
        SerperTools(api_key=os.getenv("SERPER_API_KEY")),  # Google search via Serper.dev
    ],
    description="Your goal is to find accurate and up-to-date information on the web.",
    instructions=[
        "Eres un investigador web práctico: preciso, directo y orientado a evidencias.",
        "Evalúa qué herramienta usar antes de ejecutar búsquedas; prioriza fuentes confiables y evita redundancias.",
        "Devuelve para cada búsqueda: 1) Top-3 resultados con título y URL; 2) 1–2 frases de evidencia; 3) una síntesis de una frase.",
        "Siempre cita la(s) fuente(s) usadas y marca el nivel de confianza (Alto/Medio/Bajo).",
        "Si extraes contenido de páginas, devuelve solo los fragmentos relevantes y la URL.",
        "Si una consulta requiere datos numéricos recientes, incluye la fecha de la consulta y la fuente exacta.",
        "Haz hasta 2 preguntas de clarificación si la solicitud es ambigua antes de proceder.",
    ],
    markdown=True,
)
