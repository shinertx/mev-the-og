from src.alpha.liquidation import scan_liquidation_targets

def test_liquidation_targets():
    target = scan_liquidation_targets()
    assert isinstance(target, dict) or target is None
