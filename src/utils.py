import yaml
import os
from dotenv import load_dotenv
from .core.config_manager import load_app_config

def load_config(path="config.yaml"):
    if os.path.exists('.env'):
        load_dotenv('.env')
    try:
        cfg = load_app_config(path)
    except Exception as e:
        raise RuntimeError(f"Config load failed: {e}")
    return cfg.model_dump()
