from langchain.tools import tool
from app.services.vector_search_service import vector_search_service
from app.database import SessionLocal

@tool
def search_trips(query: str, top_k: int = 3) -> str:
    """Search for trips based on user preferences. Use this when users describe what kind of trip they want."""
    db = SessionLocal()
    try:
        results = vector_search_service.search_trips(db, query, top_k)
        
        if not results:
            return "No trips found matching your criteria."
        
        response = f"Found {len(results)} matching trips:\n\n"
        for i, (trip, score) in enumerate(results, 1):
            cities = [tc.city.name for tc in trip.cities]
            response += f"{i}. {trip.country} (Match: {score:.0%})\n"
            response += f"   {trip.description}\n"
            response += f"   Duration: {trip.duration} days | Activity: {trip.activity_level} | Budget: ${trip.budget}\n"
            response += f"   Cities: {', '.join(cities)}\n\n"
        
        return response
    finally:
        db.close()

