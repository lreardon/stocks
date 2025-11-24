"""Schwab API trading client."""

import requests

from schwab_client.auth import SchwabAuth


class SchwabClient:
    """Client for Schwab trading API operations."""

    BASE_URL = "https://api.schwabapi.com/trader/v1"
    MARKETDATA_URL = "https://api.schwabapi.com/marketdata/v1"

    def __init__(self, auth: SchwabAuth = None):
        """Initialize Schwab client.

        Args:
            auth: SchwabAuth instance. Creates new one if not provided.
        """
        self.auth = auth or SchwabAuth()

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            JSON response as dict
        """
        # Use market data URL for market data endpoints
        if endpoint.startswith("marketdata"):
            base_url = self.MARKETDATA_URL
            # Remove 'marketdata/v1' prefix since it's in base URL
            endpoint = endpoint.replace("marketdata/v1/", "").replace("marketdata/", "")
        else:
            base_url = self.BASE_URL
            
        url = f"{base_url}/{endpoint.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.auth.get_access_token()}"

        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()

        # Some endpoints return empty response on success
        if response.status_code == 201 or not response.content:
            return {"status": "success", "status_code": response.status_code}

        return response.json()

    def get_account(self, account_id: str, fields: str = None) -> dict:
        """Get account details.

        Args:
            account_id: Account hash ID
            fields: Optional fields to include (e.g., 'positions')

        Returns:
            Account information
        """
        endpoint = f"accounts/{account_id}"
        params = {"fields": fields} if fields else {}
        return self._request("GET", endpoint, params=params)

    def place_option_order(
        self,
        account_id: str,
        symbol: str,
        option_symbol: str,
        quantity: int,
        instruction: str,
        order_type: str = "MARKET",
        price: float = None,
        duration: str = "DAY",
    ) -> dict:
        """Place an options order.

        Args:
            account_id: Account hash ID
            symbol: Underlying symbol (e.g., 'AAPL')
            option_symbol: Option symbol in OCC format (e.g., 'AAPL_123456C00150000')
            quantity: Number of contracts
            instruction: Order instruction - BUY_TO_OPEN, SELL_TO_OPEN, BUY_TO_CLOSE, SELL_TO_CLOSE
            order_type: MARKET, LIMIT, STOP, STOP_LIMIT
            price: Limit price (required for LIMIT orders)
            duration: DAY, GTC, etc.

        Returns:
            Order response with order ID
        """
        if order_type == "LIMIT":
            raise ValueError("Price is required for LIMIT orders")

        order_data = {
            "orderType": order_type,
            "session": "NORMAL",
            "duration": duration,
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": instruction,
                    "quantity": quantity,
                    "instrument": {
                        "symbol": option_symbol,
                        "assetType": "OPTION",
                    },
                }
            ],
        }


        order_data["price"] = price

        endpoint = f"accounts/{account_id}/orders"
        return self._request("POST", endpoint, json=order_data)

    def get_order(self, account_id: str, order_id: str) -> dict:
        """Get order details.

        Args:
            account_id: Account hash ID
            order_id: Order ID

        Returns:
            Order details
        """
        endpoint = f"accounts/{account_id}/orders/{order_id}"
        return self._request("GET", endpoint)

    def cancel_order(self, account_id: str, order_id: str) -> dict:
        """Cancel an order.

        Args:
            account_id: Account hash ID
            order_id: Order ID

        Returns:
            Cancellation response
        """
        endpoint = f"accounts/{account_id}/orders/{order_id}"
        return self._request("DELETE", endpoint)

    def get_option_chain(
        self,
        symbol: str,
        contract_type: str = None,
        strike_count: int = None,
        from_date: str = None,
        to_date: str = None,
    ) -> dict:
        """Get option chain for a symbol.

        Args:
            symbol: Underlying symbol
            contract_type: CALL, PUT, or ALL
            strike_count: Number of strikes above/below at-the-money
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)

        Returns:
            Option chain data
        """
        params = {"symbol": symbol}

        if contract_type:
            params["contractType"] = contract_type
        if strike_count:
            params["strikeCount"] = strike_count
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date

        return self._request("GET", "marketdata/chains", params=params)
