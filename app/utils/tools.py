from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from app.services.vector_search_service import vector_search_service
from app.database import SessionLocal
from app.models import TripPlan
import requests
import os
import json
import time
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
def search_transport(origin: str, destination: str, date: str, passengers: int, pref_type: str = "") -> str:
    """Search for transport options (flights, transit, cars) and return best options.
    
    Args:
        origin: Origin city IATA code
        destination: Destination city IATA code
        date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers
        pref_type: Preferred transport type ('plane', 'transit', 'car', or empty for all)
    """
    options = []

    if not pref_type or pref_type == "plane":
        flights = get_flights(origin, destination, date, passengers)
        if flights and not isinstance(flights, dict):
            options.extend(flights)
        
    if not options or not pref_type or pref_type == "transit":
        for train in get_transit(origin, destination, date, passengers):
            options.append(train)

    if not options or not pref_type or pref_type == "car":
        for car in get_car_routes(origin, destination, date, passengers):
            options.append(car)

    return options

def get_flights(origin: str, destination: str, date: str, passengers: int):
    """Find flight offers between two cities on a given date."""
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

def estimate_co2(self, distance_km: float, passengers: int) -> float:
    factor = 0.1
    return round(distance_km * factor * passengers, 2)

def get_transit(origin, destination, date, passengers):
    """Get transit options on a given date."""
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",
            "transit_mode": "train",
            "departure_time": date if date != "now" else int(time.time()),
            "key": os.getenv("GOOGLE_API_KEY"),
            "alternatives": "true"
        }
        resp = requests.get(url, params=params)
        data = resp.json()

        routes = []
        for route in data.get("routes", [])[:3]:
            leg = route["legs"][0]

            departure = leg["departure_time"]["text"]
            arrival = leg["arrival_time"]["text"]
            duration = leg["duration"]["text"]
            distance_m = leg["distance"]["value"]

            mode_type = "transit"
            fare = route.get("fare")
            price = float(fare["value"]) if fare else None
            currency = fare["currency"] if fare else None

            stops = []
            for step in leg["steps"]:
                if step.get("travel_mode") == "TRANSIT":
                    vehicle_type = step["transit_details"]["line"]["vehicle"]["type"]
                    if vehicle_type == "BUS":
                        mode_type = "bus"
                    elif vehicle_type in ("HEAVY_RAIL", "RAIL", "SUBWAY"):
                        mode_type = "train"
                    else:
                        mode_type = "transit"

                    stops.append(step["transit_details"]["headsign"])

            distance_km = distance_m / 1000
            if mode_type == "bus":
                factor = 0.1
            elif mode_type == "train":
                factor = 0.02
            else:
                factor = 0.05
            co2 = round(distance_km * factor * passengers, 2)

            routes.append({
                "mode": mode_type,
                "provider": "Google Transit",
                "price": price,
                "currency": currency,
                "duration": duration,
                "seats_available": None,
                "co2_kg": co2,
                "details": {
                    "from": leg["start_address"],
                    "to": leg["end_address"],
                    "departure": departure,
                    "arrival": arrival,
                    "stops": stops
                }
            })

        return routes
    except Exception as e:
        return {"error": str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError

def get_car_routes(origin: str, destination: str, fuel_type: str = "gasoline",
             consumption_l_per_100km: float = 7.0, fuel_price_per_l: float = 1.8,
             passengers: int = 1, seats: int = 4):
    """Find driving routes, cost, and CO2 estimates using Google Maps Routes API."""

    try:
        url = "https://routes.googleapis.com/v2/routes:computeRoutes"
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": os.getenv("GOOGLE_API_KEY")}
        body = {
            "origin": {"address": origin},
            "destination": {"address": destination},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE"
        }
        resp = requests.post(url, headers=headers, json=body)
        data = resp.json()

        routes = []
        for route in data.get("routes", [])[:3]:
            leg = route["legs"][0]
            distance_km = leg["distanceMeters"] / 1000
            duration = leg["duration"]

            liters_used = (consumption_l_per_100km / 100) * distance_km
            cost = liters_used * fuel_price_per_l

            if fuel_type == "gasoline":
                co2_factor = 2.31
            elif fuel_type == "diesel":
                co2_factor = 2.68
            else:
                co2_factor = 0.1
            co2 = liters_used * co2_factor

            routes.append({
                "mode": "car",
                "provider": "Google Routes",
                "price": round(cost, 2),
                "currency": "EUR",
                "duration": duration,
                "seats_available": seats,
                "co2_kg": round(co2 * passengers, 2),
                "details": {
                    "from": leg["startLocation"]["latLng"],
                    "to": leg["endLocation"]["latLng"],
                    "distance_km": round(distance_km, 1),
                    "fuel_type": fuel_type,
                    "consumption_l_per_100km": consumption_l_per_100km
                }
            })
        return routes
    except Exception as e:
        return {"error": str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError

@tool
def format_trip_summary(destination: str, duration_days: int, transport_info: str, hotel_info: str, preferences: str = "") -> str:
    """Format transport and hotel search results into a structured trip summary. 
    Use ONLY after you have already called search_transport AND search_hotels.
    
    Args:
        destination: The destination city or country
        duration_days: Number of days for the trip
        transport_info: The complete output string from search_transport tool
        hotel_info: The complete output string from search_hotels tool
        preferences: Additional user preferences or requirements
    """
    from app.utils.prompts import get_trip_summary_prompt
    
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
    
    structured_llm = llm.with_structured_output(TripPlan)
    prompt = get_trip_summary_prompt(destination, duration_days, transport_info, hotel_info, preferences)
    
    try:
        trip_plan = structured_llm.invoke(prompt)
        
        # Return as JSON with a special marker for the service to parse
        result = {
            "structured_output": True,
            "trip_plan": trip_plan.model_dump(),
            "text_summary": f"""Trip to {trip_plan.destination} ({trip_plan.duration_days})

🚗 Travel: {trip_plan.travel[:200]}...

🏨 Accommodation: {trip_plan.accommodation[:200]}...

💰 Costs: {trip_plan.costs[:150]}...

🗓️ Daily plan: {len(trip_plan.daily_plan)} days planned with personalized attractions and local transport info..."""
        }
        
        # Ensure JSON serialization works properly
        json_output = json.dumps(result, ensure_ascii=False)
        return f"__STRUCTURED__{json_output}__STRUCTURED__"
    except Exception as e:
        print(f"❌ Error in format_trip_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error planning trip: {str(e)}"


@tool
def search_hotels(city_code: str, check_in_date: str, check_out_date: str, adults: int = 2, room_quantity: int = 1, children: int = 0) -> str:
    """Search for hotels in a city using Amadeus API. Use when users need accommodation information.
    
    Args:
        city_code: IATA city code (e.g., 'NYC', 'PAR', 'LON')
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        adults: Number of adult guests (default: 2)
        room_quantity: Number of rooms needed (default: 1)
        children: Number of child guests (default: 0)
    """
    try:
        # First, get hotel IDs in the city using hotel list API
        hotel_list_response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code
        )
        
        if not hotel_list_response.data:
            return f"No hotels found in {city_code}."
        
        # Get hotel IDs (limit to first 50 for offer search)
        hotel_ids = [hotel['hotelId'] for hotel in hotel_list_response.data[:50]]
        
        # Build API parameters
        api_params = {
            'hotelIds': ','.join(hotel_ids),
            'checkInDate': check_in_date,
            'checkOutDate': check_out_date,
            'adults': adults,
            'roomQuantity': room_quantity
        }
        
        # Only add children parameter if > 0
        if children > 0:
            api_params['children'] = children
        
        # Now search for offers using hotel IDs
        response = amadeus.shopping.hotel_offers_search.get(**api_params)
        
        hotels = response.data[:10]
        
        if not hotels:
            return f"No hotel offers found in {city_code} for {check_in_date} to {check_out_date}."
        
        total_guests = adults + children
        output = f"Found {len(hotels)} hotel options in {city_code} for {total_guests} guest(s) in {room_quantity} room(s):\n\n"
        
        for i, hotel in enumerate(hotels, 1):
            hotel_info = hotel.get('hotel', {})
            name = hotel_info.get('name', 'Unknown Hotel')
            offers = hotel.get('offers', [])
            
            if offers:
                offer = offers[0]
                price = offer.get('price', {})
                total_price = price.get('total', 'N/A')
                currency = price.get('currency', 'USD')
                
                # Room details
                room = offer.get('room', {})
                room_type_est = room.get('typeEstimated', {})
                room_category = room_type_est.get('category', 'Standard')
                beds = room_type_est.get('beds', 1)
                bed_type = room_type_est.get('bedType', 'Unknown')
                
                # Room description
                room_description = room.get('description', {}).get('text', '')
                
                # Policies
                policies = offer.get('policies', {})
                cancellation = policies.get('cancellation', {})
                cancellation_type = cancellation.get('type', 'N/A')
                
                # Guest info
                guests = offer.get('guests', {})
                adults_allowed = guests.get('adults', adults)
                
                output += f"{i}. {name}\n"
                
                # Rating
                rating = hotel_info.get('rating')
                if rating:
                    output += f"   Rating: {rating} stars\n"
                
                # Price info
                output += f"   Price: {total_price} {currency}"
                if room_quantity > 1:
                    try:
                        per_room = float(total_price) / room_quantity
                        output += f" total ({per_room:.2f} {currency} per room)"
                    except:
                        pass
                output += "\n"
                
                # Room details
                output += f"   Room: {room_category} - {beds} {bed_type} bed(s)\n"
                output += f"   Capacity: Up to {adults_allowed} adults per room\n"
                
                # Room description if available
                if room_description:
                    desc_short = room_description[:100] + "..." if len(room_description) > 100 else room_description
                    output += f"   Description: {desc_short}\n"
                
                # Cancellation policy
                if cancellation_type != 'N/A':
                    output += f"   Cancellation: {cancellation_type}\n"
                
                # Hotel address if available
                address = hotel_info.get('address', {})
                if address:
                    city_name = address.get('cityName', '')
                    if city_name:
                        output += f"   Location: {city_name}\n"
                
                output += "\n"
            else:
                output += f"{i}. {name} - No offers available\n\n"
        
        return output
    
    except ResponseError as e:
        error_details = f"Amadeus API Error: {e.response.status_code}\n"
        error_details += f"Description: {e.description}\n"
        if hasattr(e, 'response') and hasattr(e.response, 'body'):
            error_details += f"Details: {e.response.body}"
        return f"Error searching hotels: {error_details}"
    except Exception as e:
        return f"Error: {str(e)}"
    