from app.models import ChatRequest, ChatResponse, TripRequest, TripPlan
from app.services.llm_service import llm_service
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException
import json
from app.utils.sessions import get_history, update_session

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/text", response_model=ChatResponse)
def chat(request: ChatRequest):
    query = request.message
    history = get_history(request.session_id)
    
    response = llm_service.chat(query, history)
    update_session(request.session_id, "user", query)
    update_session(request.session_id, "assistant", response)

    return ChatResponse(response=response)

@router.post("/generate", response_model=TripPlan)
async def chat(request: ChatRequest):
    query = request.message
    history = get_history(request.session_id)
    
    plan_output = ""
    async def event_stream():
        transport_result = await llm_service.run("transport", query)
        transport_output = transport_result.get("output", str(transport_result))
        yield f"data: {json.dumps({'stage': 'transport', 'result': transport_output})}\n\n"

        accommodation_result = await llm_service.run("accommodation", f"Transport options: {transport_output}\n\nYour query: {query}")
        accommodation_output = accommodation_result.get("output", str(accommodation_result))
        yield f"data: {json.dumps({'stage': 'accommodation', 'result': accommodation_output})}\n\n"

        modified_query = query
        for attempt in range(3):
            plan_result = await llm_service.run("planner", f"User query: {modified_query}, Transport options: {transport_output}, Accommodation options: {accommodation_output}", history)
            plan_output = plan_result.get("output", str(plan_result))
            try:
                trip_plan = json.loads(plan_output)
                json_str = json.dumps(trip_plan)
                yield f"data: {json.dumps({'stage': 'plan', 'result': plan_output})}\n\n"
                break
            except json.JSONDecodeError as e:
                print(f"[Warning] Invalid JSON on attempt {attempt+1}: {e}")
                modified_query = f"Previous output was invalid JSON:\n{plan_output}\nPlease return valid JSON only."

        tips_result = await llm_service.run("tips", f"User query: {modified_query}", history)
        tips_output = tips_result.get("output", str(tips_result))
        yield f"data: {json.dumps({'stage': 'tips', 'result': tips_output})}\n\n"

        risks_result = await llm_service.run("risks", f"User query: {query}", history)
        risks_output = risks_result.get("output", str(risks_result))
        yield f"data: {json.dumps({'stage': 'risks', 'result': risks_output})}\n\n"

        yield "data: [DONE]\n\n"

    update_session(request.session_id, "user", query)
    update_session(request.session_id, "assistant", plan_output)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

