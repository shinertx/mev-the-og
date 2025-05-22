import logging
from typing import Optional

from .notifier import send_telegram

class KillSwitch:
    def __init__(self, config):
        self.enabled = config.get("kill_switch_enabled", True)
        self.max_drawdown_pct = config.get("risk", {}).get("max_drawdown_pct", 5)
        self.max_loss_usd = config.get("risk", {}).get("max_loss_usd", 200)
        self.state = "RUNNING"  # RUNNING, PAUSED, HALTED
        self.pnl_history = []
        telegram = config.get("notifier", {}).get("telegram", {})
        self.tg_token = telegram.get("token") or config.get("notifier", {}).get("telegram_token")
        self.tg_chat = telegram.get("chat_id") or config.get("notifier", {}).get("telegram_chat_id")

    def update_pnl(self, pnl_usd):
        self.pnl_history.append(pnl_usd)
        if len(self.pnl_history) > 100:
            self.pnl_history = self.pnl_history[-100:]
        self._check_risk()

    def _check_risk(self):
        if not self.enabled or self.state == "HALTED":
            return
        total_pnl = sum(self.pnl_history)
        min_pnl = min(self.pnl_history) if self.pnl_history else 0
        if abs(min_pnl) > self.max_loss_usd or (total_pnl < 0 and abs(total_pnl) > self.max_loss_usd):
            self.pause("max loss exceeded")

    def pause(self, reason: str):
        if self.state != "HALTED":
            self.state = "PAUSED"
            logging.critical(f"[KILL SWITCH] Paused: {reason}")
            send_telegram(f"KILL SWITCH PAUSED: {reason}", self.tg_token, self.tg_chat)

    def halt(self, reason: str):
        self.state = "HALTED"
        logging.critical(f"[KILL SWITCH] HALTED: {reason}")
        send_telegram(f"KILL SWITCH HALTED: {reason}", self.tg_token, self.tg_chat)

    def resume(self):
        if self.state == "PAUSED":
            self.state = "RUNNING"
            logging.info("[KILL SWITCH] Resumed")
            send_telegram("KILL SWITCH RESUMED", self.tg_token, self.tg_chat)

    def is_enabled(self):
        return self.enabled and self.state == "RUNNING"
