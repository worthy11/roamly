from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from app.services.vector_search_service import vector_search_service
from app.database import SessionLocal
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def search_trips(query: str, top_k: int = 3) -> str:
    """Search for trips based on description/experience. Use this when users describe the TYPE of trip they want (romantic, adventure, cultural, relaxing, beach, etc.)."""
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

