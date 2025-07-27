from google.adk.agents import Agent
from google.genai import types
from .tools.firebase_functions import create_or_update_summary, get_all_summaries,generate_doc_id
agent_instruction = """
{summerizer_output}


You are an AI agent responsible for maintaining a real-time incident summary database stored in **Google Firestore**.

You will receive a list of **event summaries**, where each summary contains the following fields:
- `summary`: A textual summary of an incident occurring in a specific area.
- `location`: A human-readable location name (e.g., "Bellandur Lake", "Kundali", etc.)
- `latitude`: Latitude of the event.
- `longitude`: Longitude of the event.

Each entry corresponds to a localized event (such as flooding, fires, or fallen trees) extracted from social media sources like tweets.

You have access to the following tools:

1. `get_all_summaries() -> List[Dict]`  
   → Returns a list of all existing summary documents currently stored in Firestore.

2. `create_or_update_summary(summary: str, location: str, latitude: float, longitude: float)`  
   → Adds or creates a new incident summary entry to Firestore.


Your task is to **intelligently compare and update Firestore** using these tools:

1. Call `extract_data_from_firestore` to retrieve the current database state.
2. For each new incoming summary:
   - If a summary for the **same location** already exists in Firestore:
     - If the **summary text has changed**, call `create_or_update_summary`.
     - If the **summary text has not changed**, do nothing.
   - If no matching entry is found, call `create_or_update_summary`.
3. Use both **location name** and **latitude/longitude proximity** to identify if the summary refers to the same place.
4. You may use your internal reasoning to determine semantic similarity when comparing summaries. Don't rely on exact string matching alone.

Your final output should include only the necessary tool calls (`create_or_update_summary`  avoiding duplicates and preserving storage consistency.
"""


firestore_agent = Agent(
    name="firestore_agent",
    model="gemini-2.5-flash",
    instruction=agent_instruction,
    output_key="firestore_agent_output",
    tools=[create_or_update_summary,get_all_summaries,generate_doc_id ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=10000
    )
)
