from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "wsb_dd"
COLLECTION_NAME = "posts"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
posts = db[COLLECTION_NAME]

def save_post(post_data):
    posts.insert_one(post_data)

def post_exists(post_id: str) -> bool:
    return posts.find_one({"id": post_id}) is not None

def get_all_posts():
    raw_posts = list(posts.find().sort("created_at", -1))
    for post in raw_posts:
        post["_id"] = str(post["_id"])  # or `del post["_id"]` to remove
    return raw_posts
