"""Multi-channel notifier utilities."""

import logging
import requests
from typing import Optional, Dict, List


class Notifier:
    """Send alerts to multiple channels.

    The implementation intentionally keeps network calls simple so unit tests can
    monkeypatch the send functions without requiring real network access.
    """

    def __init__(self, cfg: Optional[Dict[str, str]] = None):
        cfg = cfg or {}
        self.telegram_token = cfg.get("telegram_token")
        self.telegram_chat_id = cfg.get("telegram_chat_id")
        self.email = cfg.get("email")
        self.slack_webhook = cfg.get("slack_webhook")

    # --- Channel helpers -------------------------------------------------
    def _send_telegram(self, msg: str) -> bool:
        if not self.telegram_token or not self.telegram_chat_id:
            logging.info("[Notifier] Telegram not configured.")
            return False
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": self.telegram_chat_id, "text": msg})
            logging.info("[Notifier] Sent Telegram message.")
            return True
        except Exception as e:
            logging.warning(f"[Notifier] Failed Telegram: {e}")
            return False

    def _send_email(self, msg: str) -> bool:
        if not self.email:
            logging.info("[Notifier] Email not configured.")
            return False
        # Placeholder – integrate with real provider (SMTP, SendGrid, etc.)
        logging.info(f"[Notifier] Would send email to {self.email}: {msg}")
        return True

    def _send_slack(self, msg: str) -> bool:
        if not self.slack_webhook:
            logging.info("[Notifier] Slack not configured.")
            return False
        try:
            requests.post(self.slack_webhook, json={"text": msg})
            logging.info("[Notifier] Sent Slack message.")
            return True
        except Exception as e:
            logging.warning(f"[Notifier] Failed Slack: {e}")
            return False

    # --- Public API ------------------------------------------------------
    def escalate_event(self, event: str, msg: str) -> None:
        """Send the message to all configured channels.

        If every channel fails, append to ``PANIC.log`` and print to console for
        immediate operator visibility.
        """

        results: List[bool] = [
            self._send_telegram(f"[{event.upper()}] {msg}"),
            self._send_email(f"[{event.upper()}] {msg}"),
            self._send_slack(f"[{event.upper()}] {msg}"),
        ]

        if not any(results):
            logging.critical("[Notifier] ALL channels failed! Writing to PANIC.log")
            try:
                with open("PANIC.log", "a") as f:
                    f.write(f"{event.upper()}: {msg}\n")
            except Exception as e:  # pragma: no cover - extremely unlikely
                logging.error(f"[Notifier] Failed to write PANIC.log: {e}")
            print(f"[PANIC] {event.upper()}: {msg}")

