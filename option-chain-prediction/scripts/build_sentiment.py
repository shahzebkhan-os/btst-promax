import json
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.sentiment import score_news, score_price_action

NEWS_PATH = "data/news_headlines.csv"  # optional: columns: headline
PRICE_PATH = "data/index_prices.csv"   # optional: columns: date,close
OUT = "data/sentiment.json"

news = pd.read_csv(NEWS_PATH)["headline"] if pd.io.common.file_exists(NEWS_PATH) else pd.Series([])
price = pd.read_csv(PRICE_PATH) if pd.io.common.file_exists(PRICE_PATH) else pd.DataFrame()

news_score = score_news(news)
price_score = score_price_action(price)

# simple blended score
score = 0.6 * price_score + 0.4 * news_score
conf = min(1.0, max(0.0, 0.5 + abs(score) / 4))
label = "Bullish" if score > 0.1 else "Bearish" if score < -0.1 else "Neutral"

payload = {
    "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "sentiment": label,
    "score": round(score, 3),
    "confidence": round(conf, 2),
}

with open(OUT, "w") as f:
    json.dump(payload, f, indent=2)

print("Wrote", OUT)
