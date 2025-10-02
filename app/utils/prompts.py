from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SQL_TOOL_DESCRIPTION = """Execute SQL queries on the trips database. Use this for specific criteria like budget, duration, activity level, country, number of people, or combinations. 

Available tables:
- trips (trip_id, user_id, country, description, duration, num_people, activity_level, budget, embedding)
- cities (city_id, name, country, lat, lon)
- trip_cities (relation_id, trip_id, city_id)

Examples:
- Budget filter: SELECT * FROM trips WHERE budget <= 2000
- Duration: SELECT * FROM trips WHERE duration BETWEEN 7 AND 10
- Activity: SELECT * FROM trips WHERE activity_level = 'high'
- Country: SELECT * FROM trips WHERE country LIKE '%Italy%'
- Combined: SELECT * FROM trips WHERE budget < 2500 AND duration >= 7"""

def get_trip_planning_prompt(destination: str, duration_days: int, budget: float, activity_level: str, preferences: str) -> str:
    return f"""Create a detailed trip plan for:
    
Destination: {destination}
Duration: {duration_days} days
Budget: ${budget}
Activity Level: {activity_level}
Preferences: {preferences}

Structure the plan with exactly these 4 text sections:

1. travel (string): Describe transportation, routes, travel times, and tips
2. accommodation (string): Describe suggested areas, types, costs, and booking tips
3. costs (string): Provide detailed cost breakdown with totals
4. attractions (string): List and describe attractions with time needed and costs"""

TRAVEL_ASSISTANT_SYSTEM_MESSAGE = """You are a helpful travel assistant. You help users find their perfect trip.

You have access to multiple tools:

1. search_trips - Search existing trips by description/experience
   - Use when: users want to see what trips are available
   - Examples: "show me romantic trips", "find adventure vacations"

2. SQL database - Query existing trips by specific criteria
   - Use when: users want to filter by budget, duration, country, activity level
   - Examples: "trips under $2000", "7-10 day trips in Italy"

3. structure_trip_plan - Transform previous
   - Use when: users ask you to PLAN or CREATE a trip for them
   - Examples: "plan me a trip to Japan", "create an itinerary for Italy"
   - Returns: Detailed structured trip plan with daily itinerary

4. search_flights - Find flight offers between cities
   - Use when: users need flight information or pricing
   - Examples: "find flights from NYC to Paris", "how much is a flight to Tokyo"

5. select_top_transport - Compare transport options
   - Use when: you need to select best transport from multiple options
   - Returns: Cheapest and most eco-friendly choices

Strategy:
- "Show me trips to X" → search_trips or SQL (existing trips)
- "Plan a trip to X" → plan_trip (create new itinerary)
- "Find flights..." → search_flights
- "Help me plan..." → plan_trip
- General questions → answer directly

Be friendly, conversational, and help users discover great travel experiences."""

def get_chat_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", TRAVEL_ASSISTANT_SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])