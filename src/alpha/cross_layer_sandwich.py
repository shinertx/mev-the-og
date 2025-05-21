import logging
import time
from web3 import Web3

def decode_bridge_call(tx_input, dex_sig):
    # Look for target DEX signature in calldata (stub: implement proper ABI decoding)
    return dex_sig.lower() in tx_input.lower()

def mempool_watch_and_attack(w3, bridge_addr, dex_sig, poll_interval=2):
    logging.info("[XLS] Watching mempool for L1->L2 bridge calls...")
    pending_filter = w3.eth.filter('pending')
    while True:
        tx_hashes = pending_filter.get_new_entries()
        for txh in tx_hashes:
            try:
                tx = w3.eth.get_transaction(txh)
                if tx['to'] and tx['to'].lower() == bridge_addr.lower():
                    if decode_bridge_call(tx['input'], dex_sig):
                        logging.info(f"[XLS] Detected potential L2 swap via bridge: {tx['hash']}")
                        # TODO: Build/send frontrun/backrun L1 tx here
            except Exception as e:
                continue
        time.sleep(poll_interval)

def run_cross_layer_sandwich(config):
    w3 = Web3(Web3.HTTPProvider(config['rpc_urls']['mainnet']))
    bridge_addr = config['contracts']['arbitrum_bridge']
    dex_sig = config['contracts']['target_dex_sig']
    mempool_watch_and_attack(w3, bridge_addr, dex_sig)

# TEST HARNESS
def test_decode_bridge_call():
    sig = "0x12345678"
    input_data = "0xabcdef12345678"
    assert decode_bridge_call(input_data, sig) is True

if __name__ == "__main__":
    import yaml
    config = yaml.safe_load(open("../config.yaml"))
    run_cross_layer_sandwich(config)
