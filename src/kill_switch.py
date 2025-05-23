import logging
from src.notifier import send_telegram, send_email

class KillSwitch:
    def __init__(self, config):
        self.enabled = config.get("kill_switch_enabled", True)
        self.max_drawdown_pct = config.get("risk", {}).get("max_drawdown_pct", 5)
        self.max_loss_usd = config.get("risk", {}).get("max_loss_usd", 200)
        self.trading_enabled = True
        self.pnl_history = []
        self.notifier_cfg = config.get("notifier", {})

    def update_pnl(self, pnl_usd):
        self.pnl_history.append(pnl_usd)
        if len(self.pnl_history) > 100:
            self.pnl_history = self.pnl_history[-100:]
        self._check_risk()

    def _check_risk(self):
        if not self.enabled:
            return
        total_pnl = sum(self.pnl_history)
        min_pnl = min(self.pnl_history) if self.pnl_history else 0
        if abs(min_pnl) > self.max_loss_usd or (total_pnl < 0 and abs(total_pnl) > self.max_loss_usd):
            self.trigger("max loss exceeded")

    def trigger(self, reason: str):
        self.trading_enabled = False
        logging.critical(f"[KILL SWITCH] Triggered: {reason}. Trading disabled.")
        send_telegram(f"KILL SWITCH: {reason}", self.notifier_cfg.get("telegram_token"), self.notifier_cfg.get("telegram_chat_id"))
        email = self.notifier_cfg.get("email")
        if email:
            send_email(f"KILL SWITCH: {reason}", email)

    def is_enabled(self):
        return self.trading_enabled
