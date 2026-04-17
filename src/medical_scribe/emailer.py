from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_email_report(recipient: str, subject: str, body: str) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", username or "")

    if not all([host, username, password, sender]):
        raise RuntimeError(
            "Missing SMTP configuration. Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM"
        )

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=30) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
