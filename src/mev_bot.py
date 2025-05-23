import asyncio
import logging
import os
import sqlite3
from time import time
from web3 import Web3
import sys

from .core.config_manager import load_app_config
from .risk_manager import RiskManager
from .kill_switch import KillSwitch
from .notifier import Notifier
from .dashboard import state as dashboard_state

class MEVBot:
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.network = self.config.get("network")
        self.mode = self.config.get("mode")
        self.alchemy_api_key = self.config.get("alchemy_api_key")
        self.web3 = Web3(Web3.HTTPProvider(f"https://eth-{self.network}.g.alchemy.com/v2/{self.alchemy_api_key}"))
        self.wallet = self.config.get("wallet_address")
        self.notifier = Notifier(self.config.get("notifier", {}))
        self.risk = RiskManager(self.config, notifier=self.notifier)
        self.kill = KillSwitch(self.config, notifier=self.notifier)
        print(f"[MEVBot] Initialized in {self.mode.upper()} mode on {self.network}")

    def run(self):
        print("[MEVBot] Running main bot loop (demo mode)...")
        latest = self.web3.eth.block_number
        print(f"[MEVBot] Latest block: {latest}")

        # DEMO: Update risk/kill logic (stub)
        fake_pnl = 0  # replace with real PnL calc as needed
        self.risk.update_drawdown(fake_pnl)
        self.kill.update_pnl(fake_pnl)
        dashboard_state.risk = self.risk.current_drawdown
        dashboard_state.kill_switch_state = "OK" if self.kill.is_enabled() else "TRIGGERED"
        dashboard_state.heartbeat = time.time()
        if not self.kill.is_enabled():
            print("[MEVBot] Kill switch triggered. Exiting.")
            self.notifier.escalate_event("kill_switch", "Trading disabled")
            dashboard_state.panic = True
            return
        # ... extend with further strategies or module hooks

if __name__ == "__main__":
    MEVBot().run()
