import requests
from time import sleep

def geocode_location(location_name):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_name,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "geolocat/1.0"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        if data:
            loc = data[0]
            return {
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "display_name": loc["display_name"]
            }
    except Exception as e:
        print(f"Geocoding failed for {location_name}: {e}")
    return None