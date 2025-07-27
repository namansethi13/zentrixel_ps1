from google.cloud import firestore
from datetime import datetime, timezone, timedelta

# Initialize Firestore client (ensure GOOGLE_APPLICATION_CREDENTIALS is set)
db = firestore.Client()

# Define collection name
collection_name = "tweetBatch"

# Define time threshold (1 hour ago)
now_utc = datetime.now(timezone.utc)
one_hour_ago = now_utc - timedelta(hours=6)

# Query documents with timestamp greater than one hour ago
docs = db.collection(collection_name).where("timestamp", ">", one_hour_ago).stream()
docs_1 = db.collection(collection_name).stream()
print(f"Total docs: {len(list(docs_1))}")
# Delete documents
delete_count = 0
for doc in docs:
    doc.reference.delete()
    delete_count += 1

print(f"Deleted {delete_count} documents from '{collection_name}' created in the last 1 hour.")
