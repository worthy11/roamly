from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from typing import List
import os

from app.routers import users, trips, chat

import langchain

langchain.debug = True

app = FastAPI()
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(chat.router)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

clients: List[WebSocket] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)