from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from typing import List, Dict, Optional, Tuple
from app.utils.prompts import get_chat_prompts
from app.utils.tools import search_trips, get_sql_tool, search_transport, search_hotels, web_search
from dotenv import load_dotenv
import asyncio

load_dotenv(override=True)

class LLMService:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in .env file")
        

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=openai_api_key
        )

        self.prompts = get_chat_prompts()

        sql_tools = get_sql_tool()
        transport_tools = [search_transport, web_search]
        accommodation_tools = [search_hotels]
        planning_tools = [web_search]
        common_tools = sql_tools + [search_trips]

        self.agents = {
            "chat": self._make_agent(common_tools, self.prompts["chat"]),
            "transport": self._make_agent(transport_tools, self.prompts["transport"]),
            "accommodation": self._make_agent(accommodation_tools, self.prompts["accomodation"]),
            "planner": self._make_agent(planning_tools, self.prompts["planner"]),
        }

    def _make_agent(self, tools, prompt):
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def run(self, stage: str, query: str, chat_history: List[Dict] = None):
        return await self.agents[stage].ainvoke({
            "input": query,
            "chat_history": chat_history or []
        })
    
    def chat(self, query: str, chat_history: List[dict] = None):
        return self.agents["chat"].invoke({
            "input": query,
            "chat_history": chat_history or []
        })["output"]

llm_service = LLMService()
