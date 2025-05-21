from src.alpha.nftfi import scan_nftfi_arbs

def test_nftfi_arbs():
    arb = scan_nftfi_arbs()
    assert isinstance(arb, dict) or arb is None
