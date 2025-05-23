import os
from .core.config_manager import load_app_config
from .core.env_manager import load_env_config, load_env_file

def load_config(path: str = "config.yaml"):
    load_env_file()
    load_env_config()
    cfg = load_app_config(path)
    return cfg.model_dump()
