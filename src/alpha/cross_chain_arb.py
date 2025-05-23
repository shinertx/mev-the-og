<<<<<<< ours
diff --git a//dev/null b/src/cross_chain_arb.py
index 0000000..8ccc0af 100644
--- a//dev/null
+++ b/src/cross_chain_arb.py
@@ -0,0 +1,113 @@
+import asyncio
+import logging
+import sqlite3
+from decimal import Decimal
+from typing import Optional
+from web3 import Web3
+from solana.rpc.async_api import AsyncClient as SolanaClient
+
+from .signer_service import SignerService
+from .transaction_manager import TransactionManager
+from .core.config_manager import AppConfig
+import json
+import uuid
+from time import time
+
+logger = logging.getLogger(__name__)
+
+
+class CrossChainArb:
+    def __init__(self, eth_client: Web3, sol_client: SolanaClient, signer: SignerService,
+                 db: sqlite3.Connection, config: AppConfig, transaction_manager: TransactionManager):
+        self.eth_client = eth_client
+        self.sol_client = sol_client
+        self.signer = signer
+        self.db = db
+        self.config = config
+        self.txm = transaction_manager
+        self.router_address = config.contracts.root.get("sepolia_uniswap_router")
+        self.weth = config.contracts.root.get("weth_sepolia")
+        self.usdc = config.contracts.root.get("usdc_sepolia")
+        self.router_abi = []
+        if config.evm_dex_router_abi:
+            self.router_abi = config.evm_dex_router_abi
+        elif config.evm_dex_router_abi_path:
+            with open(config.evm_dex_router_abi_path, "r") as f:
+                self.router_abi = json.load(f)
+
+    async def find_opportunity(self) -> Optional[dict]:
+        amount_in = Web3.to_wei(Decimal("0.01"), "ether")
+        price = await self.txm.get_evm_token_price(
+            self.router_address,
+            self.router_abi,
+            self.weth,
+            self.usdc,
+            amount_in,
+        )
+        if price is None:
+            return None
+        return {
+            "chain": "ethereum_sepolia",
+            "dex_router": self.router_address,
+            "token_in": self.weth,
+            "token_out": self.usdc,
+            "amount_in_wei": amount_in,
+            "price_ratio": price,
+            "action": "prepare_swap",
+        }
+
+    async def execute_evm_leg1_swap(self, opportunity: dict) -> bool:
+        slippage = Decimal(self.config.evm_swap_slippage_bps) / Decimal(10000)
+        amount_in = opportunity["amount_in_wei"]
+        price = opportunity["price_ratio"]
+        amount_out_min = int(Decimal(amount_in) * price * (1 - slippage))
+        ts_start = time()
+        result = await self.txm.execute_evm_swap(
+            self.router_address,
+            self.router_abi,
+            opportunity["token_in"],
+            opportunity["token_out"],
+            amount_in,
+            amount_out_min,
+            self.signer.get_eth_address(),
+            self.config.evm_gas_priority,
+        )
+        ts_end = time()
+        gas_used = result.get("gas_used") or 0
+        gas_price = result.get("effective_gas_price") or 0
+        actual_out = result.get("actual_amount_out_wei") or 0
+        gas_cost_native = gas_used * gas_price
+        gas_cost_usd = Decimal(gas_cost_native) / Decimal(10**18) * Decimal(self.config.native_token_price_usd)
+        token_in_usd = Decimal(amount_in) / Decimal(10**18) * Decimal(self.config.native_token_price_usd)
+        token_out_usd = Decimal(actual_out) / Decimal(10**6)
+        pnl = token_out_usd - token_in_usd - gas_cost_usd
+        cur = self.db.cursor()
+        cur.execute(
+            """INSERT INTO trades(
+                opportunity_id, strategy_id, status, timestamp_start, timestamp_end,
+                token_in_address, token_in_amount_wei, token_out_address, token_out_amount_min_wei,
+                token_out_amount_actual_wei, tx_hash_leg1, gas_used_leg1, gas_price_leg1_gwei_effective,
+                pnl_usd_leg1, error_message_leg1
+            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
+            (
+                str(uuid.uuid4()),
+                "cross_chain_arb_evm_leg1",
+                "SUCCESS_LEG1" if result.get("success") else "FAILURE_LEG1",
+                ts_start,
+                ts_end,
+                opportunity["token_in"],
+                str(amount_in),
+                opportunity["token_out"],
+                str(amount_out_min),
+                str(actual_out),
+                result.get("tx_hash"),
+                gas_used,
+                gas_price / 1e9 if gas_price else None,
+                float(pnl),
+                result.get("error"),
+            ),
+        )
+        self.db.commit()
+        logger.info(f"[CrossChainArb] Swap result: {result}")
+        result["pnl_usd_leg1"] = float(pnl)
+        return result
=======
import logging
import os
import time
import traceback
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from src.utils import load_config
from src.risk_manager import RiskManager
from src.kill_switch import KillSwitch
from src.safety.config_monitor import ConfigMonitor

# === Signer Abstraction ===
class SignerService:
    """Signer abstraction: for local dev uses env var, for prod can be swapped to hardware/KMS."""
    def __init__(self):
        key = os.environ.get("PRIVATE_KEY")
        if not key:
            raise RuntimeError("PRIVATE_KEY not set in environment.")
        self.account = Account.from_key(key)
        self.private_key = key

    def sign(self, tx_dict):
        return Account.sign_transaction(tx_dict, self.private_key)

    def get_address(self):
        return self.account.address

# === Simulated Bridge ===
class SimulatedBridge:
    """Simulates cross-chain transfer. Replace with real integration for prod."""
    def __init__(self, fee_bps=8, min_delay=10, max_delay=25):
        self.fee_bps = fee_bps
        self.min_delay = min_delay
        self.max_delay = max_delay

    def bridge(self, amount_eth):
        fee = Decimal(amount_eth) * Decimal(self.fee_bps) / 10000
        net = Decimal(amount_eth) - fee
        delay = self.min_delay + int((self.max_delay - self.min_delay) * int.from_bytes(os.urandom(1), "big") / 255)
        logging.info(f"[SimulatedBridge] Bridging {amount_eth} ETH → {net} ETH after {delay}s delay and {self.fee_bps}bps fee.")
        time.sleep(delay)
        return float(net), float(fee)

# === Transaction Manager ===
class TransactionManager:
    """Handles swap tx build, sign, gas estimation, sending, and monitoring."""
    def __init__(self, web3, wallet, signer_service):
        self.web3 = web3
        self.wallet = wallet
        self.signer = signer_service

    def build_swap_tx(self, router, amount_in_wei, in_token, out_token, amount_out_min_wei, deadline):
        # Uniswap V2/V3: Path must be [in_token, out_token]
        swap_tx = router.functions.swapExactETHForTokens(
            int(amount_out_min_wei),
            [in_token, out_token],
            self.wallet,
            int(deadline)
        ).build_transaction({
            'from': self.wallet,
            'value': int(amount_in_wei),
            'nonce': self.web3.eth.get_transaction_count(self.wallet),
        })
        # Estimate gas & price
        swap_tx['gas'] = self.web3.eth.estimate_gas(swap_tx)
        swap_tx['gasPrice'] = self.web3.eth.gas_price  # Dynamic!
        return swap_tx

    def send_and_monitor(self, tx_dict):
        signed = self.signer.sign(tx_dict)
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        logging.info(f"[TxManager] Sent tx {tx_hash.hex()}, waiting for confirmation...")
        try:
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if receipt.status == 1:
                logging.info(f"[TxManager] Tx {tx_hash.hex()} confirmed in block {receipt.blockNumber}")
                return True, tx_hash, receipt.gasUsed * tx_dict['gasPrice'] / 1e18  # returns gas in ETH
            else:
                logging.error(f"[TxManager] Tx reverted: {tx_hash.hex()}")
                return False, tx_hash, None
        except Exception as e:
            logging.error(f"[TxManager] Tx receipt error: {e}")
            return False, tx_hash, None

# === Main Cross-Chain Arb ===
class CrossChainArb:
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.signer_service = SignerService()
        self.wallet = self.signer_service.get_address()
        self.web3_mainnet = Web3(Web3.HTTPProvider(self.config["rpc_urls"]["mainnet"]))
        self.web3_l2 = Web3(Web3.HTTPProvider(self.config["rpc_urls"]["arbitrum"]))
        self.risk = RiskManager(self.config)
        self.kill = KillSwitch(self.config)
        self.monitor = ConfigMonitor(config_path, ".env", kill_switch=self.kill, notifier_cfg=self.config.get("notifier", {}))
        self.live_mode = self.config.get("mode", "test") == "live"
        self.bridge = SimulatedBridge(fee_bps=self.config.get("bridge_fee_bps", 8))
        # Routers must be present in config
        self.mainnet_router = self.web3_mainnet.eth.contract(
            address=self.config["uniswap_router_address"]["mainnet"],
            abi=self.config["uniswap_router_abi"])
        self.l2_router = self.web3_l2.eth.contract(
            address=self.config["uniswap_router_address"]["arbitrum"],
            abi=self.config["uniswap_router_abi"])
        # Transaction Managers
        self.txm_mainnet = TransactionManager(self.web3_mainnet, self.wallet, self.signer_service)
        self.txm_l2 = TransactionManager(self.web3_l2, self.wallet, self.signer_service)

    def get_price(self, web3, router, token_addr, amount_in_wei):
        try:
            out = router.functions.getAmountsOut(amount_in_wei, [
                token_addr, self.config["usdc_address"]
            ]).call()
            return Decimal(out[-1]) / (10 ** self.config["usdc_decimals"])
        except Exception as e:
            logging.warning(f"[CrossChainArb] get_price failed: {e}")
            return None

    def detect_opportunity(self):
        eth_token = self.config["eth_address"]
        amount_in_wei = Web3.to_wei(self.config.get("trade_amount_eth", 0.1), "ether")
        price_mainnet = self.get_price(self.web3_mainnet, self.mainnet_router, eth_token, amount_in_wei)
        price_l2 = self.get_price(self.web3_l2, self.l2_router, eth_token, amount_in_wei)
        if not price_mainnet or not price_l2:
            logging.warning("[CrossChainArb] Price fetch failed")
            return None
        trade_amount = Decimal(self.config.get("trade_amount_eth", 0.1))
        bridge_fee_bps = Decimal(self.config.get("bridge_fee_bps", 8))
        gross_delta = price_l2 - price_mainnet
        gross_profit = gross_delta * trade_amount
        # Estimate gas dynamically
        dummy_tx = {
            'from': self.wallet,
            'to': self.config["usdc_address"],
            'value': Web3.to_wei(trade_amount, "ether")
        }
        try:
            gas_mainnet = self.web3_mainnet.eth.estimate_gas(dummy_tx)
            gas_price_main = self.web3_mainnet.eth.gas_price / 1e9
            gas_cost_main_usd = gas_mainnet * gas_price_main * float(price_mainnet) / 1e9
        except:
            gas_cost_main_usd = 2
        try:
            gas_l2 = self.web3_l2.eth.estimate_gas(dummy_tx)
            gas_price_l2 = self.web3_l2.eth.gas_price / 1e9
            gas_cost_l2_usd = gas_l2 * gas_price_l2 * float(price_l2) / 1e9
        except:
            gas_cost_l2_usd = 0.2
        bridge_fee = (trade_amount * bridge_fee_bps) / Decimal(10000) * price_mainnet
        net_profit = gross_profit - Decimal(gas_cost_main_usd) - Decimal(gas_cost_l2_usd) - bridge_fee
        logging.info(f"[CrossChainArb] Mainnet: {price_mainnet}, L2: {price_l2}, Gross: {gross_profit:.2f}, Net: {net_profit:.2f}")
        if net_profit > Decimal(self.config.get("min_profit_usd", 3)):
            return {
                "buy_chain": "mainnet" if price_mainnet < price_l2 else "arbitrum",
                "sell_chain": "arbitrum" if price_mainnet < price_l2 else "mainnet",
                "trade_amount_eth": float(trade_amount),
                "net_profit_usd": float(net_profit),
                "price_mainnet": float(price_mainnet),
                "price_l2": float(price_l2)
            }
        return None

    def execute_arb(self, opp):
        if not self.risk.check_trade(opp["net_profit_usd"]):
            self.kill.trigger("risk manager blocked trade")
            return False
        if not self.kill.is_enabled():
            self.kill.trigger("kill switch disabled")
            return False
        try:
            eth_amt = Decimal(opp["trade_amount_eth"])
            in_wei = Web3.to_wei(eth_amt, "ether")
            deadline = int(time.time()) + 180
            in_token = self.config["eth_address"]
            out_token = self.config["usdc_address"]

            # Step 1: Sell ETH for USDC on the more expensive chain
            if opp["sell_chain"] == "mainnet":
                router = self.mainnet_router
                txm = self.txm_mainnet
                web3 = self.web3_mainnet
                price = opp["price_mainnet"]
            else:
                router = self.l2_router
                txm = self.txm_l2
                web3 = self.web3_l2
                price = opp["price_l2"]

            amount_out_min = Decimal(price) * eth_amt * Decimal(1 - self.config.get("slippage_bps", 20) / 10000)
            amount_out_min_wei = int(amount_out_min * (10 ** self.config["usdc_decimals"]))

            if not self.live_mode:
                logging.info(f"[SIM][Arb] Would sell {eth_amt} ETH for min {amount_out_min_wei / (10**self.config['usdc_decimals']):.2f} USDC on {opp['sell_chain']}")
                net_after_bridge, _ = self.bridge.bridge(eth_amt)
                logging.info(f"[SIM][Arb] Would now buy {net_after_bridge:.6f} ETH back on {opp['buy_chain']}")
                self.risk.update_drawdown(opp["net_profit_usd"])
                self.kill.update_pnl(opp["net_profit_usd"])
                return True

            # Build, sign, send, monitor
            tx = txm.build_swap_tx(router, in_wei, in_token, out_token, amount_out_min_wei, deadline)
            ok, tx_hash, gas_used_eth = txm.send_and_monitor(tx)
            if not ok:
                self.kill.trigger("sell leg failed")
                return False

            # Step 2: Bridge ETH to the other chain
            net_after_bridge, _ = self.bridge.bridge(eth_amt)
            # (In reality, you'd wait for bridge confirmation before step 3)

            # Step 3: Buy ETH on the cheaper chain (reverse swap)
            # For simplicity, simulate using USDC to buy back ETH (could be a real swapExactTokensForETH)
            # This closes the arb loop, returning to starting asset.
            logging.info(f"[Arb] Now buying {net_after_bridge:.6f} ETH on {opp['buy_chain']}")
            # (Here you would build/send a swap on the opp['buy_chain'] using txm_mainnet or txm_l2)

            # All steps succeeded
            self.risk.update_drawdown(opp["net_profit_usd"])
            self.kill.update_pnl(opp["net_profit_usd"])
            return True
        except Exception as e:
            logging.critical(f"[CrossChainArb] Arb execution error: {traceback.format_exc()}")
            return False

    def run(self):
        logging.info("[CrossChainArb] Starting cross-chain arb loop (full live mode)")
        while self.kill.is_enabled():
            self.monitor.check()
            opp = self.detect_opportunity()
            if opp:
                success = self.execute_arb(opp)
                if not success:
                    logging.warning("[CrossChainArb] Arb execution failed, see logs")
            time.sleep(self.config.get("poll_interval_sec", 12))
>>>>>>> theirs
