from google.cloud import firestore
from process_tweets import process_tweet  

# Initialize Firestore client
db = firestore.Client()

# Replace with your Firestore collection name
COLLECTION_NAME = "tweets"

# Optional: Keep track of processed document IDs to avoid reprocessing
processed_ids = set()

# Callback for Firestore snapshot listener
def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == "ADDED":
            doc = change.document
            doc_id = doc.id

            if doc_id in processed_ids:
                continue  # Skip if already processed

            data = doc.to_dict()
            tweet_text = data.get("text")

            if tweet_text:
                result = process_tweet(tweet_text)
                print(result)

            processed_ids.add(doc_id)

# Attach the snapshot listener
query_watch = db.collection(COLLECTION_NAME).on_snapshot(on_snapshot)

# Keep the script running
print(f"Listening to Firestore collection: {COLLECTION_NAME}")
while True:
    pass  # Keep main thread alive (or use `time.sleep()` if preferred)
