import json
import logging

from src.utils import load_config
from src.logger import setup_logging, log_event
from src.ai.parameter_mutator import ParameterMutator
from src.ai.edge_pruner import prune_dead_edges
from src.ai.strategy_scorer import score_strategy

if __name__ == "__main__":
    cfg = load_config("config.yaml")
    setup_logging(cfg, "logs/ai_demo.log")
    mut = ParameterMutator(cfg)
    mut.maybe_mutate("cross_chain")

    sample_stats = {"winrate": 0.4, "avg_pnl": -0.03, "fail_count": 2}
    score = score_strategy(sample_stats, cfg.get("ai", {}).get("scoring", {}))
    log_event(logging.INFO, f"Demo edge score {score}", "demo")

    perf_file = "logs/module_performance.json"
    with open(perf_file, "w") as f:
        json.dump({"cross_chain": sample_stats}, f)
    killed = prune_dead_edges(cfg, perf_file)
    log_event(logging.INFO, f"Pruner removed: {killed}", "demo")
