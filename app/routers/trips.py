from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import app.models as models
from app.database import SessionLocal
from typing import List

router = APIRouter(prefix="/trips", tags=["trips"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_trips(db: Session = Depends(get_db), response_model=List[models.TripRead]):
    trips = db.query(models.Trip).all()
    result = []
    for trip in trips:
        trip_data = models.TripRead.model_validate({
            "trip_id": trip.trip_id,
            "country": trip.country,
            "description": trip.description,
            "duration": trip.duration,
            "num_people": trip.num_people,
            "activity_level": trip.activity_level,
            "budget": trip.budget,
        })
        trip_data.cities = [models.CityRead.model_validate(tc.city) for tc in trip.cities]
        result.append(trip_data)
    return result