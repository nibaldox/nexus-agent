@echo off
echo ==========================================
echo       NEXUS AGENT AI - LAUNCHER
echo ==========================================
echo.
echo [1/2] Activating Virtual Environment...
call .venv\Scripts\activate

echo [2/2] Starting Nexus System...
python run_nexus.py

pause
