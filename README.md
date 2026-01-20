
# ⚡ Nexus Agent (Advance AI Fusion)

![Nexus Interface](frontend/screen.png)

**Nexus Agent** is an advanced, multi-agent AI framework with a sleek Cyberpunk web interface. It goes beyond simple chatbots by orchestrating a team of specialized agents, managing local memory (RAG), and providing rich, interactive visualizations.

## 🚀 Key Features

### 🤖 Multi-Agent Orchestration
Nexus utilizes a **Manager-Specialist** architecture powered by `agno`:
*   **👔 Nexus Manager**: The team lead. Orchestrates tasks, understands user intent, and delegates work to specialists.
*   **🕵️ Researcher**: Specializes in real-time web search (DuckDuckGo).
*   **📊 Analyst**: Specializes in financial data and market analysis (YFinance).
*   **📚 Librarian**: Manages local knowledge. Ingests and retrieves information from PDF documents (RAG).

### 🧠 Local RAG (Retrieval-Augmented Generation)
*   **Vector Database**: Uses `LanceDB` for high-performance local vector storage.
*   **Knowledge Base**: Simply drop PDFs into `workspace/knowledge` or upload them via the UI. Nexus will index and cite them in answers.

### 💻 Interactive Cyberpunk UI
*   **Tech Stack**: FastAPI (Backend) + Vanilla JS/Tailwind (Frontend).
*   **Streaming**: Real-time Server-Sent Events (SSE) for fluid responses.
*   **Tool Cards**: Interactive, collapsible cards showing the *thought process* and *tool outputs* (e.g., search results, code execution) separate from the chat.
*   **Agent Visualization**: Distinct visual cues (Purple Bubbles) when a sub-agent speaks to the Manager.

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.10+
*   Node.js (optional, for frontend dev, but vanilla JS works out of the box)
*   Standard Python toolchain (pip, venv)

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/nibaldox/nexus-agent.git
cd nexus-agent

# Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```ini
OPENAI_API_KEY=sk-your-key... (Required for Embeddings)
OPENROUTER_API_KEY=sk-your-key... (Required for LLM Models)
```

### 3. Running the System
Start the FastAPI server (serves both API and Static Frontend):
```bash
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at **http://127.0.0.1:8000**

## 📂 Project Structure

*   `agents/`: Definitions for Manager and Sub-agents.
*   `api.py`: FastAPI endpoints (`/chat`, `/upload`).
*   `frontend/`: HTML/CSS/JS files.
    *   `js/main.js`: Core logic for SSE and Event handling.
    *   `js/ui.js`: DOM manipulation and component rendering.
*   `workspace/knowledge`: Drop your PDFs here for ingestion.

## 📸 Screenshots

### Multi-Agent Delegation
*Nexus Manager delegating a stock analysis task to the Analyst.*
*(See `walkthrough.md` for more visuals)*

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## 📜 License
MIT
