import socks
import socket
import requests
import logging

class ProxyManager:
    def __init__(self, proxy_list):
        """
        Initializes the Proxy Manager.

        :param proxy_list: A list of proxies, where each proxy is a dictionary with 
                           'type', 'address', 'port', 'username', and 'password'.
                           'type' can be 'socks5', 'http', or 'https'.
        """
        self.proxy_list = proxy_list
        self.proxy_index = 0
        self.session = None

        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("ProxyManager")

    def _test_proxy(self, proxy_info):
        """
        Tests if a proxy is working by connecting to a known host.

        :param proxy_info: Dictionary with proxy details.
        :return: True if the proxy works, False otherwise.
        """
        try:
            if proxy_info['type'].lower() in ['socks5', 'http', 'https']:
                sock = socks.socksocket()

                # Set proxy type
                proxy_type = {
                    'socks5': socks.SOCKS5
                }.get(proxy_info['type'].lower(), socks.HTTP)

                sock.set_proxy(
                    proxy_type,
                    proxy_info['address'],
                    int(proxy_info['port']),
                    username=proxy_info.get('username'),
                    password=proxy_info.get('password')
                )

                sock.settimeout(5)  # Set connection timeout
                sock.connect(("8.8.8.8", 53))  # Connect to Google DNS
                sock.close()

                self.logger.info("A proxy is working.")
                return True
            else:
                self.logger.warning("Unsupported proxy type detected.")
                return False
        except Exception as e:
            self.logger.warning(f"A proxy failed: {str(e)}")
            return False

    def _rotate_proxy(self):
        """
        Rotates to the next proxy in the list.
        """
        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
        self.logger.info("Rotated to the next proxy.")

    def _set_proxy_for_session(self, proxy_info):
        """
        Configures the current session with a proxy.

        :param proxy_info: Dictionary with proxy details.
        """
        proxy_type = proxy_info['type'].lower()
        proxy_scheme = proxy_type

        proxy = {
            'http': f"{proxy_scheme}://{proxy_info['address']}:{proxy_info['port']}",
            'https': f"{proxy_scheme}://{proxy_info['address']}:{proxy_info['port']}"
        }

        if 'username' in proxy_info and 'password' in proxy_info:
            proxy['http'] = f"{proxy_scheme}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['address']}:{proxy_info['port']}"
            proxy['https'] = f"{proxy_scheme}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['address']}:{proxy_info['port']}"

        self.session = requests.Session()
        self.session.proxies.update(proxy)
        self.logger.info("Session configured with a proxy.")

    def _get_session_with_working_proxy(self):
        """
        Tries to create a session with a working proxy from the list.

        :return: A `requests.Session` with a working proxy or None.
        """
        for _ in range(len(self.proxy_list)):
            proxy_info = self.proxy_list[self.proxy_index]
            self.logger.info("Testing a proxy...")

            if self._test_proxy(proxy_info):
                self._set_proxy_for_session(proxy_info)
                return self.session

            self._rotate_proxy()

        self.logger.error("No working proxy found.")
        return None

    def test_current_proxy(self):
        """
        Tests the current proxy of the existing session.

        :return: True if the proxy works, False otherwise.
        """
        if self.session:
            proxy_info = self.proxy_list[self.proxy_index]
            if self._test_proxy(proxy_info):
                return True
        else:
            self.logger.warning("No active session found. Selecting a proxy.")

        self.session = self._get_session_with_working_proxy()
        return self.session is not None

    def get_working_session(self):
        """
        Gets a `requests.Session` with a working proxy.

        :return: A `requests.Session` or None if no proxy works.
        """
        if not self.session:
            self.session = self._get_session_with_working_proxy()
        else:
            if not self.test_current_proxy():
                self.logger.warning("Current proxy failed. Rotating proxies.")
                self.session = self._get_session_with_working_proxy()

        return self.session

    def initialize_session(self):
        """
        Initializes a session with the first working proxy.

        :return: A `requests.Session` or None if no proxy works.
        """
        self.logger.info("Initializing session with a proxy.")
        return self.get_working_session()
