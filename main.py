from app.reddit_client import fetch_recent_dd_posts
from app.filter import is_eligible
from app.db import post_exists, save_post
from app.summarizer import summarize_post
from app.notifier import send_email, send_discord
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def run():
    print("🔍 Fetching latest DD posts...")
    posts = fetch_recent_dd_posts()

    recipients = os.getenv("EMAIL_RECIPIENT", "").split(",")
    webhook_url = os.getenv("DISCORD_WEBHOOK")

    for post in posts:
        if not is_eligible(post):
            continue
        if post_exists(post["id"]):
            continue

        # Add created_at timestamp
        # Safely add expected keys
        post["created_at"] = datetime.fromtimestamp(post.get("created_utc", 0)).strftime('%Y-%m-%d %H:%M')
        post["tickers"] = post.get("tickers", [])
        post["url"] = f"https://reddit.com{post.get('permalink', '')}"

        print(f"\n📌 New Post: {post['title']}")

        summary = summarize_post(post["title"], post["selftext"])
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
