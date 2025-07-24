import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = os.getenv("SMTP_USERNAME")
        recipients = os.getenv("EMAIL_RECIPIENT", "").split(",")
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            server.sendmail(msg["From"], recipients, msg.as_string())


        print(f"[Email Sent] {subject}")
    except Exception as e:
        print(f"[Email Error] {e}")

import requests

def send_discord(summary_text):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("[Discord] Webhook URL not set.")
        return

    try:
        response = requests.post(
            webhook_url,
            json={"content": summary_text}
        )
        if response.status_code == 204:
            print("[Discord Sent] Successfully")
        else:
            print(f"[Discord Error] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Discord Error] {e}")
