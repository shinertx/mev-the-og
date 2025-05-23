import logging
import time
from src.ai.alpha_scraper import run_alpha_scraper
from src.ai.ai_orchestrator import AIOrchestrator
from src.logger import log_event

class EdgeWatcher:
    def __init__(self, orchestrator: AIOrchestrator):
        self.orchestrator = orchestrator

    def run_once(self):
        # 1. Scrape public feeds for new leaks
        summary = run_alpha_scraper()
        log_event(logging.INFO, f"Alpha summary:\n{summary}", "edge_watcher")

        # 2. Let LLM analyze and propose new module/config/contract upgrades
        ai_reco = self.orchestrator.openai_analyze_logs(summary)
        log_event(logging.INFO, f"Edge proposal:\n{ai_reco}", "edge_watcher")

        # 3. Human-in-the-loop: notify founder for approval, or auto-prompt orchestrator to test module/edge
        # (Optional: Plug this into Discord/Telegram alert for approval)
        print("[EdgeWatcher] New alpha recommendation:")
        print(ai_reco)
        # You can add: self.orchestrator.run_module('new_module_from_alpha')

    def run_loop(self, interval=900):
        while True:
            self.run_once()
            time.sleep(interval)

if __name__ == "__main__":
    from src.utils import load_config
    from src.logger import setup_logging
    cfg = load_config("config.yaml")
    setup_logging(cfg)
    ew = EdgeWatcher(AIOrchestrator())
    ew.run_loop()
