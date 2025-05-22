diff --git a//dev/null b/src/signer_service.py
index 0000000..a770beb 100644
--- a//dev/null
+++ b/src/signer_service.py
@@ -0,0 +1,49 @@
+import os
+from typing import Optional
+from eth_account import Account
+from Crypto.Cipher import AES
+from Crypto.Protocol.KDF import PBKDF2
+from Crypto.Random import get_random_bytes
+import hashlib
+
+PBKDF2_ITERATIONS = 250000
+SALT_SIZE = 16
+NONCE_SIZE = 12
+
+class SignerService:
+    """Simple encrypted key signer for Ethereum."""
+
+    def __init__(self):
+        password = os.getenv("ENCRYPTION_PASSWORD")
+        enc_hex = os.getenv("PRIVATE_KEY_ENC")
+        if not password or not enc_hex:
+            raise RuntimeError("Encrypted private key or password not set")
+        data = bytes.fromhex(enc_hex)
+        if len(data) < SALT_SIZE + NONCE_SIZE + 16:
+            raise RuntimeError("Encrypted key data too short")
+        salt = data[:SALT_SIZE]
+        nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
+        tag = data[-16:]
+        ciphertext = data[SALT_SIZE + NONCE_SIZE:-16]
+        key = PBKDF2(password, salt, dkLen=32, count=PBKDF2_ITERATIONS)
+        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
+        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
+        self._private_key = decrypted.decode()
+        self.eth_account = Account.from_key(self._private_key)
+
+    def sign_eth_tx(self, tx_dict: dict) -> bytes:
+        signed = self.eth_account.sign_transaction(tx_dict)
+        return signed.rawTransaction
+
+    def get_eth_address(self) -> str:
+        return self.eth_account.address
+
+    @staticmethod
+    def encrypt_private_key(private_key: str, password: str) -> str:
+        """Encrypt a private key using AES-GCM and PBKDF2, returning hex string."""
+        salt = get_random_bytes(SALT_SIZE)
+        nonce = get_random_bytes(NONCE_SIZE)
+        key = PBKDF2(password, salt, dkLen=32, count=PBKDF2_ITERATIONS)
+        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
+        ciphertext, tag = cipher.encrypt_and_digest(private_key.encode())
+        return (salt + nonce + ciphertext + tag).hex()
