#!/usr/bin/env python
"""Utility to rotate bot secrets safely."""

import os
from datetime import datetime
from pathlib import Path
import shutil

ENV_FILE = ".env"


def main():
    if not Path(ENV_FILE).exists():
        print("No .env file found.")
        return
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    backup = Path(f"{ENV_FILE}.{ts}.bak")
    shutil.copy(ENV_FILE, backup)
    print(f"Backup created: {backup}")
    print("Edit the .env file with new secrets and restart the bot.")


if __name__ == "__main__":
    main()
