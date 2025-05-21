import time
from web3 import Web3
from .utils import load_config
from .risk_manager import RiskManager
from .kill_switch import KillSwitch
from .notifier import send_telegram

class MEVBot:
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.network = self.config.get("network")
        self.mode = self.config.get("mode")
        self.alchemy_api_key = self.config.get("alchemy_api_key")
        self.web3 = Web3(Web3.HTTPProvider(f"https://eth-{self.network}.g.alchemy.com/v2/{self.alchemy_api_key}"))
        self.wallet = self.config.get("wallet_address")
        self.risk = RiskManager(self.config)
        self.kill = KillSwitch(self.config)
        print(f"[MEVBot] Initialized in {self.mode.upper()} mode on {self.network}")

    def run(self):
        print("[MEVBot] Running main bot loop (demo mode)...")
        latest = self.web3.eth.block_number
        print(f"[MEVBot] Latest block: {latest}")

        # DEMO: Update risk/kill logic (stub)
        fake_pnl = 0  # replace with real PnL calc as needed
        self.risk.update_drawdown(fake_pnl)
        self.kill.update_pnl(fake_pnl)
        if not self.kill.is_enabled():
            print("[MEVBot] Kill switch triggered. Exiting.")
            send_telegram("KILL SWITCH: Trading disabled!", self.config['notifier'].get('telegram_token',''), self.config['notifier'].get('telegram_chat_id',''))
            return
        # ... extend with further strategies or module hooks

if __name__ == "__main__":
    bot = MEVBot()
    bot.run()
