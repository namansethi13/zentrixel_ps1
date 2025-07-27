import os
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from google.cloud import firestore
import json
import datetime

credentials_path = 'C:/Users/vikik/keys/citypulse-466518-591cebdb8a32.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

timeout = 5.0                                                                       

subscriber = pubsub_v1.SubscriberClient()
subscription_path = 'projects/citypulse-466518/subscriptions/tweet_topic-sub'

db = firestore.Client(project="citypulse-466518")

collection_name = "tweets"

def save_to_firestore(message_data):
    try:
        decoded_data = message_data.decode("utf-8")
        
        # If your message is JSON, parse it
        try:
            data_json = json.loads(decoded_data)
        except json.JSONDecodeError:
            data_json = {"text": decoded_data}

        # Add a timestamp field
        data_json["timestamp"] = datetime.datetime.utcnow()

        # Save to Firestore
        db.collection(collection_name).add(data_json)
        print("Saved to Firestore:", data_json)
    except Exception as e:
        print("Error saving to Firestore:", e)

def callback(message):
    print(f'Received message: {message}')
    print(f'data: {message.data}')
    save_to_firestore(message.data)
    message.ack() 

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f'Listening for messages on {subscription_path}')

try:
    with subscriber:                                                
        try:
            streaming_pull_future.result()                          
        except TimeoutError:
            streaming_pull_future.cancel()                    
            streaming_pull_future.result()  
except KeyboardInterrupt:
    print("\nStopped.")
