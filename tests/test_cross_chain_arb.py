from src.alpha.cross_chain_arb import cross_chain_opps

def test_cross_chain_opps():
    opps = cross_chain_opps(slippage_bps=50, min_profit_usd=0.5)
    assert isinstance(opps, list)
