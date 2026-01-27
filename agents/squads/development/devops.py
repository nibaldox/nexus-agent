from agno.agent import Agent
from agents.provider import get_openrouter_model
from datetime import datetime
from tools.code_execution_tools import (
    shell_executor,
    file_reader,
    file_writer,
    package_installer
)
from tools.squad_tools import update_squad_status

devops_expert = Agent(
    name="DevOps Expert",
    role="Infrastructure & Deployment Specialist",
    instructions=[
        f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}",
        "Eres el **DevOps Expert** del escuadrón de desarrollo.",
        "Enfócate en despliegue reproducible y configuración segura.",
        "Guías:",
        "- Valida configuración existente antes de cambiar.",
        "- Docker/Compose y scripts simples.",
        "- Documenta comandos y variables de entorno.",
        "Entrega:",
        "- Reporta progreso con update_squad_status.",
        "- Guarda artefacto en `workspace/conversations/{NEXUS_SESSION_ID}/artifacts/devops/`.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo.",
        "THOUGHT PROCESS: Piensa paso a paso antes de ejecutar código. Verifica dependencias y estructura antes de escribir."
    ],
    tools=[
        shell_executor,
        file_reader,
        file_writer,
        package_installer,
        update_squad_status
    ],
    model=get_openrouter_model(max_tokens=10000),
    markdown=True
)
