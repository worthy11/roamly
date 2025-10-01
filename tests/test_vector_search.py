import sqlite3
from pathlib import Path
from app.services.embedding_service import embedding_service
from app.services.vector_search_service import vector_search_service

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "roamly.db"

def test_vector_search():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    test_queries = [
        "romantic trip to Europe with good food",
        "adventure and outdoor activities",
        "cultural experience with art and history",
        "tropical beach vacation",
        "family friendly road trip"
    ]
    
    print("\n" + "="*70)
    print("VECTOR SEARCH TEST")
    print("="*70)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 70)
        
        query_embedding = embedding_service.generate_embedding(query)
        
        cur.execute("SELECT trip_id, country, description, duration, activity_level, budget, embedding FROM trips WHERE embedding IS NOT NULL")
        trips = cur.fetchall()
        
        results = []
        for trip in trips:
            trip_id, country, description, duration, activity_level, budget, embedding_json = trip
            trip_embedding = embedding_service.deserialize_embedding(embedding_json)
            similarity = vector_search_service.cosine_similarity(query_embedding, trip_embedding)
            results.append((trip_id, country, description, duration, activity_level, budget, similarity))
        
        results.sort(key=lambda x: x[6], reverse=True)
        
        print(f"\nTop 3 matches:")
        for i, (trip_id, country, description, duration, activity_level, budget, score) in enumerate(results[:3], 1):
            print(f"\n  {i}. [{score:.4f}] {country}")
            print(f"     {description}")
            print(f"     Duration: {duration} days | Activity: {activity_level} | Budget: ${budget}")
    
    conn.close()
    print("\n" + "="*70)
    print("✓ Vector search test completed successfully!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_vector_search()

