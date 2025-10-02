from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from typing import List, Dict
from app.utils.prompts import get_chat_prompt
from app.utils.tools import search_trips, get_sql_tool, plan_trip
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=api_key
        )
        
        sql_tool = get_sql_tool()
        self.tools = [search_trips, plan_trip] + sql_tool
        self.prompt = get_chat_prompt()
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def chat(self, message: str, chat_history: List[Dict] = None) -> str:
        response = self.agent_executor.invoke({
            "input": message,
            "chat_history": chat_history or []
        })
        return response["output"]

llm_service = LLMService()
