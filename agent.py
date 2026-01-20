from pathlib import Path
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.youtube import YouTubeTools
from agno.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
from datetime import datetime
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

load_knowledge()

agent = Agent(
    model=OpenRouter(id="minimax/minimax-m2.1"),
    description="Eres Nexus, un Analista de Investigación Avanzado con acceso a herramientas de internet, archivos y finanzas.",
    tools=[
        DuckDuckGoTools(), 
        FileTools(base_dir=Path("./workspace")),
        YFinanceTools(),
        YouTubeTools()
    ],
    db=SqliteDb(db_file="agent.db", session_table="agent_sessions"),
    add_history_to_context=True,
    session_id="session-test-01",
    markdown=True,
    debug_mode=True,
    knowledge=knowledge_base,
    search_knowledge=True, # Enables 'search_knowledge' tool
    instructions=[
        "🔎 **Investigación Web**: Usa DuckDuckGo para buscar información actual.",
        "📂 **Sistema de Archivos**: Lee y crea archivos en el directorio de trabajo para persistir hallazgos importantes.",
        "📚 **Base de Conocimiento**: Si te preguntan sobre documentos PDF locales, usa la herramienta `search_knowledge`.",
        "📊 **Finanzas**: Usa YFinance para obtener datos precisos de mercado (acciones, cripto, etc). No inventes precios.",
        "📺 **Multimedia**: Si se te da un video de YouTube, analiza su contenido o subtítulos.",
        "🧠 **Memoria**: Recuerda el contexto de la conversación anterior.",
        "📝 **Formato**: Responde siempre en Markdown bien estructurado. Usa listas, negritas y tablas cuando sea apropiado.",
        "✅ **Verificación**: Cita tus fuentes siempre que sea posible.",
        f"🕒 **Tiempo Actual**: La fecha y hora actual es: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Usa esto para responder preguntas temporales."
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
