#!/usr/bin/env python
# coding: utf-8

"""
BinanceCoreClient
---------------------
This is the main module that integrates all sub-modules for:
- Proxy management
- Spot trading
- Margin trading
- Futures trading
- Public data management
- Utility functions (Utils)

Features:
- Centralized management of API keys, secrets, and configuration
- Flexible support for Binance Testnet and Mainnet
- Efficient session management with proxy support

Usage Example:
--------------
from binance_core_client import BinanceCoreClient

# Initialize client
client = BinanceCoreClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    proxy_list=[],
    testnet=True
)
"""

from proxy_manager import ProxyManager
from spot_trading import SpotTrading
from margin_trading import MarginTrading
from futures_trading import FuturesTrading
from public_data_manager import PublicDataManager
from utils import Utils


class BinanceCoreClient:
    def __init__(self, api_key, api_secret, proxy_list, testnet=False):
        """
        Initialize the Binance Core Client with API key, API secret, proxies, and testnet configuration.

        :param api_key:    Your Binance API key
        :param api_secret: Your Binance API secret
        :param proxy_list: List of proxy dicts (with address, port, username, password)
        :param testnet:    True => Use Binance Testnet for testing purposes
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        # Define Base URLs
        self.base_url_futures = "https://testnet.binancefuture.com" if testnet else "https://fapi.binance.com"
        self.base_url_spot = "https://testnet.binance.vision" if testnet else "https://api.binance.com"

        # Initialize proxy manager and session
        self.proxy_manager = ProxyManager(proxy_list)
        self.session = self.proxy_manager.initialize_session()

        # Initialize trading modules
        self.spot_trading = SpotTrading(api_key, api_secret, self.session, self.base_url_spot)
        self.margin_trading = MarginTrading(api_key, api_secret, self.session, self.base_url_spot)
        self.futures_trading = FuturesTrading(api_key, api_secret, self.session, self.base_url_futures)

        # Initialize public data manager
        self.public_data = PublicDataManager()

        # Utilities
        self.utils = Utils()

    def get_base_urls(self):
        """
        Get the base URLs for the current configuration.

        :return: A dictionary containing the Spot and Futures base URLs
        """
        return {
            "spot_base_url": self.base_url_spot,
            "futures_base_url": self.base_url_futures
        }
