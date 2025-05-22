import logging
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Deque, Tuple


@dataclass
class AlphaState:
    max_loss_usd: float
    max_trade_size_usd: float
    pnl_history: Deque[Tuple[datetime, float]] = field(default_factory=deque)
    trades: int = 0
    wins: int = 0
    losses: int = 0
    disabled: bool = False


class RiskManager:
    """Live capital tracking and gating logic"""

    def __init__(self, config: Dict):
        rcfg = config.get("risk", {})
        self.max_drawdown_pct = rcfg.get("max_drawdown_pct", 5)
        self.max_loss_usd = rcfg.get("max_loss_usd", 200)
        self.max_trade_size_usd = rcfg.get("max_trade_size_usd", 100)
        self.rolling_window_hours = rcfg.get("rolling_window_hours", 24)
        self.scale_increment = rcfg.get("scale_increment_usd", 50)
        self.starting_capital = config.get("starting_capital", 1000.0)
        self.current_capital = self.starting_capital
        self.peak_capital = self.starting_capital
        self.pnl_history: Deque[Tuple[datetime, float]] = deque()

        self.alphas: Dict[str, AlphaState] = {}
        for name, aconf in rcfg.get("per_alpha", {}).items():
            self.alphas[name] = AlphaState(
                max_loss_usd=aconf.get("max_loss_usd", self.max_loss_usd),
                max_trade_size_usd=aconf.get("max_trade_size_usd", self.max_trade_size_usd),
            )

    # --- Utility helpers ---
    def _prune(self, history: Deque[Tuple[datetime, float]]):
        cutoff = datetime.utcnow() - timedelta(hours=self.rolling_window_hours)
        while history and history[0][0] < cutoff:
            history.popleft()

    def _window_pnl(self, history: Deque[Tuple[datetime, float]]):
        self._prune(history)
        return sum(p for _, p in history)

    # --- Public API ---
    def check_trade(self, strategy: str, trade_size_usd: float) -> bool:
        alpha = self.alphas.get(strategy)
        limit = self.max_trade_size_usd
        if alpha:
            limit = min(limit, alpha.max_trade_size_usd)
            if alpha.disabled:
                logging.warning(f"[RiskManager] Strategy {strategy} is disabled")
                return False
        if trade_size_usd > limit:
            logging.warning("[RiskManager] Trade size too large; blocking trade")
            return False
        # drawdown check
        projected = self.current_capital - trade_size_usd
        if projected < self.peak_capital * (1 - self.max_drawdown_pct / 100):
            logging.critical("[RiskManager] Global drawdown limit reached")
            return False
        return True

    def update_pnl(self, strategy: str, pnl_usd: float) -> bool:
        now = datetime.utcnow()
        self.pnl_history.append((now, pnl_usd))
        alpha = self.alphas.get(strategy)
        if alpha:
            alpha.pnl_history.append((now, pnl_usd))
            alpha.trades += 1
            if pnl_usd > 0:
                alpha.wins += 1
            elif pnl_usd < 0:
                alpha.losses += 1
        self.current_capital += pnl_usd
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        # evaluate windows
        total_loss = -min(0, self._window_pnl(self.pnl_history))
        if total_loss > self.max_loss_usd:
            logging.critical("[RiskManager] Global loss limit breached")
            return False
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital * 100
        if drawdown > self.max_drawdown_pct:
            logging.critical("[RiskManager] Global drawdown exceeded")
            return False
        if alpha:
            loss_alpha = -min(0, self._window_pnl(alpha.pnl_history))
            if loss_alpha > alpha.max_loss_usd:
                alpha.disabled = True
                logging.critical(f"[RiskManager] {strategy} disabled due to losses")
                return False
        return True

    def scale_logic(self):
        """Simple scaling: increase trade size if recent pnl positive."""
        window_pnl = self._window_pnl(self.pnl_history)
        if window_pnl > 0:
            self.max_trade_size_usd += self.scale_increment
        elif window_pnl < -self.max_loss_usd / 2:
            self.max_trade_size_usd = max(self.scale_increment, self.max_trade_size_usd - self.scale_increment)

    def is_strategy_active(self, strategy: str) -> bool:
        alpha = self.alphas.get(strategy)
        return not alpha.disabled if alpha else True
