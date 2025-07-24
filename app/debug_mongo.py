import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["wsb_dd"]

print("Total documents in wsb.posts:", db.posts.count_documents({}))

# Show first one
first = db.posts.find_one()
if first:
    print("Sample document:")
    for k, v in first.items():
        print(f"  {k}: {v}")
else:
    print("No documents found.")
