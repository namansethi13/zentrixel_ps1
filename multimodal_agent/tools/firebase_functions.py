import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime

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

def generate_tweet_id() -> str:
    """
    Generate a unique document ID for a tweet.
    
    Returns:
        str: A unique tweet ID using UUID4.
    """
    return str(uuid.uuid4())

def create_tweet(data: dict) -> dict:
    """
    Creates a new tweet document in the Firestore database.
    
    Args:
        data (dict): The tweet data to be stored.
        Required attributes:
            text (str): The tweet text content.
    
    Returns:
        dict: A dictionary containing the status and document ID.
    """
    db = get_firestore_client()
    tweet_id = generate_tweet_id()
    
    # Validate required fields
    if 'text' not in data or not data['text'].strip():
        return {"status": "error", "message": "Tweet text is required"}
    
    # Prepare tweet document with only text and timestamp
    tweet_doc = {
        "text": data['text'],
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    
    doc_ref = db.collection("tweets").document(tweet_id)
    doc_ref.set(tweet_doc)
    
    return {"status": "success", "tweet_id": tweet_id}