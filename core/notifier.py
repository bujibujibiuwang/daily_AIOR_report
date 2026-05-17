import os
import smtplib
from datetime import date
from email.message import EmailMessage


def send_email_notification(content: str, today: date) -> None:
    if os.getenv("ENABLE_EMAIL", "0") != "1":
        return

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_FROM") or smtp_user
    recipients = [a.strip() for a in os.getenv("EMAIL_TO", "").split(",") if a.strip()]

    if not smtp_host or not sender or not recipients:
        print("[notifier] Email config incomplete, skipping.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"AI+OR 每日论文精选 {today}"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(content)

    use_tls = os.getenv("SMTP_TLS", "0") == "1"
    try:
        if use_tls:
            with smtplib.SMTP(smtp_host, smtp_port) as s:
                s.starttls()
                if smtp_user and smtp_password:
                    s.login(smtp_user, smtp_password)
                s.send_message(msg)
        else:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as s:
                if smtp_user and smtp_password:
                    s.login(smtp_user, smtp_password)
                s.send_message(msg)
        print("[notifier] Email sent successfully.")
    except Exception as e:
        print(f"[notifier] Email failed: {e}")
