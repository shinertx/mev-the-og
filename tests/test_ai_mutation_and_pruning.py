import json
import hashlib

from src.ai.parameter_mutator import ParameterMutator
from src.ai.edge_pruner import prune_dead_edges
from src.ai.strategy_scorer import score_strategy
from src.logger import setup_logging
from src.kill_switch import KillSwitch


def base_config():
    return {
        "alpha": {"params": {"mod": {"x": 1.0}}},
        "ai": {
            "mutation_frequency": 1,
            "decay_threshold": -0.01,
            "scoring": {"winrate_weight": 0.5, "pnl_weight": 0.5, "fail_weight": 0.1},
        },
        "risk": {"max_drawdown_pct": 5, "max_loss_usd": 200},
        "kill_switch_enabled": True,
    }


def test_parameter_mutation(tmp_path):
    cfg = base_config()
    log_file = tmp_path / "log.log"
    expected_hash = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]
    setup_logging(cfg, str(log_file))
    mut = ParameterMutator(cfg)
    assert mut.maybe_mutate("mod")
    assert cfg["alpha"]["params"]["mod"]["x"] != 1.0
    contents = log_file.read_text()
    assert expected_hash in contents


def test_pruning_and_kill_switch(tmp_path):
    cfg = base_config()
    perf = {"bad": {"winrate": 0.2, "avg_pnl": -0.05, "fail_count": 3}}
    perf_file = tmp_path / "perf.json"
    perf_file.write_text(json.dumps(perf))
    ks = KillSwitch(cfg)
    killed = prune_dead_edges(cfg, str(perf_file))
    assert "bad" in killed
    assert ks.is_enabled()


def test_strategy_scoring():
    stats = {"winrate": 0.6, "avg_pnl": 0.02, "fail_count": 1}
    score = score_strategy(stats, {"winrate_weight": 0.5, "pnl_weight": 0.5, "fail_weight": 0.1})
    assert score > 0

