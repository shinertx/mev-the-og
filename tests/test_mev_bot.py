from src.mev_bot import MEVBot

def test_mev_bot_init_and_run(monkeypatch):
    # Setup a test config.yaml with dummy/testnet values first
    bot = MEVBot("config.yaml")
    assert bot.network in ["mainnet", "goerli", "sepolia"]
    assert bot.mode in ["test", "live"]
    # Monkeypatch kill switch to always be enabled for run()
    monkeypatch.setattr(bot.kill, "is_enabled", lambda: True)
    bot.run()
