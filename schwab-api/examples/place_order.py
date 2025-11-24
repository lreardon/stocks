"""Example: Place an options order using Schwab API."""

from schwab_client import SchwabClient


def main():
    """Example of placing an options order."""
    # Initialize client (will use .env credentials)
    client = SchwabClient()

    # If not authorized yet, run authorization flow
    # Uncomment the line below on first run:
    # client.auth.authorize()

    # Your account ID (get this from Schwab API or account info)
    ACCOUNT_ID = "your_account_hash_id_here"

    # Get account info
    print("Fetching account info...")
    account = client.get_account(ACCOUNT_ID, fields="positions")
    print(f"Account: {account.get('securitiesAccount', {}).get('accountNumber', 'N/A')}")

    # Get option chain for a symbol
    print("\nFetching AAPL option chain...")
    chain = client.get_option_chain(
        symbol="AAPL",
        contract_type="CALL",
        strike_count=5,  # 5 strikes above and below ATM
    )
    print(f"Found {len(chain.get('callExpDateMap', {}))} expiration dates")

    # Example: Place a limit order to buy a call option
    print("\nPlacing options order...")
    order = client.place_option_order(
        account_id=ACCOUNT_ID,
        symbol="AAPL",
        option_symbol="AAPL_123456C00150000",  # Replace with actual option symbol from chain
        quantity=1,
        instruction="BUY_TO_OPEN",
        order_type="LIMIT",
        price=5.50,
        duration="DAY",
    )
    print(f"Order placed: {order}")

    # Get order status
    if order.get("status") == "success":
        order_id = "order_id_from_response"  # Extract from response headers if needed
        order_details = client.get_order(ACCOUNT_ID, order_id)
        print(f"Order status: {order_details.get('status')}")


if __name__ == "__main__":
    main()
