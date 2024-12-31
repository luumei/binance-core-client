"""
Utils Module
---------------------
This module provides shared utility functions for Binance API interaction,
including:
- Generating API request signatures
- Fetching the current Unix timestamp in milliseconds
- Creating request headers with the API key
"""

import time
from hashlib import sha256
from urllib.parse import urlencode
import hmac


class Utils:
    @staticmethod
    def get_current_timestamp_ms() -> int:
        """
        Returns the current Unix timestamp in milliseconds.

        :return: The current timestamp in milliseconds.
        """
        return int(time.time() * 1000)

    @staticmethod
    def generate_signature(params: dict, api_secret: str) -> str:
        """
        Generates a signature for Binance API requests.

        :param params:      A dictionary of request parameters.
        :param api_secret:  Your Binance API secret key.
        :return:            HMAC-SHA256 signature as a string.
        """
        query_string = urlencode(params)
        return hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), sha256).hexdigest()

    @staticmethod
    def generate_headers(api_key: str) -> dict:
        """
        Generates headers for Binance API requests.

        :param api_key: Your Binance API key.
        :return:        A dictionary containing the headers.
        """
        return {'X-MBX-APIKEY': api_key}
