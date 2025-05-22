from web3 import Web3, EthereumTesterProvider


def test_gas_wars_and_reorg():
    provider = EthereumTesterProvider()
    w3 = Web3(provider)
    acct0 = w3.eth.accounts[0]
    acct1 = w3.eth.accounts[1]

    # Flood mempool with varying gas prices
    for i in range(10):
        tx = {
            'from': acct0,
            'to': acct1,
            'value': 1,
            'gas': 21000,
            'gasPrice': w3.to_wei(1 + i, 'gwei')
        }
        w3.eth.send_transaction(tx)

    snapshot = provider.ethereum_tester.take_snapshot()
    start_block = w3.eth.block_number
    w3.provider.make_request('evm_mine', [])
    provider.ethereum_tester.revert_to_snapshot(snapshot)
    assert w3.eth.block_number == start_block

