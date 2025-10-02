from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from app.services.vector_search_service import vector_search_service
from app.database import SessionLocal
from app.models import TripPlan
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def search_trips(query: str, top_k: int = 3) -> str:
    """Search existing trips in database based on description/experience. Use when users want to see what trips are available (not when planning a new trip)."""
    db = SessionLocal()
    try:
        results = vector_search_service.search_trips(db, query, top_k)
        
        if not results:
            return "No trips found matching your criteria."
        
        response = f"Found {len(results)} matching trips:\n\n"
        for i, (trip, score) in enumerate(results, 1):
            cities = [tc.city.name for tc in trip.cities]
            response += f"{i}. {trip.country} (Match: {score:.0%})\n"
            response += f"   {trip.description}\n"
            response += f"   Duration: {trip.duration} days | Activity: {trip.activity_level} | Budget: ${trip.budget}\n"
            response += f"   Cities: {', '.join(cities)}\n\n"
        
        return response
    finally:
        db.close()

@tool
def plan_trip(destination: str, duration_days: int, budget: float, activity_level: str, preferences: str = ""
) -> str:
    """Plan a NEW custom trip itinerary. Use when users ask you to PLAN or CREATE a trip (not when searching existing trips)."""
    from app.utils.prompts import get_trip_planning_prompt
    
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
    
    structured_llm = llm.with_structured_output(TripPlan)
    prompt = get_trip_planning_prompt(destination, duration_days, budget, activity_level, preferences)
    
    try:
        trip_plan = structured_llm.invoke(prompt)
        
        result = f"""# {trip_plan.destination} Trip Plan

**Duration:** {trip_plan.duration_days}

---

## 🚗 Travel

{trip_plan.travel}

---

## 🏨 Accommodation

{trip_plan.accommodation}

---

## 💰 Costs

{trip_plan.costs}

---

## 🎯 Attractions

{trip_plan.attractions}
"""
        
        return result
    except Exception as e:
        return f"Error planning trip: {str(e)}"

def get_sql_tool():
    """Get SQL database tool for querying trip database."""
    from app.utils.prompts import SQL_TOOL_DESCRIPTION
    
    db = SQLDatabase.from_uri("sqlite:///./db/roamly.db")
    
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_tools = toolkit.get_tools()
    
    for tool in sql_tools:
        if tool.name == "sql_db_query":
            tool.description = SQL_TOOL_DESCRIPTION
    
    return [t for t in sql_tools if t.name in ["sql_db_query", "sql_db_schema", "sql_db_list_tables"]]

from amadeus import Client, ResponseError

amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

def normalize_flight(offer):
    itinerary = offer["itineraries"][0]
    segment = itinerary["segments"][0]
    return {
        "mode": "flight",
        "provider": "Amadeus",
        "price": float(offer["price"]["total"]),
        "currency": offer["price"]["currency"],
        "duration": itinerary["duration"],
        "seats_available": offer.get("numberOfBookableSeats"),
        "co2_kg": offer["travelerPricings"][0]
            .get("fareDetailsBySegment", [{}])[0]
            .get("co2Emissions", [{}])[0]
            .get("weight", None),
        "details": {
            "airline": segment["carrierCode"],
            "from": segment["departure"]["iataCode"],
            "to": segment["arrival"]["iataCode"],
            "departure": segment["departure"]["at"],
            "arrival": segment["arrival"]["at"],
        }
    }

@tool
def search_flights():
    name = "flight_search"
    description = "Find flight offers between two cities on a given date."

    def _run(self, origin: str, destination: str, date: str, passengers: int = 1):
        try:
            resp = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=date,
                adults=passengers,
                max=5
            )
            results = [normalize_flight(offer) for offer in resp.data]
            return results
        except ResponseError as e:
            return {"error": str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError

def search_trains():
    name = "train_search"
    description = "Find train connections."
    def _run(self, origin, destination, date, passengers):
        # Call DB/SNCF API
        return [ {...}, {...} ]

def get_car_route():
    name = "car_route"
    description = "Find car route cost and duration."
    def _run(self, origin, destination, passengers, vehicle):
        # Call HERE/TollGuru
        return [ {...} ]
    
def select_top_transport():
    name = "transport_selector"
    description = "Select cheapest, fastest, and most eco-friendly from transport options."
    
    def _run(self, options: list):
        cheapest = min(options, key=lambda x: x["price"])
        eco = min(options, key=lambda x: x["co2_kg"])
        # fastest = min(options, key=lambda x: parse_duration(x["duration"]))
        return {
            "cheapest": cheapest,
            "eco": eco,
            # "fastest": fastest,
        }

@tool
def search_hotels(city_code: str, check_in_date: str, check_out_date: str, adults: int = 1, radius: int = 5) -> str:
    """Search for hotels in a city using Amadeus API. Use when users need accommodation information.
    
    Args:
        city_code: IATA city code (e.g., 'NYC', 'PAR', 'LON')
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        adults: Number of adult guests (default: 1)
        radius: Search radius in km (default: 5)
    """
    try:
        response = amadeus.shopping.hotel_offers_search.get(
            cityCode=city_code,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=adults,
            radius=radius,
            radiusUnit='KM',
            ratings=['3', '4', '5'],
            bestRateOnly=True
        )
        
        hotels = response.data[:10]
        
        if not hotels:
            return f"No hotels found in {city_code} for {check_in_date} to {check_out_date}."
        
        output = f"Found {len(hotels)} hotel options in {city_code}:\n\n"
        
        for i, hotel in enumerate(hotels, 1):
            name = hotel.get('hotel', {}).get('name', 'Unknown Hotel')
            offers = hotel.get('offers', [])
            
            if offers:
                offer = offers[0]
                price = offer.get('price', {})
                total = price.get('total', 'N/A')
                currency = price.get('currency', 'USD')
                room = offer.get('room', {})
                room_type = room.get('typeEstimated', {}).get('category', 'Standard')
                beds = room.get('typeEstimated', {}).get('beds', 1)
                
                output += f"{i}. {name}\n"
                output += f"   Price: {total} {currency} per stay\n"
                output += f"   Room: {room_type} ({beds} bed(s))\n"
                
                rating = hotel.get('hotel', {}).get('rating')
                if rating:
                    output += f"   Rating: {rating} stars\n"
                
                output += "\n"
            else:
                output += f"{i}. {name} - No offers available\n\n"
        
        return output
    
    except ResponseError as e:
        return f"Error searching hotels: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
    