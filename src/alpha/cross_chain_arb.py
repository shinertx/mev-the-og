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
