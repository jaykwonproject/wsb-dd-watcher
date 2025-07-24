from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Optional: make sure required variables exist
REQUIRED_ENV_VARS = [
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "REDDIT_USER_AGENT",
    "OPENAI_API_KEY",
    "SMTP_SERVER",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "EMAIL_RECIPIENT",
    "DISCORD_WEBHOOK_URL",
    "MONGO_URI"
]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")
