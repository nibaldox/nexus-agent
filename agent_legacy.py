from pathlib import Path
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools
from tools.workspace_file_tools import FileTools
from agno.tools.yfinance import YFinanceTools
from tools.squad_tools import update_squad_status
from agno.tools.youtube import YouTubeTools
from agno.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
from datetime import datetime
from skills.research_skills import ResearchSkills
from skills.docs_skills import DocsSkills
from skills.visualization_skills import VisualizationSkills
from skills.quality_skills import QualitySkills
from skills.triage_skills import TriageSkills
from skills.source_validation_skills import SourceValidationSkills
from skills.data_normalization_skills import DataNormalizationSkills
from skills.synthesis_skills import SynthesisSkills
from skills.workflow_skills import WorkflowSkills
from skills.risk_skills import RiskSkills
from skills.memory_skills import MemorySkills
from skills.tool_decision_skills import ToolDecisionSkills
from skills.context_compression_skills import ContextCompressionSkills
from skills.decision_log_skills import DecisionLogSkills
import os
import glob

load_dotenv()

# --- Knowledge Base Setup ---
# Initialize Vector DB (LanceDB)
vector_db = LanceDb(
    table_name="agent_documents",
    uri="./lancedb_data",  # Local storage for vectors
    search_type="hybrid",   # Requires tantivy installed
    embedder=OpenAIEmbedder(id="text-embedding-3-small") # Requires OPENAI_API_KEY
)

# Initialize Knowledge Base
knowledge_base = Knowledge(
    vector_db=vector_db,
)

# Load/Ingest documents on start
def load_knowledge():
    knowledge_dir = "workspace/knowledge"
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)
        print(f"Created knowledge directory: {knowledge_dir}")
    
    pdf_files = glob.glob(os.path.join(knowledge_dir, "*.pdf"))
    if pdf_files:
        print(f"📚 Loading {len(pdf_files)} documents into knowledge base...")
        # Recreate=False avoids re-embedding unchanged files if logic supports it, 
        # but Knowledge.load doesn't exist. We use insert.
        # For simplicity in this demo, we insert (upsert=True by default usually).
        # We can scan and insert.
        for pdf_path in pdf_files:
            try:
                knowledge_base.insert(path=pdf_path, reader=PDFReader(chunk=True))
                print(f"  - Loaded: {pdf_path}")
            except Exception as e:
                print(f"  - Failed to load {pdf_path}: {e}")
    else:
        print("ℹ️ No PDF documents found in workspace/knowledge")

AUTO_INGEST_ON_START = False

if AUTO_INGEST_ON_START:
    load_knowledge()

agent = Agent(
    model=OpenRouter(id="nvidia/nemotron-3-nano-30b-a3b:free"),
    description="Eres Nexus, un Analista de Investigación Avanzado con acceso a herramientas de internet, archivos y finanzas.",
    tools=[
        DuckDuckGoTools(), 
        FileTools(),
        YFinanceTools(),
        YouTubeTools(),
        ResearchSkills(),
        DocsSkills(),
        VisualizationSkills(),
        QualitySkills(),
        TriageSkills(),
        SourceValidationSkills(),
        DataNormalizationSkills(),
        SynthesisSkills(),
        WorkflowSkills(),
        RiskSkills(),
        MemorySkills(),
        ToolDecisionSkills(),
        ContextCompressionSkills(),
        DecisionLogSkills(),
        update_squad_status
    ],
    db=SqliteDb(db_file="agent.db", session_table="agent_sessions"),
    add_history_to_context=True,
    session_id="session-test-01",
    markdown=True,
    debug_mode=True,
    knowledge=knowledge_base,
    search_knowledge=True, # Enables 'search_knowledge' tool
    instructions=[
        "Eres Nexus, asistente experto y fiable.",
        "Usa herramientas cuando aporten evidencia (web, KB, finanzas, archivos).",
        "Entrega: resumen breve, evidencia/fuentes y síntesis clara.",
        "Si no puedes verificar, indica nivel de confianza y pasos para validar.",
        "Si generas código, aplica cambios mínimos y agrega un ejemplo corto.",
        "Reporta progreso con update_squad_status.",
        "Guarda artefacto en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/agent/.",
        f"Tiempo actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]
)

if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 Nexus - Analista de Investigación Avanzado")
    print("📝 Escribe 'exit' o 'quit' para terminar la sesión.")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    while True:
        try:
            print("\n👤 Tú:")
            user_input = input("> ")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 Nexus: ¡Ha sido un placer asistirte! Hasta pronto. 👋")
                break

            if not user_input.strip():
                continue

            agent.print_response(user_input, stream=True)
        
        except KeyboardInterrupt:
            print("\n\n🤖 Nexus: Sesión finalizada. ¡Adiós!")
            break
