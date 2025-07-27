import firebase_admin

from firebase_admin import credentials, firestore
from typing import List

db = None
def get_firestore_client():
    global db
    if db is None:
        if not firebase_admin._apps:
            try:
                firebase_admin.initialize_app()
            except DefaultCredentialsError:
                service_account_path = r"/home/saksham/googleAgenticAiHackthon/google-agentic-ai-agentic-microservice-and-deloyment-script/workflow_1/tools/hackathon-zentrixel-firebase-adminsdk.json"
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
        db = firestore.client()
    return db

def generate_doc_id(longitude: float, latitude: float, location: str) -> str:
    """
    Generate a unique document ID for Firestore based on location data.

    Args:
        longitude (float): Longitude of the location.
        latitude (float): Latitude of the location.
        location (str): Human-readable location string.

    Returns:
        str: A normalized document ID in the format 'longitude_latitude_location'.
    """
    loc_str = location.lower().replace(" ", "_")
    return f"{round(longitude, 5)}_{round(latitude, 5)}_{loc_str}"


def create_or_update_summary(data: dict) -> dict:
    """
    Creates or updates a mood summary document in the Firestore database.

    If a document for the location already exists, it merges with the new data.
    Otherwise, it creates a new document.

    Args:
        data (dict): The mood summary data to be stored.
        Attributes:
        longitude (float): Longitude of the location.
        latitude (float): Latitude of the location.
        location (str): Human-readable name of the location (e.g., a neighborhood or locality).
        summary (str): Expressive, human-written description of the event or situation.
        mood (str): Categorized mood derived from the sentiment score. One of:
            'angry', 'sad', 'happy', 'frustrated', 'hopeful', or 'neutral'.
        score (float): Sentiment score between -1.0 (strongly negative) and +1.0 (strongly positive).

    Returns:
        dict: A dictionary containing the status and document ID.
    """
    db = get_firestore_client()
    doc_id = generate_doc_id(data['longitude'], data["latitude"], data["location"])

    doc_ref = db.collection("mood_summaries").document(doc_id)
    doc_ref.set({
        "longitude": data["longitude"],
        "latitude": data['latitude'],
        "location": data['location'],
        "summary": data['summary'],
        "mood": data['mood'],
        "score": data['score'],
        "timestamp": firestore.SERVER_TIMESTAMP,
    }, merge=True)

    return {"status": "success", "doc_id": doc_id}


def get_all_summaries() -> List[dict]:
    """
    Fetch all mood summaries currently stored in the Firestore 'mood_summaries' collection.

    This can be used by an LLM or analysis pipeline to make a decision on which summary to prioritize,
    display, or aggregate.

    Returns:
        List[dict]: A list of all summaries in the database, parsed as MoodSummary dicts.
        Attributes:
        longitude (float): Longitude of the location.
        latitude (float): Latitude of the location.
        location (str): Human-readable name of the location (e.g., a neighborhood or locality).
        summary (str): Expressive, human-written description of the event or situation.
        mood (str): Categorized mood derived from the sentiment score. One of:
            'angry', 'sad', 'happy', 'frustrated', 'hopeful', or 'neutral'.
        score (float): Sentiment score between -1.0 (strongly negative) and +1.0 (strongly positive).
    """
    db = get_firestore_client()
    collection_ref = db.collection("mood_summaries")
    docs = collection_ref.stream()

    summaries: List[dict] = []
    for doc in docs:
        data = doc.to_dict()
        try:
            summary = data
            summaries.append(summary)
        except Exception as e:
            print(f"Skipping invalid document {doc.id}: {e}")

    return summaries