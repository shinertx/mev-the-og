from src.notifier import Notifier
from src.kill_switch import KillSwitch
from src.risk_manager import RiskManager
from src.core.config_manager import load_app_config


class DummyNotifier(Notifier):
    def __init__(self):
        super().__init__({})
        self.events = []

    def _send_telegram(self, msg):
        self.events.append(msg)
        return True

    _send_email = _send_telegram
    _send_slack = _send_telegram


def test_kill_switch_escalation(tmp_path):
    cfg = {"risk": {"max_loss_usd": 1}, "kill_switch_enabled": True}
    notifier = DummyNotifier()
    kill = KillSwitch(cfg, notifier=notifier)
    kill.update_pnl(-5)
    assert not kill.is_enabled()
    assert any("KILL_SWITCH" in e for e in notifier.events)


def test_risk_manager_escalation():
    cfg = {"risk": {"max_loss_usd": 1}, "trade_amount_usd": 1}
    notifier = DummyNotifier()
    risk = RiskManager(cfg, notifier=notifier)
    assert not risk.update_drawdown(-5)
    assert any("RISK" in e for e in notifier.events)


def test_notifier_escalation_fail(tmp_path, monkeypatch):
    n = Notifier({"telegram_token": "bad", "telegram_chat_id": "1", "email": "a@b", "slack_webhook": "http://example.com"})
    monkeypatch.setattr(n, "_send_telegram", lambda m: False)
    monkeypatch.setattr(n, "_send_email", lambda m: False)
    monkeypatch.setattr(n, "_send_slack", lambda m: False)
    panic_file = tmp_path / "PANIC.log"
    monkeypatch.chdir(tmp_path)
    n.escalate_event("risk", "fail test")
    assert panic_file.read_text().strip() == "RISK: fail test"


def test_config_tamper(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("network: mainnet\nprivate_key: bad")
    notifier = DummyNotifier()
    try:
        load_app_config(str(cfg_file), notifier=notifier)
    except AssertionError:
        pass
    assert any("CONFIG" in e for e in notifier.events)
