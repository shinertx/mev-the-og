diff --git a//dev/null b/tests/test_transaction_manager.py
index 0000000..0b749c9 100644
--- a//dev/null
+++ b/tests/test_transaction_manager.py
@@ -0,0 +1,67 @@
+import asyncio
+from unittest.mock import MagicMock
+from decimal import Decimal
+
+import pytest
+
+from src.transaction_manager import TransactionManager
+from src.core.config_manager import AppConfig, RiskConfig, RPCUrlsConfig
+
+
+class DummySigner:
+    def __init__(self):
+        self.eth_account = MagicMock(address="0xdead")
+
+    def sign_eth_tx(self, tx):
+        return b"signed"
+
+    def get_eth_address(self):
+        return "0xdead"
+
+
+def make_config():
+    return AppConfig(
+        network="sepolia",
+        wallet_address="0xdead",
+        rpc_urls=RPCUrlsConfig({"sepolia": "http://localhost"}),
+        mode="test",
+        gas_limit=1000000,
+        slippage_bps=50,
+        trade_amount_usd=1.0,
+        risk=RiskConfig(max_drawdown_pct=5, max_loss_usd=10),
+    )
+
+
+@pytest.mark.asyncio
+async def test_get_evm_token_price():
+    web3 = MagicMock()
+    router = MagicMock()
+    web3.eth.contract.return_value = router
+    router.functions.getAmountsOut.return_value.call.return_value = [0, 200]
+    tm = TransactionManager(web3, None, DummySigner(), make_config())
+    price = await tm.get_evm_token_price("0xrouter", [], "0xA", "0xB", 100)
+    assert price == Decimal(200) / Decimal(100)
+
+
+@pytest.mark.asyncio
+async def test_execute_evm_swap_success():
+    web3 = MagicMock()
+    router = MagicMock()
+    func = MagicMock()
+    func.build_transaction.return_value = {"to": "0xrouter"}
+    router.functions.swapExactTokensForTokens.return_value = func
+    web3.eth.contract.return_value = router
+    web3.eth.estimate_gas.return_value = 21000
+    web3.eth.get_block.return_value = {"baseFeePerGas": 100}
+    web3.eth.max_priority_fee = 2
+    web3.eth.get_transaction_count.return_value = 1
+    web3.eth.estimate_gas.return_value = 21000
+    web3.eth.send_raw_transaction.return_value = b"\x12"
+    receipt = MagicMock(status=1, gasUsed=21000, effectiveGasPrice=104)
+    receipt.logs = []
+    web3.eth.wait_for_transaction_receipt.return_value = receipt
+    tm = TransactionManager(web3, None, DummySigner(), make_config())
+    result = await tm.execute_evm_swap("0xrouter", [], "0xA", "0xB", 100, 90, "0xdead")
+    assert result["success"]
+    assert result["gas_used"] == 21000
+    assert result["effective_gas_price"] == 104
