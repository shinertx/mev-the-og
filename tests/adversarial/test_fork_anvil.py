import subprocess
import shutil
import time
import pytest
from web3 import Web3


def test_mainnet_fork_with_anvil():
    anvil_bin = shutil.which("anvil")
    if not anvil_bin:
        pytest.skip("anvil not installed")
    proc = subprocess.Popen([anvil_bin, "--fork-url", "https://eth-mainnet.g.alchemy.com/v2/demo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        for _ in range(20):
            if w3.is_connected():
                break
            time.sleep(0.5)
        assert w3.is_connected()
        assert w3.eth.block_number >= 0
    finally:
        proc.terminate()
        proc.wait()
