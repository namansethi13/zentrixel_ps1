import requests
import polyline
import time
import folium
from typing import List, Tuple

GOOGLE_MAPS_API_KEY = "AIzaSyA1oLmuz3a5N9kYoImTzRjf7WhwC3bz5YA"
OPENWEATHER_API_KEY = "c21150fffc9a14b66ecaca8df51732dc"
WAQI_API_TOKEN = "ab3f7f27fb12233db5b64696266cd52cc625b9ba"

def geocode_address(address: str) -> Tuple[float, float]:
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}
    response = requests.get(url, params=params).json()
    if response.get("status") == "OK":
        loc = response["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    else:
        raise Exception(f"Geocoding failed: {response}")

def get_directions(origin: str, destination: str, mode: str = "walking") -> List[List[Tuple[float, float]]]:
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "alternatives": "true",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params).json()
    all_routes = []
    for route in response.get("routes", []):
        encoded = route["overview_polyline"]["points"]
        points = polyline.decode(encoded)
        all_routes.append(points)
    return all_routes


def get_directions_test(origin: str, destination: str, mode: str = "WALK") -> List[List[Tuple[float, float]]]:
    origin_lat, origin_lng = geocode_address(origin)
    dest_lat, dest_lng = geocode_address(destination)
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.polyline.encodedPolyline"
    }
    body = {
        "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}},
        "destination": {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lng}}},
        "travelMode": mode,
        "computeAlternativeRoutes": True
    }
    response = requests.post(url, headers=headers, json=body).json()
    all_routes = []
    for route in response.get("routes", []):
        encoded = route["polyline"]["encodedPolyline"]
        points = polyline.decode(encoded)
        all_routes.append(points)
    return all_routes

def sample_waypoints(route: List[Tuple[float, float]], step: int = 5) -> List[Tuple[float, float]]:
    return route[::step]

def get_weather(lat: float, lon: float) -> dict:
    url = f"https://api.openweathermap.org/data/2.5/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,hourly,daily,alerts",
        "appid": OPENWEATHER_API_KEY
    }
    return requests.get(url, params=params).json()

def get_aqi(lat: float, lon: float) -> int:
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/"
    params = {"token": WAQI_API_TOKEN}
    response = requests.get(url, params=params).json()
    if response.get("status") == "ok":
        return int(response["data"].get("aqi", 999))
    return 999

def get_elevation(waypoints: List[Tuple[float, float]]) -> List[float]:
    url = f"https://maps.googleapis.com/maps/api/elevation/json"
    locations = "|".join([f"{lat},{lon}" for lat, lon in waypoints])
    params = {"locations": locations, "key": GOOGLE_MAPS_API_KEY}
    data = requests.get(url, params=params).json()
    return [pt["elevation"] for pt in data.get("results", [])]

def compute_score(aqi: float, uv: float, elevation_gain: float) -> float:
    return (0.4 * (100 - aqi)) + (0.2 * (100 - uv * 10)) - (0.2 * elevation_gain)

# def evaluate_routes(routes: List[List[Tuple[float, float]]]) -> List[dict]:
#     evaluated = []
#     for route in routes:
#         waypoints = sample_waypoints(route, step=5)
#         aqis = []
#         uvs = []
#         elevations = get_elevation(waypoints)
#         for lat, lon in waypoints:
#             weather = get_weather(lat, lon)
#             uv = weather.get("current", {}).get("uvi", 0)
#             uvs.append(uv)
#             aqi = get_aqi(lat, lon)
#             aqis.append(aqi)
#             time.sleep(1)
#         avg_aqi = sum(aqis) / len(aqis)
#         avg_uv = sum(uvs) / len(uvs)
#         elevation_gain = max(elevations) - min(elevations) if elevations else 0
#         score = compute_score(avg_aqi, avg_uv, elevation_gain)
#         evaluated.append({
#             "route": route,
#             "avg_aqi": avg_aqi,
#             "avg_uv": avg_uv,
#             "elevation_gain": elevation_gain,
#             "score": score
#         })
#     return sorted(evaluated, key=lambda x: x["score"], reverse=True)

from concurrent.futures import ThreadPoolExecutor, as_completed

def evaluate_routes(routes: List[List[Tuple[float, float]]], max_workers: int = 10) -> List[dict]:
    evaluated = []
    for route in routes:
        waypoints = sample_waypoints(route, step=20)  # fewer waypoints for faster execution

        # Elevation batch request
        elevations = get_elevation(waypoints)
        
        aqis = []
        uvs = []

        def fetch_weather_aqi(latlon):
            lat, lon = latlon
            try:
                weather = get_weather(lat, lon)
                uv = weather.get("current", {}).get("uvi", 0)
                aqi = get_aqi(lat, lon)
                return (aqi, uv)
            except:
                return (999, 0)

        # Parallelize API calls
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_coord = {executor.submit(fetch_weather_aqi, coord): coord for coord in waypoints}
            for future in as_completed(future_to_coord):
                aqi, uv = future.result()
                aqis.append(aqi)
                uvs.append(uv)

        avg_aqi = sum(aqis) / len(aqis) if aqis else 999
        avg_uv = sum(uvs) / len(uvs) if uvs else 0
        elevation_gain = max(elevations) - min(elevations) if elevations else 0
        score = compute_score(avg_aqi, avg_uv, elevation_gain)

        evaluated.append({
            "route": route,
            "avg_aqi": avg_aqi,
            "avg_uv": avg_uv,
            "elevation_gain": elevation_gain,
            "score": score
        })

    return sorted(evaluated, key=lambda x: x["score"], reverse=True)


def plot_route(route: List[Tuple[float, float]], filename: str = "route_map.html"):
    if not route:
        print("Empty route, nothing to plot.")
        return
    m = folium.Map(location=route[0], zoom_start=14)
    folium.PolyLine(route, color="blue", weight=5, opacity=0.8).add_to(m)
    folium.Marker(route[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(route[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(m)
    m.save(filename)
    print(f"✅ Route map saved to {filename}")

if __name__ == "__main__":
    origin = "Bangalore Airport, India"
    destination = "Electronic City, Bangalore, India"
    mode = 'walking'
    routes = get_directions(origin, destination, mode)
    results = evaluate_routes(routes)
    # for i, result in enumerate(results):
    #     print(f"\nRoute {i+1}:")
    #     print(f"Score: {result['score']:.2f}")
    #     print(f"Avg AQI: {result['avg_aqi']:.2f}")
    #     print(f"Avg UV Index: {result['avg_uv']:.2f}")
    #     print(f"Elevation Gain: {result['elevation_gain']:.2f} m")
    #     best_route = results[0]["route"]
    #     print(best_route)
    if results:
        best_route = results[0]["route"]
        plot_route(best_route, filename="best_route_map.html")
