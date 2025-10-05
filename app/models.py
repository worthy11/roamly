from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()

class Trip(Base):
    __tablename__ = "trips"
    trip_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    duration = Column(Integer)
    num_people = Column(Integer)
    activity_level = Column(String)
    budget = Column(Float)
    cities = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    embedding = Column(Text)

class TripCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None
    num_people: Optional[int] = None
    activity_level: Optional[str] = None
    budget: Optional[float] = None
    cities: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class TripRead(BaseModel):
    trip_id: int
    title: str
    description: Optional[str]
    duration: Optional[int]
    num_people: Optional[int]
    activity_level: Optional[str]
    budget: Optional[float]
    cities: str
    lat: Optional[float]
    lng: Optional[float]

    model_config = dict(from_attributes=True)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class Attraction(BaseModel):
    name: str
    time_of_day: str
    lat: float
    lon: float

class DailyPlan(BaseModel):
    day: int
    date: str
    description: str
    major_attractions: Optional[List[Attraction]] = None
    transport_info: Optional[str] = None
    time_schedule: Optional[str] = None
    notes: Optional[str] = None

class TripPlan(BaseModel):
    destination: str
    duration_days: str
    travel: str
    accommodation: str
    costs: str
    daily_plan: List[DailyPlan]

class ChatResponse(BaseModel):
    response: str
    trip_plan: Optional[TripPlan] = None

class TripRequest(BaseModel):
    start_location: str
    destination: Optional[str] = ""
    transport: Optional[str] = ""
    num_people: Optional[int] = 1
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    activity_level: Optional[str] = ""
    pop_density: Optional[str] = "medium"
    budget: Optional[float] = 1000
    keypoints: Optional[List[str]] = []