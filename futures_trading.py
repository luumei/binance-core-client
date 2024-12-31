"""
Futures Trading Module
---------------------
This module provides functions for Binance Futures trading, including:
- Placing futures orders
- Setting leverage for positions
- Fetching account and position details
- Managing margin type
- Fetching all open positions
"""

import logging
from utils import Utils


class FuturesTrading:
    def __init__(self, api_key, api_secret, session, base_url_futures):
        """
        Initializes the FuturesTrading module.

        :param api_key:         Your Binance API key
        :param api_secret:      Your Binance API secret
        :param session:         A pre-configured requests.Session with proxy support
        :param base_url_futures: Base URL for Binance Futures trading
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = session
        self.base_url_futures = base_url_futures
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------------
    # Account and Position Methods
    # ------------------------------------------------------------------------

    def get_futures_exchange_info(self) -> dict:
        """
        Fetches exchange info (symbols, trading rules) for the Futures market.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v1/exchangeInfo"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching Futures exchange info: {e}")
            return None

    def check_futures_balance(self) -> dict:
        """
        Checks the Futures account balance and positions.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v2/account"
            timestamp = Utils.get_current_timestamp_ms()
            params = {'timestamp': timestamp}
            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error checking Futures balance: {e}")
            return None

    def get_futures_position_information(self, symbol: str) -> dict:
        """
        Fetches information about open Futures positions for a symbol.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v2/positionRisk"
            timestamp = Utils.get_current_timestamp_ms()
            params = {'symbol': symbol, 'timestamp': timestamp}
            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching Futures position info: {e}")
            return None

    def get_all_open_futures_positions(self) -> dict:
        """
        Fetches all open Futures positions on the account.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v2/positionRisk"
            timestamp = Utils.get_current_timestamp_ms()
            params = {'timestamp': timestamp}
            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching all open Futures positions: {e}")
            return None

    # ------------------------------------------------------------------------
    # Order Methods
    # ------------------------------------------------------------------------

    def create_futures_order(self, symbol: str, side: str, order_type: str, quantity: float, 
                             price: float = None, leverage: int = None, stop_loss: float = None, 
                             take_profit: float = None) -> dict:
        """
        Creates a Futures order. Optionally sets leverage, stop loss, or take profit.
        """
        if leverage:
            self.set_leverage(symbol, leverage)

        try:
            url = f"{self.base_url_futures}/fapi/v1/order"
            timestamp = Utils.get_current_timestamp_ms()
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
                'timestamp': timestamp
            }

            if order_type == 'LIMIT':
                params.update({'price': price, 'timeInForce': 'GTC'})

            if stop_loss:
                params.update({'stopPrice': stop_loss, 'type': 'STOP_LOSS_LIMIT', 'timeInForce': 'GTC'})

            if take_profit:
                params.update({'stopPrice': take_profit, 'type': 'TAKE_PROFIT_LIMIT', 'timeInForce': 'GTC'})

            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.post(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error creating Futures order: {e}")
            return None

    def close_futures_position_with_reduce_only(self, symbol: str, side: str, quantity: float) -> dict:
        """
        Closes a Futures position using reduceOnly = true.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v1/order"
            timestamp = Utils.get_current_timestamp_ms()
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'reduceOnly': 'true',
                'quantity': round(quantity, 8),
                'timestamp': timestamp
            }
            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.post(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error closing Futures position: {e}")
            return None

    # ------------------------------------------------------------------------
    # Leverage and Margin Methods
    # ------------------------------------------------------------------------

    def set_leverage(self, symbol: str, leverage: int) -> dict:
        """
        Sets the leverage for a given Futures symbol.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v1/leverage"
            timestamp = Utils.get_current_timestamp_ms()
            params = {
                'symbol': symbol,
                'leverage': leverage,
                'timestamp': timestamp
            }
            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.post(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error setting leverage: {e}")
            return None

    def change_futures_margin_type(self, symbol: str, margin_type: str) -> dict:
        """
        Changes the margin type (ISOLATED or CROSSED) for a Futures symbol.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v1/marginType"
            timestamp = Utils.get_current_timestamp_ms()
            params = {
                'symbol': symbol,
                'marginType': margin_type,
                'timestamp': timestamp
            }
            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.post(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error changing margin type: {e}")
            return None

    def get_max_futures_leverage(self, symbol: str) -> int:
        """
        Fetches the maximum possible leverage level for a given Futures symbol.
        """
        try:
            url = f"{self.base_url_futures}/fapi/v1/leverageBracket"
            timestamp = Utils.get_current_timestamp_ms()
            params = {'symbol': symbol, 'timestamp': timestamp}
            params['signature'] = Utils.generate_signature(params, self.api_secret)
            headers = Utils.generate_headers(self.api_key)

            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()

            leverage_data = response.json()
            for bracket in leverage_data:
                if bracket['symbol'] == symbol:
                    return bracket['brackets'][0]['initialLeverage']
            return None
        except Exception as e:
            self.logger.error(f"Error fetching max leverage for {symbol}: {e}")
            return None
