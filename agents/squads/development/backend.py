from agno.agent import Agent
from agents.provider import get_openrouter_model
from datetime import datetime
from tools.code_execution_tools import (
    python_executor,
    node_executor,
    shell_executor,
    file_reader,
    file_writer,
    package_installer,
    execute_python_code
)
from tools.squad_tools import update_squad_status

backend_expert = Agent(
    name="Backend Expert",
    role="Backend & API Architecture Specialist",
    instructions=[
        f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}",
        "Eres el **Backend Expert** del escuadrón de desarrollo.",
        "Prioriza APIs claras, validación y manejo de errores.",
        "Guías:",
        "- Implementa endpoints y modelos con cambios mínimos.",
        "- Documenta rutas y supuestos clave.",
        "- Coordina con Frontend/DevOps cuando aplique.",
        "Entrega:",
        "- Reporta progreso con update_squad_status.",
        "- Guarda artefacto en `workspace/conversations/{NEXUS_SESSION_ID}/artifacts/backend/`.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo.",
        "THOUGHT PROCESS: Piensa paso a paso antes de ejecutar código. Verifica dependencias y estructura antes de escribir."
    ],
    tools=[
        python_executor,
        node_executor,
        shell_executor,
        file_reader,
        file_writer,
        package_installer,
        update_squad_status,
        execute_python_code
    ],
    model=get_openrouter_model(max_tokens=10000),
    markdown=True
)
