
# Tareas para Agente General con Agno

## Fase 1: Fundamentos [COMPLETADA]
... (igual) ...

## Fase 2: Interactividad y Expansión [EN PROGRESO]
- [x] **Etapa 6: Modo Interactivo (CLI)** 💬
    - [x] Implementar bucle de chat continuo en `agent.py`.

- [x] **Markdown & Tables**: Implementado con buffer de streaming y estilos correjidos.
- [x] **Tool Cards**: Implementado visualización interactiva y robusta (eventos anidados, rich search).
- [x] **Time Awareness**: Timestamps en UI y contexto de tiempo en backend.
- [x] **Smart Autoscroll**: Detener scroll si el usuario sube manualmente.
- [x] **Etapa 8: Base de Conocimiento (RAG)** 🧠
    - [x] Instalar dependencias (`lancedb`, `pypdf`, `lancde`).
    - [x] Configurar `Knowledge` y `PDFReader` en `agent.py`.
    - [x] Verificar integración en UI (Tool Card `search_knowledge`).
    - [x] **File Upload**: Checkbox para endpoint y UI de subida.
    - [x] Levantar servidor API (`uvicorn`).
    - [x] **Refactorización**: Modularizar frontend (`html`, `js/`).


- [x] **Etapa 9: Arquitectura Multi-Agente** 🤖
    - [x] Crear estructura de carpetas `workspace/agents`.
    - [x] Implementar `Researcher Agent` (Web).
    - [x] Implementar `Analyst Agent` (Finance).
    - [x] Implementar `Librarian Agent` (RAG).
    - [x] Configurar `Manager Agent` (Nexus Lead) para orquestación.
    - [x] Refactorizar `api.py` para usar el Manager.

- [x] **Etapa 10: Visualización de Delegación** 👁️
    - [x] Identificar eventos de comunicación entre agentes (`TeamRunEvent`).
    - [x] Actualizar `api.py` para enviar metadata del agente (nombre/rol).
    - [x] Actualizar Frontend para mostrar "Tarjetas de Agente" (similar a Tools).
