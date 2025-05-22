# src/services/blockchain_service.py

import logging
from typing import Any, Callable, Dict, List, Optional
from tenacity import retry, wait_random_exponential, stop_after_attempt
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.providers.websocket import WebsocketProvider
from web3.contract import ContractEvent
from web3._utils.filters import LogFilter

logger = logging.getLogger(__name__)


class BlockchainService:
    def __init__(self, config):
        self.network = config.network
        self.rpc_url = config.rpc_urls.root.get(self.network)
        self.wss_url = config.wss_urls.root.get(self.network)

        if not self.rpc_url:
            raise ValueError(f"No HTTP RPC URL configured for network: {self.network}")

        self.http_web3 = Web3(HTTPProvider(self.rpc_url))
        self.wss_web3 = Web3(WebsocketProvider(self.wss_url)) if self.wss_url else None

        logger.info(f"[BlockchainService] Initialized for network: {self.network}")
        logger.info(f"HTTP RPC: {self.rpc_url}")
        logger.info(f"WSS RPC: {self.wss_url or 'Not configured'}")

    def is_http_connected(self) -> bool:
        return self.http_web3.is_connected()

    def is_wss_connected(self) -> bool:
        return self.wss_web3.is_connected() if self.wss_web3 else False

    def get_http_web3(self) -> Web3:
        if not self.is_http_connected():
            logger.warning("[BlockchainService] HTTP disconnected, reconnecting...")
            self.http_web3 = Web3(HTTPProvider(self.rpc_url))
        return self.http_web3

    def get_wss_web3(self) -> Optional[Web3]:
        if self.wss_web3 and not self.is_wss_connected():
            logger.warning("[BlockchainService] WSS disconnected, reconnecting...")
            self.wss_web3 = Web3(WebsocketProvider(self.wss_url))
        return self.wss_web3

    # --- Read-only operations (via HTTP) ---

    def get_current_block_number(self) -> Optional[int]:
        try:
            return self.get_http_web3().eth.block_number
        except Exception as e:
            logger.error(f"[get_current_block_number] Error: {e}")
            return None

    def get_balance(self, address: str, block_identifier: Any = "latest") -> Optional[int]:
        try:
            return self.get_http_web3().eth.get_balance(address, block_identifier)
        except Exception as e:
            logger.error(f"[get_balance] Error for {address}: {e}")
            return None

    def get_block(self, block_identifier: Any, full_transactions: bool = False) -> Optional[Dict[str, Any]]:
        try:
            return self.get_http_web3().eth.get_block(block_identifier, full_transactions)
        except Exception as e:
            logger.error(f"[get_block] Error for {block_identifier}: {e}")
            return None

    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        try:
            return self.get_http_web3().eth.get_transaction(tx_hash)
        except Exception as e:
            logger.error(f"[get_transaction] Error: {e}")
            return None

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        try:
            return self.get_http_web3().eth.get_transaction_receipt(tx_hash)
        except Exception as e:
            logger.error(f"[get_transaction_receipt] Error: {e}")
            return None

    def get_chain_id(self) -> Optional[int]:
        try:
            return self.get_http_web3().eth.chain_id
        except Exception as e:
            logger.error(f"[get_chain_id] Error: {e}")
            return None

    def get_gas_price(self) -> Optional[int]:
        try:
            return self.get_http_web3().eth.gas_price
        except Exception as e:
            logger.error(f"[get_gas_price] Error: {e}")
            return None

    def eth_call(self, transaction: Dict[str, Any], block_identifier: Any = "latest") -> Optional[bytes]:
        try:
            return self.get_http_web3().eth.call(transaction, block_identifier=block_identifier)
        except Exception as e:
            logger.error(f"[eth_call] Error: {e}")
            return None

    # --- Event Subscription (WSS) ---

    def subscribe_to_new_blocks(self, callback: Callable[[Dict[str, Any]], None]) -> Optional[Any]:
        try:
            w3 = self.get_wss_web3()
            if w3:
                sub = w3.eth.subscribe("newHeads", callback=callback)
                logger.info("[subscribe_to_new_blocks] Subscribed to new blocks.")
                return sub
        except Exception as e:
            logger.error(f"[subscribe_to_new_blocks] Error: {e}")
        return None

    def subscribe_to_pending_transactions(self, callback: Callable[[str], None]) -> Optional[Any]:
        try:
            w3 = self.get_wss_web3()
            if w3:
                sub = w3.eth.subscribe("pendingTransactions", callback=callback)
                logger.info("[subscribe_to_pending_transactions] Subscribed to pending transactions.")
                return sub
        except Exception as e:
            logger.error(f"[subscribe_to_pending_transactions] Error: {e}")
        return None

    def create_contract_event_filter(
        self,
        contract_address: str,
        abi: List[Dict[str, Any]],
        event_name: str,
        argument_filters: Optional[Dict[str, Any]] = None,
        from_block: Any = "latest",
        to_block: Any = "latest",
    ) -> Optional[LogFilter]:
        try:
            contract = self.get_http_web3().eth.contract(address=contract_address, abi=abi)
            event: ContractEvent = getattr(contract.events, event_name)
            return event.create_filter(
                fromBlock=from_block,
                toBlock=to_block,
                argument_filters=argument_filters or {}
            )
        except Exception as e:
            logger.error(f"[create_contract_event_filter] Error: {e}")
            return None

    def get_filter_logs(self, log_filter: LogFilter) -> Optional[List[Dict[str, Any]]]:
        try:
            return log_filter.get_all_entries()
        except Exception as e:
            logger.error(f"[get_filter_logs] Error: {e}")
            return None

    def unsubscribe(self, subscription_id: Any) -> bool:
        try:
            w3 = self.get_wss_web3()
            if w3:
                return w3.eth.unsubscribe(subscription_id)
        except Exception as e:
            logger.error(f"[unsubscribe] Error: {e}")
        return False

