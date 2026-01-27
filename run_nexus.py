import uvicorn
import webbrowser
import threading
import time
import os
import sys

def open_browser():
    """Wait for server to start then open browser"""
    print("⏳ Waiting for server to start...")
    time.sleep(3) 
    print("🚀 Opening Nexus Interface...")
    webbrowser.open("http://127.0.0.1:8000/index.html")

if __name__ == "__main__":
    print("⚡ Starting Nexus Agent System...")
    
    # Check if api.py exists
    if not os.path.exists("api.py"):
        print("❌ Error: api.py not found. Please run this script from the project root.")
        sys.exit(1)

    # Start browser opener in separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        # Run Uvicorn with reload, but exclude workspace directory
        # This prevents infinite reload loops when Developer Agent creates files
        uvicorn.run(
            "api:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            reload_excludes=["workspace/*", "*.db", "*.log", "__pycache__/*"]
        )
    except KeyboardInterrupt:
        print("\n👋 Nexus Agent stopping...")
