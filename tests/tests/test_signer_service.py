diff --git a//dev/null b/tests/test_signer_service.py
index 0000000..7bc48fb 100644
--- a//dev/null
+++ b/tests/test_signer_service.py
@@ -0,0 +1,12 @@
+import os
+from src.signer_service import SignerService
+
+
+def test_encrypt_decrypt_roundtrip(monkeypatch):
+    password = "pass"
+    priv = "deadbeef" * 4
+    enc = SignerService.encrypt_private_key(priv, password)
+    monkeypatch.setenv("ENCRYPTION_PASSWORD", password)
+    monkeypatch.setenv("PRIVATE_KEY_ENC", enc)
+    ss = SignerService()
+    assert ss._private_key == priv
