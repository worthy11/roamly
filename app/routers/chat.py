from app.models import ChatRequest, ChatResponse, TripRequest, TripPlan
from app.services.llm_service import llm_service
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException
import json
import asyncio

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/text", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = str(llm_service.chat(request.message))
    return ChatResponse(response=response)

@router.post("/generate", response_model=TripPlan)
async def chat(request: ChatRequest):
    query = request.message
    async def event_stream():
        transport_result = await llm_service.run("transport", query)
        yield f"data: {json.dumps({'stage': 'transport', 'result': transport_result})}\n\n"

        accommodation_result = await llm_service.run("accommodation", f"Transport options: {transport_result}\n\nYour query: {query}")
        yield f"data: {json.dumps({'stage': 'accommodation', 'result': accommodation_result})}\n\n"

        plan_result = await llm_service.run("planner", f"Transport options: {transport_result}\n\nAccommodation result: {accommodation_result}\n\nYour query: {query}")
        yield f"data: {json.dumps({'stage': 'plan', 'result': plan_result})}\n\n"

        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

