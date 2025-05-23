import logging
import json
import os

from src.logger import log_event
from .strategy_scorer import score_strategy

def prune_dead_edges(config, module_perf_log="logs/module_performance.json"):
    """Disable edges whose score falls below threshold."""
    threshold = config.get("ai", {}).get("decay_threshold", -0.01)
    weights = config.get("ai", {}).get("scoring", {})
    if not os.path.exists(module_perf_log):
        log_event(logging.INFO, "No performance log found.", "pruner")
        return []
    with open(module_perf_log, "r") as f:
        perf = json.load(f)
    killed = []
    for mod, stats in perf.items():
        score = score_strategy(stats, weights)
        if score < threshold or stats.get("fail_count", 0) > 2:
            log_event(logging.WARNING, f"Killing module {mod} score {score}", "pruner")
            killed.append(mod)
    return killed

if __name__ == "__main__":
    from src.utils import load_config
    cfg = load_config("config.yaml")
    log_event(logging.INFO, "Pruner run standalone", "pruner")
    print(prune_dead_edges(cfg))
