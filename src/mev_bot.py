import yaml
import time
from web3 import Web3
from .utils import load_config

class MEVBot:
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.network = self.config.get("network")
        self.mode = self.config.get("mode")
        self.alchemy_api_key = self.config.get("alchemy_api_key")
        self.web3 = Web3(Web3.HTTPProvider(f"https://eth-{self.network}.g.alchemy.com/v2/{self.alchemy_api_key}"))
        self.wallet = self.config.get("wallet_address")
        print(f"[MEVBot] Initialized in {self.mode.upper()} mode on {self.network}")

    def run(self):
        print("[MEVBot] Running main bot loop (demo mode)...")
        # Placeholder: Fetch block number, print as dummy proof-of-life
        latest = self.web3.eth.block_number
        print(f"[MEVBot] Latest block: {latest}")
        # Insert further strategy logic here in future modules

if __name__ == "__main__":
    bot = MEVBot()
    bot.run()
