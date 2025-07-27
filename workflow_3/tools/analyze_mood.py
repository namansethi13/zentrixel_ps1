from google.cloud import language_v1

def analyze_mood(text: str) -> dict:
    """
    Analyzes the mood of a given text using Google Cloud Natural Language API.
    """
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(
        content=text,
        type_=language_v1.Document.Type.PLAIN_TEXT,
    )
    response = client.analyze_sentiment(request={"document": document})
    sentiment = response.document_sentiment

    result = {
        "mood": "positive" if sentiment.score > 0 else "negative" if sentiment.score < 0 else "neutral",
        "score": sentiment.score,
    }
    return result
