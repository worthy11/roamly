from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse, TripRequest, TripPlan
from app.services.llm_service import llm_service
import json

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

@router.post("/generate", response_model=TripPlan)
def chat(request: TripRequest):
    try:
        response = llm_service.chat(f"Generate a trip plan with the following parameters: {json.dumps(request)}")
        return TripRequest(
            response=response
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

