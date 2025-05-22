"""Centralised kill switch handling all critical failure modes."""

from __future__ import annotations

import logging
from typing import Callable, Dict, Optional
from datetime import datetime


KILL_SWITCH: "KillSwitch" | None = None


def init_global_kill_switch(config: Dict, notifier: Optional[Callable[[str], None]] = None) -> "KillSwitch":
    """Initialise the global kill switch singleton."""
    global KILL_SWITCH
    if KILL_SWITCH is None:
        KILL_SWITCH = KillSwitch(config, notifier=notifier)
    return KILL_SWITCH


def get_kill_switch() -> "KillSwitch":
    if KILL_SWITCH is None:
        raise RuntimeError("Kill switch not initialised")
    return KILL_SWITCH


class KillSwitch:
    """Multi-tier kill switch with escalation logic."""

    RUNNING = 0
    PAUSE = 1
    REDUCE_RISK = 2
    LIQUIDATE = 3
    HALT = 4

    STATE_NAMES = {
        RUNNING: "running",
        PAUSE: "pause",
        REDUCE_RISK: "reduce_risk",
        LIQUIDATE: "liquidate",
        HALT: "halt",
    }

    def __init__(self, config: Dict, notifier: Optional[Callable[[str], None]] = None):
        self.enabled = config.get("kill_switch_enabled", True)
        self.max_drawdown_pct = config.get("risk", {}).get("max_drawdown_pct", 5)
        self.max_loss_usd = config.get("risk", {}).get("max_loss_usd", 200)
        self.max_errors = config.get("kill_switch_max_errors", 3)
        self.state = self.RUNNING
        self.pnl_history: list[float] = []
        self.error_count = 0
        self.notifier = notifier
        self.risk_manager = None

    # --- State helpers -------------------------------------------------

    def is_trading_allowed(self) -> bool:
        return self.state in (self.RUNNING, self.REDUCE_RISK)

    def is_enabled(self) -> bool:
        return self.enabled and self.state < self.HALT

    def _notify(self, message: str) -> None:
        logging.critical(message)
        if self.notifier:
            try:
                self.notifier(message)
            except Exception as e:  # pragma: no cover - notifier failures shouldn't break bot
                logging.error(f"[KillSwitch] notifier error: {e}")

    def _escalate(self, new_state: int, reason: str) -> None:
        if not self.enabled or new_state <= self.state:
            return
        self.state = new_state
        self._notify(f"[KILL SWITCH] Escalated to {self.STATE_NAMES[new_state].upper()}: {reason}")

    def attach_risk_manager(self, rm) -> None:
        self.risk_manager = rm

    # --- External hooks -------------------------------------------------

    def record_trade_error(self, reason: str) -> None:
        self.error_count += 1
        if self.error_count >= self.max_errors and self.state < self.PAUSE:
            self._escalate(self.PAUSE, reason)
        elif self.error_count >= self.max_errors * 2 and self.state < self.HALT:
            self._escalate(self.HALT, reason)

    def record_api_disconnect(self, reason: str = "rpc disconnect") -> None:
        if self.state < self.PAUSE:
            self._escalate(self.PAUSE, reason)
        elif self.state < self.HALT:
            self._escalate(self.HALT, reason)

    def manual_override(self, new_state: int, reason: str = "manual override", *, confirm: bool = False, source: str = "manual") -> None:
        if new_state == self.HALT and not confirm:
            logging.warning("[KillSwitch] HALT override requested without confirm")
            self._notify("HALT override attempted without confirmation")
            return
        self._notify(
            f"Override by {source} at {datetime.utcnow().isoformat()} : {self.STATE_NAMES[new_state].upper()} - {reason}"
        )
        self._escalate(new_state, reason)

    # --- PnL/Risk tracking ---------------------------------------------

    def update_pnl(self, pnl_usd: float) -> None:
        self.pnl_history.append(pnl_usd)
        if len(self.pnl_history) > 100:
            self.pnl_history = self.pnl_history[-100:]
        self._check_risk()

    def _check_risk(self) -> None:
        if not self.enabled:
            return
        total_pnl = sum(self.pnl_history)
        min_pnl = min(self.pnl_history) if self.pnl_history else 0
        if abs(min_pnl) > self.max_loss_usd or (total_pnl < 0 and abs(total_pnl) > self.max_loss_usd):
            self._escalate(self.HALT, "max loss exceeded")

    def record_risk_breach(self, reason: str) -> None:
        """Explicit risk breach trigger from RiskManager."""
        self._escalate(self.HALT, reason)

