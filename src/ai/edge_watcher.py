import logging
import time
from src.ai.alpha_scraper import run_alpha_scraper
from src.ai.ai_orchestrator import AIOrchestrator

class EdgeWatcher:
    def __init__(self, orchestrator: AIOrchestrator):
        self.orchestrator = orchestrator

    def run_once(self):
        # 1. Scrape public feeds for new leaks
        summary = run_alpha_scraper()
        logging.info(f"[EdgeWatcher] Alpha summary:\n{summary}")

        # 2. Let LLM analyze and propose new module/config/contract upgrades
        ai_reco = self.orchestrator.openai_analyze_logs(summary)
        logging.info(f"[EdgeWatcher][LLM] Edge proposal:\n{ai_reco}")

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
    import logging
    logging.basicConfig(filename="logs/mev_og.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    from src.ai.ai_orchestrator import AIOrchestrator
    ew = EdgeWatcher(AIOrchestrator())
    ew.run_loop()
