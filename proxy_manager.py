"""
Proxy Manager Module
---------------------
This module handles proxy management, including:
- Initializing sessions with proxies
- Switching between proxies in case of failures
"""
import requests

class ProxyManager:
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        self.proxy_index = 0

    def initialize_session(self):
        proxy = self.proxy_list[self.proxy_index]
        session = requests.Session()
        session.proxies = {
            'http': f"socks5h://{proxy['username']}:{proxy['password']}@{proxy['address']}:{proxy['port']}",
            'https': f"socks5h://{proxy['username']}:{proxy['password']}@{proxy['address']}:{proxy['port']}"
        }
        return session
