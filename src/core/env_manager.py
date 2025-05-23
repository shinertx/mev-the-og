import os
from typing import Dict
from pydantic import BaseModel, ValidationError

class EnvConfig(BaseModel):
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None
    INFURA_PROJECT_ID: str | None = None
    OPENAI_API_KEY: str | None = None
    KMS_API_KEY: str | None = None
    KMS_KEY_ID: str | None = None
    LOCAL_SIGNER_KEY_PATH: str | None = None

    model_config = {"extra": "ignore"}


def load_env_file(path: str = ".env") -> Dict[str, str]:
    if not os.path.exists(path):
        return {}
    data: Dict[str, str] = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise RuntimeError(f"Malformed env line: {line}")
            k, v = line.split("=", 1)
            data[k] = v
            os.environ.setdefault(k, v)
    return data


def load_env_config(path: str = ".env") -> EnvConfig:
    raw = load_env_file(path)
    try:
        return EnvConfig(**raw)
    except ValidationError as e:
        raise RuntimeError(f"Env validation failed:\n{e}")
