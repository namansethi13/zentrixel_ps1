from extractor import extract_locations
from geocoder import geocode_location
from llm_fallback import llm_extract_locations

def process_tweet(text):
    locations = extract_locations(text)
    geocoded = []

    if not locations:
        locations = llm_extract_locations(text)

    for loc in locations:
        geo = geocode_location(loc)
        if geo:
            geocoded.append({
                "text_location": loc,
                "geo": geo
            })

    return {
        "tweet": text,
        "locations": geocoded
    }