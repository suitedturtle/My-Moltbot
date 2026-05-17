"""
Standalone Clawbot email listener.
Run this separately from the calcojobs web app:

  python run_clawbot_email.py

Requires env vars:
  SMTP_USER, SMTP_PASSWORD, OWNER_EMAIL
Optional:
  SMTP_HOST, SMTP_PORT, FROM_EMAIL, EMAIL_POLL_MINUTES
"""
import sys
import time
from main import build_bot
from src.email_listener import start_listener, POLL_MINUTES, OWNER_EMAIL

if __name__ == "__main__":
    if not OWNER_EMAIL:
        print("[clawbot] ERROR: OWNER_EMAIL env var not set. Exiting.")
        sys.exit(1)

    print(f"[clawbot] Starting email listener for {OWNER_EMAIL}")
    print(f"[clawbot] Polling every {POLL_MINUTES} minutes")

    bot = build_bot()
    start_listener(bot)

    # Keep the process alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("[clawbot] Stopped.")
