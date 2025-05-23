import logging
import json
import hashlib
import os
import time

CONFIG_HASH = "unknown"


def setup_logging(config, log_file="logs/mev_og.log"):
    """Initialize logging with UTC timestamps and config hash."""
    global CONFIG_HASH
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    config_str = json.dumps(config, sort_keys=True)
    CONFIG_HASH = hashlib.sha256(config_str.encode()).hexdigest()[:8]
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(message)s",
    )
    logging.Formatter.converter = time.gmtime
    logging.info(f"[Logger] Initialized with config hash {CONFIG_HASH}")


def log_event(level, message, context=""):
    prefix = f"[CFG:{CONFIG_HASH}]"
    if context:
        msg = f"{prefix} [{context}] {message}"
    else:
        msg = f"{prefix} {message}"
    logging.log(level, msg)
