from src.mev_bot import MEVBot
from src.signer_service import SignerService

def test_mev_bot_init_and_run(monkeypatch):
    enc = SignerService.encrypt_private_key("deadbeef" * 4, "pass")
    monkeypatch.setenv("ENCRYPTION_PASSWORD", "pass")
    monkeypatch.setenv("PRIVATE_KEY_ENC", enc)
    bot = MEVBot("config.yaml")
    assert bot.network in ["mainnet", "goerli", "sepolia"]
    assert bot.mode in ["test", "live"]
    monkeypatch.setattr(bot.web3.eth, "block_number", 1)
    bot.kill.state = bot.kill.RUNNING
    bot.run()
