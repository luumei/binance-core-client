"""
Public Data Manager
---------------------
This module provides functions for fetching public Binance data without requiring authentication, including:
- Server status and time
- Current spot prices for symbols
- Extended kline (candlestick) data for Spot and Futures markets
"""

import requests
import pandas as pd
import datetime
import time


class PublicDataManager:
    @staticmethod
    def ping() -> dict:
        """
        Simple ping to check Binance server status.
        
        :return: Server status response as a dictionary.
        """
        url = "https://api.binance.com/api/v3/ping"
        try:
            resp = requests.get(url)
            if resp.ok:
                return resp.json() if resp.text else {"status": "ok"}
        except Exception as e:
            print(f"Exception in ping(): {e}")
        return None

    @staticmethod
    def get_server_time() -> dict:
        """
        Retrieves current Binance server time.
        
        :return: Server time response as a dictionary.
        """
        url = "https://api.binance.com/api/v3/time"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Error get_server_time: {resp.status_code}, {resp.content}")
        except Exception as e:
            print(f"Exception in get_server_time(): {e}")
        return None

    @staticmethod
    def get_symbol_price_spot(symbol: str) -> float:
        """
        Returns the current spot price for a symbol (e.g., BTCUSDT).
        
        :param symbol: The trading pair symbol.
        :return: Current spot price as a float, or None if an error occurs.
        """
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return float(data['price'])
            else:
                print(f"Error get_symbol_price_spot: {resp.status_code}, {resp.content}")
        except Exception as e:
            print(f"Exception in get_symbol_price_spot: {e}")
        return None

    def get_spot_klines_extended(self, symbol='BTCUSDT', interval='4h', limit=1500, current_time=None) -> pd.DataFrame:
        """
        Fetches extended kline data for Spot market.
        """
        return self._fetch_klines_extended(symbol, interval, limit, current_time, is_futures=False)

    def get_futures_klines_extended(self, symbol='BTCUSDT', interval='4h', limit=1500, current_time=None) -> pd.DataFrame:
        """
        Fetches extended kline data for Futures market.
        """
        return self._fetch_klines_extended(symbol, interval, limit, current_time, is_futures=True)

    def _fetch_klines_extended(self, symbol, interval, limit=1500, current_time=None, is_futures=False) -> pd.DataFrame:
        """
        Iteratively fetches large amounts of candlestick (kline) data.
        """
        columns = [
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ]

        if current_time:
            end_time = int(current_time.timestamp() * 1000)
        else:
            end_time = int(datetime.datetime.now().timestamp() * 1000)

        df = pd.DataFrame()

        while limit > 0:
            chunk_size = min(limit, 1000)
            base_url = "https://fapi.binance.com" if is_futures else "https://api.binance.com"
            url = (f"{base_url}/fapi/v1/klines?" if is_futures else f"{base_url}/api/v3/klines?")
            url += f"symbol={symbol}&interval={interval}&limit={chunk_size}&endTime={end_time}"

            try:
                resp = requests.get(url)
                if resp.status_code != 200:
                    print(f"Error fetching klines chunk: Status={resp.status_code}, Content={resp.content}")
                    break

                chunk_data = resp.json()
                if not chunk_data:
                    break

                tmp_df = pd.DataFrame(chunk_data, columns=columns)
                tmp_df['open_time'] = pd.to_datetime(tmp_df['open_time'], unit='ms')
                tmp_df['close_time'] = pd.to_datetime(tmp_df['close_time'], unit='ms')

                numeric_cols = columns[1:-1]
                tmp_df[numeric_cols] = tmp_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

                df = pd.concat([df, tmp_df], ignore_index=True)

                first_open_time = tmp_df.iloc[0]['open_time']
                end_time = int(first_open_time.value // 10**6 - 1)

                limit -= chunk_size
                if limit > 1000:
                    time.sleep(1)
            except Exception as e:
                print(f"Error in _fetch_klines_extended: {e}")
                break

        df.set_index('open_time', inplace=True)
        df.sort_index(inplace=True)
        return df
        
    def get_spot_order_book(self, symbol: str, limit=100) -> dict:
        """
        Retrieve the order book for a given symbol from the Spot market.

        Parameters:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            limit (int): The number of orders to retrieve from the order book (default is 100).

        Returns:
            dict: The order book data if successful, None otherwise.
        """
        return self._fetch_order_book(symbol=symbol, limit=limit, is_futures=False, testnet=False)

    def get_futures_order_book(self, symbol: str, limit=100, testnet=False) -> dict:
        """
        Retrieve the order book for a given symbol from the Futures market.

        Parameters:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            limit (int): The number of orders to retrieve from the order book (default is 100).
            testnet (bool): Whether to use the testnet for Futures (default is False).

        Returns:
            dict: The order book data if successful, None otherwise.
        """
        return self._fetch_order_book(symbol=symbol, limit=limit, is_futures=True, testnet=testnet)

    def _fetch_order_book(self, symbol: str, limit=100, is_futures=False, testnet=False) -> dict:
        """
        Fetches the order book for a given symbol from Spot or Futures market.

        Parameters:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            limit (int): The number of orders to retrieve from the order book (default is 100).
            is_futures (bool): Whether the market is Futures or Spot.
            testnet (bool): Whether to use the testnet for Futures (default is False).

        Returns:
            dict: The order book data if successful, None otherwise.
        """
        try:
            # Set the base URL and endpoint
            if is_futures:
                base_url = "https://testnet.binancefuture.com" if testnet else "https://fapi.binance.com"
                endpoint = '/fapi/v1/depth'
            else:
                base_url = "https://api.binance.com"
                endpoint = '/api/v3/depth'

            # Make the API request
            response = requests.get(base_url + endpoint, params={'symbol': symbol, 'limit': limit})

            # Handle the response
            if response.status_code == 200:
                return response.json()
            else:
                print(f'Error fetching order book. Status code: {response.status_code}')
                print(f'Response content: {response.content}')
                return None

        except Exception as e:
            print(f"Error fetching order book for symbol {symbol}. Exception: {e}")
            return None
