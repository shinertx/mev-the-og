import yaml
import os
from dotenv import load_dotenv

def load_config(path="config.yaml"):
    if os.path.exists('.env'):
        load_dotenv('.env')
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    # Override with env vars if present
    for key in ["alchemy_api_key", "private_key", "wallet_address"]:
        env_val = os.environ.get(key.upper())
        if env_val:
            config[key] = env_val
    return config
