import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
API_URL = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

def llm_extract_locations(text):
    try:
        prompt = (
            f"Extract the most likely geographic location(s) from this tweet:\n\n"
            f"Tweet: \"{text}\"\n\n"
            f"Return a list of names of places (neighborhoods, roads, areas, cities)."
        )

        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "You extract exact and in depth with accuracy locations from social media text."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        output = response.json()
        message = output["choices"][0]["message"]["content"]

        # Simple cleanup to extract locations from LLM output
        return [loc.strip() for loc in message.strip().split(",") if loc.strip()]
    except Exception as e:
        print(f"LLM Fallback Error: {e}")
        return []