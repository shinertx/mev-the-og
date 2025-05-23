import time
import logging
import importlib
import openai
import os
from src.utils import load_config
from src.safety.config_monitor import ConfigMonitor

OPENAI_MODEL = "gpt-4o"  # Or use "gpt-3.5-turbo" if needed

class AIOrchestrator:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = load_config(config_path)
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        self.monitor = ConfigMonitor(config_path, ".env", notifier_cfg=self.config.get("notifier", {}))
        self.alpha_modules = [
            "cross_chain_arb",
            "l2_sandwich",
            "bridge_games",
            "mev_share",
            "flash_loan",
            "liquidation",
            "nftfi",
            "edge_bridge_arb"
        ]
        self.module_results = {}

    def run_module(self, module_name, mode="test"):
        try:
            logging.info(f"[AIOrchestrator] Running {module_name} in {mode} mode")
            mod = importlib.import_module(f"src.alpha.{module_name}")
            run_func = getattr(mod, f"run_{module_name}", None)
            if run_func:
                run_func(self.config)
                self.module_results[module_name] = "success"
            else:
                logging.warning(f"[AIOrchestrator] No run_{module_name} function in {module_name}.py")
                self.module_results[module_name] = "missing_run_func"
        except Exception as e:
            logging.warning(f"[AIOrchestrator] Module {module_name} failed: {e}")
            self.module_results[module_name] = f"fail: {e}"

    def get_logs(self, log_path="logs/mev_og.log", n=100):
        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
                return "".join(lines[-n:])
        except Exception as e:
            return f"Failed to read logs: {e}"

    def openai_analyze_logs(self, logs):
        prompt = (
            "You are a world-class adversarial DeFi/MEV quant. "
            "Given these bot logs, identify any new arbitrage/MEV opportunities, vulnerabilities, and suggest new edges or parameter tweaks "
            "that would maximize edge or reduce risk. Output only actionable recommendations and code/config edits if relevant.\n\n"
            "LOGS:\n" + logs
        )
        try:
            resp = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a world-class MEV quant research agent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=700,
            )
            return resp["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[AIOrchestrator] OpenAI analysis failed: {e}"

    def main_loop(self, interval_sec=600):
        logging.info("[AIOrchestrator] Starting perpetual alpha coordination loop.")
        while True:
            self.monitor.check()
            for module in self.alpha_modules:
                self.run_module(module, mode=self.config.get("mode", "test"))
                time.sleep(3)  # Stagger modules

            logs = self.get_logs()
            ai_recommendations = self.openai_analyze_logs(logs)
            logging.info(f"[AIOrchestrator][OpenAI] Alpha/edge recommendations:\n{ai_recommendations}")

            # Optional: Auto-update config/params based on LLM suggestions (require human-in-the-loop for prod safety)
            if "PROMOTE TO LIVE" in ai_recommendations and self.config.get("mode") != "live":
                logging.info("[AIOrchestrator] OpenAI recommends switching to live mode! (manual approval required)")
                # (Optional) Hook for notification/approval here

            # Sleep until next cycle
            time.sleep(interval_sec)

if __name__ == "__main__":
    import sys
    logging.basicConfig(filename="logs/mev_og.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    orchestrator = AIOrchestrator()
    orchestrator.main_loop()
