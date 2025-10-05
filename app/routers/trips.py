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


@router.post("/", response_model=models.TripRead)
def create_trip(trip: models.TripCreate, db: Session = Depends(get_db)):
  
    embedding_json = None
    if trip.description:
        embedding = embedding_service.generate_embedding(trip.description)
        embedding_json = embedding_service.serialize_embedding(embedding)

    new_trip = models.Trip(
        country=trip.country,
        description=trip.description,
        duration=trip.duration,
        num_people=trip.num_people,
        activity_level=trip.activity_level,
        budget=trip.budget,
        embedding=embedding_json
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    for city_name in trip.cities:
        city_obj = db.query(models.City).filter(models.City.name == city_name).first()
        if not city_obj:
            raise HTTPException(status_code=404, detail=f"City '{city_name}' not found")
        
        trip_city = models.TripCity(trip_id=new_trip.trip_id, city_id=city_obj.city_id)
        db.add(trip_city)
    
    db.commit()
    db.refresh(new_trip)

    response = models.TripRead.model_validate({
        "trip_id": new_trip.trip_id,
        "country": new_trip.country,
        "description": new_trip.description,
        "duration": new_trip.duration,
        "num_people": new_trip.num_people,
        "activity_level": new_trip.activity_level,
        "budget": new_trip.budget,
        "cities": [models.CityRead.model_validate(tc.city) for tc in new_trip.cities]
    })
    return response