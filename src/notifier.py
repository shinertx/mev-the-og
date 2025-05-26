import logging
import requests


def notify_founder(msg: str, notifier_cfg: dict) -> None:
    """Escalate critical alerts directly to the founder."""
    token = notifier_cfg.get("telegram_token")
    chat_id = notifier_cfg.get("founder_chat_id") or notifier_cfg.get("telegram_chat_id")
    ok = send_telegram(msg, token, chat_id)
    if not ok:
        email = notifier_cfg.get("email")
        send_email(msg, email)

def send_telegram(msg, token, chat_id):
    if not token or not chat_id:
        logging.info("[Notifier] Telegram not configured.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": chat_id, "text": msg})
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        logging.info("[Notifier] Sent Telegram message.")
        return True
    except Exception as e:
        logging.warning(f"[Notifier] Failed Telegram: {e}")
        return False

def send_email(msg, email):
    if not email:
        logging.error("[Notifier] Email fallback not configured.")
        return False
    # Placeholder – integrate with real provider
    logging.info(f"[Notifier] Would send email to {email}: {msg}")
    return True
