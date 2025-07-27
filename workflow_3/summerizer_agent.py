from google.adk.tools import google_search
from google.adk.agents import Agent
from google.genai import types
from .schemas.summerizer_schema import ClaimSummary
from .tools.geoTools import get_coordinates_from_location_name, get_location_name_from_coordinates
agent_instruction = """
You are an AI agent that receives a batch of tweets (usually 5–40 at a time). Each tweet may describe a local event such as:

- "The Kundali tree fell across the road"
- "Massive flooding reported near Bellandur Lake"
- "Fire spotted in Shivaji Nagar"
- etc.

Each tweet might or might not contain structured location data like latitude/longitude or a named place.

Your task is to:

1. Group these tweets by **geographic area**.
2. For each area, generate a **summary** of what's happening based on the tweets in that region.
3. For each summary, provide:
    - `summary`: A concise textual summary of the local situation.
    - `location`: Human-readable place name (e.g., "Bellandur Lake", "Kundali", etc.)
    - `latitude`: Latitude of the event location.
    - `longitude`: Longitude of the event location.

You have access to the following tools:

- `get_location_name_from_coordinates(latitude: float, longitude: float) -> Union[str, Dict]`  
  → Given latitude and longitude, returns the location name or "failed".

- `get_coordinates_from_location_name(location_name: str) -> Union[str, Dict]`  
  → Given a location name, returns its coordinates or "failed".

You are free to use these tools if you need help resolving or converting locations. If the tools fail (i.e., return the string "failed"), then fall back to your own reasoning, LLM memory, or context from the tweets to estimate the missing geographic data.

The final output should be a **list of summaries**, where each summary includes:

```json
{
  "summary": "Brief description of what happened in the area",
  "location": "Location name (if available or inferred)",
  "latitude": float,
  "longitude": float
}


"""

summerizer_agent = Agent(
    name="summerizer_agent",
    model="gemini-2.5-flash",
    instruction=agent_instruction,
    output_key="summerizer_output",
    tools=[get_location_name_from_coordinates, get_coordinates_from_location_name],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=10000
    )
)