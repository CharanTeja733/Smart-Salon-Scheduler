from textblob import TextBlob


class SentimentService:
    @staticmethod
    def analyze(text: str) -> dict:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        if polarity > 0.2:
            label = "positive"
        elif polarity < -0.2:
            label = "negative"
        else:
            label = "neutral"
        return {
            "sentiment_score": round(polarity, 3),
            "sentiment_label": label,
            "confidence": abs(polarity)  # simplistic confidence
        }
