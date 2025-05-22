import logging
from typing import Dict

from .kill_switch import KillSwitch


class RiskManager:
    def __init__(self, config: Dict, kill_switch: KillSwitch):
        self.kill_switch = kill_switch
        if hasattr(self.kill_switch, "attach_risk_manager"):
            self.kill_switch.attach_risk_manager(self)
        self.max_drawdown_pct = config.get("risk", {}).get("max_drawdown_pct", 5)
        self.max_loss_usd = config.get("risk", {}).get("max_loss_usd", 200)
        self.max_trade_size_usd = config.get("trade_amount_usd", 100)
        self.current_drawdown = 0

    def check_trade(self, trade_size_usd: float) -> float:
        if self.kill_switch.state >= KillSwitch.PAUSE:
            logging.warning("[RiskManager] Trading paused by KillSwitch")
            return 0

        if self.kill_switch.state == KillSwitch.REDUCE_RISK:
            trade_size_usd = min(trade_size_usd, self.max_trade_size_usd / 2)
        elif trade_size_usd > self.max_trade_size_usd:
            logging.warning("[RiskManager] Trade size too large, reducing.")
            trade_size_usd = self.max_trade_size_usd
        return trade_size_usd

    def update_drawdown(self, pnl: float) -> bool:
        self.current_drawdown += pnl
        if abs(self.current_drawdown) > self.max_loss_usd:
            logging.critical("[RiskManager] Max drawdown breached!")
            if hasattr(self.kill_switch, "record_risk_breach"):
                self.kill_switch.record_risk_breach("drawdown")
            else:  # pragma: no cover - old API fallback
                self.kill_switch.manual_override(KillSwitch.HALT, "drawdown")
            return False
        return True
