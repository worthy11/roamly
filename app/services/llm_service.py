from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from typing import List, Dict, Optional, Tuple
from app.utils.prompts import get_chat_prompt
from app.utils.tools import search_trips, get_sql_tool, format_trip_summary, search_transport, search_hotels
from app.models import TripPlan
import os
import json
import re
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
        self.tools = [search_trips, format_trip_summary, search_transport, search_hotels] + sql_tool
        self.prompt = get_chat_prompt()
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def chat(self, message: str, chat_history: List[Dict] = None) -> Tuple[str, Optional[TripPlan]]:
        """
        Process a chat message and return the response text and optional structured trip plan.
        
        Returns:
            Tuple of (response_text, trip_plan) where trip_plan is None if no structured output
        """
        response = self.agent_executor.invoke({
            "input": message,
            "chat_history": chat_history or []
        })
        
        output = response["output"]
        
        # Check if output contains structured trip plan
        match = re.search(r'__STRUCTURED__(.+?)__STRUCTURED__', output, re.DOTALL)
        if match:
            try:
                structured_data = json.loads(match.group(1))
                trip_plan_data = structured_data.get("trip_plan")
                text_summary = structured_data.get("text_summary", "")
                
                if trip_plan_data:
                    trip_plan = TripPlan(**trip_plan_data)
                    
                    # Print structured output to console
                    print("\n" + "="*80)
                    print("📋 STRUCTURED TRIP PLAN OUTPUT")
                    print("="*80)
                    print(f"🌍 Destination: {trip_plan.destination}")
                    print(f"📅 Duration: {trip_plan.duration_days}")
                    print(f"\n🚗 TRAVEL:\n{trip_plan.travel}")
                    print(f"\n🏨 ACCOMMODATION:\n{trip_plan.accommodation}")
                    print(f"\n💰 COSTS:\n{trip_plan.costs}")
                    print(f"\n🎯 ATTRACTIONS:\n{trip_plan.attractions}")
                    print("="*80 + "\n")
                    
                    # Return the text summary and the structured plan
                    return (text_summary, trip_plan)
            except Exception as e:
                print(f"Error parsing structured output: {e}")
                return (output, None)
        
        return (output, None)

llm_service = LLMService()
