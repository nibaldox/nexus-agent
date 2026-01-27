from agno.agent import Agent
from agents.provider import get_openrouter_model
from agno.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from tools.workspace_file_tools import FileTools
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from dotenv import load_dotenv
import os
import glob
from datetime import datetime
from tools.squad_tools import update_squad_status

load_dotenv()

# Initialize Vector DB (LanceDB) - Lazy initialization
vector_db = None
knowledge_base = None

def get_vector_db():
    global vector_db
    if vector_db is None:
        try:
            print("🔄 Inicializando base de conocimientos...")
            print("📥 Descargando modelo de embeddings (sentence-transformers/all-MiniLM-L6-v2 ~23MB)...")

            # Try primary embedder
            embedder = SentenceTransformerEmbedder(
                id="sentence-transformers/all-MiniLM-L6-v2",
            )

            vector_db = LanceDb(
                table_name="agent_documents",
                uri="./lancedb_data",  # Local storage for vectors
                search_type="hybrid",   # Requires tantivy installed
                embedder=embedder
            )
            print("✅ Base de conocimientos inicializada correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar vector DB: {e}")
            print("\n🔧 SOLUCIONES PARA EL ERROR 'fail to fetch':")
            print("1. ✅ Verifica tu conexión a internet")
            print("2. ⏳ Espera a que termine la descarga del modelo (~23MB)")
            print("3. 🔄 Si se interrumpe, ejecuta el servidor nuevamente")
            print("4. 🌐 Si hay restricciones de red, configura proxy si es necesario")
            print("5. 💡 Como alternativa, puedes usar un modelo local más pequeño")
            print("\n📚 El Librarian funcionará sin base de conocimientos por ahora")
            return None
    return vector_db

def get_knowledge_base():
    global knowledge_base
    if knowledge_base is None:
        db = get_vector_db()
        if db:
            try:
                knowledge_base = Knowledge(vector_db=db)
                print("✅ Knowledge base creada exitosamente")
            except Exception as e:
                print(f"⚠️ Error al crear knowledge base: {e}")
                return None
        else:
            return None
    return knowledge_base

# Load/Ingest documents on start
def load_knowledge():
    kb = get_knowledge_base()
    if not kb:
        return
        
    knowledge_dir = "workspace/knowledge"
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)
        print(f"Created knowledge directory: {knowledge_dir}")
    
    pdf_files = glob.glob(os.path.join(knowledge_dir, "*.pdf"))
    if pdf_files:
        print(f"📚 Loading {len(pdf_files)} documents into Librarian's knowledge base...")
        for pdf_path in pdf_files:
            try:
                kb.insert(path=pdf_path, reader=PDFReader(chunk=True))
                # print(f"  - Loaded: {pdf_path}") # Noise reduction
            except Exception as e:
                print(f"  - Failed to load {pdf_path}: {e}")
    else:
        print("ℹ️ Librarian: No PDF documents found in workspace/knowledge")

AUTO_INGEST_ON_START = False

if AUTO_INGEST_ON_START:
    load_knowledge()

librarian = Agent(
    name="Librarian",
    role="Knowledge Base Manager",
    model=get_openrouter_model(max_tokens=40000),  # Knowledge base indexing needs good context
    knowledge=get_knowledge_base(),  # Will be None if initialization failed
    search_knowledge=get_knowledge_base() is not None,  # Only search if KB is available
    tools=[FileTools(), update_squad_status],
    description="Your goal is to manage document search, retrieval, and knowledge base operations efficiently.",
    instructions=[
        "Rol: Librarian. Busca en KB y documentos locales (workspace/knowledge).",
        "Si la KB no está disponible, indícalo y sugiere usar Researcher.",
        "Entrega: citas relevantes, ruta de documento y breve síntesis.",
        "Evita forzar resultados irrelevantes; reporta limitaciones si aplica.",
        "Reporta progreso con update_squad_status.",
        "Guarda artefacto en workspace/conversations/{NEXUS_SESSION_ID}/artifacts/librarian/.",
        "CRITICAL: Si una herramienta falla, no inventes el resultado. Reporta el error y sugiere un camino alternativo."
    ],
    markdown=True,
)
