from src.alpha.flash_loan_liquidation import find_liquidation_targets

def test_find_liquidation_targets():
    targets = find_liquidation_targets()
    assert isinstance(targets, list)
    assert "account" in targets[0]
