from src.mev_bot import MEVBot

def test_init_and_run():
    bot = MEVBot("config.yaml")
    assert bot.network in ["mainnet", "goerli", "sepolia"]
    bot.run()
