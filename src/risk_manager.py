import logging
from typing import Optional

from .notifier import Notifier

class RiskManager:
    def __init__(self, config, notifier: Optional[Notifier] = None):
        self.max_drawdown_pct = config.get("risk", {}).get("max_drawdown_pct", 5)
        self.max_loss_usd = config.get("risk", {}).get("max_loss_usd", 200)
        self.max_trade_size_usd = config.get("trade_amount_usd", 100)
        self.current_drawdown = 0
        self.notifier = notifier

    def check_trade(self, trade_size_usd):
        if trade_size_usd > self.max_trade_size_usd:
            logging.warning("[RiskManager] Trade size too large, reducing.")
            return self.max_trade_size_usd
        return trade_size_usd

    def update_drawdown(self, pnl):
        self.current_drawdown += pnl
        if abs(self.current_drawdown) > self.max_loss_usd:
            logging.critical("[RiskManager] Max drawdown breached!")
            if self.notifier:
                self.notifier.escalate_event(
                    "risk",
                    "Max drawdown breached",
                )
            return False
        return True
