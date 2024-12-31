"""
Spot Trading Module
---------------------
This module provides functions for Binance Spot trading, including:
- Placing spot orders (market, limit, and limit-maker)
- Canceling individual or all spot orders
- Fetching open spot orders
"""

import logging
import requests
from utils import Utils

class SpotTrading:
    def __init__(self, api_key, api_secret, session, base_url_spot):
        """
        Initializes the SpotTrading module.

        :param api_key:       Your Binance API key
        :param api_secret:    Your Binance API secret
        :param session:       A pre-configured requests.Session with proxy support
        :param base_url_spot: Base URL for Binance Spot trading
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = session
        self.base_url_spot = base_url_spot
        self.logger = logging.getLogger(__name__)

    def place_spot_order(self, symbol: str, side: str, order_type: str, quantity: str, 
                         price: str = None, time_in_force: str = "GTC") -> dict:
        """
        Places a spot order (MARKET, LIMIT, LIMIT_MAKER).

        :param symbol:       e.g. 'BTCUSDT'
        :param side:         'BUY' or 'SELL'
        :param order_type:   'MARKET', 'LIMIT', 'LIMIT_MAKER'
        :param quantity:     Order quantity (as string)
        :param price:        Limit price (only needed for LIMIT, LIMIT_MAKER)
        :param time_in_force 'GTC', 'FOK', 'IOC' (relevant for LIMIT)
        :return: Response from Binance API
        """
        try:
            endpoint = "/api/v3/order"
            url = f'{self.base_url_spot}{endpoint}'
            timestamp = Utils.get_current_timestamp_ms()

            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'timestamp': timestamp
            }

            if order_type == 'LIMIT':
                params.update({'timeInForce': time_in_force, 'price': price, 'quantity': quantity})
            elif order_type == 'LIMIT_MAKER':
                params.update({'price': price, 'quantity': quantity})
            elif order_type == 'MARKET':
                params['quantity'] = quantity

            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = {'X-MBX-APIKEY': self.api_key}

            response = self.session.post(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"Spot order placed: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Error placing spot order for {symbol}: {e}")
            return {}

    def cancel_spot_order(self, symbol: str, order_id: str) -> dict:
        """
        Cancels an existing spot order by order ID.

        :param symbol:   Trading pair (e.g. 'BTCUSDT')
        :param order_id: Binance order ID
        :return: Response from Binance API
        """
        try:
            endpoint = "/api/v3/order"
            url = f'{self.base_url_spot}{endpoint}'
            timestamp = Utils.get_current_timestamp_ms()
            params = {'symbol': symbol, 'orderId': order_id, 'timestamp': timestamp}

            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = {'X-MBX-APIKEY': self.api_key}

            response = self.session.delete(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"Spot order canceled: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Error canceling spot order ({order_id}) for {symbol}: {e}")
            return {}

    def cancel_all_spot_orders(self, symbol: str) -> dict:
        """
        Cancels all open spot orders for a given symbol.

        :param symbol: Trading pair (e.g. 'BTCUSDT')
        :return: List of canceled orders
        """
        try:
            endpoint = "/api/v3/openOrders"
            url = f'{self.base_url_spot}{endpoint}'
            timestamp = Utils.get_current_timestamp_ms()
            params = {'symbol': symbol, 'timestamp': timestamp}

            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = {'X-MBX-APIKEY': self.api_key}

            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            open_orders = response.json()

            for order in open_orders:
                self.cancel_spot_order(symbol, order['orderId'])

            self.logger.info(f"All open spot orders for {symbol} canceled.")
            return {"cancelled_orders": open_orders}
        except Exception as e:
            self.logger.error(f"Error canceling all spot orders for {symbol}: {e}")
            return {}
