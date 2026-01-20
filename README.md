
# ⚡ Nexus Agent (Fusión de IA Avanzada)

![Interfaz Nexus](frontend/screen.png)

**Nexus Agent** es un framework avanzado de IA multi-agente con una elegante interfaz web estilo Cyberpunk. Va más allá de los chatbots simples al orquestar un equipo de agentes especializados, gestionar memoria local (RAG) y proporcionar visualizaciones ricas e interactivas.

## 🚀 Características Clave

### 🤖 Orquestación Multi-Agente
Nexus utiliza una arquitectura **Gerente-Especialista** impulsada por `agno`:
*   **👔 Nexus Manager**: El líder del equipo. Orquesta tareas, entiende la intención del usuario y delega el trabajo a los especialistas.
*   **🕵️ Researcher**: Especialista en búsqueda web en tiempo real (DuckDuckGo).
*   **📊 Analyst**: Especialista en datos financieros y análisis de mercado (YFinance).
*   **📚 Librarian**: Gestiona el conocimiento local. Ingiere y recupera información de documentos PDF (RAG).

### 🧠 RAG Local (Generación Aumentada por Recuperación)
*   **Base de Datos Vectorial**: Usa `LanceDB` para almacenamiento vectorial local de alto rendimiento.
*   **Base de Conocimiento**: Simplemente arrastra PDFs a `workspace/knowledge` o súbelos vía UI. Nexus los indexará y citará en sus respuestas.

### 💻 UI Cyberpunk Interactiva
*   **Stack Tecnológico**: FastAPI (Backend) + Vanilla JS/Tailwind (Frontend).
*   **Streaming**: Server-Sent Events (SSE) en tiempo real para respuestas fluidas.
*   **Tarjetas de Herramientas**: Tarjetas interactivas y colapsables que muestran el *proceso de pensamiento* y *salidas de herramientas* (ej. resultados de búsqueda, ejecución de código) separados del chat.
*   **Visualización de Agentes**: Señales visuales distintivas (Burbujas Moradas) cuando un sub-agente habla con el Manager.

## 🛠️ Instalación y Configuración

### Requisitos Previos
*   Python 3.10+
*   Node.js (opcional, para desarrollo frontend, pero vanilla JS funciona directo)
*   Herramientas estándar de Python (pip, venv)

### 1. Configuración del Backend
```bash
# Clonar el repositorio
git clone https://github.com/nibaldox/nexus-agent.git
cd nexus-agent

# Crear y activar entorno virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración
Crea un archivo `.env` en el directorio raíz:
```ini
OPENAI_API_KEY=sk-tu-clave... (Requerido para Embeddings)
OPENROUTER_API_KEY=sk-tu-clave... (Requerido para Modelos LLM)
```

### 3. Ejecución Rápida (Windows) 🚀
¡Haz doble clic en el archivo `run.bat`!

Este script automatizado:
1.  Activará el entorno virtual.
2.  Iniciará el servidor backend.
3.  Abrirá tu navegador automáticamente en la interfaz.

### Ejecución Manual
Si prefieres hacerlo paso a paso:
```bash
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
Abre tu navegador en **http://127.0.0.1:8000**

## 📂 Estructura del Proyecto

*   `agents/`: Definiciones para Manager y Sub-agentes.
*   `api.py`: Endpoints de FastAPI (`/chat`, `/upload`).
*   `frontend/`: Archivos HTML/CSS/JS.
    *   `js/main.js`: Lógica central para SSE y manejo de eventos.
    *   `js/ui.js`: Manipulación del DOM y renderizado de componentes.
*   `workspace/knowledge`: Arrastra tus PDFs aquí para ingestión.

## 📸 Capturas de Pantalla

### Delegación Multi-Agente
*Nexus Manager delegando una tarea de análisis de acciones al Analista.*
*(Ver `docs/walkthrough.md` para más visuales)*

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Por favor abre un issue o envía un pull request.

## 📜 Licencia
MIT
