from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse, TripRequest
from app.services.llm_service import llm_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/text", response_model=ChatResponse)
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

@router.post("/generate", response_model=ChatResponse)
def chat(request: TripRequest):
    try:
        # TODO: Change return type
        response = llm_service.chat(request.message)
        return ChatResponse(
            response=response,
            user_id=request.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

