from src.mev_bot import MEVBot
from src.signer_service import SignerService

def test_mev_bot_init_and_run(monkeypatch):
    enc = SignerService.encrypt_private_key("deadbeef" * 4, "pass")
    monkeypatch.setenv("ENCRYPTION_PASSWORD", "pass")
    monkeypatch.setenv("PRIVATE_KEY_ENC", enc)
    bot = MEVBot("config.yaml")

    # Adapt attribute checks based on your actual MEVBot class
    # Use whichever is correct in your codebase
    if hasattr(bot, 'config'):
        assert bot.config.network in ["mainnet", "goerli", "sepolia"]
        assert bot.config.mode in ["test", "live"]
        assert bot.db is not None
    else:
        assert bot.network in ["mainnet", "goerli", "sepolia"]
        assert bot.mode in ["test", "live"]

    # Merge monkeypatch logic
    if hasattr(bot, "web3"):
        monkeypatch.setattr(bot.web3.eth, "block_number", 1)
    if hasattr(bot.kill, "state") and hasattr(bot.kill, "RUNNING"):
        bot.kill.state = bot.kill.RUNNING
    elif hasattr(bot.kill, "is_enabled"):
        monkeypatch.setattr(bot.kill, "is_enabled", lambda: True)
    if hasattr(bot, "arb") and hasattr(bot.arb, "find_opportunity"):
        async def fake_find():
            return None
        monkeypatch.setattr(bot.arb, "find_opportunity", fake_find)

    bot.run()
