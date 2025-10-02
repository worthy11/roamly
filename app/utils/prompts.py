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

3. search_transport - Find transport options (flights, trains, cars)
   - Use when: users need transport information or pricing
   - Examples: "find flights from NYC to Paris", "how do I get to Tokyo"
   - Returns: Best transport options (cheapest, most eco-friendly)

4. search_hotels - Find accommodation options
   - Use when: users need hotel information or pricing
   - Examples: "find hotels in Paris", "where should I stay in Tokyo"
   - Returns: List of available hotels with prices and ratings

5. structure_trip_plan - Transform previous
    - Use when: users ask you to PLAN or CREATE a trip for them and you have the transport and hotel options
    - Examples: "plan me a trip to Japan", "create an itinerary for Italy"
    - Returns: Detailed structured trip plan with daily itinerary

Strategy:
- "Show me trips to X" → search_trips or SQL (existing trips)
- "Find flights/transport..." → search_transport
- "Find hotels..." → search_hotels
- General questions → answer directly

For trip planning requests you should use the tools in the following order:
1. search_transport
2. search_hotels
3. structure_trip_plan

Be friendly, conversational, and help users discover great travel experiences."""

def get_chat_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", TRAVEL_ASSISTANT_SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])