from src.alpha.cross_layer_sandwich import decode_bridge_call


def test_cross_domain_replay_detection():
    sig = "0xabcdefff"
    call = "0x0000abcdefff0000"
    assert decode_bridge_call(call, sig)

