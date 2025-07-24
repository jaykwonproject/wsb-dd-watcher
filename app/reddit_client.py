import os
import praw
from datetime import datetime, timezone

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def fetch_recent_dd_posts(limit=50):
    subreddit = reddit.subreddit("wallstreetbets")
    posts = []
    for post in subreddit.new(limit=limit):
        if post.link_flair_text and "dd" in post.link_flair_text.lower():
            posts.append({
                "id": post.id,
                "title": post.title,
                "author": str(post.author),
                "created_utc": post.created_utc,
                "permalink": f"https://reddit.com{post.permalink}",
                "flair_text": post.link_flair_text,
                "score": post.score,
                "num_comments": post.num_comments,
                "selftext": post.selftext,
                "url": post.url,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })
    return posts
