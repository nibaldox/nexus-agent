from agno.agent import Agent
from agents.provider import get_openrouter_model
from datetime import datetime
from tools.code_execution_tools import (
    python_executor,
    node_executor,
    shell_executor,
    file_reader,
    file_writer,
    package_installer
)
from tools.squad_tools import update_squad_status

frontend_expert = Agent(
    name="Frontend Expert",
    role="Frontend Development Specialist",
    instructions=[
        f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}",
        "Eres el **Frontend Expert** del escuadrón de desarrollo.",
        "Construyes UI claras, accesibles y coherentes con el backend.",
        "Guías:",
        "- Cambios mínimos en componentes y estilos.",
        "- Evita duplicar lógica; integra con APIs existentes.",
        "- Explica el resultado esperado si no puedes renderizar.",
        "Entrega:",
        "- Reporta progreso con update_squad_status.",
        "- Guarda artefacto en `workspace/conversations/{NEXUS_SESSION_ID}/artifacts/frontend/`.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo.",
        "THOUGHT PROCESS: Piensa paso a paso antes de ejecutar código. Verifica dependencias y estructura antes de escribir."
    ],
    tools=[
        node_executor,
        shell_executor,
        file_reader,
        file_writer,
        package_installer,
        update_squad_status
    ],
    model=get_openrouter_model(max_tokens=10000),
    markdown=True
)
