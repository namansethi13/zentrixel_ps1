import json
import time
from datetime import datetime, timedelta
from threading import Timer, Lock
from typing import Dict, List, Any, Optional
from firebase_functions import firestore_fn, options
from firebase_functions.firestore_fn import Event, Change, DocumentSnapshot
from firebase_admin import initialize_app, firestore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
initialize_app()

# Initialize Firestore client
db = firestore.client()

def send_message(resource_id: str, user_id: str, session_id: str, message: str) -> None:
    """Sends a message to the deployed agent."""
    try:
        # Import here to avoid initialization issues
        from vertexai import agent_engines
        
        remote_app = agent_engines.get(resource_id)
        
        logger.info(f"Sending message to session {session_id}: {message[:100]}...")
        
        for event in remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            logger.info(f"Agent response: {event}")
            
    except Exception as e:
        logger.error(f"Error sending message to agent: {e}")

# Global variables for batching
current_batch: List[Dict[str, Any]] = []
batch_lock = Lock()
batch_timer: Optional[Timer] = None

def create_batch_document(tweets: List[Dict[str, Any]], batch_start_time: datetime) -> Dict[str, Any]:
    """Create a batch document with metadata and tweets."""
    batch_end_time = batch_start_time + timedelta(minutes=2)
    
    return {
        'batch_id': f"batch_{int(batch_start_time.timestamp())}",
        'batch_start_time': batch_start_time,
        'batch_end_time': batch_end_time,
        'tweet_count': len(tweets),
        'tweets': tweets,
        'created_at': datetime.now(),
        'processing_status': 'completed'
    }

def save_batch_to_firestore():
    """Save the current batch to Firestore and reset for next batch."""
    global current_batch, batch_timer
    
    with batch_lock:
        if not current_batch:
            logger.info("No tweets in current batch, skipping save")
            batch_timer = None
            return
        
        # Calculate batch start time (2 minutes ago)
        batch_start_time = datetime.now() - timedelta(minutes=2)
        
        # Create batch document
        pruned_batch = current_batch[:40]
        batch_doc = create_batch_document(pruned_batch.copy(), batch_start_time)
        
        try:
            # Save to tweetBatch collection
            batch_ref = db.collection('tweetBatch').document(batch_doc['batch_id'])
            batch_ref.set(batch_doc)
            
            logger.info(f"Saved batch {batch_doc['batch_id']} with {len(pruned_batch)} tweets")
            
            # Send batch info to agent - convert to JSON string
            batch_message = json.dumps({
                'batch_id': batch_doc['batch_id'],
                'tweet_count': batch_doc['tweet_count'],
                'tweets': [tweet['text'] for tweet in batch_doc['tweets']]  # Only send text
            })
            
            send_message("5994950811006795776", "test_user", "8562832180131135488", batch_message)
            
            # Clear current batch
            pruned_batch.clear()
            
        except Exception as e:
            logger.error(f"Error saving batch to Firestore: {e}")
        finally:
            # Reset timer
            batch_timer = None

def schedule_batch_save():
    """Schedule the next batch save in 2 minutes."""
    global batch_timer
    
    if batch_timer is not None:
        return  # Timer already scheduled
    
    try:
        batch_timer = Timer(120.0, save_batch_to_firestore)  # 120 seconds = 2 minutes
        batch_timer.start()
        logger.info("Scheduled batch save in 2 minutes")
    except Exception as e:
        logger.error(f"Error scheduling batch save: {e}")

def extract_tweet_data(doc_snapshot: DocumentSnapshot) -> Dict[str, Any]:
    """Extract tweet data from document snapshot."""
    try:
        data = doc_snapshot.to_dict()
        if data is None:
            logger.warning(f"Document {doc_snapshot.id} has no data")
            return {
                'tweet_id': doc_snapshot.id,
                'text': '',
                'added_to_batch_at': datetime.now()
            }
        
        return {
            'tweet_id': doc_snapshot.id,
            'text': data.get('text', ''),
            'added_to_batch_at': datetime.now()
        }
    except Exception as e:
        logger.error(f"Error extracting tweet data: {e}")
        return {
            'tweet_id': doc_snapshot.id,
            'text': '',
            'added_to_batch_at': datetime.now()
        }

@firestore_fn.on_document_written(
    document="tweets/{tweetId}",
    region="us-central1",
    memory=options.MemoryOption.GB_1,
    timeout_sec=540
)
def on_tweet_written(event: Event[Change[DocumentSnapshot]]) -> None:
    """Triggered when a tweet is created or updated in the tweets collection."""
    global current_batch
    
    try:
        # Check if event data exists
        if event.data is None or event.data.after is None:
            logger.warning("No data found in event")
            return
        
        # Determine if this is a create or update
        is_create = event.data.before is None
        action_type = "created" if is_create else "updated"
        
        # Extract tweet data from the 'after' snapshot
        tweet_data = extract_tweet_data(event.data.after)
        tweet_data['action_type'] = action_type
        
        # Skip if no text content
        if not tweet_data.get('text', '').strip():
            logger.warning(f"Skipping tweet {tweet_data['tweet_id']} - no text content")
            return
        
        with batch_lock:
            # Add tweet to current batch
            current_batch.append(tweet_data)
            text_preview = tweet_data['text'][:50] + "..." if len(tweet_data['text']) > 50 else tweet_data['text']
            logger.info(f"Added {action_type} tweet '{text_preview}' to batch. Current batch size: {len(current_batch)}")
            
            # Schedule batch save if not already scheduled
            schedule_batch_save()
            
    except Exception as e:
        logger.error(f"Error processing tweet: {e}")
        # Don't re-raise the exception to avoid function failure

# Cleanup function for graceful shutdown (note: this won't be called in Cloud Functions)
def cleanup_batch_timer():
    """Cancel the batch timer if it exists."""
    global batch_timer
    if batch_timer is not None:
        batch_timer.cancel()
        batch_timer = None
        logger.info("Batch timer cancelled")

# Uncommented topic function with error handling
@firestore_fn.on_document_written(
    document="topics/{docId}",
    region="us-central1", 
    memory=options.MemoryOption.GB_1,
    timeout_sec=540
)
def on_topic_update(event: Event[Change[DocumentSnapshot]]):
    """Cloud Function triggered on Firestore document write events for 'topics' collection."""
    try:
        logger.info("Firestore topics event triggered")

        if event.data is None or event.data.after is None:
            logger.warning("No data found in event")
            return

        doc_data = event.data.after.to_dict()
        if doc_data is None:
            logger.warning("Document data is None")
            return

        claims = doc_data.get("claims", [])
        latitude = doc_data.get("latitude", "0.0")
        longitude = doc_data.get("longitude", "0.0")
        title = doc_data.get("title", "")
        location = doc_data.get("location", "")

        if not claims or latitude == "0.0" or longitude == "0.0" or not title or not location:
            logger.warning("Missing or invalid required fields")
            return

        message = f"claim: {claims}, latitude: {latitude}, longitude: {longitude}, title: {title}, location: {location}"

        resource_id = "4565620879270084608"
        user_id = "test_user"
        session_id = "2159839409917132800"

        send_message(resource_id, user_id, session_id, message)
        
    except Exception as e:
        logger.error(f"Error in on_topic_update : {e}")