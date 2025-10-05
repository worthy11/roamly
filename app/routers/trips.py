from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.models as models
from app.database import SessionLocal
from typing import List
from app.services.embedding_service import embedding_service

router = APIRouter(prefix="/trips", tags=["trips"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_trips(db: Session = Depends(get_db)):
    trips = db.query(models.Trip).all()
    return trips


@router.post("/", response_model=models.TripRead)
def create_trip(trip: models.TripCreate, db: Session = Depends(get_db)):
  
    embedding_json = None
    if trip.description:
        embedding = embedding_service.generate_embedding(trip.description)
        embedding_json = embedding_service.serialize_embedding(embedding)

    new_trip = models.Trip(
        title=trip.title,
        description=trip.description,
        duration=trip.duration,
        num_people=trip.num_people,
        activity_level=trip.activity_level,
        budget=trip.budget,
        cities=trip.cities,
        lat=trip.lat,
        lng=trip.lng,
        embedding=embedding_json
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    return new_trip