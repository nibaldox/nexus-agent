
# 🚀 Nexus AI Walkthrough

## 🌟 Overview
This project transforms a simple Agent script into a **full-fledged interactive AI Assistant ("Nexus")**.
Key features include a **Web UI**, **Multi-Agent Orchestration**, **Local RAG (Knowledge Base)**, and **Rich Tool Cards**.

## ✨ Features Implemented

### 1. **Interactive Web UI**
- **Tech Stack**: FastAPI (Backend) + Vanilla JS/HTML/CSS (Frontend).
- **Features**: 
  - Streaming responses (SSE).
  - Rich Markdown rendering (Tables, Code blocks).
  - **Tool Cards**: Expandable cards showing tool inputs/outputs (e.g., Search Results).
  - **Agent Identity**: "Nexus Interface" branding with Cyberpunk aesthetics.

### 2. **Multi-Agent Architecture** 🤖 [NEW]
- **Structure**: A "Manager" agent orchestrates a team of specialists.
- **Agents**:
  - **Manager (Nexus Lead)**: Interfaces with the user and delegates tasks.
  - **Researcher**: Uses DuckDuckGo for web searches.
  - **Analyst**: Uses YFinance for stock data.
  - **Librarian**: Manages the local PDF knowledge base (RAG).
- **Visual Delegation**:
  - Distinct purple bubbles for sub-agent responses (e.g., "ANALYST" speaking to Manager).
  - Clear separation of tools and conversation flow.

### 3. **Local RAG (Knowledge Base)** 🧠
- **Tech**: `LanceDb` (Vector Store) + `OpenAIEmbeddings`.
- **Functionality**:
  - **Ingestion**: Drop PDF files into `workspace/knowledge` (or use UI Upload).
  - **Retrieval**: Agent intelligently searches documents to answer queries.
  - **File Upload**: UI supports direct PDF upload to the knowledge base.

### 4. **Smart Autoscroll**
- **UX Improvement**: Chat only autoscrolls if the user is already at the bottom. Allows reading history during generation.

## 📸 Verification

### Sub-Agent Visualization (Delegation)
![Sub-Agent Bubble](images/sub_agent_purple_bubble_1768871494645.png)
*Nexus Manager delegating to Analyst. Note the distinct "ANALYST" bubble showing internal team communication.*

### Multi-Agent Interaction
![Multi-Agent Verification](images/nexus_multiagent_verification_1768867360885.png)
*Nexus Manager delegating to Librarian to find PDF documents.*

### Chat Restoration (Team Event Fix)
![Chat Restored](images/chat_restored_1768869707318.png)
*Verifying successful communication and delegation after fixing the Team Event stream issue.*

### Rich Search Cards
![Search Cards](../frontend/assets/search_card_demo.png) *(Placeholder if present in repo)*

## 🛠️ Next Steps
- [ ] **Voice Interaction**: Add TTS/STT capabilities.
- [ ] **Memory Persistence**: Ensure session history persists across reloads (partially implemented via SqliteDb).
