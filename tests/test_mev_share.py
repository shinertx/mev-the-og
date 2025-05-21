from src.alpha.mev_share import get_mev_share_opportunities

def test_mev_share():
    resp = get_mev_share_opportunities()
    assert resp is None or isinstance(resp, dict) or isinstance(resp, list)
