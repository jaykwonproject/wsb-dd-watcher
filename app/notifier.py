import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import requests
import os

def send_email(post, summary, recipients):
    subject = f"🧠 New DD Alert: {post['title']}"
    
    body = f"""🧠 New DD Alert: {post['title']}

📅 Posted on {post['created_at']}  
📈 Tickers: {post['tickers'] or 'None'}  
🔍 Sentiment: {extract_sentiment(summary)}

{extract_section(summary, 'TL;DR')}

👍 Pros:
{extract_section(summary, 'Pros')}

👎 Cons:
{extract_section(summary, 'Cons')}

🔗 Link: {post['url']}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = formataddr(("DD Watcher", os.getenv("EMAIL_SENDER")))
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
        server.sendmail(msg["From"], recipients, msg.as_string())

def send_discord(post, summary, webhook_url):
    content = f"""**🧠 New DD Alert: {post['title']}**  
📅 {post['created_at']}  
📈 Tickers: {post['tickers'] or 'None'}  
{get_sentiment_emoji(summary)} Sentiment: {extract_sentiment(summary)}

**{extract_section(summary, 'TL;DR')}**

**Pros:**  
{extract_section(summary, 'Pros')}

**Cons:**  
{extract_section(summary, 'Cons')}

🔗 {post['url']}
"""

    data = {"content": content}
    requests.post(webhook_url, json=data)

def extract_sentiment(summary):
    for line in summary.splitlines():
        if line.lower().startswith("sentiment:"):
            return line.split(":", 1)[1].strip()
    return "Unknown"

def extract_section(summary, header):
    lines = summary.splitlines()
    start = None
    collected = []
    for i, line in enumerate(lines):
        if line.lower().startswith(header.lower()):
            start = i + 1
            break
    if start is not None:
        for line in lines[start:]:
            if line.strip() == "" or ":" in line and not line.strip().startswith("-"):
                break
            collected.append(line.strip("•- ").strip())
    return "\n".join(f"• {line}" for line in collected)

def get_sentiment_emoji(summary):
    sentiment = extract_sentiment(summary).lower()
    if "bullish" in sentiment:
        return "🟢"
    elif "bearish" in sentiment:
        return "🔴"
    else:
        return "🟡"
