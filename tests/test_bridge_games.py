from src.alpha.bridge_games import run_bridge_games
from src.utils import load_config

def test_run_bridge_games():
    config = load_config("config.example.yaml")
    run_bridge_games(config)
    assert True  # If no exceptions, test passes
