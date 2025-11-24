"""Get account information from Schwab API."""

from schwab_client import SchwabClient


def get_accounts():
    """Fetch all account information."""
    client = SchwabClient()
    
    print("🔍 Fetching your Schwab accounts...\n")
    
    try:
        # Get all accounts
        # The accounts endpoint returns a list of all linked accounts
        accounts = client._request("GET", "accounts")
        
        if not accounts:
            print("❌ No accounts found")
            return
        
        print(f"✅ Found {len(accounts)} account(s):\n")
        
        for i, account in enumerate(accounts, 1):
            account_data = account.get("securitiesAccount", {})
            
            print(f"Account {i}:")
            print(f"  Account Number: {account_data.get('accountNumber', 'N/A')}")
            print(f"  Account Hash ID: {account_data.get('accountId', 'N/A')}")
            print(f"  Type: {account_data.get('type', 'N/A')}")
            print(f"  Round Trips: {account_data.get('roundTrips', 'N/A')}")
            print(f"  Day Trader: {account_data.get('isDayTrader', 'N/A')}")
            print()
            
            # Show positions if any
            positions = account_data.get("positions", [])
            if positions:
                print(f"  📊 Positions ({len(positions)}):")
                for pos in positions[:5]:  # Show first 5
                    instrument = pos.get("instrument", {})
                    print(f"    - {instrument.get('symbol', 'N/A')}: {pos.get('longQuantity', 0)} shares")
                if len(positions) > 5:
                    print(f"    ... and {len(positions) - 5} more")
                print()
        
        # Show which hash ID to use
        if len(accounts) == 1:
            hash_id = accounts[0].get("securitiesAccount", {}).get("accountId", "")
            print(f"💡 Use this account hash ID in your code:")
            print(f"   {hash_id}")
        else:
            print("💡 You have multiple accounts. Use the appropriate accountId for each.")
            
    except Exception as e:
        print(f"❌ Error fetching accounts: {e}")
        print("\nMake sure you're authorized. Run the Flask app if needed:")
        print("  python app.py")


if __name__ == "__main__":
    get_accounts()
