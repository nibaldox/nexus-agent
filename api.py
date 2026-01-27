import sys
import os
# Force using virtual environment packages
venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'Lib', 'site-packages')
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import sqlite3
from typing import Optional, List, Dict, Any
# Import Multi-Agent Team
from agents.squads.knowledge.librarian import librarian
from tools.squad_tools import start_task
import uvicorn
import time
from config import settings
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("NexusAPI")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    exec_manager.start_cleanup()
    yield
    # Shutdown
    exec_manager.stop_cleanup()

app = FastAPI(title="Nexus API", lifespan=lifespan)

# Configurar CORS
cors_origins = settings.cors_origins
allow_credentials = settings.cors_allow_credentials
if allow_credentials and "*" in cors_origins:
    # Browsers reject credentials with wildcard origins
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (gráficos, assets, etc.)
app.mount("/assets", StaticFiles(directory=str(settings.workspace_dir / "assets")), name="assets")
# Servir el workspace completo para permitir la descarga de artefactos
app.mount("/workspace", StaticFiles(directory=str(settings.workspace_dir)), name="workspace")


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.get("/api/health")
def health_check():
    return {"status": "Nexus Online (Multi-Agent)", "version": "3.0.0"}

# --- Session Management Endpoints ---
def get_db_connection():
    conn = sqlite3.connect(settings.agent_db_path, timeout=max(1, settings.sqlite_busy_timeout_ms / 1000))
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(f"PRAGMA journal_mode={settings.sqlite_journal_mode}")
        conn.execute(f"PRAGMA busy_timeout={settings.sqlite_busy_timeout_ms}")
        conn.execute("PRAGMA synchronous=NORMAL")
    except Exception:
        pass
    return conn

@app.get("/sessions")
def get_sessions():
    try:
        conn = get_db_connection()
        # Fetch minimal info first
        sessions = conn.execute("SELECT session_id, created_at, updated_at FROM nexus_team_sessions ORDER BY updated_at DESC").fetchall()
        
        # Get available columns for title extraction
        cursor = conn.execute("SELECT * FROM nexus_team_sessions LIMIT 1")
        cols = [description[0] for description in cursor.description]

        result = []
        for s in sessions:
            title = "New Mission"
            session_id = s['session_id']
            
            # Efficient title extraction
            try:
                # 1. Try memory
                if 'memory' in cols:
                    row = conn.execute("SELECT memory FROM nexus_team_sessions WHERE session_id = ?", (session_id,)).fetchone()
                    if row and row['memory']:
                        data = json.loads(row['memory'])
                        for msg in data.get('messages', []):
                            if msg.get('role') == 'user':
                                title = (msg.get('content') or '')[:50] + "..."
                                break
                
                # 2. Try runs (if title still default)
                if title == "New Mission" and 'runs' in cols:
                    row = conn.execute("SELECT runs FROM nexus_team_sessions WHERE session_id = ?", (session_id,)).fetchone()
                    if row and row['runs']:
                        runs = json.loads(row['runs'])
                        if isinstance(runs, list) and runs:
                            # Check first run (which is usually the start)
                            first_run = runs[-1] if len(runs) > 0 else {}
                            # Or iterate to find user input
                            for run in runs:
                                inp = run.get('input', {})
                                content = str(inp.get('input_content') if isinstance(inp, dict) else inp)
                                if content:
                                    title = content[:50] + "..."
                                    break
            except Exception as e:
                logger.warning(f"Error extracting title for session {session_id}: {e}")

            result.append({
                "session_id": session_id,
                "created_at": s['created_at'],
                "updated_at": s['updated_at'],
                "title": title
            })
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}", exc_info=True)
        return []

@app.get("/api/squads/status")
def get_squads_status():
    status_file = str(settings.workspace_dir / "squad_status.json")
    if not os.path.exists(status_file):
        return {"squads": {}, "variables": {}}
    try:
        with open(status_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e), "squads": {}}

# --- Helper Functions ---
import re

