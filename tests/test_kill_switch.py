import pytest
from src.kill_switch import KillSwitch
from src.risk_manager import RiskManager

BASIC_CFG = {
    "risk": {"max_loss_usd": 10},
    "kill_switch_enabled": True,
    "kill_switch_max_errors": 2,
    "trade_amount_usd": 10,
    "notifier": {"telegram_token": "x", "founder_chat_id": "1"},
}

def dummy_notifier(msg):
    pass


def test_trade_error_escalation():
    ks = KillSwitch(BASIC_CFG, notifier=dummy_notifier)
    ks.record_trade_error("fail")
    ks.record_trade_error("fail")
    assert ks.state == KillSwitch.PAUSE
    ks.record_trade_error("fail")
    ks.record_trade_error("fail")
    assert ks.state == KillSwitch.HALT


def test_api_disconnect_escalation():
    ks = KillSwitch(BASIC_CFG, notifier=dummy_notifier)
    ks.record_api_disconnect()
    assert ks.state == KillSwitch.PAUSE
    ks.record_api_disconnect()
    assert ks.state == KillSwitch.HALT


def test_risk_breach_triggers_halt():
    ks = KillSwitch(BASIC_CFG, notifier=dummy_notifier)
    rm = RiskManager(BASIC_CFG, ks)
    rm.update_drawdown(-5)
    assert ks.state == KillSwitch.RUNNING
    rm.update_drawdown(-6)
    assert ks.state == KillSwitch.HALT


def test_manual_override():
    ks = KillSwitch(BASIC_CFG, notifier=dummy_notifier)
    ks.manual_override(KillSwitch.LIQUIDATE, "maintenance", confirm=True)
    assert ks.state == KillSwitch.LIQUIDATE
    ks.manual_override(KillSwitch.HALT, "bad", confirm=False)
    assert ks.state == KillSwitch.LIQUIDATE  # no change without confirm
