from flask import Flask, render_template
from app.db import get_all_posts

app = Flask(__name__)

@app.route("/")
def index():
    posts = get_all_posts()
    return render_template("index.html", posts=posts)
