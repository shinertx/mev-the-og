import os
import yaml
from dotenv import load_dotenv
from typing import Optional, Dict
from pydantic import BaseModel, Field, ValidationError, RootModel

# Load .env if present
load_dotenv()

# --- Pydantic Models matching your config.yaml ---

class NotifierConfig(BaseModel):
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email: Optional[str] = None

class RiskConfig(BaseModel):
    max_drawdown_pct: float = Field(gt=0, lt=100)
    max_loss_usd: float = Field(gt=0)

class ContractsConfig(RootModel[Dict[str, str]]):
    pass

class RPCUrlsConfig(RootModel[Dict[str, str]]):
    pass

class WSSUrlsConfig(RootModel[Dict[str, Optional[str]]]):
    pass

class AppConfig(BaseModel):
    network: str
    wallet_address: str
    uniswap_wallet_address: Optional[str] = None
    rpc_urls: RPCUrlsConfig
    wss_urls: Optional[WSSUrlsConfig] = None
    contracts: Optional[ContractsConfig] = None
    mode: str
    gas_limit: int
    slippage_bps: int
    trade_amount_usd: float
    notifier: Optional[NotifierConfig] = None
    risk: RiskConfig
    kill_switch_enabled: Optional[bool] = True
    target_profit: Optional[float] = None
    starting_capital: Optional[float] = None

    model_config = {"extra": "forbid"}  # Strict: forbid extra fields

# --- ENV overlay logic ---

def overlay_env_vars(raw_config: dict):
    infura_id = os.getenv("INFURA_PROJECT_ID")
    if infura_id:
        # RPC URLs
        if "rpc_urls" in raw_config:
            for k, v in raw_config["rpc_urls"].items():
                if isinstance(v, str) and "YOUR_INFURA_PROJECT_ID" in v:
                    raw_config["rpc_urls"][k] = v.replace("YOUR_INFURA_PROJECT_ID", infura_id)
        # WSS URLs
        if "wss_urls" in raw_config:
            for k, v in raw_config["wss_urls"].items():
                if isinstance(v, str) and "YOUR_INFURA_PROJECT_ID" in v:
                    raw_config["wss_urls"][k] = v.replace("YOUR_INFURA_PROJECT_ID", infura_id)
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if telegram_token:
        if "notifier" not in raw_config or raw_config["notifier"] is None:
            raw_config["notifier"] = {}
        raw_config["notifier"]["telegram_token"] = telegram_token
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_chat_id:
        if "notifier" not in raw_config or raw_config["notifier"] is None:
            raw_config["notifier"] = {}
        raw_config["notifier"]["telegram_chat_id"] = telegram_chat_id
    return raw_config

def load_app_config(config_path: str = "config.yaml") -> AppConfig:
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)
    raw_config = overlay_env_vars(raw_config)
    try:
        config = AppConfig(**raw_config)
    except ValidationError as e:
        raise RuntimeError(f"Config validation failed:\n{e}")

    # Forbid private key in config
    def scan_private_key(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if "private_key" in k.lower():
                    raise AssertionError("Private key must not be loaded in config!")
                scan_private_key(v)
        elif isinstance(d, list):
            for v in d:
                scan_private_key(v)
    scan_private_key(raw_config)
    return config
