import argparse
import logging
import sys
import os

from src.mev_bot import MEVBot
from src.utils import load_config

sys.path.append(os.path.join(os.path.dirname(__file__), 'src/alpha'))

def main():
    parser = argparse.ArgumentParser(description="MEV The OG – main entry")
    parser.add_argument("--mode", type=str, default=None, help="test or live")
    parser.add_argument("--alpha", type=str, default=None, help="alpha module: cross_chain, l2_sandwich, bridge_games, mev_share, flash_loan, liquidation, nftfi")
    parser.add_argument("--dashboard", action="store_true", help="launch dashboard")
    args = parser.parse_args()

    # Setup logging
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(filename='logs/mev_og.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    config = load_config("config.yaml")
    if args.mode:
        config['mode'] = args.mode

    if args.dashboard:
        from src.dashboard import launch_dashboard
        port = config.get('dashboard', {}).get('port', 8501)
        launch_dashboard(port)
        return

    alpha_map = {
        "cross_chain": "cross_chain_arb",
        "l2_sandwich": "l2_sandwich",
        "bridge_games": "bridge_games",
        "mev_share": "mev_share",
        "flash_loan": "flash_loan",
        "liquidation": "liquidation",
        "nftfi": "nftfi",
    }

    if args.alpha and args.alpha in alpha_map:
        mod = __import__(f"src.alpha.{alpha_map[args.alpha]}", fromlist=["run_"+alpha_map[args.alpha]])
        getattr(mod, f"run_{alpha_map[args.alpha]}")(config)
    else:
        bot = MEVBot()
        bot.run()

if __name__ == "__main__":
    main()
