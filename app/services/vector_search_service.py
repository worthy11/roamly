import numpy as np
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.services.embedding_service import embedding_service
from app import models

class VectorSearchService:
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        vec1_arr = np.array(vec1)
        vec2_arr = np.array(vec2)
        dot_product = np.dot(vec1_arr, vec2_arr)
        norm1 = np.linalg.norm(vec1_arr)
        norm2 = np.linalg.norm(vec2_arr)
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
    
    def search_trips(
        self, 
        db: Session, 
        query: str, 
        top_k: int = 5
    ) -> List[Tuple[models.Trip, float]]:
        query_embedding = embedding_service.generate_embedding(query)
        
        trips = db.query(models.Trip).filter(models.Trip.embedding.isnot(None)).all()
        
        results = []
        for trip in trips:
            trip_embedding = embedding_service.deserialize_embedding(trip.embedding)
            similarity = self.cosine_similarity(query_embedding, trip_embedding)
            results.append((trip, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

vector_search_service = VectorSearchService()
