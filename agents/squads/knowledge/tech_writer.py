from agno.agent import Agent
from agents.provider import get_openrouter_model
from datetime import datetime
from tools.code_execution_tools import file_reader, file_writer
from tools.squad_tools import update_squad_status
from skills.docs_skills import DocsSkills
from skills.synthesis_skills import SynthesisSkills

tech_writer = Agent(
    name="Technical Writer",
    role="Technical Documentation Specialist",
    instructions=[
        f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}",
        "Eres el **Technical Writer** del escuadrón de conocimiento.",
        "Transformas hallazgos técnicos en documentación clara y profesional.",
        "Formato sugerido:",
        "- Título",
        "- Resumen ejecutivo",
        "- Secciones con encabezados",
        "- Conclusiones y próximos pasos",
        "Reglas:",
        "- Usa Markdown por defecto; HTML solo si se solicita.",
        "- Enlaza gráficos y referencias cuando existan.",
        "- Reporta progreso con update_squad_status.",
        "- Guarda artefacto en `workspace/conversations/{NEXUS_SESSION_ID}/artifacts/technical_writer/`.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    tools=[DocsSkills(), SynthesisSkills(), file_reader, file_writer, update_squad_status],
    model=get_openrouter_model(max_tokens=30000),  # Technical writing is focused and structured
    markdown=True
)
