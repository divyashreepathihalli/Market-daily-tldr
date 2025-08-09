from __future__ import annotations

import os
import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
except Exception:  # pragma: no cover - optional dependency
    SendGridAPIClient = None  # type: ignore
    Mail = Email = To = Content = None  # type: ignore


def _get_bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "y"}


def _html_to_text(html: str) -> str:
    # naive HTML to text fallback
    text = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def send_via_sendgrid(
    *,
    subject: str,
    html_body: str,
    recipients: list[str],
    from_address: str,
    from_name: str | None = None,
) -> None:
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY not set")

    if SendGridAPIClient is None:
        raise RuntimeError("sendgrid package not available. Install it from requirements.txt")

    sg = SendGridAPIClient(api_key)
    from_email = Email(from_address, from_name) if from_name else Email(from_address)

    message = Mail(from_email=from_email, subject=subject)
    # Add plain first, then HTML
    message.add_content(Content("text/plain", _html_to_text(html_body) or subject))
    message.add_content(Content("text/html", html_body))
    for addr in recipients:
        message.add_to(To(email=addr))

    response = sg.client.mail.send.post(request_body=message.get())
    if response.status_code >= 300:
        raise RuntimeError(f"SendGrid error: {response.status_code} {response.body}")


def send_via_gmail(
    *,
    subject: str,
    html_body: str,
    recipients: Iterable[str],
    from_address: str,
    from_name: str | None = None,
) -> None:
    username = os.getenv("GMAIL_USERNAME")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not username or not password:
        raise RuntimeError("GMAIL_USERNAME or GMAIL_APP_PASSWORD not set")

    host = "smtp.gmail.com"
    port = 587

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_address}>" if from_name else from_address
    msg["To"] = ", ".join(recipients)

    # Plain first, then HTML
    part_plain = MIMEText(_html_to_text(html_body) or subject, "plain", _charset="utf-8")
    part_html = MIMEText(html_body, "html", _charset="utf-8")
    msg.attach(part_plain)
    msg.attach(part_html)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(username, password)
        server.sendmail(from_address, list(recipients), msg.as_string())


def send_email(
    *,
    subject: str,
    html_body: str,
    recipients: list[str],
    from_address: str,
    from_name: str | None = None,
) -> None:
    # Prefer Gmail minimal config
    if os.getenv("GMAIL_USERNAME") and os.getenv("GMAIL_APP_PASSWORD"):
        send_via_gmail(
            subject=subject,
            html_body=html_body,
            recipients=recipients,
            from_address=from_address,
            from_name=from_name,
        )
        return

    # Optional SendGrid fallback if configured
    if os.getenv("SENDGRID_API_KEY"):
        send_via_sendgrid(
            subject=subject,
            html_body=html_body,
            recipients=recipients,
            from_address=from_address,
            from_name=from_name,
        )
        return

    raise RuntimeError("No email provider configured. Set GMAIL_USERNAME and GMAIL_APP_PASSWORD in environment.") 