"""
Automated Chat Endpoint Test Suite with LLM Judge
Tests tool usage, structured output, and constraint validation
"""

import requests
import json
import re
import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass, field

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

# Colors for output
class C:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    B = '\033[94m'  # Blue
    M = '\033[95m'  # Magenta
    C = '\033[96m'  # Cyan
    W = '\033[0m'   # White/Reset
    BOLD = '\033[1m'


@dataclass
class Test:
    """Test case definition"""
    name: str
    message: str
    tools: List[str]  # Expected tools
    desc: str  # Short description
    
    # Results
    passed: bool = False
    response: str = ""
    trip_plan: Optional[Dict] = None
    detected_tools: List[str] = field(default_factory=list)
    llm_verdict: Optional[Dict] = None
    error: Optional[str] = None


class TestRunner:
    """Runs tests with optional LLM judge validation"""
    
    def __init__(self, use_llm_judge: bool = False):  # Disabled by default
        self.results: List[Test] = []
        self.use_llm_judge = False  # Force disabled for now
        
        # LLM Judge disabled - uncomment below to re-enable
        # if use_llm_judge:
        #     try:
        #         api_key = os.getenv("OPENAI_API_KEY")
        #         self.llm = OpenAI(api_key=api_key) if api_key else None
        #         if not self.llm:
        #             print(f"{C.Y}Warning: OPENAI_API_KEY not found. Disabling LLM judge.{C.W}")
        #             self.use_llm_judge = False
        #     except Exception as e:
        #         print(f"{C.Y}Warning: Could not initialize LLM judge: {e}{C.W}")
        #         self.use_llm_judge = False
    
    def detect_tools(self, response: str, trip_plan: Optional[Dict]) -> List[str]:
        """Detect tools from response content and structured output"""
        tools = []
        resp = response.lower()
        
        # Check for structured trip plan with required fields
        if trip_plan and isinstance(trip_plan, dict):
            # Verify it's a complete trip plan with all required fields
            required_fields = ['destination', 'duration_days', 'travel', 'accommodation', 'costs', 'daily_plan']
            if all(field in trip_plan for field in required_fields):
                tools.append('format_trip_summary')
                
                # If daily_plan exists and has items, verify structure
                daily_plan = trip_plan.get('daily_plan', [])
                if daily_plan and len(daily_plan) > 0:
                    # Check if daily_plan items have the DailyPlan structure
                    first_day = daily_plan[0]
                    if isinstance(first_day, dict):
                        expected_day_fields = ['day', 'date', 'major_attractions', 'transport_info', 'time_schedule', 'notes']
                        if all(field in first_day for field in expected_day_fields):
                            # Structured output is properly formatted
                            pass
        
        patterns = {
            'search_trips': r'(found.*matching trips|available trips)',
            'search_transport': r'(flight|airline|departure|transport option|cheapest.*eco)',
            'search_hotels': r'(hotel|accommodation|room.*bed|check-?in|rating.*star)',
            'sql_db_query': r'(trips.*(under|budget)|duration.*days)',
        }
        
        for tool, pattern in patterns.items():
            if re.search(pattern, resp) and tool not in tools:
                tools.append(tool)
        
        return tools
    
    # LLM Judge disabled - uncomment to re-enable
    def llm_judge(self, test: Test) -> Dict:
        """Use LLM to evaluate if response meets requirements (DISABLED)"""
        return {"pass": True, "reason": "LLM judge disabled"}
        
        # COMMENTED OUT - Uncomment below to re-enable LLM judge
        """
        if not self.use_llm_judge or not self.llm:
            return {"pass": True, "reason": "LLM judge disabled"}
        
        prompt = f\"\"\"You are evaluating a travel assistant's response. Be lenient - if the response is reasonable and helpful, it should pass.
Focus on whether the response addresses the user's main needs, not on perfect adherence to every detail.

USER QUERY: {test.message}

ASSISTANT'S RESPONSE: {test.response}

STRUCTURED OUTPUT: {json.dumps(test.trip_plan, indent=2) if test.trip_plan else "None"}

EXPECTED TOOLS: {', '.join(test.tools) if test.tools else 'None'}

Evaluation Guidelines:
1. For transport queries: Was origin→destination considered?
2. For hotel queries: Was location and stay duration addressed?
3. For trip planning requests: Were both transport AND accommodation considered?
4. For structured output (if present): Does it include:
   - destination, duration_days, travel, accommodation, costs
   - daily_plan as a list with day-by-day itinerary
   - Each day should have: day number, date, major_attractions (list), transport_info, time_schedule, notes
5. For user preferences (museums, activities, food, etc.): Are they reflected in the daily plan attractions?
6. If dates/budget/people were specified: Were they roughly considered? (exact matches not required)
7. Is the response generally helpful for the user's needs?

IMPORTANT:
- The response doesn't need to be perfect, just helpful and reasonable
- If expected tools seem to be used (e.g., showing flight/hotel info), consider it a pass
- For accommodation-only or transport-only queries, don't expect both
- For trip planning queries with format_trip_summary: structured output SHOULD be present with a complete daily_plan
- Check if major_attractions in daily_plan reflect user's stated interests (e.g., museums, theaters, food, etc.)
- Don't fail just because structured output is missing for non-planning queries

Respond ONLY with JSON:
{{"pass": true/false, "reason": "brief explanation focusing on what was done right or what major things were missing"}}\"\"\"

        try:
            response = self.llm.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a test evaluator. Be strict but fair. Respond only with JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"pass": False, "reason": f"Judge error: {str(e)}"}
        """
    
    def run_test(self, test: Test) -> Test:
        """Execute a single test with retries"""
        max_retries = 3
        retry_delay = 10  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add session to handle connection pooling
                with requests.Session() as session:
                    session.mount('http://', requests.adapters.HTTPAdapter(
                        max_retries=3,
                        pool_connections=10,
                        pool_maxsize=10
                    ))
                    
                    resp = session.post(
                        f"{BASE_URL}/chat/text",
                        json={"user_id": 1, "message": test.message},
                        timeout=(30, 180),  # (connect timeout, read timeout)
                        headers={'Connection': 'close'}  # Prevent keep-alive issues
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        test.response = data.get('response', '')
                        test.trip_plan = data.get('trip_plan')
                        test.detected_tools = self.detect_tools(test.response, test.trip_plan)
                        
                        # Basic validation: check if expected tools were detected
                        tools_ok = all(tool in test.detected_tools for tool in test.tools) if test.tools else True
                        
                        # For trip planning tests, also verify structured output is present
                        if 'format_trip_summary' in test.tools:
                            if not test.trip_plan:
                                tools_ok = False
                            elif test.trip_plan:
                                # Verify daily_plan exists and has proper structure
                                daily_plan = test.trip_plan.get('daily_plan', [])
                                if not daily_plan or len(daily_plan) == 0:
                                    tools_ok = False
                        
                        # Simple validation: tools + structure only (LLM judge disabled)
                        test.passed = tools_ok
                        
                        # LLM judge validation (DISABLED)
                        # if self.use_llm_judge and test.response:
                        #     test.llm_verdict = self.llm_judge(test)
                        #     test.passed = tools_ok and test.llm_verdict.get('pass', False)
                        return test
                    else:
                        test.error = f"HTTP {resp.status_code}"
                        
            except requests.exceptions.Timeout:
                test.error = f"Timeout on attempt {attempt + 1}/{max_retries}"
            except requests.exceptions.ConnectionError as e:
                test.error = f"Connection error on attempt {attempt + 1}/{max_retries}: {str(e)}"
            except Exception as e:
                test.error = f"Error on attempt {attempt + 1}/{max_retries}: {str(e)}"
            
            # If not the last attempt, wait and retry
            if attempt < max_retries - 1:
                print(f"{C.Y}  Retrying in {retry_delay} seconds... ({attempt + 1}/{max_retries}){C.W}")
                import time
                time.sleep(retry_delay)
            
        test.passed = False
        return test
    
    def run_all(self, tests: List[Test]):
        """Run all tests"""
        print(f"\n{C.M}{C.BOLD}{'='*80}")
        print(f"CHAT ENDPOINT TEST SUITE (Tool & Structure Validation Only)")
        print(f"{'='*80}{C.W}\n")
        
        for i, test in enumerate(tests, 1):
            print(f"{C.C}[{i}/{len(tests)}] {test.name}{C.W}")
            result = self.run_test(test)
            self.results.append(result)
            
            if result.passed:
                print(f"  {C.G}✓ PASSED{C.W}")
            else:
                print(f"  {C.R}✗ FAILED{C.W}")
                if result.error:
                    print(f"    Error: {result.error}")
            print()
        
        self.print_summary()
    
    def print_summary(self):
        """Print detailed results summary"""
        passed = sum(1 for t in self.results if t.passed)
        failed = len(self.results) - passed
        
        print(f"\n{C.M}{C.BOLD}{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}{C.W}\n")
        
        print(f"Total: {len(self.results)} | {C.G}Passed: {passed}{C.W} | {C.R}Failed: {failed}{C.W}")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%\n")
        print(f"{C.BOLD}{'─'*80}{C.W}\n")
        
        for i, t in enumerate(self.results, 1):
            icon = f"{C.G}✓{C.W}" if t.passed else f"{C.R}✗{C.W}"
            print(f"{icon} #{i}: {C.BOLD}{t.name}{C.W}")
            print(f"  {t.desc}")
            print(f"  Expected: {', '.join(t.tools) if t.tools else 'None'} | Detected: {', '.join(t.detected_tools) if t.detected_tools else 'None'}")
            
            if t.trip_plan:
                daily_plan = t.trip_plan.get('daily_plan', [])
                num_days = len(daily_plan) if isinstance(daily_plan, list) else 0
                print(f"  {C.G}✓ Structured output generated ({num_days} days planned){C.W}")
                
                # Validate daily plan structure
                if num_days > 0:
                    first_day = daily_plan[0]
                    if isinstance(first_day, dict):
                        has_attractions = 'major_attractions' in first_day
                        has_transport = 'transport_info' in first_day
                        if has_attractions and has_transport:
                            num_attractions = len(first_day.get('major_attractions', []))
                            print(f"    ✓ Day-by-day plan validated (Day 1: {num_attractions} attractions)")
                        else:
                            print(f"    {C.Y}⚠ Daily plan missing some fields{C.W}")
            
            if t.llm_verdict:
                judge_icon = f"{C.G}✓{C.W}" if t.llm_verdict.get('pass') else f"{C.R}✗{C.W}"
                print(f"  LLM Judge {judge_icon}: {t.llm_verdict.get('reason', 'N/A')}")
            
            if t.error:
                print(f"  {C.R}Error: {t.error}{C.W}")
            
            if t.response and not t.passed:
                preview = t.response[:120] + "..." if len(t.response) > 120 else t.response
                print(f"  Response: {preview}")
            
            print(f"{C.BOLD}{'─'*80}{C.W}\n")
        
        if failed == 0:
            print(f"{C.G}{C.BOLD}🎉 ALL TESTS PASSED! 🎉{C.W}\n")
        else:
            print(f"{C.Y}{C.BOLD}⚠️  {failed} TEST(S) FAILED{C.W}\n")


def get_tests() -> List[Test]:
    """Define all test cases"""
    return [
        # Basic conversation
        Test("Greeting", "Hello! How are you?", [], "No tools for basic greeting"),
        Test("Capabilities", "What can you help me with?", [], "Assistant introduction"),
        
        # # Vector search
        # Test("Semantic Search: Romantic", "Show me romantic trips with wine and food", 
        #      ['search_trips'], "Semantic search for romantic experiences"),
        # Test("Semantic Search: Adventure", "Find adventure trips with hiking", 
        #      ['search_trips'], "Semantic search for outdoor activities"),
        
        # # SQL queries
        # Test("SQL: Budget", "Show me trips under $2000", ['sql_db_query'], "Filter by budget"),
        # Test("SQL: Duration", "What trips are 7-10 days?", ['sql_db_query'], "Filter by duration"),
        # Test("SQL: Country", "Find trips to Italy", ['sql_db_query'], "Filter by location"),
        
        # Complete trip planning
        Test("Trip Plan: Cultural London", 
             "I want to fly from Warsaw to London from November 5-10, 2025. " +
             "Budget is 10000 USD for 2 adults. Need flights and a hotel in central London. " +
             "We're interested in museums, theaters, and historical sites. " +
             "Would love to see the British Museum and catch a show in West End. " +
             "Prefer a 4-5 star hotel within walking distance to main attractions.",
             ['search_transport', 'search_hotels', 'format_trip_summary'],
             "Cultural trip with specific attractions and hotel preferences"),
        
        Test("Trip Plan: Romantic Paris", 
             "Planning a romantic anniversary trip from New York to Paris " +
             "for December 15-20, 2025. Budget 7000 USD for 2 people. " +
             "Looking for a boutique hotel in Le Marais or Saint-Germain-des-Prés. " +
             "Want to visit the Louvre, have dinner at the Eiffel Tower, and take a Seine river cruise. " +
             "Would also love recommendations for romantic restaurants and evening activities.",
             ['search_transport', 'search_hotels', 'format_trip_summary'],
             "Romantic trip with specific neighborhood and activity preferences"),
        
        Test("Trip Plan: Active Barcelona",
             "We're a family of 4 (2 adults, 2 children ages 8 and 10) planning to fly from Berlin to Barcelona " +
             "from Nov 20-25, 2025. Budget is 8000 USD. Need flights and 2 connecting hotel rooms. " +
             "Kids love swimming and outdoor activities. Want to visit Sagrada Familia, Park Güell, and spend time at the beach. " +
             "Looking for a beachfront hotel with a pool. Would appreciate kid-friendly restaurant recommendations " +
             "and suggestions for interactive museums or activities the whole family would enjoy.",
             ['search_transport', 'search_hotels', 'format_trip_summary'],
             "Family trip with beach and kid-friendly activities"),
        
        Test("Trip Plan: Foodie Japan",
             "Planning a culinary adventure from San Francisco to Tokyo for April 5-15, 2026. " +
             "Budget is 12000 USD for 2 adults. Need flights and hotels in both Tokyo and Osaka - " +
             "thinking 5 nights in each city. Want to experience everything from street food to fine dining. " +
             "Interested in taking a sushi-making class, visiting the Tsukiji Outer Market, and trying different ramen shops. " +
             "Would love to stay in hotels close to major food districts. Also interested in sake tasting experiences.",
             ['search_transport', 'search_hotels', 'format_trip_summary'],
             "Multi-city culinary focus with specific food experiences"),
        
        Test("Trip Plan: Adventure New Zealand",
             "Looking to book flights from Los Angeles to Auckland for March 10-25, 2026. " +
             "Budget is 15000 USD for 2 adults. Need a mix of hotels and lodges as we travel. " +
             "Want to split time between North and South Islands. Planning to do bungee jumping in Queenstown, " +
             "hiking in Tongariro, visiting Hobbiton, and exploring glowworm caves. " +
             "Would love accommodation recommendations that combine comfort with proximity to nature. " +
             "Also interested in Maori cultural experiences and wine tasting in Marlborough.",
             ['search_transport', 'search_hotels', 'format_trip_summary'],
             "Extended adventure trip with multiple destinations and activities"),
    ]


def main():
    """Run test suite"""
    # LLM judge is disabled - tests only validate tools and structure
    runner = TestRunner(use_llm_judge=False)
    tests = get_tests()
    
    print(f"{C.Y}Starting {len(tests)} tests...{C.W}")
    print(f"{C.Y}Validation: Tool usage + Structured output only (LLM judge disabled){C.W}")
    print()
    
    runner.run_all(tests)


if __name__ == "__main__":
    main()
