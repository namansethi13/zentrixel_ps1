import os
from google.cloud import pubsub_v1
import tweet_simulator as ts
import time

credentials_path = 'C:/Users/vikik/keys/citypulse-466518-591cebdb8a32.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


publisher = pubsub_v1.PublisherClient()
topic_path = 'projects/citypulse-466518/topics/tweet_topic'


# data = 'A tweet simulation is ready!'
# data = data.encode('utf-8')
# attributes = {
#     'sensorName': 'tweet_simulation-01',
#     'temperature': '75.0',
#     'humidity': '60'
# }

print("Starting Human-like Tweet Generator...\n")
try:
    while True:
        # print(generate_natural_tweet())
        data = ts.generate_natural_tweet() 
        data = data.encode('utf-8')
        future = publisher.publish(topic_path, data)
        print(f'published message id {future.result()}')
        time.sleep(3)  # One tweet every 3 seconds

except KeyboardInterrupt:
    print("\nStopped.")


