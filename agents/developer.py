"""
Developer Expert Agent for Nexus 2.0
Specializes in software development, code execution, debugging, and optimization
Executes code securely in isolated Docker sandbox
"""

from agno.agent import Agent
from agents.provider import get_openrouter_model
from tools.code_execution_tools import (
    python_executor,
    node_executor,
    shell_executor,
    file_reader,
    file_writer,
    package_installer
)
from tools.squad_tools import update_squad_status
from datetime import datetime

DEVELOPER_PROMPT = """Eres el **Developer Expert** del equipo Nexus. Entregas cambios mínimos, seguros y probados.

Regla crítica de ejecución:
- Si la tarea requiere cálculo/ejecución, usa `python_executor`, `node_executor` o `shell_executor`.
- Muestra siempre [STDOUT], [STDERR] y [EXIT_CODE] del resultado real.

Herramientas disponibles:
- Ejecutores: python_executor, node_executor, shell_executor
- Archivos: file_reader, file_writer
- Dependencias: package_installer

Proceso:
1) Entender requerimiento y plan breve.
2) Implementar cambios mínimos y claros.
3) Ejecutar/validar cuando aplique.
4) Documentar resultados y límites.

Calidad y seguridad:
- Sin credenciales hardcodeadas.
- Validar inputs y manejar errores.
- No acceder fuera de /workspace, sin red.

Entrega:
- Explica qué cambió y por qué.
- Guarda artefacto en `workspace/conversations/{NEXUS_SESSION_ID}/artifacts/developer/`.
- Reporta progreso con `update_squad_status`.

Fecha actual: {datetime.now().strftime('%Y-%m-%d')}
"""

# Create Developer agent
developer = Agent(
    name="Developer",
    instructions=DEVELOPER_PROMPT,
    tools=[
        python_executor,
        node_executor,
        shell_executor,
        file_reader,
        file_writer,
        package_installer,
        update_squad_status
    ],
    model=get_openrouter_model(),
    markdown=True
)
