import os
import pytest
from src.core.env_manager import load_env_config, load_env_file
from src.safety.config_monitor import ConfigMonitor
from src.kill_switch import KillSwitch


def test_env_validation_error(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("BADLINE")
    with pytest.raises(RuntimeError):
        load_env_config(str(env_file))


def test_runtime_config_tamper(monkeypatch, tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("network: sepolia\nmode: test\nrisk:\n  max_drawdown_pct: 5\n  max_loss_usd: 100\n")
    envf = tmp_path / ".env"
    envf.write_text("TELEGRAM_BOT_TOKEN=x\nTELEGRAM_CHAT_ID=y\n")
    ks = KillSwitch({'risk': {'max_drawdown_pct':5, 'max_loss_usd':100}, 'notifier': {'telegram_token':'x','telegram_chat_id':'y'}})
    messages = []
    monkeypatch.setattr('src.notifier.send_telegram', lambda m,t,c: messages.append(m))
    monitor = ConfigMonitor(str(cfg), str(envf), kill_switch=ks, notifier_cfg={'telegram_token':'x','telegram_chat_id':'y'})
    cfg.write_text("tampered: true")
    changed = monitor.check()
    assert changed
    assert not ks.is_enabled()
    assert messages
