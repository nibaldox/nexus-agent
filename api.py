from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
# Import Multi-Agent Team
from agents.manager import manager
from agents.librarian import librarian
import uvicorn

app = FastAPI(title="Nexus API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



import sqlite3
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.get("/")
def health_check():
    return {"status": "Nexus Online (Multi-Agent)", "version": "3.0.0"}

# --- Session Management Endpoints ---
def get_db_connection():
    conn = sqlite3.connect('agent.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/sessions")
def get_sessions():
    try:
        conn = get_db_connection()
        # Fetch basic columns first to avoid selecting non-existent columns
        sessions = conn.execute("SELECT session_id, created_at, updated_at FROM nexus_team_sessions ORDER BY updated_at DESC").fetchall()

        # Inspect available columns once
        cols = [r[1] for r in conn.execute("PRAGMA table_info('nexus_team_sessions')").fetchall()]

        result = []
        for s in sessions:
            title = "New Mission"
            try:
                # Try memory if present
                if 'memory' in cols:
                    r2 = conn.execute("SELECT memory FROM nexus_team_sessions WHERE session_id = ?", (s['session_id'],)).fetchone()
                    if r2 and r2['memory']:
                        memory_json = json.loads(r2['memory'])
                        messages = memory_json.get('messages', [])
                        for msg in messages:
                            if msg.get('role') == 'user':
                                title = (msg.get('content') or '')[:50] + "..."
                                break
                # Try runs if present
                elif 'runs' in cols:
                    r2 = conn.execute("SELECT runs FROM nexus_team_sessions WHERE session_id = ?", (s['session_id'],)).fetchone()
                    if r2 and r2['runs']:
                        runs = json.loads(r2['runs'])
                        found = False
                        for run in runs:
                            for msg in run.get('messages', []) or []:
                                if msg.get('role') == 'user':
                                    title = (msg.get('content') or '')[:50] + "..."
                                    found = True
                                    break
                            if found:
                                break
                            inp = run.get('input', {})
                            if isinstance(inp, dict):
                                input_content = inp.get('input_content') or inp.get('content')
                                if input_content:
                                    title = str(input_content)[:50] + "..."
                                    break
                # Try session_data as last resort
                elif 'session_data' in cols:
                    r2 = conn.execute("SELECT session_data FROM nexus_team_sessions WHERE session_id = ?", (s['session_id'],)).fetchone()
                    if r2 and r2['session_data']:
                        try:
                            sd = json.loads(r2['session_data'])
                            msgs = sd.get('messages', [])
                            for m in msgs:
                                if m.get('role') == 'user':
                                    title = (m.get('content') or '')[:50] + "..."
                                    break
                        except Exception:
                            pass
            except Exception:
                pass

            result.append({
                "session_id": s['session_id'],
                "created_at": s['created_at'],
                "updated_at": s['updated_at'],
                "title": title
            })
        conn.close()
        return result
    except Exception as e:
        # If table doesn't exist yet, return empty
        return []

@app.get("/sessions/{session_id}")
def get_session_history(session_id: str, limit: int = 200):
    """Return reconstructed session messages.

    Tries several storage formats and reconstructs a chronological list of messages,
    parsing `runs` if present and iterating from newest to oldest to gather the
    most recent `limit` messages in an efficient way.
    """
    try:
        # Cap limit to avoid huge responses
        limit = max(1, min(limit, 1000))

        conn = get_db_connection()
        cols = [r[1] for r in conn.execute("PRAGMA table_info('nexus_team_sessions')").fetchall()]
        row = conn.execute("SELECT * FROM nexus_team_sessions WHERE session_id = ?", (session_id,)).fetchone()
        conn.close()

        if not row:
            return {"messages": []}

        # 0) Compact view (fastest - O(1))
        if 'compact_messages' in cols and row.get('compact_messages'):
            try:
                compact = json.loads(row['compact_messages'])
                # Apply limit to compact view
                return {"messages": compact[-limit:]}
            except Exception:
                pass

        # 1) Old schema: memory
        if 'memory' in cols and row['memory']:
            try:
                memory = json.loads(row['memory'])
                msgs = memory.get('messages', []) or []
                return {"messages": msgs[-limit:]}
            except Exception:
                pass

        # 2) Newer schema: runs (may be large, so iterate in reverse and stop when limit reached)
        if 'runs' in cols and row['runs']:
            try:
                runs_raw = row['runs']
                runs = None
                is_corrupted = False
                
                # Check if runs is corrupted (list of single chars) - known issue in some Agno versions
                if isinstance(runs_raw, str) and len(runs_raw) > 0:
                    # Try to parse as JSON array
                    try:
                        parsed = json.loads(runs_raw)
                        # Validate: if it's a list of strings where each string is a single char, it's corrupted
                        if isinstance(parsed, list) and len(parsed) > 0:
                            if isinstance(parsed[0], str) and len(parsed[0]) == 1:
                                # Corrupted - can't extract messages from this session
                                return {"messages": [], "warning": "Session runs data is corrupted (characters stored as separate elements). Messages cannot be recovered from this session."}
                            else:
                                runs = parsed
                    except Exception:
                        pass
                
                # If runs is still None, try parsing as dict or keep as is
                if runs is None:
                    if isinstance(runs_raw, str):
                        try:
                            runs = json.loads(runs_raw)
                        except Exception:
                            runs = None
                    else:
                        runs = runs_raw
                
                # If we have a valid runs list, process it
                if runs and isinstance(runs, list) and len(runs) > 0 and isinstance(runs[0], dict):
                    collected = []
                    # ... extraction logic continues below

                import re
                # Helper to extract messages/content from an opaque run string using regex
                def extract_from_run_string(s, max_items=10):
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

                # Process runs from newest to oldest so we can stop early
                for raw_run in reversed(runs):
                    if len(collected) >= limit:
                        break

                    run = None
                    if isinstance(raw_run, str):
                        # Try to parse string; if it fails, fall back to regex extraction
                        try:
                            run = json.loads(raw_run)
                        except Exception:
                            # fallback
                            extracted = extract_from_run_string(raw_run, max_items=3)
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

                    # If run contains structured messages, iterate them newest-first
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

                    # Otherwise, reconstruct from run input/content
                    inp = run.get('input')
                    content = run.get('content')

                    # Input could be dict or primitive
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

                # Reverse to chronological order before returning
                collected.reverse()
                return {"messages": collected}
            except Exception:
                pass

        # 3) session_data fallback
        if 'session_data' in cols and row['session_data']:
            try:
                sd = json.loads(row['session_data'])
                msgs = sd.get('messages', []) or []
                return {"messages": msgs[-limit:]}
            except Exception:
                pass

        return {"messages": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

        import re
        def extract_from_run_string(s, max_items=20):
            items = []
            # Try to find a messages array
            m_arr = re.search(r'"messages"\s*:\s*\[(.*?)\]\s*(?:,|})', s, re.S)
            if m_arr:
                block = m_arr.group(1)
                for m in re.finditer(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', block, re.S):
                    txt = m.group(1)
                    try:
                        txt = json.loads('"' + txt + '"')
                    except Exception:
                        pass
                    items.append({'role': 'assistant', 'content': txt})
                    if len(items) >= max_items:
                        return items
            # Try input_content
            m_inp = re.search(r'"input_content"\s*:\s*"((?:\\.|[^"\\])*)"', s, re.S)
            if m_inp:
                txt = m_inp.group(1)
                try:
                    txt = json.loads('"' + txt + '"')
                except Exception:
                    pass
                items.append({'role': 'user', 'content': txt})
            # Try standalone content
            m_cont = re.search(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', s, re.S)
            if m_cont:
                txt = m_cont.group(1)
                try:
                    txt = json.loads('"' + txt + '"')
                except Exception:
                    pass
                items.append({'role': 'assistant', 'content': txt})
            return items

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

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        try:
            # Run Manager Agent with Session ID
            # If session_id is provided, Agno will load/save to that session
            stream = manager.run(
                request.message, 
                session_id=request.session_id, 
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
                if data.get("event") == "TeamRunContent":
                    data["event"] = "RunContent"
                elif data.get("event") == "TeamRunStarted":
                    data["event"] = "RunStarted"
                elif data.get("event") == "TeamRunCompleted":
                    data["event"] = "RunCompleted"
                
                # Formato SSE
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(0)  
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = {"event": "Error", "content": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    import shutil
    import os
    from agno.knowledge.reader.pdf_reader import PDFReader

    try:
        # Ensure knowledge directory exists
        knowledge_dir = "workspace/knowledge"
        if not os.path.exists(knowledge_dir):
            os.makedirs(knowledge_dir)

        # Save file
        file_path = os.path.join(knowledge_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trigger ingestion via Librarian
        if librarian.knowledge:
            librarian.knowledge.insert(path=file_path, reader=PDFReader(chunk=True))
            return {"status": "success", "filename": file.filename, "message": "File uploaded and indexed by Librarian."}
        else:
             return {"status": "warning", "filename": file.filename, "message": "File saved but Librarian Knowledge Base not active."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Montar archivos estáticos AL FINAL para que no intercepten las rutas de la API
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
