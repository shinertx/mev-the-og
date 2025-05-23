"""Lightweight operator dashboard."""

import time
from dataclasses import dataclass, asdict
from fastapi import FastAPI
import uvicorn


@dataclass
class DashboardState:
    risk: float = 0.0
    capital_at_risk: float = 0.0
    kill_switch_state: str = "OK"
    alpha_performance: dict = None
    notifier_health: dict = None
    last_config_event: str = "None"
    heartbeat: float = time.time()
    panic: bool = False


state = DashboardState(alpha_performance={}, notifier_health={})


def launch_dashboard(port: int = 8501, state_obj: DashboardState = state):
    """Launch the FastAPI dashboard exposing internal state."""

    app = FastAPI()

    @app.get("/")
    def status():
        return asdict(state_obj)

    @app.post("/override")
    def override_kill_switch():
        state_obj.kill_switch_state = "MANUAL_OVERRIDE"
        state_obj.panic = False
        return {"status": "override engaged"}

    uvicorn.run(app, host="0.0.0.0", port=port)
