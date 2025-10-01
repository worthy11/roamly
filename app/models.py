from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    pass_hash = Column(String, nullable=False)

    trips = relationship("Trip", back_populates="user")


class Trip(Base):
    __tablename__ = "trips"
    trip_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    country = Column(String, nullable=False)
    description = Column(Text)
    duration = Column(Integer)
    num_people = Column(Integer)
    activity_level = Column(String)
    budget = Column(Float)
    embedding = Column(Text)

    user = relationship("User", back_populates="trips")
    cities = relationship("TripCity", back_populates="trip")


class City(Base):
    __tablename__ = "cities"
    city_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    lat = Column(Float)
    lon = Column(Float)

    trips = relationship("TripCity", back_populates="city")


class TripCity(Base):
    __tablename__ = "trip_cities"
    relation_id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.city_id"), nullable=False)

    trip = relationship("Trip", back_populates="cities")
    city = relationship("City", back_populates="trips")


class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserRead(BaseModel):
    user_id: int
    name: str
    email: str

    model_config = dict(from_attributes=True)


class TripCreate(BaseModel):
    country: str
    description: Optional[str] = None
    duration: Optional[int] = None
    num_people: Optional[int] = None
    activity_level: Optional[str] = None
    budget: Optional[float] = None
    cities: List[str]

class CityRead(BaseModel):
    name: str
    lat: float
    lon: float
    model_config = dict(from_attributes=True)

class TripRead(BaseModel):
    trip_id: int
    country: str
    description: Optional[str]
    duration: Optional[int]
    num_people: Optional[int]
    activity_level: Optional[str]
    budget: Optional[float]
    cities: List[CityRead] = []

    model_config = dict(from_attributes=True)

class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    response: str
    user_id: int