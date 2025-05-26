from src.alpha.l2_sandwich import simulate_l2_sandwich
from src.utils import load_config

def test_simulate_l2_sandwich():
    config = load_config("config.example.yaml")
    simulate_l2_sandwich(config)
    assert True  # If no exceptions, test passes

def run_l2_sandwich(config):
    simulate_l2_sandwich(config)
