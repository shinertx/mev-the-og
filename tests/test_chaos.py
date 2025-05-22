from src.kill_switch import KillSwitch
from src.risk_manager import RiskManager
from src.notifier import notify_founder

EVENTS = []

def dummy_notifier(msg):
    EVENTS.append(msg)

CFG = {
    "risk": {"max_loss_usd": 5},
    "kill_switch_enabled": True,
    "kill_switch_max_errors": 1,
    "trade_amount_usd": 1,
    "notifier": {"telegram_token": "x", "founder_chat_id": "1", "email": "f@example.com"},
}


def test_chaos_sequence(monkeypatch):
    ks = KillSwitch(CFG, notifier=dummy_notifier)
    rm = RiskManager(CFG, ks)

    # notifier outage -> telegram fails
    monkeypatch.setattr('src.notifier.requests.post', lambda *a, **k: (_ for _ in ()).throw(Exception('fail')))

    ks.record_trade_error('trade fail1')
    ks.record_api_disconnect('rpc fail')
    ks.manual_override(KillSwitch.HALT, 'unauth', confirm=False, source='unauth')
    rm.update_drawdown(-10)

    assert ks.state == KillSwitch.HALT
    assert any('HALT' in e for e in EVENTS)

