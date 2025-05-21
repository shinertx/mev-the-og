import logging
import json
import os

def load_module_perf(path="logs/module_performance.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def auto_scale_modules(config, perf_path="logs/module_performance.json"):
    perf = load_module_perf(perf_path)
    capital_allocation = {}
    for mod, stats in perf.items():
        winrate = stats.get("winrate", 0.5)
        avg_pnl = stats.get("avg_pnl", 0)
        loss = stats.get("loss", 0)
        drawdown = stats.get("drawdown", 0)
        # Example: scale capital up if winrate and PnL are positive, down if not
        scale = max(0.01, min(1.0, winrate + avg_pnl - drawdown))
        capital_allocation[mod] = float(config.get("starting_capital", 1000)) * scale
    logging.info(f"[AutoScaler] Updated capital allocation: {capital_allocation}")
    # For prod: update live config, notify orchestrator, or re-balance wallets accordingly
    return capital_allocation

if __name__ == "__main__":
    import yaml
    config = yaml.safe_load(open("config.yaml"))
    print(auto_scale_modules(config))
