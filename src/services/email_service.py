import email
import imaplib
import smtplib
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core.config import settings
from src.core.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ParsedEmail:
    """Structured representation of a raw email."""
    sender: str
    subject: str
    body: str
    attachments: list[dict] = field(default_factory=list)


def fetch_unread_emails(max_count: int = 10) -> list[ParsedEmail]:
    """Connect to IMAP server and fetch unread emails."""
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        logger.warning(
            "Email credentials not configured. Skipping email fetch."
        )
        return []

    emails_list: list[ParsedEmail] = []
    try:
        mail = imaplib.IMAP4_SSL(
            settings.MAIL_IMAP_SERVER, settings.MAIL_IMAP_PORT
        )
        mail.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        mail.select("INBOX")

        _, message_numbers = mail.search(None, "UNSEEN")

        for num in message_numbers[0].split()[:max_count]:
            _, msg_data = mail.fetch(num, "(RFC822)")
            email_body = msg_data[0][1]
            msg = email.message_from_bytes(email_body)

            parsed = _parse_email(msg)
            emails_list.append(parsed)

            # Mark as read
            mail.store(num, "+FLAGS", "\\Seen")

        mail.logout()
        logger.info(f"Fetched {len(emails_list)} unread emails")
    except Exception as e:
        logger.error(f"Failed to fetch emails: {e}")

    return emails_list


def _parse_email(msg: email.message.Message) -> ParsedEmail:
    """Extract sender, subject, body, and attachments from a raw email."""
    sender = email.utils.parseaddr(msg["From"])[1]
    subject = msg["Subject"] or "(No Subject)"
    body = ""
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in disposition:
                attachments.append({
                    "filename": part.get_filename() or "unknown",
                    "content_type": content_type,
                    "data": part.get_payload(decode=True),
                })
            elif content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode("utf-8", errors="replace")

    return ParsedEmail(
        sender=sender,
        subject=subject,
        body=body,
        attachments=attachments,
    )


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email via SMTP."""
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        logger.warning(
            "Email credentials not configured. Skipping email send."
        )
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.MAIL_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(
            settings.MAIL_SMTP_SERVER, settings.MAIL_SMTP_PORT
        ) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
