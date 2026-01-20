try:
    print("⏳ Importing Researcher...")
    from agents.researcher import researcher
    print("✅ Researcher imported successfully!")
    print(f"🔧 Tools: {[tool.name for tool in researcher.tools]}")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
