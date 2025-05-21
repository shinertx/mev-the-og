import logging
import json
import os

def prune_dead_edges(module_perf_log="logs/module_performance.json", threshold=-0.01):
    if not os.path.exists(module_perf_log):
        logging.info("[EdgePruner] No performance log found.")
        return []
    with open(module_perf_log, "r") as f:
        perf = json.load(f)
    killed = []
    for mod, stats in perf.items():
        if stats.get("avg_pnl", 0) < threshold or stats.get("fail_count", 0) > 2:
            logging.warning(f"[EdgePruner] Killing module {mod} due to PnL decay or repeated fails.")
            killed.append(mod)
            # (Optionally) disable in config, move to archive, etc.
    return killed

if __name__ == "__main__":
    print(prune_dead_edges())
