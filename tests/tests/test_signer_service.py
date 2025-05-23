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
