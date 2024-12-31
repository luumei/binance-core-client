"""
Margin Trading Module
---------------------
This module provides functionality for Binance Margin trading, including:
- Fetching margin balance (isolated and cross)
- Placing margin orders (standard and OCO)
- Canceling margin orders (single and all)
- Repaying margin loans
- Checking margin loan limits
- Fetching margin asset details
"""

import logging
import requests
from utils import Utils

class MarginTrading:
    def __init__(self, api_key, api_secret, session, base_url_spot):
        """
        Initializes the MarginTrading module.

        :param api_key:       Your Binance API key
        :param api_secret:    Your Binance API secret
        :param session:       A pre-configured requests.Session with proxy support
        :param base_url_spot: Base URL for Binance Spot and Margin trading
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = session
        self.base_url_spot = base_url_spot
        self.logger = logging.getLogger(__name__)

    def fetch_margin_balance(self, is_isolated: bool = True, symbol: str = None) -> dict:
        """
        Fetches the margin balance (isolated or cross).

        :param is_isolated: True => isolated margin (requires `symbol`)
                            False => cross margin
        :param symbol:      e.g. 'BTCUSDT' (required if is_isolated=True)
        """
        if not self.session:
            return {}

        try:
            endpoint = "/sapi/v1/margin/isolated/account" if is_isolated else "/sapi/v1/margin/account"
            url = f'{self.base_url_spot}{endpoint}'
            timestamp = Utils.get_current_timestamp_ms()

            params = {'timestamp': timestamp}
            if is_isolated:
                if not symbol:
                    self.logger.error("Please provide a symbol (e.g. 'BTCUSDT') for isolated margin.")
                    return {}
                params['symbols'] = symbol

            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = {'X-MBX-APIKEY': self.api_key}

            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching margin balance (isolated={is_isolated}): {e}")
            return {}

    def place_margin_order(self, symbol: str, side: str, order_type: str, quantity: str,
                           price: str = None, is_isolated: bool = True, side_effect_type: str = 'NO_SIDE_EFFECT') -> dict:
        """
        Places a margin order (cross or isolated).

        :param symbol:          e.g. 'BTCUSDT'
        :param side:            'BUY' or 'SELL'
        :param order_type:      'MARKET' or 'LIMIT'
        :param quantity:        Order quantity (string)
        :param price:           Limit price (only needed for LIMIT)
        :param is_isolated:     True => isolated margin, False => cross margin
        :param side_effect_type e.g. 'MARGIN_BUY', 'AUTO_REPAY', 'NO_SIDE_EFFECT'
        """
        if not self.session:
            return {}

        try:
            endpoint = "/sapi/v1/margin/order"
            url = f'{self.base_url_spot}{endpoint}'
            timestamp = Utils.get_current_timestamp_ms()

            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
                'sideEffectType': side_effect_type,
                'timestamp': timestamp,
                'isIsolated': 'TRUE' if is_isolated else 'FALSE'
            }

            if order_type == 'LIMIT' and price is not None:
                params['price'] = price

            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = {'X-MBX-APIKEY': self.api_key}

            response = self.session.post(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error placing margin order (isIsolated={is_isolated}): {e}")
            return {}

    def repay_margin_loan(self, symbol: str, asset: str, amount: float, is_isolated: bool = True) -> dict:
        """
        Repays a margin loan (isolated or cross).

        :param symbol:      e.g. 'BTCUSDT'
        :param asset:       Asset to repay (e.g. 'BTC')
        :param amount:      Amount to repay
        :param is_isolated: True => isolated margin, False => cross margin
        """
        if not self.session:
            return {}

        try:
            endpoint = "/sapi/v1/margin/repay"
            url = f"{self.base_url_spot}{endpoint}"
            timestamp = Utils.get_current_timestamp_ms()

            params = {
                'symbol': symbol,
                'asset': asset,
                'amount': str(amount),
                'timestamp': timestamp,
                'isIsolated': 'TRUE' if is_isolated else 'FALSE'
            }

            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = {'X-MBX-APIKEY': self.api_key}

            response = self.session.post(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error repaying margin loan: {e}")
            return {}
