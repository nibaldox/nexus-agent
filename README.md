
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
# ⚡ Nexus Agent (Fusión de IA Avanzada)

![Interfaz Nexus](frontend/screen.png)

`Nexus Agent` es un framework multi-agente para orquestar especialistas (Researcher, Analyst, Librarian, Visualizer) con una interfaz web ligera, RAG local y herramientas de búsqueda.

## Novedades (Resumen rápido)

- Agregado `SerperTools` (Serper.dev) y ampliadas las capacidades de búsqueda: DuckDuckGo, WebSearch, Website tools, HackerNews, Exa, Arxiv, Newspaper.
- Nuevo agente `Visualizer` + `ChartTools` con gráficos modernos (line, bar, pie, scatter, area, histogram, box plot).
- Interfaz responsive y barra lateral colapsable (toggle persistente en `localStorage`).
- Mejor experiencia: auto-scroll inteligente, salida de búsquedas formateada y subida de PDFs para ingestión RAG.

## Características principales

- Orquestación Multi-Agente usando `agno`.
- RAG local con `LanceDB` para vectores y búsqueda en documentos.
- Búsqueda web multi-backend y extracción de noticias.
- Visualizaciones generadas por `ChartTools` (guardadas en `frontend/assets/charts`).
- UI: FastAPI backend + Vanilla JS + Tailwind, SSE para streaming.

## Requisitos

- Python 3.10+ (se recomienda 3.11+)
- Entorno virtual (`venv`)
- `requirements.txt` contiene dependencias principales

## Instalación y ejecución

1. Clona el repositorio:

```bash
git clone https://github.com/nibaldox/nexus-agent.git
cd nexus-agent
```

2. Crea y activa un entorno virtual:

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Crea `.env` con claves necesarias (opcional según tu configuración):

```ini
OPENAI_API_KEY=sk-...
SERPER_API_KEY=sk-...   # para SerperTools
EXA_API_KEY=...         # si usas Exa
```

5. Ejecuta el servidor:

```bash
.
# Windows (incluido run.bat):
# run.bat  (doble clic o ejecutar en PowerShell)

# Ejecución manual:
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

Abre http://127.0.0.1:8000 en tu navegador.

## Uso y notas rápidas

- Sidebar colapsable: haz clic en el botón superior izquierdo (el estado se guarda en `localStorage`).
- Subida de PDFs: usa el botón de adjuntar para agregar documentos al índice RAG.
- Visualizaciones: el agente `Visualizer` puede crear gráficos y los resultados se almacenan en `frontend/assets/charts/`.
- Búsquedas: el `Researcher` tiene varias herramientas; si usas Serper asegúrate de añadir `SERPER_API_KEY`.

## Estructura destacada

- `agents/` — definiciones de agentes (Researcher, Analyst, Librarian, Visualizer, etc.)
- `frontend/` — UI estática, JS y CSS; `responsive.css` contiene las reglas responsive y de toggle
- `api.py` — FastAPI app y endpoints (chat, upload)
- `workspace/knowledge` — arrastra PDFs aquí para ingestión local

## Contribuir

- Abrir issues para bugs o features.
- Crear branches temáticos y enviar pull requests.

## Licencia

MIT

---

_Última actualización: 2026-01-20_
