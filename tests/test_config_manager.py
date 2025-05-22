import os
import pytest
from src.core.config_manager import load_app_config, AppConfig

VALID_CONFIG = """
network: sepolia
wallet_address: "0xA061e51F27F49EeD5F6F1Afed049206764Be7A9c"
uniswap_wallet_address: "0x67Da2453139cA6D3D6989AB3BC3fd0583E9F7B3d"
rpc_urls:
  mainnet: "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
  sepolia: "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
wss_urls:
  mainnet: "wss://mainnet.infura.io/ws/v3/YOUR_INFURA_PROJECT_ID"
contracts:
  aave_v3_sepolia: "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951"
mode: "test"
gas_limit: 3500000
slippage_bps: 50
trade_amount_usd: 100
notifier:
  telegram_token: ""
  telegram_chat_id: ""
  email: ""
risk:
  max_drawdown_pct: 5
  max_loss_usd: 200
kill_switch_enabled: true
target_profit: 0.02
starting_capital: 2000.0
"""

def test_valid_config_load(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(VALID_CONFIG)
    cfg = load_app_config(str(cfg_file))
    assert isinstance(cfg, AppConfig)
    assert cfg.network == "sepolia"
    assert "mainnet" in cfg.rpc_urls.root

def test_env_var_injection(monkeypatch, tmp_path):
    config_text = VALID_CONFIG
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(config_text)
    monkeypatch.setenv("INFURA_PROJECT_ID", "abc123xyz")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "abcde")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    cfg = load_app_config(str(cfg_file))
    assert "abc123xyz" in cfg.rpc_urls.root["mainnet"]
    assert cfg.notifier.telegram_token == "abcde"
    assert cfg.notifier.telegram_chat_id == "123456"

def test_type_validation_error(tmp_path):
    config_text = VALID_CONFIG.replace('gas_limit: 3500000', 'gas_limit: "notanumber"')
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(config_text)
    with pytest.raises(RuntimeError):
        load_app_config(str(cfg_file))

def test_constraint_violation(tmp_path):
    config_text = VALID_CONFIG.replace("max_drawdown_pct: 5", "max_drawdown_pct: 150")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(config_text)
    with pytest.raises(RuntimeError):
        load_app_config(str(cfg_file))

def test_forbid_extra_fields(tmp_path):
    config_text = VALID_CONFIG + "\nprivate_key: 'shouldnotbehere'"
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(config_text)
    with pytest.raises(RuntimeError):
        load_app_config(str(cfg_file))
