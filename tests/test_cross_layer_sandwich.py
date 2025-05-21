from src.alpha.cross_layer_sandwich import decode_bridge_call

def test_decode_bridge_call():
    sig = "0x1234"
    input_data = "0x1111234abc"
    assert decode_bridge_call(input_data, sig)
