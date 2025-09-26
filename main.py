from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
from datetime import datetime
from typing import List, Optional

app = FastAPI(
    title="HackYeah2025 API",
    description="A FastAPI backend for HackYeah 2025",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    environment: str

class Message(BaseModel):
    content: str
    timestamp: Optional[datetime] = None

clients: List[WebSocket] = []

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/api/info")
async def api_info():
    return {
        "message": "Welcome to HackYeah2025 API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "websocket": "/ws",
            "docs": "/docs",
            "frontend": "/"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        environment=os.getenv("ENVIRONMENT", "development")
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            response = {
                "message": message_data.get("message", "Hello from server!"),
                "timestamp": datetime.utcnow().isoformat(),
                "client_count": len(clients)
            }
            
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in clients:
            clients.remove(websocket)

@app.get("/clients/count")
async def get_clients_count():
    return {
        "connected_clients": len(clients),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/broadcast")
async def broadcast_message(message: Message):
    if not clients:
        raise HTTPException(status_code=404, detail="No clients connected")
    
    response_data = {
        "content": message.content,
        "timestamp": datetime.utcnow().isoformat(),
        "type": "broadcast"
    }
    
    disconnected_clients = []
    for client in clients:
        try:
            await client.send_text(json.dumps(response_data))
        except:
            disconnected_clients.append(client)
    
    for client in disconnected_clients:
        clients.remove(client)
    
    return {
        "message": "Broadcast sent successfully",
        "recipients": len(clients),
        "disconnected_clients": len(disconnected_clients)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)