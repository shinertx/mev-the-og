import hashlib
import logging
import os
from typing import Optional

from src.notifier import send_telegram, send_email


def _hash_file(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


class ConfigMonitor:
    """Watches config.yaml and .env for changes."""

    def __init__(self, config_path: str, env_path: str, kill_switch=None, notifier_cfg: Optional[dict] = None):
        self.config_path = config_path
        self.env_path = env_path
        self.kill_switch = kill_switch
        self.notifier_cfg = notifier_cfg or {}
        self.config_hash = _hash_file(config_path)
        self.env_hash = _hash_file(env_path)

    def check(self) -> bool:
        changed = False
        new_cfg = _hash_file(self.config_path)
        new_env = _hash_file(self.env_path)
        if new_cfg != self.config_hash or new_env != self.env_hash:
            changed = True
            self.config_hash = new_cfg
            self.env_hash = new_env
            logging.critical("[ConfigMonitor] Configuration or secret changed!")
            if self.kill_switch:
                self.kill_switch.trigger("CONFIG CHANGE DETECTED")
            token = self.notifier_cfg.get("telegram_token")
            chat = self.notifier_cfg.get("telegram_chat_id")
            email = self.notifier_cfg.get("email")
            send_telegram("CONFIG CHANGED - TRADING HALTED", token, chat)
            if email:
                send_email("CONFIG CHANGED - TRADING HALTED", email)
        return changed
