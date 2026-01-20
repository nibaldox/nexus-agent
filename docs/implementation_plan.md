
# Plan de Implementación de Mejoras (Fase 2)

## Etapa 7: Interfaz Web (Custom UI)
**Objetivo:** Hacer funcional el mockup `frontend/code.html` y conectarlo a Nexus.

### Hallazgos
- `frontend/code.html` es un diseño estático (mockup) sin lógica JavaScript.
- No hace ninguna llamada a API actualmente.

### Plan Actualizado
1.  **Backend (`api.py`):**
    -   Crear servidor FastAPI.
    -   Endpoint `POST /chat`: Recibe `{message: str}` y devuelve stream o texto.
    -   Habilitar CORS para permitir llamadas desde el archivo local/servidor frontend.

2.  **Frontend Logic (`frontend/code.html`):**
    -   **Inyectar Script:** Agregar JavaScript al final del body.
    -   **Eventos:** Escuchar clicks en botón "Exec" y Enter en textarea.
    -   **DOM Manipulation:**
        -   Capturar valor del textarea.
        -   Crear elementos HTML dinámicos para los mensajes del usuario.
        -   Llamar a `fetch('http://localhost:8000/chat')`.
        -   Renderizar respuesta de Nexus (idealmente soportando Markdown simple o texto plano por ahora).

### Stack Propuesto
-   **Backend:** FastAPI + Uvicorn + Agno Agent.
-   **Frontend:** Vanilla JS (inyectado en el HTML existente).

## Etapa 7b: Refinamiento de UI (Markdown & Tools)
1.  **Markdown Styling (Beautiful):**
    -   **Tipografía**: Aplicar clase `prose prose-invert` (Tailwind Typography) al contenedor del mensaje para estilizar automáticamente listas, encabezados y párrafos.
    -   **Highlighting**: Integrar `highlight.js` para coloreado de sintaxis en bloques de código.
    -   **Tema**: Ajustar colores de `prose` para coincidir con la paleta Cyberpunk (Cyan/Orange).
2.  **Tool Cards:**
    -   (Completado) Implementado sistema de tarjetas expandibles.

## Etapa 7c: Time Awareness & Timestamps
**Objetivo:** Agente consciente del tiempo y UI informativa.
1.  **Backend (Time Awareness):**
    -   Inyectar fecha/hora actual en las instrucciones del Agente (`agent.py`).
2.  **Frontend (UI Timestamps):**
    -   Actualizar `ui.js` (`createOperatorBubble`, `createAgentBubble`) para mostrar hora local `HH:MM`.
    -   Estilizar timestamp con opacidad reducida y fuente mono.

## Etapa 7d: Smart Autoscroll
**Objetivo:** Mejorar UX evitando saltos bruscos.
1.  **Frontend (Scroll Logic):**
    -   Detectar si el usuario está al final (`scrollTop + clientHeight ≈ scrollHeight`).
    -   Solo aplicar `scrollTop = scrollHeight` si el usuario estaba al final.
    -   Permitir leer historial sin interrupciones durante el streaming.

## Etapa 8: Base de Conocimiento (RAG) 🧠
**Objetivo:** Permitir al agente leer y "recordar" información de documentos PDF localmente.
1.  **Instalación de Dependencias:**
    -   `lancedb`: Base de datos vectorial local (rápida, sin servidor).
    -   `tantivy`: Motor de búsqueda para LanceDB.
    -   `pypdf`: Para leer archivos PDF.
    -   `xmltodict`: Dependencia común para parsing.
2.  **Backend (Conocimiento):**
    -   Crear carpeta `workspace/knowledge`.
    -   Modificar `agent.py` para integrar `VectorKnowledgeBase` (o `PDFUrlKnowledgeBase` para pruebas, pero usaremos `PDFKnowledgeBase` local).
    -   Configurar `LanceDb` como vector store.
    -   **Embeddings**: Usar `OpenAIEmbeddings` (requiere key) o `HuggingFaceEmbeddings` (local/gratis). *Por defecto usaremos OpenAI si la key está disponible, o OllamaEmbeddings si el usuario prefiere local.*
3.  **Integración en Agente:**
    -   Añadir el objeto `knowledge_base` al constructor del Agente.
    -   Habilitar `show_tool_calls=True` (ya activo) y `search_knowledge` tool.
    -   (Completado) Verificar que `search_knowledge_base` aparezca como tarjeta de herramienta.

## Etapa 9: Arquitectura Multi-Agente 🤖
**Objetivo:** Transición de un Agente Generalista a un Equipo Especializado liderado por un Manager.

### Estructura Propuesta
1.  **Manager Agent (Nexus Lead)**:
    -   Orquesta la conversación.
    -   Delega tareas a especialistas.
    -   Sintetiza respuestas finales.
2.  **Specialist Agents**:
    -   🕵️‍♂️ **Researcher**: Experto en búsqueda web (DuckDuckGo).
    -   📊 **Analyst**: Experto financiero (YFinance).
    -   📚 **Librarian**: Gestor de conocimiento (RAG/PDFs).

### Plan de Refactorización
1.  **Directorio `agents/`**:
    -   Crear módulos separados para cada rol (`researcher.py`, `analyst.py`, `librarian.py`).
2.  **Agente Principal (`agent.py`)**:
    -   Reconfigurar para usar el modo `Team` o `Agent(team=[...])` de Agno.
    -   Instrucciones para delegar explícitamente.
3.  **UI Updates**:
    -   Reflejar qué agente está actuando (si es posible vía eventos de `stream`).
