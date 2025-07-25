import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import requests
import os

def send_email(post, summary, recipients):
    subject = f"🧠 New DD Alert: {post['title']}"
    
    body = (
        f"🧠 New DD Alert: {post['title']}\n\n"
        f"📅 Posted on {post['created_at']}  \n"
        f"📈 Tickers: {post['tickers'] or 'None'}  \n"
        f"🤔 Sentiment: {extract_sentiment(summary)}\n"
        f"\n🔎 TL;DR: {extract_tldr(summary)}\n\n"
        f"{extract_section(summary, 'Pros', prefix='👍 Pros:\n')}\n"
        f"{extract_section(summary, 'Cons', prefix='\n👎 Cons:\n')}\n\n"
        f"🔗 Link: {post['url']}"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = formataddr(("DD Watcher", os.getenv("SMTP_USERNAME")))
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        server.sendmail(msg["From"], recipients, msg.as_string())

def send_discord(post, summary, webhook_url):
    content = (
        f"**🧠 New DD Alert: {post['title']}**  \n"
        f"📅 {post['created_at']}  \n"
        f"📈 Tickers: {post['tickers'] or 'None'}  \n"
        f"🤔 Sentiment: {extract_sentiment(summary)}\n"
        f"\n🔎 **TL;DR:** {extract_tldr(summary)}\n\n"
        f"**Pros:**  \n{extract_section(summary, 'Pros')}\n\n"
        f"**Cons:**  \n{extract_section(summary, 'Cons')}\n\n"
        f"🔗 {post['url']}"
    )

    data = {"content": content}
    requests.post(webhook_url, json=data)

def extract_sentiment(summary):
    for line in summary.splitlines():
        if line.lower().startswith("sentiment:"):
            return line.split(":", 1)[1].strip()
    return "Unknown"

def extract_section(summary, header, prefix=""):
    lines = summary.splitlines()
    start = None
    collected = []

    for i, line in enumerate(lines):
        if line.strip().lower().startswith(header.lower()):
            start = i + 1
            break

    if start is not None:
        for line in lines[start:]:
            line_strip = line.strip()
            if not line_strip:
                continue
            if ":" in line_strip and not line_strip.startswith(("-", "•")):
                break
            collected.append(line_strip.strip("•- ").strip())

    if collected:
        return prefix + "\n".join(f"• {line}" for line in collected)
    return ""

def extract_tldr(summary):
    for line in summary.splitlines():
        if line.lower().startswith("tl;dr:"):
            return line.split(":", 1)[1].strip()
    return ""
