import random
import time

LOCATIONS = [
    "Indiranagar", "BTM Layout", "Koramangala",
    "Whitefield", "HSR Layout", "MG Road", "Marathahalli"
]

ISSUES = ["garbage", "potholes", "traffic", "noise", "waterlogging", "pollution", "construction"]
POSITIVE_FEEDBACK = [
    "Clean and calm today", 
    "Looks beautiful this morning 🌄", 
    "No traffic today, unbelievable! 🚗💨",
    "Smells fresh for a change 🍃",
    "Peaceful vibes in", 
    "Such a pleasant walk today in",
    "Zero complaints today in"
]

TAGS = ["#civicIssue", "#cleanCity", "#Bangalore", "#civicAlert", "#fixit", "#goodVibes"]

NEGATIVE_STARTERS = [
    "Ugh, the", "Can't believe the", "Why is the", "Seriously, the", 
    "Frustrated with the", "Another day, same", "Still struggling with the"
]

ACTIONS = [
    "is out of control", "needs immediate fixing", "is horrible today", 
    "is making life miserable", "isn't being handled", 
    "just got worse", "has been ignored again"
]

POSITIVE_PROBABILITY = 0.2  # 20% tweets are positive

def generate_natural_tweet():
    location = random.choice(LOCATIONS)
    
    if random.random() < POSITIVE_PROBABILITY:
        feedback = random.choice(POSITIVE_FEEDBACK)
        tweet = f"{feedback} {location}! {random.choice(TAGS)}"
    else:
        issue = random.choice(ISSUES)
        starter = random.choice(NEGATIVE_STARTERS)
        action = random.choice(ACTIONS)
        tweet = f"{starter} {issue} in {location} {action}. {random.choice(TAGS)}"
    
    return tweet

# Main loop
# if __name__ == "__main__":
#     print("Starting Human-like Tweet Generator...\n")
#     try:
#         while True:
#             print(generate_natural_tweet())
#             time.sleep(3)  # One tweet every 3 seconds
#     except KeyboardInterrupt:
#         print("\nStopped.")
