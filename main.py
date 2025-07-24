from app.reddit_client import fetch_recent_dd_posts
from app.filter import is_eligible
from app.db import post_exists, save_post
from app.summarizer import summarize_post
from app.notifier import send_email, send_discord

def run():
    print("🔍 Fetching latest DD posts...")
    posts = fetch_recent_dd_posts()

    for post in posts:
        if not is_eligible(post):
            continue
        if post_exists(post["id"]):
            continue

        print(f"\n📌 New Post: {post['title']}")

        summary = summarize_post(post["title"], post["selftext"])
        if not summary:
            print("⚠️ Skipping due to summary error.")
            continue

        email_subject = f"🧠 New WSB DD: {post['title']}"
        email_body = f"{post['title']}\n\nLink: {post['permalink']}\nUpvotes: {post['score']} | Comments: {post['num_comments']}\n\n{summary}"
        send_email(email_subject, email_body)
        send_discord(f"**{post['title']}**\n{post['permalink']}\n\n{summary}")

        # Store in MongoDB
        post["summary"] = summary
        post["notified_via"] = ["email", "discord"]
        save_post(post)

if __name__ == "__main__":
    run()
