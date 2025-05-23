from typing import Dict, Any


def score_strategy(stats: Dict[str, Any], weights: Dict[str, float] | None = None) -> float:
    """Return a meta-edge score for the given performance stats."""
    if weights is None:
        weights = {}
    win_w = weights.get("winrate_weight", 0.5)
    pnl_w = weights.get("pnl_weight", 0.5)
    fail_w = weights.get("fail_weight", 0.0)
    winrate = stats.get("winrate", 0)
    pnl = stats.get("avg_pnl", 0)
    fails = stats.get("fail_count", 0)
    return win_w * winrate + pnl_w * pnl - fail_w * fails
