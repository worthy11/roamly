from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

TRAVEL_ASSISTANT_SYSTEM_MESSAGE = """You are a helpful travel assistant. You help users find their perfect trip.

When users describe what kind of trip they want, use the search_trips tool to find matching trips.
Be friendly, conversational, and help users discover great travel experiences.

If users ask general questions about travel, answer them naturally.
If they describe preferences or ask for trip recommendations, use the search tool."""

def get_chat_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", TRAVEL_ASSISTANT_SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

