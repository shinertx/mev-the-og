import time
import logging
import requests
from web3 import Web3

DEX_APIS = {
    "mainnet": "https://api.dexscreener.io/latest/dex/tokens/ETH",
    "arbitrum": "https://api.dexscreener.io/latest/dex/tokens/ETH?chain=arbitrum",
    "optimism": "https://api.dexscreener.io/latest/dex/tokens/ETH?chain=optimism",
    "base": "https://api.dexscreener.io/latest/dex/tokens/ETH?chain=base"
}

CROSS_CHAIN_PAIRS = [
    ("mainnet", "arbitrum"),
    ("mainnet", "optimism"),
    ("arbitrum", "base"),
    ("optimism", "base"),
]

def get_price(chain):
    try:
        r = requests.get(DEX_APIS[chain])
        data = r.json()
        return float(data['pairs'][0]['priceUsd'])
    except Exception as e:
        logging.warning(f"Failed to get price for {chain}: {e}")
        return None

def cross_chain_opps(slippage_bps=50, min_profit_usd=1.0):
    prices = {chain: get_price(chain) for chain in DEX_APIS}
    opps = []
    for a, b in CROSS_CHAIN_PAIRS:
        if prices[a] and prices[b]:
            diff = prices[a] - prices[b]
            if abs(diff) > min_profit_usd:
                direction = f"{a}->{b}" if diff > 0 else f"{b}->{a}"
                opps.append({
                    "direction": direction,
                    "profit": abs(diff),
                    "from": a if diff > 0 else b,
                    "to": b if diff > 0 else a,
                    "price_from": prices[a] if diff > 0 else prices[b],
                    "price_to": prices[b] if diff > 0 else prices[a]
                })
    return opps

def execute_arbitrage(from_chain, to_chain, config, trade_amount=100):
    logging.info(f"[ARBITRAGE] Executing {from_chain}->{to_chain} trade for {trade_amount} USD.")
    time.sleep(2)
    return True

def run_cross_chain_arb(config):
    logging.info("[Alpha] Starting Cross-Chain Arbitrage Scanner.")
    opps = cross_chain_opps(slippage_bps=config.get('slippage_bps',50), min_profit_usd=1.0)
    for opp in opps:
        logging.info(f"[Alpha] Found opportunity: {opp}")
        if config['mode'] == 'test':
            logging.info("[SIM] Would execute arbitrage trade: %s", opp)
        else:
            execute_arbitrage(opp['from'], opp['to'], config, config['trade_amount_usd'])

if __name__ == "__main__":
    import yaml
    config = yaml.safe_load(open("config.yaml"))
    run_cross_chain_arb(config)
