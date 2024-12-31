# Binance Core Client

## Overview

The **Binance Core Client** is a modular Python library for interacting with the Binance API. It supports features like Spot trading, Futures trading, Margin trading, and public data management.

### Key Features
- **Spot Trading**: Place market, limit, and stop-limit orders.
- **Futures Trading**: Manage leverage, margin, and open positions.
- **Margin Trading**: Support for cross-margin and isolated-margin trading.
- **Public Data Management**: Fetch public data like order books, server status, and kline data.
- **Proxy Support**: Handle API requests with proxies to bypass restrictions or manage load.
- **Testnet Integration**: Seamlessly switch between Binance Testnet and Mainnet.

---
binance-core-client/
├── binance_core_client.py  # Main module for integrating submodules
├── proxy_manager.py        # Proxy management for session handling
├── spot_trading.py         # Spot trading functionality
├── futures_trading.py      # Futures trading functionality
├── margin_trading.py       # Margin trading functionality
├── public_data_manager.py  # Public data management
├── utils.py                # Utility functions (e.g., timestamp, signature generation)
└── README.md               # Documentation

