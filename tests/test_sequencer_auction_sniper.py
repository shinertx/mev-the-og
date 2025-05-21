from src.alpha.sequencer_auction_sniper import estimate_mev_for_next_block

def test_estimate_mev_for_next_block():
    assert estimate_mev_for_next_block() >= 0
