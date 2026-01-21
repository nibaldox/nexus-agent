#!/usr/bin/env python3
"""
Nexus AI - Script de inicio simplificado
"""

import sys
import os

# Force using virtual environment packages
venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'Lib', 'site-packages')
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

from api import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando Nexus AI Server...")
    print("🌐 URL: http://127.0.0.1:8000/static/index.html")
    print("🛑 Presiona Ctrl+C para detener")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)