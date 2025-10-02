import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat(message: str, expected_tools: str, user_id: int = 1):
    print(f"\n{'='*70}")
    print(f"Expected: {expected_tools}")
    print(f"User: {message}")
    print(f"{'='*70}")
    
    response = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "user_id": user_id,
            "message": message
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAssistant: {data['response']}\n")
    else:
        print(f"\nError {response.status_code}: {response.text}\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Testing Chat Endpoint - Tool Usage Scenarios")
    print("="*70)
    
    test_cases = [
        ("What is the capital of France?", "No tools"),
        ("Hello! Can you help me plan a trip?", "No tools"),
        
        ("Show me romantic trips with great food", "Vector search"),
        ("Find me adventure trips with outdoor activities", "Vector search"),
        
        ("Show me all trips under $2000", "SQL"),
        ("What trips are 7-10 days long?", "SQL"),
        ("Find trips in Italy", "SQL"),
        
        ("Plan a 7-day trip to Japan for $3000", "plan_trip"),
        ("Help me plan a romantic trip to Italy with $2500 budget", "plan_trip"),
        ("Create a 10-day adventure itinerary for Iceland", "plan_trip"),
    ]
    
    for i, (query, expected) in enumerate(test_cases, 1):
        print(f"\n\n{'#'*70}")
        print(f"Test Case {i}/{len(test_cases)}")
        print(f"{'#'*70}")
        test_chat(query, expected)
        
        if i < len(test_cases):
            input("Press Enter to continue...")
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)
