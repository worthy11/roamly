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

TRAVEL_ASSISTANT_SYSTEM_MESSAGE = """You are a helpful travel assistant. You help users find their perfect trip.

You have access to multiple tools:

1. search_trips tool - Use for description-based search when users describe the TYPE of experience:
   - "romantic trip", "adventure vacation", "cultural experience"
   - "relaxing beach holiday", "hiking trip"

2. SQL database tool - Use for specific criteria and filtering:
   - Budget constraints: "trips under $2000", "between $1500 and $2500"
   - Duration: "7-10 days", "longer than 2 weeks"
   - Activity level: "high activity", "low activity", "medium"
   - Country/location: "trips in Italy", "European destinations"
   - Combinations: "high activity trips in Canada under $5000"

Strategy:
- For experience descriptions → use search_trips
- For specific criteria regarding budget, duration, activity level, country, or combinations → query the SQL database
- For complex queries → combine both approaches

Be friendly, conversational, and help users discover great travel experiences."""

def get_chat_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", TRAVEL_ASSISTANT_SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

