"""
Temporary test file for testing Google Routes API v2 in isolation
Testing car routes between fixed locations and counting gas stations/rest stops
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

def search_places_along_route(google_api_key, route_polyline, place_types):
    """Search for places along the route using the actual route polyline"""
    if not route_polyline:
        print("No route polyline available for place search")
        return {
            "gas_stations": 0,
            "rest_stops": 0
        }
    
    print(f"Searching for places along route polyline...")
    
    places_url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_api_key,
        "X-Goog-FieldMask": "places.displayName,places.location,places.types,places.rating,places.priceLevel,places.formattedAddress,places.userRatingCount"
    }
    
    # Counters for essential stops
    gas_station_count = 0
    rest_stop_count = 0
    
    # Map place types to search queries
    place_queries = {
        "gas_station": "gas station",
        "rest_stop": "rest stop service area"
    }
    
    for place_type in place_types:
        try:
            search_query = place_queries.get(place_type, place_type.replace("_", " "))
            
            # Use searchAlongRoute with the actual polyline
            body = {
                "textQuery": search_query,
                "searchAlongRouteParameters": {
                    "polyline": {
                        "encodedPolyline": route_polyline
                    }
                },
                "maxResultCount": 20,  # Get more results to count
                "languageCode": "en"
            }
            
            response = requests.post(places_url, headers=headers, json=body)
            
            print(f"Searching for {place_type}: Status {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.text}")
                continue
            
            if response.status_code == 200:
                data = response.json()
                if "places" in data:
                    print(f"  Found {len(data['places'])} places for {place_type}")
                    
                    for place in data["places"]:
                        place_name = place.get("displayName", {}).get("text", "Unknown")
                        place_address = place.get("formattedAddress", "")
                        
                        # Count all gas stations and rest stops found along the route
                        if place_type == "gas_station":
                            gas_station_count += 1
                            print(f"    ✓ Gas station: {place_name} - {place_address}")
                        elif place_type == "rest_stop":
                            rest_stop_count += 1
                            print(f"    ✓ Rest stop: {place_name} - {place_address}")
                else:
                    print(f"  No places found for {place_type}")
        except Exception as e:
            print(f"Error searching for {place_type}: {e}")
    
    return {
        "gas_stations": gas_station_count,
        "rest_stops": rest_stop_count
    }

def test_google_routes_api():
    """Test Google Routes API v2 with fixed inputs"""
    print("=" * 80)
    print("TESTING GOOGLE ROUTES API v2 - CAR MODE")
    print("=" * 80)
    
    # Get API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables")
        return
    
    print(f"✅ Google API Key found: {google_api_key[:10]}...")
    
    # Fixed test parameters
    origin = "Warsaw, Poland"
    destination = "Krakow, Poland"
    
    print(f"\n📍 Origin: {origin}")
    print(f"📍 Destination: {destination}")
    
    # Prepare the request
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_api_key,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs,routes.polyline,routes.travelAdvisory"
    }
    
    # Request body for car routes
    body = {
        "origin": {
            "address": origin
        },
        "destination": {
            "address": destination
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "departureTime": datetime.now().isoformat() + "Z"
    }
    
    print("\n" + "=" * 50)
    print("MAKING API REQUEST")
    print("=" * 50)
    
    print("Making request to Google Routes API v2...")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps({k: v if k != 'X-Goog-Api-Key' else '***' for k, v in headers.items()}, indent=2)}")
    print(f"Request body: {json.dumps(body, indent=2)}")
    print()
    
    # Make the request
    response = requests.post(url, headers=headers, json=body)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    # Parse response
    data = response.json()
    print("Full API Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()
    
    # Process the response
    if response.status_code == 200 and "routes" in data:
        print("✅ SUCCESS: Car routes found!")
        print(f"Number of routes: {len(data['routes'])}")
        
        for i, route in enumerate(data["routes"][:3]):  # Show first 3 routes
            print(f"\n--- ROUTE {i+1} ---")
            
            # Basic info
            duration_seconds = int(route["duration"].replace("s", ""))
            distance_meters = int(route["distanceMeters"])
            
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            
            print(f"Duration: {duration_text}")
            print(f"Distance: {distance_meters/1000:.1f} km")
            
            # Check for traffic information
            if "travelAdvisory" in route:
                traffic = route["travelAdvisory"]
                print(f"Traffic Info: {traffic}")
            
            # Process legs and steps
            if "legs" in route and route["legs"]:
                leg = route["legs"][0]
                print(f"Legs: {len(route['legs'])}")
                
                # Show start and end locations
                if "startLocation" in leg:
                    start = leg["startLocation"]
                    print(f"Start: {start.get('latLng', {}).get('latitude', 'N/A')}, {start.get('latLng', {}).get('longitude', 'N/A')}")
                
                if "endLocation" in leg:
                    end = leg["endLocation"]
                    print(f"End: {end.get('latLng', {}).get('latitude', 'N/A')}, {end.get('latLng', {}).get('longitude', 'N/A')}")
                
                # Show steps (driving directions) - detailed for technical analysis
                if "steps" in leg:
                    all_steps = leg["steps"]
                    print(f"Total steps: {len(all_steps)}")
                    
                    # Show detailed steps for technical analysis
                    print("\n--- DETAILED STEPS (for technical analysis) ---")
                    for j, step in enumerate(all_steps[:10]):  # Show first 10 steps
                        print(f"\n  Step {j+1}:")
                        print(f"    Travel Mode: {step.get('travelMode', 'Unknown')}")
                        print(f"    Instructions: {step.get('instructions', 'No instructions')}")
                        
                        if "distanceMeters" in step:
                            print(f"    Distance: {step['distanceMeters']/1000:.1f} km")
                        
                        if "duration" in step:
                            step_duration = int(step["duration"].replace("s", ""))
                            step_minutes = step_duration // 60
                            print(f"    Duration: {step_minutes} min")
                
                # Show overall polyline and search for places along route
                if "polyline" in route:
                    polyline = route["polyline"]
                    encoded_polyline = polyline.get('encodedPolyline', '')
                    print(f"\nOverall Polyline: {encoded_polyline[:100]}...")
                    
                    # Search for useful places along the route
                    print("\n--- PLACES ALONG ROUTE ---")
                    place_types = [
                        "gas_station",
                        "rest_stop"
                    ]
                    
                    places_data = search_places_along_route(google_api_key, encoded_polyline, place_types)
                    
                    if places_data:
                        print(f"\n--- ESSENTIAL STOPS ALONG ROUTE ---")
                        print(f"⛽ Gas Stations: {places_data['gas_stations']}")
                        print(f"🛑 Rest Stops: {places_data['rest_stops']}")
                    else:
                        print("No places found along the route")
    else:
        print("❌ NO ROUTES FOUND")
        if "error" in data:
            print(f"Error: {data['error']}")
        elif "message" in data:
            print(f"Message: {data['message']}")
        else:
            print("Unknown error occurred")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_google_routes_api()