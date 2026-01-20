try:
    print("⏳ Importing Librarian...")
    from agents.librarian import librarian
    print("✅ Librarian imported successfully!")
    print(f"🧩 Embedder: {librarian.knowledge.vector_db.embedder}")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
