import requests
from typing import Dict, Union

def get_location_name_from_coordinates(latitude: float, longitude: float) -> Dict[str, Union[str, float]]:
    """
    Fetches the location name using latitude and longitude.

    Returns:
        dict: {
            "latitude": float,
            "longitude": float,
            "location_name": str,
            "status": "success" or "failed"
        }
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {'lat': latitude, 'lon': longitude, 'format': 'json'}
    headers = {'User-Agent': 'geotool-agent'}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'display_name' in data:
            return {
                'latitude': latitude,
                'longitude': longitude,
                'location_name': data['display_name'],
                'status': 'success'
            }
        else:
            return {
                'latitude': latitude,
                'longitude': longitude,
                'location_name': '',
                'status': 'failed'
            }
    except Exception:
        return {
            'latitude': latitude,
            'longitude': longitude,
            'location_name': '',
            'status': 'failed'
        }


def get_coordinates_from_location_name(location_name: str) -> Dict[str, Union[str, float]]:
    """
    Fetches coordinates using location name.

    Returns:
        dict: {
            "location_name": str,
            "latitude": float,
            "longitude": float,
            "status": "success" or "failed"
        }
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': location_name, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'geotool-agent'}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            return {
                'location_name': location_name,
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon']),
                'status': 'success'
            }
        else:
            return {
                'location_name': location_name,
                'latitude': 0.0,
                'longitude': 0.0,
                'status': 'failed'
            }
    except Exception:
        return {
            'location_name': location_name,
            'latitude': 0.0,
            'longitude': 0.0,
            'status': 'failed'
        }
