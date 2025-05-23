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
<<<<<<< ours
from .monitoring import Monitoring
from .signer_service import SignerService
from .transaction_manager import TransactionManager
from .cross_chain_arb import CrossChainArb

logger = logging.getLogger(__name__)


class MEVBot:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_app_config(config_path)
        rpc_url = self.config.rpc_urls.root.get(self.config.network)
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if "web3_mock" in sys.modules or "eth_account_mock" in sys.modules:
            logger.critical("CRITICAL: Mock web3/eth_account modules detected!")
            raise RuntimeError("Mock modules loaded")
        self.network = self.config.network
        self.mode = self.config.mode
        self.signer = SignerService()
        os.makedirs(os.path.dirname(self.config.database_path), exist_ok=True)
        self.db = sqlite3.connect(self.config.database_path)
        self._init_db()
        self.txm = TransactionManager(self.web3, None, self.signer, self.config)
        self.arb = CrossChainArb(self.web3, None, self.signer, self.db, self.config, self.txm)
        self.risk = RiskManager(self.config.model_dump())
        self.kill = KillSwitch(self.config.model_dump())
        self.monitor = Monitoring(self.db)
        logger.info(f"[MEVBot] Initialized on {self.config.network} in {self.config.mode}")

    def _init_db(self):
        cur = self.db.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                opportunity_id TEXT,
                strategy_id TEXT,
                status TEXT,
                timestamp_start REAL,
                timestamp_end REAL,
                token_in_address TEXT,
                token_in_amount_wei TEXT,
                token_out_address TEXT,
                token_out_amount_min_wei TEXT,
                token_out_amount_actual_wei TEXT,
                tx_hash_leg1 TEXT,
                gas_used_leg1 INTEGER,
                gas_price_leg1_gwei_effective REAL,
                pnl_usd_leg1 REAL,
                error_message_leg1 TEXT
            )
            """
        )
        self.db.commit()

    async def run_arbitrage(self):
        opp = await self.arb.find_opportunity()
        if opp and self.kill.is_enabled():
            start = time()
            result = await self.arb.execute_evm_leg1_swap(opp)
            latency = time() - start
            pnl = result.get("pnl_usd_leg1", 0.0)
            self.monitor.record_trade(result.get("tx_hash", ""), pnl, latency)
            logger.info(f"[MEVBot] Swap success={result.get('success')}")

    def run(self):
        asyncio.run(self.run_arbitrage())

=======
from .notifier import send_telegram
from .safety.config_monitor import ConfigMonitor

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
        self.monitor = ConfigMonitor(config_path, ".env", kill_switch=self.kill, notifier_cfg=self.config.get("notifier", {}))
        print(f"[MEVBot] Initialized in {self.mode.upper()} mode on {self.network}")

    def run(self):
        print("[MEVBot] Running main bot loop (demo mode)...")
        latest = self.web3.eth.block_number
        print(f"[MEVBot] Latest block: {latest}")

        # DEMO: Update risk/kill logic (stub)
        fake_pnl = 0  # replace with real PnL calc as needed
        self.risk.update_drawdown(fake_pnl)
        self.kill.update_pnl(fake_pnl)
        self.monitor.check()
        if not self.kill.is_enabled():
            print("[MEVBot] Kill switch triggered. Exiting.")
            send_telegram("KILL SWITCH: Trading disabled!", self.config['notifier'].get('telegram_token',''), self.config['notifier'].get('telegram_chat_id',''))
            return
        # ... extend with further strategies or module hooks
>>>>>>> theirs

if __name__ == "__main__":
    MEVBot().run()
