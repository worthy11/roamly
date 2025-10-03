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

def get_trip_summary_prompt(destination: str, duration_days: int, transport_info: str, hotel_info: str, preferences: str = "") -> str:
    return f"""Format the following trip search results into a structured summary:

Destination: {destination}
Duration: {duration_days} days
User Preferences: {preferences}

TRANSPORT OPTIONS FOUND:
{transport_info}

ACCOMMODATION OPTIONS FOUND:
{hotel_info}

Create a formatted summary with exactly these sections:

1. destination (string): The destination name
2. duration_days (string): Trip duration
3. travel (string): Summarize the transport options found, highlighting the best choices with prices and times
4. accommodation (string): Summarize the hotel options found, highlighting good value options with prices and locations
5. costs (string): Calculate and present total estimated costs based on the actual prices from transport and hotels
6. attractions (string): Based on the destination, suggest key attractions and activities to visit"""

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
   - Parameters: city_code, check_in_date, check_out_date, adults (default: 2), room_quantity (default: 1), children (default: 0)
   - Examples: "find hotels in Paris for 4 people", "where should I stay in Tokyo with 2 adults and 1 child"
   - Returns: List of hotels with prices (total and per room), ratings, room details, capacity, descriptions, and cancellation policies

5. structure_trip_plan - Transform previous
    - Use when: users ask you to PLAN or CREATE a trip for them and you have the transport and hotel options
    - Examples: "plan me a trip to Japan", "create an itinerary for Italy"
    - Returns: Detailed structured trip plan with daily itinerary

Strategy:
- "Show me trips to X" → search_trips or SQL (existing trips)
- "Find flights/transport..." → search_transport
- "Find hotels..." → search_hotels
- "Plan a trip to X" → First search_transport, then search_hotels, then format_trip_summary
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