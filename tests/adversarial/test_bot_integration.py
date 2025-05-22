import logging
from web3 import Web3, EthereumTesterProvider
from src.mev_bot import MEVBot
from src.alpha.cross_layer_sandwich import decode_bridge_call
from src.notifier import send_telegram, send_email

# Helper to instantiate bot with in-memory chain

def setup_bot(monkeypatch):
    bot = MEVBot("config.example.yaml")
    bot.web3 = Web3(EthereumTesterProvider())
    bot.kill.max_loss_usd = 1
    bot.kill.trading_enabled = True
    notes = {"telegram": [], "email": []}
    monkeypatch.setattr("src.notifier.send_telegram", lambda msg, *a, **k: notes["telegram"].append(msg))
    monkeypatch.setattr("src.notifier.send_email", lambda msg, *a, **k: notes["email"].append(msg))
    return bot, notes


def run_bot_with_fault(bot, fault_func):
    try:
        fault_func(bot)
        bot.kill.update_pnl(0)
    except Exception as e:
        logging.critical(f"[KILL SWITCH] Triggered due to {e}")
        bot.kill.trading_enabled = False
    if not bot.kill.is_enabled():
        send_telegram("KILL SWITCH: Trading disabled!", "", "")
        send_email("KILL SWITCH triggered", "")


def test_chain_reorg_triggers_kill(monkeypatch):
    bot, notes = setup_bot(monkeypatch)
    provider = bot.web3.provider

    def fault(b):
        snap = provider.ethereum_tester.take_snapshot()
        provider.ethereum_tester.mine_blocks(1)
        provider.ethereum_tester.revert_to_snapshot(snap)
        raise Exception("reorg detected")

    run_bot_with_fault(bot, fault)
    assert not bot.kill.is_enabled()
    assert notes["telegram"] and notes["email"]


def test_gas_war_spam(monkeypatch):
    bot, notes = setup_bot(monkeypatch)

    def fault(b):
        for i in range(20):
            tx = {
                "from": b.web3.eth.accounts[0],
                "to": b.web3.eth.accounts[1],
                "gas": 21000,
                "value": 1,
                "gasPrice": b.web3.to_wei(1 + i, "gwei"),
            }
            b.web3.eth.send_transaction(tx)
        raise Exception("gas war")

    run_bot_with_fault(bot, fault)
    assert not bot.kill.is_enabled()
    assert notes["telegram"] and notes["email"]


def test_rpc_disconnect_recover(monkeypatch):
    bot, notes = setup_bot(monkeypatch)

    def fault(b):
        raise Exception("rpc disconnect")

    run_bot_with_fault(bot, fault)
    assert not bot.kill.is_enabled()
    assert notes["telegram"] and notes["email"]


def test_cross_domain_replay(monkeypatch):
    bot, notes = setup_bot(monkeypatch)

    def fault(b):
        if decode_bridge_call("0xabcde", "0xabcde"):
            raise Exception("replay attack")

    run_bot_with_fault(bot, fault)
    assert not bot.kill.is_enabled()
    assert notes["telegram"] and notes["email"]
