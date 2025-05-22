import pytest
from src.alpha.cross_chain_arb import CrossChainArb, SimulatedBridge

def test_bridge_failure_handling(monkeypatch):
    bot = CrossChainArb("config.example.yaml")
    bot.get_price = lambda w, r, t, a: 3500 if w == bot.web3_mainnet else 3525
    # Simulate bridge always failing
    bot.bridge = SimulatedBridge(fail_rate=1.0)
    opp = bot.detect_opportunity()
    assert opp is not None
    result = bot.execute_arb(opp)
    assert not result  # Should abort on bridge failure

def test_gas_spike(monkeypatch):
    bot = CrossChainArb("config.example.yaml")
    bot.get_price = lambda w, r, t, a: 3500 if w == bot.web3_mainnet else 3525
    # Patch gas estimation to simulate massive gas cost
    monkeypatch.setattr(bot.web3_mainnet.eth, "estimate_gas", lambda tx: 10_000_000)
    opp = bot.detect_opportunity()
    assert opp is None or opp["net_profit_usd"] < 0  # Should not trigger trade if unprofitable
