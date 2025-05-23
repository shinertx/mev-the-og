+import asyncio
+from unittest.mock import MagicMock
+
+import pytest
+
+from src.cross_chain_arb import CrossChainArb
+from src.transaction_manager import TransactionManager
+from src.core.config_manager import AppConfig, RiskConfig, RPCUrlsConfig
+
+
+class DummyTM(TransactionManager):
+    def __init__(self):
+        self.called = False
+
+    async def get_evm_token_price(self, *a, **k):
+        return 2
+
+    async def execute_evm_swap(self, *a, **k):
+        self.called = True
+        return {
+            "success": True,
+            "tx_hash": "0x1",
+            "gas_used": 21000,
+            "effective_gas_price": 100,
+            "actual_amount_out_wei": 2000000,
+            "error": None,
+        }
+
+
+@pytest.mark.asyncio
+async def test_find_and_execute():
+    cfg = AppConfig(
+        network="sepolia",
+        wallet_address="0xdead",
+        rpc_urls=RPCUrlsConfig({"sepolia": "http://localhost"}),
+        mode="test",
+        gas_limit=1000000,
+        slippage_bps=50,
+        trade_amount_usd=1.0,
+        risk=RiskConfig(max_drawdown_pct=5, max_loss_usd=10),
+        evm_swap_slippage_bps=50,
+        evm_gas_priority="fast",
+        contracts={"sepolia_uniswap_router": "0xrouter", "weth_sepolia": "0xA", "usdc_sepolia": "0xB"},
+        evm_dex_router_abi=[{"name": "swapExactTokensForTokens"}],
+        database_path="/tmp/test.db",
+        native_token_price_usd=2000.0,
+    )
+    db = MagicMock()
+    db.cursor.return_value.execute.return_value = None
+    db.commit.return_value = None
+    tm = DummyTM()
+    arb = CrossChainArb(MagicMock(), MagicMock(), MagicMock(), db, cfg, tm)
+    opp = await arb.find_opportunity()
+    assert opp is not None
+    result = await arb.execute_evm_leg1_swap(opp)
+    assert result["success"]
+    assert tm.called
