from src.mev_bot import MEVBot
from src.signer_service import SignerService

def test_mev_bot_init_and_run(monkeypatch):
    enc = SignerService.encrypt_private_key("deadbeef" * 4, "pass")
    monkeypatch.setenv("ENCRYPTION_PASSWORD", "pass")
    monkeypatch.setenv("PRIVATE_KEY_ENC", enc)
    bot = MEVBot("config.yaml")
    assert bot.config.network in ["mainnet", "goerli", "sepolia"]
    assert bot.config.mode in ["test", "live"]
    assert bot.db is not None
    monkeypatch.setattr(bot.kill, "is_enabled", lambda: True)
    async def fake_find():
        return None
    monkeypatch.setattr(bot.arb, "find_opportunity", fake_find)
    bot.run()
