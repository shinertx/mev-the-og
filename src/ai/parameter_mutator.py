import random
import logging
from typing import Dict, Any

from src.logger import log_event


class ParameterMutator:
    """Live parameter mutation helper."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        ai_cfg = config.get("ai", {})
        self.mutation_freq = ai_cfg.get("mutation_frequency", 10)
        self.counter = 0

    def maybe_mutate(self, module_name: str) -> bool:
        """Mutate numeric parameters if frequency threshold reached."""
        self.counter += 1
        if self.counter % self.mutation_freq != 0:
            return False
        params = (
            self.config.get("alpha", {})
            .get("params", {})
            .get(module_name, {})
        )
        mutated = {}
        for k, v in params.items():
            if isinstance(v, (int, float)):
                delta = random.uniform(-0.1, 0.1) * (abs(v) if v != 0 else 1)
                new_val = type(v)(v + delta)
                params[k] = new_val
                mutated[k] = new_val
        if mutated:
            log_event(logging.INFO, f"Mutated params {mutated}", f"mutator:{module_name}")
            return True
        return False
