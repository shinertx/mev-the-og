import logging
import time
from src.kill_switch import get_kill_switch
from src.risk_manager import RiskManager

def scan_nftfi_arbs():
    logging.info("[Alpha][NFTfi] Scanning for NFT loan/arbitrage...")
    return {"platform": "NFTfi", "loan_id": 42, "expected_profit": 0.2}

def execute_nftfi_arb(config, opportunity):
    logging.info(f"[Alpha][NFTfi] Executing NFTfi arb on loan {opportunity['loan_id']}")
    time.sleep(1)
    pnl = opportunity.get("expected_profit", 0)
    kill = get_kill_switch()
    rm: RiskManager = kill.risk_manager  # type: ignore[attr-defined]
    rm.update_drawdown(pnl)
    kill.update_pnl(pnl)
    return True

def run_nftfi(config):
    opp = scan_nftfi_arbs()
    if opp:
        if config["mode"] == "test":
            logging.info(f"[SIM][NFTfi] Would execute: {opp}")
        else:
            execute_nftfi_arb(config, opp)

if __name__ == "__main__":
    import yaml
    config = yaml.safe_load(open("config.yaml"))
    run_nftfi(config)
