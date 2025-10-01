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
        
        ("I want a romantic getaway with great food", "Vector search"),
        ("Show me adventure trips with hiking and outdoor activities", "Vector search"),
        ("Find me a relaxing beach vacation", "Vector search"),
        
        ("Show me all trips under $2000", "SQL"),
        ("What trips are 7-10 days long?", "SQL"),
        ("Find trips in Italy", "SQL"),
        ("Show me high activity level trips", "SQL"),
        ("What's the average budget for all trips?", "SQL"),
        
        ("I want a romantic trip to Italy under $2000", "Both (SQL + Vector)"),
        ("Show me adventure trips in Canada that are less than $4500", "Both (SQL + Vector)"),
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
