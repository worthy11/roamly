from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.llm_service import llm_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    response: str
    user_id: int

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = llm_service.chat(request.message)
        return ChatResponse(
            response=response,
            user_id=request.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

