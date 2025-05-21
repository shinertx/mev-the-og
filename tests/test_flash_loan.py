from src.alpha.flash_loan import scan_flash_loan_opportunities

def test_flash_loan_opps():
    opp = scan_flash_loan_opportunities()
    assert isinstance(opp, dict) or opp is None
