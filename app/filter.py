import time

MIN_SCORE = 10
MIN_AGE_MINUTES = 30
MAX_AGE_MINUTES = 2880  # 2 days

def is_eligible(post):
    current_time = time.time()
    post_age_minutes = (current_time - post["created_utc"]) / 60

    return (
        post["score"] >= MIN_SCORE and
        MIN_AGE_MINUTES <= post_age_minutes <= MAX_AGE_MINUTES
    )
