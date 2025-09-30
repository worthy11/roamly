from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import SessionLocal
from typing import List

router = APIRouter(prefix="/trips", tags=["trips"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=models.UserRead)
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    pass

@router.get("/", response_model=List[models.TripRead])
def get_all_trips(db: Session = Depends(get_db)):
    trips = db.query(models.Trip).all()
    return trips