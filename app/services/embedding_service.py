from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
import json

class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    def generate_embedding(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)
    
    def generate_trip_text(self, trip_data: dict) -> str:
        parts = []
        if trip_data.get('country'):
            parts.append(f"Country: {trip_data['country']}")
        if trip_data.get('description'):
            parts.append(f"Description: {trip_data['description']}")
        if trip_data.get('activity_level'):
            parts.append(f"Activity level: {trip_data['activity_level']}")
        if trip_data.get('duration'):
            parts.append(f"Duration: {trip_data['duration']} days")
        if trip_data.get('budget'):
            parts.append(f"Budget: ${trip_data['budget']}")
        return " | ".join(parts)
    
    def serialize_embedding(self, embedding: List[float]) -> str:
        return json.dumps(embedding)
    
    def deserialize_embedding(self, embedding_str: str) -> List[float]:
        return json.loads(embedding_str)

embedding_service = EmbeddingService()
