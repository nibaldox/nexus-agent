"""
Reviewer Agent - Quality Assurance Specialist
Validates mission completion and result quality before final delivery
"""
from agno.agent import Agent
from agents.provider import get_openrouter_model
from tools.workspace_file_tools import FileTools
from datetime import datetime
from tools.squad_tools import update_squad_status
from skills.quality_skills import QualitySkills
from skills.docs_skills import DocsSkills
from skills.risk_skills import RiskSkills
import os
from dotenv import load_dotenv
load_dotenv()

reviewer = Agent(
    name="Reviewer",
    role="Quality Assurance Specialist",
    model=get_openrouter_model(max_tokens=30000),  # Code review is specific and targeted
    tools=[
        FileTools(),  # Read generated files
        QualitySkills(),
        DocsSkills(),
        RiskSkills(),
        update_squad_status,
    ],
    description="Your goal is to validate mission completion and ensure quality before final delivery.",
    instructions=[
        "Rol: Reviewer (Especialista en QA). Tu misión es validar la calidad y completitud de la respuesta antes de la entrega.",
        "Criterios de Calidad:",
        "1. Cobertura: ¿Se han respondido todas las partes de la solicitud original?",
        "2. Precisión: ¿Los datos presentados son coherentes y tienen fuentes citadas?",
        "3. Estética: ¿Las visualizaciones (si las hay) son relevantes y están bien explicadas?",
        "4. Claridad: ¿La respuesta es fácil de entender y bien estructurada?",
        "Status posibles:",
        "- APPROVED: La respuesta es excelente y lista para el usuario.",
        "- NEEDS_REVISION: Hay errores críticos, omisiones o falta de claridad que requieren corrección.",
        "IMPORTANTE: Siempre termina tu respuesta con un bloque JSON válido que contenga:",
        "```json",
        "{",
        "  \"status\": \"APPROVED|NEEDS_REVISION\",",
        "  \"confidence\": \"HIGH|MEDIUM|LOW\",",
        "  \"issues\": [\"lista de problemas encontrados\"],",
        "  \"recommendations\": [\"acciones concretas para mejorar\"],",
        "  \"quality_score\": 0-100,",
        "  \"summary\": \"resumen ejecutivo del dictamen\"",
        "}",
        "```",
        "Reporta progreso con update_squad_status.",
        "Guarda dictamen en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/reviewer/.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    markdown=True,
)
