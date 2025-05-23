+import logging
+import sqlite3
+from typing import Optional
+
+logger = logging.getLogger(__name__)
+
+
+class Monitoring:
+    def __init__(self, db: sqlite3.Connection):
+        self.db = db
+
+    def record_trade(self, tx_hash: str, pnl: float, latency: float) -> None:
+        logger.info(f"[Monitoring] tx={tx_hash} pnl={pnl} latency={latency}")
