import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat(message: str, user_id: int = 1):
    print(f"\n{'='*70}")
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
    print("\nTesting Chat Endpoint with Vector Search Tool\n")
    
    test_queries = [
        "Hello! Can you help me find a trip?",
        "I want a romantic getaway in Europe with great food",
        "Show me some adventure trips with outdoor activities",
        "What about a cultural trip with museums and history?"
    ]
    
    for query in test_queries:
        test_chat(query)
        input("Press Enter to continue...")

