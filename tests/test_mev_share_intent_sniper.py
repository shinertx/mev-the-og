from src.alpha.mev_share_intent_sniper import predict_swap_target

def test_predict_swap_target():
    assert predict_swap_target({"from_token": "USDC"}) in ["USDC", "WETH", "DAI"]
