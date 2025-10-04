from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from app.services.vector_search_service import vector_search_service
from app.database import SessionLocal
from app.models import TripPlan
import requests
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv(override=True)

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
def search_transport(origin: str, destination: str, date: str, passengers: int=1, pref_type: str = "") -> str:
    """Search for transport options (flights, trains, cars) and return best options.
    
    Args:
        origin: Origin city name or IATA code
        destination: Destination city name or IATA code
        date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers
        pref_type: Preferred transport type ('plane', 'transit', 'car', or empty for all)
    """
    print(f"\n{'='*80}")
    print(f"SEARCH_TRANSPORT CALLED")
    print(f"{'='*80}")
    print(f"Parameters:")
    print(f"  origin: {origin}")
    print(f"  destination: {destination}")
    print(f"  date: {date}")
    print(f"  passengers: {passengers}")
    print(f"  pref_type: {pref_type}")
    print(f"{'='*80}\n")
    
    options = []
    errors = []

    if not pref_type or pref_type == "plane":
        flights = get_flights(origin, destination, date, passengers)
        
        if flights and not isinstance(flights, dict):
            options.extend(flights)
        elif isinstance(flights, dict) and "error" in flights:
            errors.append(f"Flights: {flights['error']}")
        
    if not options or not pref_type or pref_type == "transit":
        transit_result = get_transit(origin, destination, date, passengers)
        
        if isinstance(transit_result, dict) and "error" in transit_result:
            errors.append(f"Transit: {transit_result['error']}")
        else:
            for train in transit_result:
                options.append(train)

    if not options or not pref_type or pref_type == "car":
        cars = get_car_routes(origin, destination, date, passengers)
        
        if isinstance(cars, dict) and "error" in cars:
            errors.append(f"Cars: {cars['error']}")
        else:
            for car in cars:
                options.append(car)
    
    top_k = select_top_transport(options)
    
    # Add warnings if there are errors but we have some valid options
    if errors and isinstance(top_k, dict) and "error" not in top_k:
        top_k["warnings"] = errors
    
    return top_k

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
    except Exception as e:
        return {"error": str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError

def estimate_co2(self, distance_km: float, passengers: int) -> float:
    factor = 0.1
    return round(distance_km * factor * passengers, 2)

def get_transit(origin, destination, date, passengers):
    """Get transit options using Google Routes API v2."""
    print(f"\n{'='*80}")
    print(f"GET_TRANSIT CALLED")
    print(f"{'='*80}")
    print(f"Parameters received:")
    print(f"  origin: {origin}")
    print(f"  destination: {destination}")
    print(f"  date: {date}")
    print(f"  passengers: {passengers}")
    
    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        print(f"  API key present: {bool(google_api_key)}")
        
        # Convert date to Unix timestamp
        if date == "now":
            departure_timestamp = int(time.time())
        else:
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                departure_timestamp = int(date_obj.timestamp())
            except ValueError:
                departure_timestamp = int(time.time())
        
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-Goog-Api-Key": google_api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.steps.transitDetails"
        }
        
        # Convert timestamp to RFC3339 format
        departure_time_rfc3339 = datetime.fromtimestamp(departure_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Routes API v2 request body
        body = {
            "origin": {
                "address": origin
            },
            "destination": {
                "address": destination
            },
            "travelMode": "TRANSIT",
            "transitPreferences": {
                "routingPreference": "LESS_WALKING"
            },
            "departureTime": departure_time_rfc3339,
            "computeAlternativeRoutes": True
        }
        
        print(f"\nRequest details:")
        print(f"  URL: {url}")
        print(f"  Departure time (RFC3339): {departure_time_rfc3339}")
        
        resp = requests.post(url, headers=headers, json=body)
        data = resp.json()
        
        print(f"\nAPI Response:")
        print(f"  Status code: {resp.status_code}")
        print(f"  Response data:")
        import json as json_lib
        print(json_lib.dumps(data, indent=2, ensure_ascii=False))

        routes = []
        if "routes" in data:
            for route in data["routes"][:3]:
                leg = route["legs"][0]
                
                # Extract basic info
                duration_seconds = int(route["duration"].replace("s", ""))
                distance_meters = int(route["distanceMeters"])
                
                # Convert duration to readable format
                hours = duration_seconds // 3600
                minutes = (duration_seconds % 3600) // 60
                duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                
                # Calculate CO2 (transit is more eco-friendly)
                distance_km = distance_meters / 1000
                co2_factor = 0.05  # Transit CO2 factor
                co2 = round(distance_km * co2_factor * passengers, 2)
                
                # Extract fare information (if available)
                fare_info = route.get("fare", {})
                price = fare_info.get("value") if fare_info else None
                currency = fare_info.get("currency") if fare_info else None
                
                # Extract transit details and times from steps
                transit_details = []
                first_departure = None
                last_arrival = None
                
                if "steps" in leg:
                    for step in leg["steps"]:
                        if step.get("travelMode") == "TRANSIT":
                            transit_info = step.get("transitDetails", {})
                            if transit_info:
                                line_info = transit_info.get("transitLine", {})
                                
                                # Capture first departure and last arrival times
                                dep_time = transit_info.get("departureTime", "")
                                arr_time = transit_info.get("arrivalTime", "")
                                
                                if not first_departure and dep_time:
                                    first_departure = dep_time
                                if arr_time:
                                    last_arrival = arr_time
                                
                                transit_details.append({
                                    "line": line_info.get("nameShort", line_info.get("name", "Unknown")),
                                    "vehicle": line_info.get("vehicle", {}).get("type", "Unknown"),
                                    "agency": line_info.get("agencies", [{}])[0].get("name", "Unknown") if line_info.get("agencies") else "Unknown",
                                    "departure_stop": transit_info.get("stopDetails", {}).get("departureStop", {}).get("name", "Unknown"),
                                    "arrival_stop": transit_info.get("stopDetails", {}).get("arrivalStop", {}).get("name", "Unknown"),
                                    "departure_time": dep_time,
                                    "arrival_time": arr_time
                                })
                
                departure_time = first_departure if first_departure else f"Departs at {departure_time_rfc3339}"
                arrival_time = last_arrival if last_arrival else f"Arrives {duration_text} later"
                
                routes.append({
                    "mode": "transit",
                    "provider": "Google Routes API",
                    "price": price if price else 0,
                    "currency": currency,
                    "duration": duration_text,
                    "seats_available": None,
                    "co2_kg": co2,
                    "details": {
                        "from": origin,
                        "to": destination,
                        "departure": departure_time,
                        "arrival": arrival_time,
                        "transit_details": transit_details
                    }
                })

        print(f"\nParsed routes:")
        print(f"  Number of routes: {len(routes)}")
        if routes:
            print(f"  First route summary:")
            print(f"    Duration: {routes[0]['duration']}")
            print(f"    Price: {routes[0]['price']} {routes[0]['currency']}" if routes[0]['price'] else "    Price: Not available")
            print(f"    Transit details: {len(routes[0]['details']['transit_details'])} leg(s)")
        print(f"{'='*80}\n")
        
        return routes
    except Exception as e:
        print(f"\nERROR in get_transit: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")
        return {"error": str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError

def get_car_routes(origin: str, destination: str, fuel_type: str = "gasoline",
             consumption_l_per_100km: float = 7.0, fuel_price_per_l: float = 1.8,
             passengers: int = 1, seats: int = 4):
    """Find driving routes, cost, and CO2 estimates using Google Maps Routes API."""
    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        url = "https://routes.googleapis.com/v2/routes:computeRoutes"
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": google_api_key}
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

def select_top_transport(options: list):
    """Select cheapest and most eco-friendly from transport options."""
    if not options:
        return {}
    
    # Find cheapest option
    cheapest = min(options, key=lambda x: x.get("price", float('inf')))
    
    # Find most eco-friendly option
    eco_options = [o for o in options if o.get("co2_kg") is not None]
    eco = min(eco_options, key=lambda x: x["co2_kg"]) if eco_options else cheapest
    
    return {
        "cheapest": cheapest,
        "eco": eco,
    }

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
    

@tool
def web_search(query: str) -> str:
    """Search the web for information using the Tavily API.
    
    Args:
        query: The search query
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        return "Error: TAVILY_API_KEY not configured"
    
    tavily_client = TavilyClient(api_key=tavily_api_key)
    results = tavily_client.search(query, max_results=5)
    summary = "\n".join([r["title"] + ": " + r["url"] for r in results["results"]])
    return f"Search results for '{query}':\n{summary}"