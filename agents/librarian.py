from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from dotenv import load_dotenv
import os
import glob

load_dotenv()

# Initialize Vector DB (LanceDB)
vector_db = LanceDb(
    table_name="agent_documents",
    uri="./lancedb_data",  # Local storage for vectors
    search_type="hybrid",   # Requires tantivy installed
    embedder=SentenceTransformerEmbedder(
        id="sentence-transformers/all-MiniLM-L6-v2",
    ) 
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
        print(f"📚 Loading {len(pdf_files)} documents into Librarian's knowledge base...")
        for pdf_path in pdf_files:
            try:
                knowledge_base.insert(path=pdf_path, reader=PDFReader(chunk=True))
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
    model=OpenRouter(id="minimax/minimax-m2.1", max_tokens=8192),
    knowledge=knowledge_base,
    search_knowledge=True,
    description="Your goal is to answer questions based on the local knowledge base (documents).",
    instructions=[
        "Use the `search_knowledge` tool to find information in the provided PDFs.",
        "Always cite the document name if possible.",
        "If the information is not in the documents, state it clearly."
    ],
    markdown=True,
)
