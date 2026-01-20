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



class ChatRequest(BaseModel):
    message: str

@app.get("/")
def health_check():
    return {"status": "Nexus Online (Multi-Agent)", "version": "3.0.0"}

from fastapi.responses import StreamingResponse
from dataclasses import asdict, is_dataclass
import json
import asyncio

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        try:
            # Run Manager Agent
            stream = manager.run(request.message, stream=True, stream_events=True)
            for chunk in stream:
                # Serializar el evento a JSON
                if hasattr(chunk, "to_dict"):
                    data = chunk.to_dict()
                elif is_dataclass(chunk):
                    data = asdict(chunk)
                else:
                    data = {"event": "Unknown", "content": str(chunk)}
                
                # DEBUG: Print data keys to console
                # print(f"API STREAM CHUNK: event={data.get('event')}, agent={data.get('agent_name') or data.get('team_name')}")
                # Ensure agent_name is preserved/extracted if hidden
                if not data.get("agent_name") and hasattr(chunk, "agent_name"):
                     data["agent_name"] = chunk.agent_name
                
                # Normalizar eventos de Team a eventos genéricos para el frontend
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
