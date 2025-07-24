import os
from flask import Flask, render_template
from bson import ObjectId
from app.stocks import get_cached_stock_data
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    from pymongo import MongoClient
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["wsb_dd"]
    posts = list(db.posts.find().sort("fetched_at", -1).limit(10))
    print(f"Fetched {len(posts)} posts")


    for post in posts:
        post["id"] = str(post["_id"])  # for canvas ID
        del post["_id"]  # remove ObjectId to avoid JSON serialization error

        if isinstance(post.get("created_utc"), float):
            dt = datetime.utcfromtimestamp(post["created_utc"])
            post["timestamp"] = dt.strftime("%Y-%m-%d %H:%M")
        else:
            post["timestamp"] = ""

        # Preprocess summary
        post["pros_list"] = []
        post["cons_list"] = []
        post["op_sentiment"] = ""
        if "summary" in post and isinstance(post["summary"], str):
            lines = post["summary"].splitlines()
            current_section = None
            for line in lines:
                line = line.strip()
                if line.lower().startswith("pros:"):
                    current_section = "pros"
                    continue
                elif line.lower().startswith("cons:"):
                    current_section = "cons"
                    continue
                elif line.lower().startswith("sentiment:"):
                    post["op_sentiment"] = line.replace("Sentiment:", "").strip()
                    continue

                if current_section == "pros":
                    post["pros_list"].append(line.lstrip("- ").strip())
                elif current_section == "cons":
                    post["cons_list"].append(line.lstrip("- ").strip())

        # Optional: fetch stock data
        tickers = post.get("tickers", [])
        post["stock_data"] = {}
        for ticker in tickers:
            post["stock_data"][ticker] = get_cached_stock_data(ticker)

    return render_template("index.html", posts=posts)
