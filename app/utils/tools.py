from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from app.services.vector_search_service import vector_search_service
from app.database import SessionLocal
from app.models import TripPlan
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def search_trips(query: str, top_k: int = 3) -> str:
    """Search existing trips in database based on description/experience. Use when users want to see what trips are available (not when planning a new trip)."""
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

@tool
def plan_trip(destination: str, duration_days: int, budget: float, activity_level: str, preferences: str = ""
) -> str:
    """Plan a NEW custom trip itinerary. Use when users ask you to PLAN or CREATE a trip (not when searching existing trips)."""
    from app.utils.prompts import get_trip_planning_prompt
    
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
    
    structured_llm = llm.with_structured_output(TripPlan)
    prompt = get_trip_planning_prompt(destination, duration_days, budget, activity_level, preferences)
    
    try:
        trip_plan = structured_llm.invoke(prompt)
        
        result = f"""# {trip_plan.destination} Trip Plan

**Duration:** {trip_plan.duration_days}

---

## 🚗 Travel

{trip_plan.travel}

---

## 🏨 Accommodation

{trip_plan.accommodation}

---

## 💰 Costs

{trip_plan.costs}

---

## 🎯 Attractions

{trip_plan.attractions}
"""
        
        return result
    except Exception as e:
        return f"Error planning trip: {str(e)}"

def get_sql_tool():
    """Get SQL database tool for querying trip database."""
    from app.utils.prompts import SQL_TOOL_DESCRIPTION
    
    db = SQLDatabase.from_uri("sqlite:///./db/roamly.db")
    
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_tools = toolkit.get_tools()
    
    for tool in sql_tools:
        if tool.name == "sql_db_query":
            tool.description = SQL_TOOL_DESCRIPTION
    
    return [t for t in sql_tools if t.name in ["sql_db_query", "sql_db_schema", "sql_db_list_tables"]]

