
from datetime import datetime, timedelta
from google.cloud import firestore
from datetime import datetime, timedelta, timezone
from collections import defaultdict

db = firestore.Client(project="hackathon-zentrixel")

def fetch_recent_moods():
    now_utc = datetime.now(timezone.utc)
    five_minutes_ago = now_utc - timedelta(minutes=50)

    docs = list(db.collection("mood_summaries").stream())

    recent = []
    for d in docs:
        data = d.to_dict()
        ts = data.get("timestamp")

        if ts and ts > five_minutes_ago:
            recent.append(data)

    return recent

def analyze_alert_test(mood_docs):
    mood_count = {}

    # print(f"\n hahaha")
    # print(mood_docs)
    # print(f"\n hahaha")
    for doc in mood_docs:
        mood = doc.get("mood", "unknown")
        # print("\n hehe")
        # print(mood)
        mood_count[mood] = mood_count.get(mood, 0) + 1

    if not mood_count:
        return None

    # Simple logic: if negative moods dominate, trigger bad alert
    bad_moods = {"sad", "angry", "depressed"}
    good_moods = {"hopeful", "happy"}
    neutral_moods = {"neutral"}

    bad_total = good_total = neutral_total = 0

    bad_total = sum(v for k, v in mood_count.items() if k in bad_moods)
    good_total = sum(v for k, v in mood_count.items() if k in good_moods)
    neutral_total = sum(v for k, v in mood_count.items() if k in good_moods)

    print(f"Bad Mood, {bad_total}")
    print(f"Good Mood: {good_total}")
    print(f"Neutral : {neutral_total}")

    if bad_total > good_total:
        return "Bad Mood Alert: Many users are feeling down."
    else:
        return "Good Mood Alert: Users are feeling positive!"

def analyze_alert(mood_docs):
    mood_count = {}
    mood_summaries = defaultdict(list)


    # Count each mood
    for doc in mood_docs:
        mood = doc.get("mood", "unknown")
        summary = doc.get("summary", "")
        mood_count[mood] = mood_count.get(mood, 0) + 1
        mood_summaries[mood].append(summary)

    if not mood_count:
        return None

    # Define categories
    bad_moods = {"sad", "angry", "depressed"}
    good_moods = {"hopeful", "happy"}
    neutral_moods = {"neutral"}

    # Count totals
    bad_total = sum(v for k, v in mood_count.items() if k in bad_moods)
    good_total = sum(v for k, v in mood_count.items() if k in good_moods)
    neutral_total = sum(v for k, v in mood_count.items() if k in neutral_moods)

    print(f"Bad Mood Count: {bad_total}")
    print(f"Good Mood Count: {good_total}")
    print(f"Neutral Mood Count: {neutral_total}")

    dominant_mood = max(mood_count, key=mood_count.get)
    dominant_summary = " ".join(mood_summaries[dominant_mood])

    # Determine dominant mood category
    if bad_total > good_total:
        return f"Bad Mood Alert: Many users are feeling down. {dominant_summary}"
    elif good_total > bad_total:
        return f"Good Mood Alert: Users are feeling positive! {dominant_summary}"
    elif neutral_total >= bad_total and neutral_total >= good_total:
        return f"Neutral Mood Alert: Most users are feeling neutral. {dominant_summary}"
    else:
        return "Mixed Mood Alert: Users have mixed emotions."


def get_all_emails():
    users = db.collection("users").stream()
    return [user.to_dict().get("email") for user in users if "email" in user.to_dict()]

def send_email_to_all(alert_msg, recipients):
    email_list = get_all_emails()
    # sg = sendgrid.SendGridAPIClient(api_key="YOUR_SENDGRID_API_KEY")
    # for email in recipients:
    #     message = Mail(
    #         from_email="your@email.com",
    #         to_emails=email,
    #         subject="Mood Alert Notification",
    #         plain_text_content=alert_msg
    #     )
    #     try:
    #         response = sg.send(message)
    #         print(f"Email sent to {email}, Status: {response.status_code}")
    #     except Exception as e:
    #         print(f"Failed to send to {email}: {e}")

def main():
    recent_moods = fetch_recent_moods()
    alert = analyze_alert(recent_moods)
    print(f"Alter: {alert}")
    if alert:
        emails = get_all_emails()
        print(emails)
        # send_email_to_all(alert, emails)
    else:
        print("No recent mood data to analyze.")

if __name__ == "__main__":
    main()
