import argparse
import logging
import sys
import os
from src.mev_bot import MEVBot

sys.path.append(os.path.join(os.path.dirname(__file__), 'src/alpha'))

def main():
    parser = argparse.ArgumentParser(description="MEV The OG – main entry")
    parser.add_argument("--mode", type=str, default=None, help="test or live")
    parser.add_argument("--alpha", type=str, default=None, help="alpha module: cross_chain, l2_sandwich, bridge_games")
    args = parser.parse_args()
    # Setup logging
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(filename='logs/mev_og.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    # Config
    from src.utils import load_config
    config = load_config("config.yaml")
    if args.mode:
        config['mode'] = args.mode
    if args.alpha == "cross_chain":
        from src.alpha.cross_chain_arb import run_cross_chain_arb
        run_cross_chain_arb(config)
    elif args.alpha == "l2_sandwich":
        from src.alpha.l2_sandwich import simulate_l2_sandwich
        simulate_l2_sandwich(config)
    elif args.alpha == "bridge_games":
        from src.alpha.bridge_games import run_bridge_games
        run_bridge_games(config)
    else:
        bot = MEVBot()
        bot.run()

if __name__ == "__main__":
    main()
