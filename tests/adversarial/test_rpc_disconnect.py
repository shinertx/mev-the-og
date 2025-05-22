from types import SimpleNamespace
from src.services.blockchain_service import BlockchainService


def test_rpc_disconnect_recovery(monkeypatch):
    config = SimpleNamespace(
        network="mainnet",
        rpc_urls=SimpleNamespace(root={"mainnet": "http://localhost:8545"}),
        wss_urls=SimpleNamespace(root={"mainnet": None})
    )
    service = BlockchainService(config)

    call_count = {"n": 0}

    def fake_is_connected():
        call_count["n"] += 1
        return call_count["n"] > 1

    monkeypatch.setattr(service.http_web3, "is_connected", fake_is_connected)
    _ = service.get_current_block_number()
    assert call_count["n"] >= 1

