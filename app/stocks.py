import os
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz

client = MongoClient(os.getenv("MONGO_URI"))
db = client["wsb_dd"]
cache = db["stock_cache"]

ALPACA_BASE_URL = "https://data.alpaca.markets/v2/stocks"
ALPACA_HEADERS = {
    "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
    "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY"),
}

TIME_RANGES = {
    "1d": ("1Min", 1),
    "1w": ("15Min", 7),
    "1m": ("1Hour", 30),
    "3m": ("1Day", 90),
    "1y": ("1Day", 365),
    "max": ("1Day", 1825),
}


def get_cached_stock_data(ticker: str):
    cache.delete_one({"ticker": ticker.upper()})
    cached = cache.find_one({"ticker": ticker.upper()})
    now = datetime.utcnow()

    if cached and "fetched_at" in cached:
        age = now - cached["fetched_at"]
        if age < timedelta(hours=6):  # reuse cache
            return cached.get("data", {})

    result = {}
    for label, (resolution, days) in TIME_RANGES.items():
        from_time = now - timedelta(days=days)
        url = f"{ALPACA_BASE_URL}/{ticker}/bars"
        params = {
            "timeframe": resolution,
            "start": from_time.replace(microsecond=0).isoformat() + "Z",
            "end": now.replace(microsecond=0).isoformat() + "Z",
            "limit": 500,
            "feed": "iex",
        }

        try:
            res = requests.get(url, headers=ALPACA_HEADERS, params=params)
            print(f"[{label}] API URL: {res.url}")
            print(f"[{label}] API RESPONSE: {res.status_code}, {res.text[:300]}")

            if res.status_code != 200:
                print(f"Error fetching {label} data for {ticker}: {res.text}")
                result[label] = None
                continue

            bars = res.json().get("bars", [])
            if not bars:
                result[label] = None
                continue

            result[label] = [
                {
                    "time": datetime.fromisoformat(bar["t"].replace("Z", "+00:00"))
                    .astimezone(pytz.timezone("US/Eastern"))
                    .strftime("%m/%d %H:%M"),
                    "price": bar["c"],
                }
                for bar in bars
            ]
        except Exception as e:
            print(f"Exception: {e}")
            result[label] = None

    cache.update_one(
        {"ticker": ticker.upper()},
        {"$set": {"ticker": ticker.upper(), "data": result, "fetched_at": now}},
        upsert=True,
    )

    return result
