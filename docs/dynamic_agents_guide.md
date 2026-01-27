# Ejemplo de Uso: Creación Dinámica de Agentes en Nexus

## ¿Cómo Funciona?

El Manager ahora puede evaluar automáticamente las necesidades de una tarea y crear agentes especializados dinámicos cuando sea necesario.

## Proceso de Evaluación

1. **Análisis Inicial**: El Manager evalúa la descripción de la tarea
2. **Determinación de Necesidades**: Identifica si los agentes existentes son suficientes
3. **Creación Dinámica**: Si falta especialización, crea agentes nuevos con:
   - Nombre único
   - Rol específico
   - Instrucciones detalladas
   - Herramientas apropiadas

## Ejemplo Práctico

**Tarea**: "Analizar el impacto de las criptomonedas en la economía global y crear un informe detallado"

**Evaluación del Manager**:
- Agentes existentes: Researcher, Analyst, Librarian, Visualizer, Reviewer
- Necesidad identificada: Agente especializado en cripto (CryptoAnalyst)

**Creación Dinámica**:
```json
{
  "name": "CryptoAnalyst",
  "role": "Especialista en análisis de criptomonedas y blockchain",
  "instructions": [
    "Analizar tendencias del mercado crypto",
    "Evaluar impacto económico de las criptomonedas",
    "Identificar riesgos y oportunidades",
    "Proporcionar análisis técnico y fundamental"
  ],
  "tools": ["YFinance", "ResearchSkills", "DataNormalizationSkills"]
}
```

## Beneficios

- **Adaptabilidad**: El sistema se adapta automáticamente a tareas nuevas
- **Especialización**: Agentes creados específicamente para la tarea
- **Eficiencia**: No requiere intervención manual para agregar agentes
- **Escalabilidad**: Puede crear múltiples agentes según complejidad

## Limitaciones Actuales

- Los agentes dinámicos existen solo durante la sesión actual
- Requiere prompts claros para definir correctamente los agentes
- Depende de la precisión del LLM para evaluar necesidades

## Uso en Código

```python
from agents.manager import evaluate_and_create_agents, create_dynamic_agent

# Evaluación automática
nuevos_agentes = evaluate_and_create_agents("Analizar mercado de cripto")

# Creación manual
spec = {
    "name": "CryptoExpert",
    "role": "Experto en criptomonedas",
    "instructions": ["Analizar tendencias", "Evaluar riesgos"],
    "tools": ["YFinance", "ResearchSkills"]
}
agente = create_dynamic_agent(spec)
```</content>
<parameter name="filePath">d:\12_WindSurf\42-Agents\10-Agent-Agno\02-general001\docs\dynamic_agents_guide.md