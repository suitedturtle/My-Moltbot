"""
Email command listener for Clawbot.
Polls Gmail via IMAP every N minutes, executes commands from the owner
email only, and replies with the result via SMTP.
"""
import imaplib
import email
import os
import time
import threading
from email.header import decode_header
from datetime import datetime, timezone

# Reuse SMTP settings already in app.py env vars
SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER     = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL    = os.environ.get("FROM_EMAIL", SMTP_USER)
OWNER_EMAIL   = os.environ.get("OWNER_EMAIL", "").strip().lower()
POLL_MINUTES  = int(os.environ.get("EMAIL_POLL_MINUTES", "5"))

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993


def _decode_header_value(value: str) -> str:
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def _get_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return ""


def _send_reply(to: str, subject: str, body: str):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    if not SMTP_USER or not SMTP_PASSWORD:
        print("[email_listener] SMTP not configured, skipping reply")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    msg["From"]    = f"Clawbot <{FROM_EMAIL}>"
    msg["To"]      = to

    html = f"""
    <div style="font-family:monospace;max-width:600px;margin:auto;background:#0f1117;color:#e2e8f0;padding:24px;border-radius:8px;">
      <h3 style="color:#a78bfa;margin-bottom:16px;">Clawbot Response</h3>
      <pre style="background:#1a1d27;padding:16px;border-radius:6px;color:#86efac;white-space:pre-wrap;">{body}</pre>
      <p style="font-size:0.75rem;color:#475569;margin-top:16px;">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
    </div>"""

    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASSWORD)
            s.sendmail(FROM_EMAIL, to, msg.as_string())
        print(f"[email_listener] replied to {to}")
    except Exception as e:
        print(f"[email_listener] reply failed: {e}")


def check_inbox(bot):
    """Connect to Gmail IMAP, find unread emails from owner, execute and reply."""
    if not OWNER_EMAIL:
        print("[email_listener] OWNER_EMAIL not set — skipping")
        return
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[email_listener] SMTP credentials not set — skipping")
        return

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASSWORD)
        mail.select("INBOX")

        # Search for unread emails from the owner only
        _, data = mail.search(None, f'(UNSEEN FROM "{OWNER_EMAIL}")')
        ids = data[0].split()

        if not ids:
            mail.logout()
            return

        print(f"[email_listener] found {len(ids)} command email(s)")

        for num in ids:
            _, msg_data = mail.fetch(num, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            sender  = email.utils.parseaddr(msg.get("From", ""))[1].strip().lower()
            subject = _decode_header_value(msg.get("Subject", "Clawbot Command"))
            body    = _get_body(msg).strip()

            # Double-check sender is owner
            if sender != OWNER_EMAIL:
                mail.store(num, "+FLAGS", "\\Seen")
                continue

            if not body:
                mail.store(num, "+FLAGS", "\\Seen")
                continue

            # Use only the first line as the command (ignore email signatures)
            command = body.splitlines()[0].strip()
            print(f"[email_listener] executing: {command}")

            try:
                result = bot.execute(command)
            except Exception as e:
                result = f"Error: {e}"

            _send_reply(sender, subject, result)
            mail.store(num, "+FLAGS", "\\Seen")

        mail.logout()

    except Exception as e:
        print(f"[email_listener] IMAP error: {e}")


def start_listener(bot):
    """Start background polling thread."""
    def _loop():
        print(f"[email_listener] started — polling every {POLL_MINUTES} min for {OWNER_EMAIL}")
        while True:
            check_inbox(bot)
            time.sleep(POLL_MINUTES * 60)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t
