from src.risk_manager import RiskManager


def test_slow_bleed_triggers_global_limit():
    cfg = {
        "risk": {
            "max_loss_usd": 10,
            "max_drawdown_pct": 50,
            "rolling_window_hours": 24,
            "max_trade_size_usd": 5,
        },
        "starting_capital": 100,
    }
    r = RiskManager(cfg)
    for _ in range(5):
        ok = r.update_pnl("alpha", -3)
    assert not ok  # should breach after cumulative -15


def test_per_alpha_disable_only_strategy():
    cfg = {
        "risk": {
            "max_loss_usd": 100,
            "rolling_window_hours": 24,
            "max_trade_size_usd": 50,
            "per_alpha": {"s1": {"max_loss_usd": 5, "max_trade_size_usd": 10}},
        },
        "starting_capital": 100,
    }
    r = RiskManager(cfg)
    for _ in range(2):
        r.update_pnl("s1", -3)
    assert r.alphas["s1"].disabled
    assert r.is_strategy_active("s1") is False
    # another strategy should remain active
    assert r.is_strategy_active("other") is True


def test_scaling_logic_adjusts_trade_size():
    cfg = {
        "risk": {
            "max_loss_usd": 100,
            "rolling_window_hours": 24,
            "max_trade_size_usd": 10,
            "scale_increment_usd": 5,
        },
        "starting_capital": 100,
    }
    r = RiskManager(cfg)
    for _ in range(3):
        r.update_pnl("s1", 2)
    r.scale_logic()
    assert r.max_trade_size_usd == 15
