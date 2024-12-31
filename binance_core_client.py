"""
BinanceCoreClient
---------------------
This is the main module that integrates all sub-modules for:
- Proxy management
- Spot trading
- Margin trading
- Futures trading
"""

from proxy_manager import ProxyManager
from spot_trading import SpotTrading
from margin_trading import MarginTrading
from futures_trading import FuturesTrading
from utils import Utils

class BinanceCoreClient:
    def __init__(self, api_key, api_secret, proxy_list, testnet=False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.proxy_manager = ProxyManager(proxy_list)
        self.spot_trading = SpotTrading(api_key, api_secret)
        self.margin_trading = MarginTrading(api_key, api_secret)
        self.futures_trading = FuturesTrading(api_key, api_secret)
