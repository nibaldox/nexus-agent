from agno.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from dotenv import load_dotenv
import os

load_dotenv()

print("Checking environment keys...")
print(f"OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}")

try:
    print("Initializing LanceDB...")
    vector_db = LanceDb(
        table_name="test_documents",
        uri="./lancedb_data_test",
        search_type="hybrid", 
        embedder=OpenAIEmbedder(id="text-embedding-3-small")
    )

    print("Initializing Knowledge Base...")
    kb = Knowledge(
        vector_db=vector_db,
    )

    print("Loading documents...")
    # Manual load for debug
    pdf_path = "workspace/knowledge/dummy.pdf"
    if os.path.exists(pdf_path):
        print(f"Inserting {pdf_path}...")
        kb.insert(path=pdf_path, reader=PDFReader(chunk=True))
    else:
        print(f"File {pdf_path} not found!")

    print("Searching...")
    results = kb.search("What is in the dummy pdf?", max_results=1)
    
    if results:
        print("Search successful!")
        for res in results:
            print(f"- Content: {res.content[:100]}...")
            print(f"- Meta: {res.meta_data}")
    else:
        print("No results found.")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
