import logging
import requests

def send_telegram(msg, token, chat_id):
    if not token or not chat_id:
        logging.info("[Notifier] Telegram not configured.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": msg})
        logging.info("[Notifier] Sent Telegram message.")
    except Exception as e:
        logging.warning(f"[Notifier] Failed Telegram: {e}")

def send_email(msg, email):
    # Placeholder – integrate with SendGrid, SMTP, etc.
    logging.info(f"[Notifier] Would send email to {email}: {msg}")
