"""Low-level Binance Futures Testnet REST client."""

import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("binance_client")


class BinanceAPIError(Exception):
    """Raised when Binance returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error [{code}]: {message}")


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        """Append a HMAC-SHA256 signature to the params dict."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> dict:
        """Parse response JSON and raise BinanceAPIError on failure."""
        logger.debug("HTTP %s | URL: %s", response.status_code, response.url)
        try:
            data = response.json()
        except Exception:
            response.raise_for_status()
            return {}

        logger.debug("Response body: %s", data)

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        response.raise_for_status()
        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> dict:
        """Ping the server and return server time (no auth needed)."""
        url = f"{BASE_URL}/fapi/v1/time"
        logger.debug("GET %s", url)
        resp = self.session.get(url, timeout=10)
        return self._handle_response(resp)

    def get_account_info(self) -> dict:
        """Return account details including balances."""
        url = f"{BASE_URL}/fapi/v2/account"
        params = self._sign({})
        logger.info("Fetching account info …")
        logger.debug("GET %s | params: %s", url, params)
        resp = self.session.get(url, params=params, timeout=10)
        return self._handle_response(resp)

    def get_open_orders(self, symbol: str | None = None) -> list:
        """Return open orders for a symbol (or all symbols)."""
        url = f"{BASE_URL}/fapi/v1/openOrders"
        params: dict = {}
        if symbol:
            params["symbol"] = symbol
        params = self._sign(params)
        logger.info("Fetching open orders …")
        resp = self.session.get(url, params=params, timeout=10)
        return self._handle_response(resp)

    def place_order(self, **kwargs) -> dict:
        """
        Place a futures order.

        Required kwargs:
            symbol, side, type, quantity
        Optional:
            price (LIMIT), stopPrice (STOP_MARKET), timeInForce
        """
        url = f"{BASE_URL}/fapi/v1/order"
        params = {k: v for k, v in kwargs.items()}
        params = self._sign(params)
        logger.info("Placing order → %s", {k: v for k, v in kwargs.items()})
        resp = self.session.post(url, params=params, timeout=10)
        result = self._handle_response(resp)
        logger.info("Order placed successfully. ID: %s", result.get("orderId"))
        return result

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an existing order by ID."""
        url = f"{BASE_URL}/fapi/v1/order"
        params = self._sign({"symbol": symbol, "orderId": order_id})
        logger.info("Cancelling order %s for %s …", order_id, symbol)
        resp = self.session.delete(url, params=params, timeout=10)
        return self._handle_response(resp)

    def get_position_risk(self, symbol: str | None = None) -> list:
        """Return position risk info."""
        url = f"{BASE_URL}/fapi/v2/positionRisk"
        params: dict = {}
        if symbol:
            params["symbol"] = symbol
        params = self._sign(params)
        resp = self.session.get(url, params=params, timeout=10)
        return self._handle_response(resp)
