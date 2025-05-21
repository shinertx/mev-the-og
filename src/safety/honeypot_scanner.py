import logging
from web3 import Web3

def is_honeypot_or_scam(web3: Web3, token_address: str) -> bool:
    try:
        code = web3.eth.get_code(token_address)
        # If bytecode is minimal or matches known scam patterns, abort
        if len(code) < 40:
            logging.warning(f"[SAFETY] Contract {token_address} is a likely honeypot (tiny code).")
            return True
        # Add more rules as needed (fee-on-transfer, proxy, blacklists, etc.)
    except Exception as e:
        logging.warning(f"[SAFETY] Error checking contract {token_address}: {e}")
        return True
    return False