def extract_from_run_string(s: str, max_items: int = 10) -> list:
    """Extract messages/content from an opaque run string using regex.
    
    This is a fallback parser for when JSON deserialization fails.
    It attempts to extract content from various fields in the run data.
    
    Args:
        s: String representation of run data
        max_items: Maximum number of items to extract
        
    Returns:
        List of message dictionaries with 'role' and 'content' keys
    """
    items = []
    
    # Try to find a messages array and extract "content" values
    m_arr = re.search(r'"messages"\s*:\s*\[(.*?)\]\s*(?:,|})', s, re.S)
    if m_arr:
        block = m_arr.group(1)
        for m in re.finditer(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', block, re.S):
            txt = m.group(1)
            # unescape basic JSON escapes
            try:
                txt = json.loads('"' + txt + '"')
            except Exception:
                pass
            items.append({'role': 'assistant', 'content': txt})
            if len(items) >= max_items:
                return items

    # Try to find input_content
    m_inp = re.search(r'"input_content"\s*:\s*"((?:\\.|[^"\\])*)"', s, re.S)
    if m_inp:
        txt = m_inp.group(1)
        try:
            txt = json.loads('"' + txt + '"')
        except Exception:
            pass
        items.append({'role': 'user', 'content': txt})

    # Try to find standalone content
    m_cont = re.search(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', s, re.S)
    if m_cont:
        txt = m_cont.group(1)
        try:
            txt = json.loads('"' + txt + '"')
        except Exception:
            pass
        items.append({'role': 'assistant', 'content': txt})

    return items

def _parse_messages_from_runs(runs_data: Any, limit: int) -> List[Dict[str, Any]]:
    """Helper to extract messages from 'runs' column."""
    if not runs_data:
        return []

    collected = []
    try:
        if isinstance(runs_data, str):
            # Known issue correction: parsing corrupted strings or single chars
            if len(runs_data) > 0 and runs_data[0] == '[' and runs_data[1] != '{' and len(runs_data) < 5:
                 return []
            runs = json.loads(runs_data)
        else:
            runs = runs_data

        if not isinstance(runs, list):
            return []

        # Iterate newest to oldest
        for run in reversed(runs):
            if len(collected) >= limit:
                break
            
            if isinstance(run, str):
                try:
                    run = json.loads(run)
                except:
                    # Fallback regex extraction
                    # Assuming extract_from_run_string is in the same file or globally accessible
                    items = extract_from_run_string(run, max_items=5)
                    collected.extend(reversed(items)) # We want newest first in collected (to be reversed later)
                    continue
            
            if not isinstance(run, dict):
                continue
                
            # 1. Structured messages
            if run.get('messages'):
                msgs = run['messages']
                for m in reversed(msgs):
                    if len(collected) >= limit: break
                    collected.append({
                        'role': m.get('role', 'assistant'),
                        'content': m.get('content', ''),
                        'tool_calls': m.get('tool_calls'),
                        'tool_call_id': m.get('tool_call_id'),
                        'name': m.get('name'),
                        'agent_name': m.get('agent_name')
                    })
            
            # 2. Input/Content
            else:
                inp = run.get('input')
                out = run.get('content') or run.get('response')
                
                # We collect newest first. Output follows input, so Output is newer.
                
                # Output first (Newer)
                if out:
                    collected.append({
                        'role': 'assistant', 
                        'content': out,
                        'tool_calls': run.get('tool_calls'),
                        'agent_name': run.get('agent_name')
                    })
                
                # Input second (Older)
                if inp:
                    txt = inp.get('input_content') if isinstance(inp, dict) else str(inp)
                    if txt:
                        collected.append({'role': 'user', 'content': txt})

    except Exception as e:
        logger.warning(f"Error parsing runs: {e}")
        
    return collected

@app.get("/sessions/{session_id}")
def get_session_history(session_id: str, limit: int = 200):
    try:
        limit = max(1, min(limit, 1000))
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM nexus_team_sessions WHERE session_id = ?", (session_id,)).fetchone()
        
        if not row:
            conn.close()
            return {"messages": []}
            
        # Get column names
        cols = row.keys()
        conn.close()

        messages = []

        # Strategy 1: Compact Messages (Preferred)
        if 'compact_messages' in cols and row['compact_messages']:
            try:
                messages = json.loads(row['compact_messages'])
                return {"messages": messages[-limit:]}
            except Exception as e:
                logger.warning(f"Failed to load compact_messages for {session_id}: {e}")

        # Strategy 2: Runs (Rich history)
        if not messages and 'runs' in cols:
            messages = _parse_messages_from_runs(row['runs'], limit)
            # Messages are collected newest-first, so reverse to get chronological order
            if messages:
                return {"messages": list(reversed(messages))[-limit:]} # Apply limit after reversing

        # Strategy 3: Memory (Legacy)
        if not messages and 'memory' in cols and row['memory']:
            try:
                mem = json.loads(row['memory'])
                messages = mem.get('messages', [])
                return {"messages": messages[-limit:]}
            except Exception as e:
                 logger.warning(f"Failed to load legacy memory for {session_id}: {e}")

        return {"messages": messages or []}

    except Exception as e:
        logger.error(f"Error retrieving session history {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error retrieving session")

class CompactRequest(BaseModel):
    limit: int = 1000

@app.post("/sessions/{session_id}/compact")
def compact_session(session_id: str, req: CompactRequest = None):
    """Process runs and store a compact messages view for fast retrieval.

    This creates or updates a 'compact_messages' column with a pre-processed
    JSON array of messages extracted from runs. Once compacted, GET /sessions/{id}
    will use this view for O(1) retrieval instead of parsing runs each time.
    """
    limit = req.limit if req else 1000
    limit = max(1, min(limit, 5000))  # Cap at 5000

    try:
        conn = get_db_connection()
        cols = [r[1] for r in conn.execute("PRAGMA table_info('nexus_team_sessions')").fetchall()]

        # Check if compact_messages column exists
        if 'compact_messages' not in cols:
            conn.execute("ALTER TABLE nexus_team_sessions ADD COLUMN compact_messages TEXT")
            conn.commit()

        row = conn.execute("SELECT runs FROM nexus_team_sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row or not row['runs']:
            conn.close()
            return {"status": "no_runs", "messages_extracted": 0}

        runs = json.loads(row['runs'])
        collected = []

        # Process runs from newest to oldest
        for raw_run in reversed(runs):
            if len(collected) >= limit:
                break
            run = None
            if isinstance(raw_run, str):
                try:
                    run = json.loads(raw_run)
                except Exception:
                    extracted = extract_from_run_string(raw_run, max_items=5)
                    for it in extracted:
                        collected.append(it)
                        if len(collected) >= limit:
                            break
                    continue
            elif isinstance(raw_run, dict):
                run = raw_run
            else:
                continue

            if not isinstance(run, dict):
                continue

            # Extract from structured messages
            if isinstance(run.get('messages'), list) and run.get('messages'):
                for m in reversed(run.get('messages')):
                    role = m.get('role', 'assistant') if isinstance(m, dict) else 'assistant'
                    content = m.get('content', '') if isinstance(m, dict) else str(m)
                    collected.append({'role': role, 'content': content})
                    if len(collected) >= limit:
                        break
                if len(collected) >= limit:
                    break
                continue

            # Reconstruct from input/content
            inp = run.get('input')
            content = run.get('content')
            if isinstance(inp, dict):
                input_content = inp.get('input_content') or inp.get('content')
            else:
                input_content = inp
            if input_content:
                collected.append({'role': 'user', 'content': input_content})
                if len(collected) >= limit:
                    break
            if content:
                collected.append({'role': 'assistant', 'content': content})
                if len(collected) >= limit:
                    break

        collected.reverse()
        compact_json = json.dumps(collected)

        # Update the row
        conn.execute("UPDATE nexus_team_sessions SET compact_messages = ? WHERE session_id = ?",
                     (compact_json, session_id))
        conn.commit()
        conn.close()

        return {
            "status": "success",
            "session_id": session_id,
            "messages_extracted": len(collected),
            "limit_used": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------

from fastapi.responses import StreamingResponse
from dataclasses import asdict, is_dataclass
import json
import asyncio
from collections import deque

TOOL_LOG_DIR = os.path.join("workspace", "logs", "tools")
REQUEST_LOG_DIR = os.path.join("workspace", "logs", "requests")

def _append_tool_log(session_id: str, task_id: str, payload: dict) -> None:
    try:
        os.makedirs(TOOL_LOG_DIR, exist_ok=True)
        log_path = os.path.join(TOOL_LOG_DIR, f"{session_id}.jsonl")
        record = {
            "timestamp": time.time(),
            "session_id": session_id,
            "task_id": task_id,
            "event": payload.get("event"),
            "agent_name": payload.get("agent_name"),
            "tool": payload.get("tool") or payload.get("tool_name"),
            "data": payload
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Never block streaming on log errors
        return

def _append_request_log(session_id: str, message: str) -> None:
    try:
        os.makedirs(REQUEST_LOG_DIR, exist_ok=True)
        log_path = os.path.join(REQUEST_LOG_DIR, f"{session_id}.jsonl")
        record = {
            "timestamp": time.time(),
            "session_id": session_id,
            "message_len": len(message or ""),
            "message_preview": (message or "")[:300]
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        return

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    from nexus_workflow import NexusWorkflow
    workflow = NexusWorkflow()
    
    async def event_generator():
        try:
            if request.session_id:
                session_id = request.session_id
            else:
                import uuid
                session_id = f"session_{uuid.uuid4().hex[:12]}"

            _append_request_log(session_id, request.message or "")

            # Check if we should create a mission plan for complex requests
            should_plan = workflow.should_create_plan(request.message)

            # Only create task entries when a mission is actually initiated
            task_id = "default"
            if should_plan:
                task_id = start_task(request.message[:80], session_id=session_id)
            if isinstance(task_id, str) and task_id.startswith("task_"):
                os.environ["NEXUS_TASK_ID"] = task_id
            else:
                os.environ["NEXUS_TASK_ID"] = "default"
            
            if should_plan:
                # Send planning event to frontend
                planning_event = {
                    "event": "PlanningStarted",
                    "content": "📋 Analizando solicitud y creando plan de misión...",
                    "session_id": session_id
                }
                yield f"data: {json.dumps(planning_event)}\n\n"
                await asyncio.sleep(0)
            
            # Ensure tools know the active session for file routing
            os.environ["NEXUS_SESSION_ID"] = session_id

            # Run Agno Workflow with Session ID
            stream = workflow.run(
                user_request=request.message,
                session_id=session_id,
                stream=True,
                stream_events=True
            )
            for chunk in stream:
                # Serializar el evento a JSON
                if hasattr(chunk, "to_dict"):
                    data = chunk.to_dict()
                elif is_dataclass(chunk):
                    data = asdict(chunk)
                else:
                    data = {"event": "Unknown", "content": str(chunk)}
                
                # Ensure agent_name is preserved/extracted if hidden
                if not data.get("agent_name") and hasattr(chunk, "agent_name"):
                     data["agent_name"] = chunk.agent_name
                
                # Normalizar eventos de Team a eventos genéricos
                if data.get("event") == "WorkflowStarted":
                    data["event"] = "RunStarted"
                elif data.get("event") == "WorkflowCompleted":
                    data["event"] = "RunCompleted"
                elif data.get("event") == "StepOutput" and data.get("step_name") == "Planificación":
                    plan_data = data.get("content") or {}
                    if plan_data.get("created"):
                        plan_created_event = {
                            "event": "PlanCreated",
                            "content": f"✅ Plan de misión creado: {len(plan_data.get('tasks', []))} tareas identificadas",
                            "plan_path": plan_data.get("plan_path"),
                            "session_id": session_id
                        }
                        yield f"data: {json.dumps(plan_created_event)}\n\n"
                        await asyncio.sleep(0)
                elif data.get("event") == "TeamRunContent":
                    data["event"] = "RunContent"
                elif data.get("event") == "TeamRunStarted":
                    data["event"] = "RunStarted"
                elif data.get("event") == "TeamRunCompleted":
                    data["event"] = "RunCompleted"

                # Tool event logging (for workflow inspection)
                if "session_id" not in data:
                    data["session_id"] = session_id
                event_type = (data.get("event") or "").lower()
                if "tool" in event_type:
                    _append_tool_log(session_id, os.environ.get("NEXUS_TASK_ID", "default"), data)
                
                # Formato SSE
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(0)  
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = {"event": "Error", "content": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/logs/tools")
def get_tool_logs(session_id: str, tail: int = 200):
    """Return recent tool-call logs for a session."""
    tail = max(1, min(tail, 1000))
    log_path = os.path.join(TOOL_LOG_DIR, f"{session_id}.jsonl")
    if not os.path.exists(log_path):
        return {"exists": False, "session_id": session_id, "events": []}
    lines = deque(maxlen=tail)
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                lines.append(line.strip())
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except Exception:
            events.append({"raw": line})
    return {"exists": True, "session_id": session_id, "events": events}

@app.get("/mission_plan/{session_id}")
def get_mission_plan(session_id: str):
    """Retrieve the mission plan file for a session"""
    import glob
    from nexus_workflow import NexusWorkflow
    
    try:
        workflow = NexusWorkflow()
        plan_path = workflow.get_plan_path_for_session(session_id)
        
        if plan_path and os.path.exists(plan_path):
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_content = f.read()
            return {
                "plan": plan_content, 
                "file": plan_path,
                "exists": True
            }
        else:
            return {
                "plan": None, 
                "message": "No plan found for this session",
                "exists": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    import shutil
    import os
    from agno.knowledge.reader.pdf_reader import PDFReader

    try:
        # Ensure knowledge directory exists
        knowledge_dir = str(settings.workspace_dir / "knowledge")
        if not os.path.exists(knowledge_dir):
            os.makedirs(knowledge_dir)

        # Save file (prevent path traversal via filename)
        safe_name = os.path.basename(file.filename)
        if not safe_name:
            raise HTTPException(status_code=400, detail="Invalid filename")
        file_path = os.path.join(knowledge_dir, safe_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trigger ingestion via Librarian
        from agents.squads.knowledge.librarian import get_knowledge_base
        kb = get_knowledge_base()
        if kb:
            kb.insert(path=file_path, reader=PDFReader(chunk=True))
            return {"status": "success", "filename": file.filename, "message": "File uploaded and indexed by Librarian."}
        else:
             return {"status": "warning", "filename": file.filename, "message": "File saved but Librarian Knowledge Base not active."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== TERMINAL STREAMING (SSE) ==========

import asyncio
from fastapi.responses import StreamingResponse
from datetime import datetime as dt
from datetime import timedelta
import uuid

# Global state for active code executions
class ExecutionManager:
    """Singleton to manage active terminal executions."""
    def __init__(self):
        self.active_executions = {}
        self.lock = asyncio.Lock()
        self.cleanup_task = None

    async def register(self, execution_id: str, state: 'ExecutionState'):
        async with self.lock:
            self.active_executions[execution_id] = state

    async def get(self, execution_id: str) -> Optional['ExecutionState']:
        return self.active_executions.get(execution_id)

    async def remove(self, execution_id: str):
        async with self.lock:
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]

    async def cleanup_loop(self):
        while True:
            await asyncio.sleep(settings.execution_cleanup_interval)
            cutoff = dt.now() - timedelta(seconds=settings.execution_ttl_seconds)
            async with self.lock:
                stale_ids = [
                    eid for eid, exc in self.active_executions.items()
                    if exc.last_activity < cutoff
                ]
                for eid in stale_ids:
                    del self.active_executions[eid]

    def start_cleanup(self):
        self.cleanup_task = asyncio.create_task(self.cleanup_loop())

    def stop_cleanup(self):
        if self.cleanup_task:
            self.cleanup_task.cancel()

exec_manager = ExecutionManager()

class ExecutionState:
    """Manages state for a single code execution"""
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.status = 'running'
        self.output_queue = asyncio.Queue()
        self.started_at = dt.now()
        self.last_activity = self.started_at
        self.exit_code = None
        
    async def add_line(self, line: str, stream_type: str, elapsed_time: float):
        """Add output line to queue"""
        self.last_activity = dt.now()
        await self.output_queue.put({
            'type': stream_type,
            'line': line,
            'timestamp': dt.now().isoformat(),
            'elapsed': round(elapsed_time, 3)
        })
    
    async def complete(self, exit_code: int, elapsed_time: float):
        """Mark execution as complete"""
        self.status = 'complete'
        self.exit_code = exit_code
        self.last_activity = dt.now()
        await self.output_queue.put({
            'type': 'complete',
            'exit_code': exit_code,
            'timestamp': dt.now().isoformat(),
            'elapsed': round(elapsed_time, 3)
        })



@app.get("/api/terminal/stream/{execution_id}")
async def stream_terminal_output(execution_id: str):
    """
    SSE endpoint for real-time terminal output streaming.
    
    Args:
        execution_id: Unique execution identifier
        
    Returns:
        Server-Sent Events stream
    """
    async def event_generator():
        """Generate SSE events from execution output"""
        # Wait for execution to be registered
        timeout = 10  # Wait up to 10 seconds for execution to start
        waited = 0
        execution = await exec_manager.get(execution_id)
        while not execution and waited < timeout:
            await asyncio.sleep(0.1)
            waited += 0.1
            execution = await exec_manager.get(execution_id)
        
        if not execution:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Execution not found'})}\n\n"
            return
        
        # execution = active_executions[execution_id] (Already got it)
        
        try:
            # Stream output lines as they arrive
            while execution.status == 'running' or not execution.output_queue.empty():
                try:
                    # Get next output with timeout
                    event = await asyncio.wait_for(execution.output_queue.get(), timeout=0.5)
                    yield f"data: {json.dumps(event)}\n\n"
                    
                    # Check if execution completed
                    if event.get('type') == 'complete':
                        break
                        
                except asyncio.TimeoutError:
                    # Send keep-alive
                    yield f": keepalive\n\n"
                    continue
            
            # Send final completion event if not already sent
            if execution.status != 'complete':
                yield f"data: {json.dumps({'type': 'complete', 'exit_code': execution.exit_code or -1})}\n\n"
                
        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            # Cleanup output queue but keep execution state for stats until TTL
            pass # Cleanup is handled by the background loop or explicitly when finished
            # async with execution_lock:
            #    if execution_id in active_executions:
            #        del active_executions[execution_id]
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

# Helper function to register new execution
async def register_execution(execution_id: str = None) -> str:
    """Register new execution and return execution ID"""
    if not execution_id:
        execution_id = str(uuid.uuid4())
    
    await exec_manager.register(execution_id, ExecutionState(execution_id))
    
    return execution_id

# Helper function to emit output to streaming clients
async def emit_to_stream(execution_id: str, line: str, stream_type: str, elapsed_time: float):
    """Emit output line to active streaming clients"""
    execution = await exec_manager.get(execution_id)
    if execution:
        await execution.add_line(line, stream_type, elapsed_time)

# ========== COST TRACKING ENDPOINTS ==========

from costs.database import (
    get_total_cost,
    get_request_count,
    get_recent_requests,
    get_cost_by_agent,
    get_cost_by_model,
    get_daily_costs
)
from costs.pricing import list_available_models, get_pricing_info

@app.get("/api/costs/summary")
def get_cost_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    agent: Optional[str] = None,
    model: Optional[str] = None
):
    """
    Get cost summary with optional filters.
    
    Query params:
        start_date: ISO timestamp (e.g., "2026-01-01T00:00:00")
        end_date: ISO timestamp
        agent: Filter by agent name
        model: Filter by model name
    """
    try:
        total_cost = get_total_cost(start_date, end_date, agent, model)
        request_count = get_request_count(start_date, end_date, agent)
        
        # Calculate average cost per request
        avg_cost = total_cost / request_count if request_count > 0 else 0
        
        # Get breakdowns
        cost_by_agent = get_cost_by_agent(start_date, end_date)
        cost_by_model = get_cost_by_model(start_date, end_date)
        daily_costs = get_daily_costs(30)
        
        return {
            "total_cost": round(total_cost, 4),
            "total_requests": request_count,
            "average_cost_per_request": round(avg_cost, 4),
            "breakdown_by_agent": cost_by_agent,
            "breakdown_by_model": cost_by_model,
            "daily_costs": daily_costs,
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "agent": agent,
                "model": model
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/costs/recent")
def get_recent_cost_requests(limit: int = 50):
    """
    Get most recent LLM requests with cost data.
    
    Query params:
        limit: Number of requests to return (max 100)
    """
    try:
        limit = min(limit, 100)  # Cap at 100
        requests = get_recent_requests(limit)
        
        return {
            "requests": requests,
            "count": len(requests)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/costs/analytics")
def get_cost_analytics():
    """
    Get analytics and insights about costs.
    """
    try:
        # Get data for last 30 days
        daily_costs = get_daily_costs(30)
        cost_by_agent = get_cost_by_agent()
        cost_by_model = get_cost_by_model()
        total_cost = get_total_cost()
        total_requests = get_request_count()
        
        # Calculate insights
        most_expensive_agent = max(cost_by_agent.items(), key=lambda x: x[1])[0] if cost_by_agent else None
        most_used_model = max(cost_by_model.items(), key=lambda x: x[1])[0] if cost_by_model else None
        
        # Daily averages
        days_with_data = len([d for d in daily_costs if d['cost'] > 0])
        avg_cost_per_day = sum(d['cost'] for d in daily_costs) / days_with_data if days_with_data > 0 else 0
        avg_requests_per_day = sum(d['requests'] for d in daily_costs) / days_with_data if days_with_data > 0 else 0
        avg_tokens_per_day = sum(d['tokens'] for d in daily_costs) / days_with_data if days_with_data > 0 else 0
        
        return {
            "total_cost_all_time": round(total_cost, 4),
            "total_requests_all_time": total_requests,
            "most_expensive_agent": most_expensive_agent,
            "most_used_model": most_used_model,
            "average_cost_per_day": round(avg_cost_per_day, 4),
            "average_requests_per_day": round(avg_requests_per_day, 2),
            "average_tokens_per_day": round(avg_tokens_per_day, 0),
            "days_tracked": days_with_data,
            "cost_breakdown": {
                "by_agent": cost_by_agent,
                "by_model": cost_by_model
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/costs/models")
def get_available_models_pricing():
    """Get list of available models with pricing information."""
    try:
        models = list_available_models()
        model_info = []
        
        for model in models:
            pricing_str = get_pricing_info(model)
            model_info.append({
                "model": model,
                "pricing": pricing_str
            })
        
        return {
            "models": model_info,
            "count": len(model_info)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Montar archivos estáticos ANTES del endpoint catch-all
# Mount assets folder for Visualizer charts
app.mount("/assets", StaticFiles(directory="workspace/assets"), name="assets")
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

# Servir archivos desde la raíz usando un manejador personalizado que prioriza la API
from fastapi.responses import FileResponse
import os

@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend files, but let API routes take priority"""
    # Check if it's an API route first (this shouldn't happen due to route ordering)
    if path.startswith(("chat", "upload", "sessions")):
        return {"error": "API route should be handled by specific endpoints"}

    # For static files, let the mounted StaticFiles handle it
    if path.startswith("static/"):
        # This should be handled by the mounted StaticFiles, but if not, serve manually
        static_path = path[7:]  # Remove 'static/' prefix
        file_path = os.path.join("frontend", static_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

    # Serve index.html for root path
    if path == "" or path == "/":
        return FileResponse("frontend/index.html", media_type="text/html")

    # Serve other frontend files
    file_path = os.path.join("frontend", path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # Fallback to index.html for SPA routing
    return FileResponse("frontend/index.html", media_type="text/html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
