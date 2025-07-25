from app.reddit_client import fetch_recent_dd_posts
from app.filter import is_eligible
from app.db import post_exists, save_post
from app.summarizer import summarize_post
from app.notifier import send_email, send_discord
from datetime import datetime
import os
from dotenv import load_dotenv
import re
load_dotenv()

def extract_tickers(summary):
    match = re.search(r'Tickers:\s*(.+)', summary)
    if match:
        raw = match.group(1).strip()
        return [t.strip().upper() for t in raw.split(",") if t.strip()]
    return []

def clean_permalink(permalink):
    return permalink if permalink.startswith("http") else "https://reddit.com" + permalink

def run():
    print("🔍 Fetching latest DD posts...")
    posts = fetch_recent_dd_posts()

    recipients = os.getenv("EMAIL_RECIPIENT", "").split(",")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    for post in posts:
        if not is_eligible(post):
            continue
        if post_exists(post["id"]):
            continue

        # Add created_at timestamp
        # Safely add expected keys
        post["created_at"] = datetime.fromtimestamp(post.get("created_utc", 0)).strftime('%Y-%m-%d %H:%M')
        print(f"\n📌 New Post: {post['title']}")

        summary = summarize_post(post["title"], post["selftext"])
        post["summary"] = summary
        post["tickers"] = extract_tickers(summary)
        post["url"] = clean_permalink(post["permalink"])

        if not summary:
            print("⚠️ Skipping due to summary error.")
            continue

        # Send notifications
        try:
            send_email(post, summary, recipients)
            send_discord(post, summary, webhook_url)
        except Exception as e:
            print(f"❌ Notification failed: {e}")

        # Store in MongoDB
        post["summary"] = summary
        post["notified_via"] = ["email", "discord"]
        save_post(post)

if __name__ == "__main__":
    run()
