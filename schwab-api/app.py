"""Flask app for Schwab trading API."""

import os
import webbrowser
from threading import Timer
# from urllib.parse import parse_qs, urlparse

from flask import Flask, redirect, render_template, request, url_for, jsonify
from dotenv import load_dotenv

from schwab_client import SchwabClient

loaded_environment_variables: bool = load_dotenv()

if (not loaded_environment_variables):
    print("⚠ Warning: .env file not found or failed to load. "
          "Make sure environment variables are set properly.")
    exit(1)

app = Flask(__name__, template_folder='views')
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

# Global client instance
client = SchwabClient()


@app.route("/")
def index():
    """Home page - redirect to dashboard if authorized, otherwise show login."""
    is_authorized = client.auth.access_token is not None
    
    if is_authorized:
        return redirect(url_for("dashboard"))
    
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    """Dashboard page for authorized users."""
    if not client.auth.access_token:
        return redirect(url_for("index"))
    
    return render_template("dashboard.html", expiry=client.auth.token_expiry)


@app.route("/authorize")
def authorize():
    """Start OAuth authorization flow."""
    auth_url = (
        f"{client.auth.AUTHORIZE_URL}"
        f"?client_id={client.auth.app_key}"
        f"&redirect_uri={client.auth.redirect_uri}"
        f"&response_type=code"
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """Handle OAuth callback."""
    auth_code = request.args.get("code")
    error = request.args.get("error")
    
    # Handle error from OAuth provider
    if error:
        return render_template(
            "authorization_failed.html",
            error=error,
            error_description=request.args.get("error_description", "Unknown error"),
        ), 400
    
    if not auth_code:
        return render_template("no_auth_code.html"), 400
    
    try:
        # Exchange code for tokens
        client.auth.get_tokens(auth_code)
        
        # Redirect to dashboard after successful authorization
        return redirect(url_for("dashboard"))
    except Exception as e:
        return render_template("authorization_error.html", error=str(e)), 500


@app.route("/test-connection")
def test_connection():
    """Test API connection by fetching account information."""
    if not client.auth.access_token:
        return redirect(url_for("index"))
    
    try:
        # Call the accounts endpoint
        accounts = client._request("GET", "accounts")
        
        # Format the response nicely
        account_count = len(accounts) if accounts else 0
        account_info = []
        
        for account in accounts:
            acc_data = account.get("securitiesAccount", {})
            account_info.append({
                "number": acc_data.get("accountNumber", "N/A"),
                "hash_id": acc_data.get("accountId", "N/A"),
                "type": acc_data.get("type", "N/A"),
            })
        
        return render_template(
            "connection_success.html",
            account_count=account_count,
            accounts=account_info,
        )
        
    except Exception as e:
        return render_template("connection_failed.html", error=str(e)), 500


@app.route("/options-chain")
def options_chain_page():
    """Display option chain page with symbol input."""
    if not client.auth.access_token:
        return redirect(url_for("index"))
    
    # Get symbol from query parameter
    symbol = request.args.get("symbol", "").upper().strip()
    
    # If no symbol provided, show the input form
    if not symbol:
        return render_template("options_chain_form.html")
    
    # Symbol provided - fetch and display the option chain
    try:
        # Fetch option chain - get nearby strikes for calls and puts
        chain = client.get_option_chain(
            symbol=symbol,
            strike_count=10,  # 10 strikes above and below ATM
        )
        
        # Parse the chain data
        call_exp_map = chain.get("callExpDateMap", {})
        put_exp_map = chain.get("putExpDateMap", {})
        underlying_price = chain.get("underlyingPrice", 0)
        
        # Get first expiration date's options
        expirations = sorted(call_exp_map.keys()) if call_exp_map else []
        
        calls = []
        puts = []
        
        if expirations:
            first_exp = expirations[0]
            
            # Process calls
            call_strikes = call_exp_map.get(first_exp, {})
            for _strike_price, options_list in sorted(call_strikes.items()):
                for opt in options_list:
                    calls.append({
                        "strike": opt.get("strikePrice", 0),
                        "symbol": opt.get("symbol", ""),
                        "bid": opt.get("bid", 0),
                        "ask": opt.get("ask", 0),
                        "last": opt.get("last", 0),
                        "volume": opt.get("totalVolume", 0),
                        "oi": opt.get("openInterest", 0),
                        "iv": opt.get("volatility", 0),
                    })
            
            # Process puts
            put_strikes = put_exp_map.get(first_exp, {})
            for _strike_price, options_list in sorted(put_strikes.items()):
                for opt in options_list:
                    puts.append({
                        "strike": opt.get("strikePrice", 0),
                        "symbol": opt.get("symbol", ""),
                        "bid": opt.get("bid", 0),
                        "ask": opt.get("ask", 0),
                        "last": opt.get("last", 0),
                        "volume": opt.get("totalVolume", 0),
                        "oi": opt.get("openInterest", 0),
                        "iv": opt.get("volatility", 0),
                    })
        
        return render_template(
            "options_chain_table.html",
            symbol=symbol,
            underlying_price=underlying_price,
            expiration=expirations[0] if expirations else "N/A",
            total_expirations=len(expirations),
            calls=calls,
            puts=puts,
        )
        
    except Exception as e:
        return render_template(
            "options_chain_error.html",
            symbol=symbol,
            error=str(e),
        ), 500


@app.route("/api/options-chain/<symbol>")
def get_options_chain_data(symbol):
    """API endpoint to get options chain data as JSON without full page refresh."""
    if not client.auth.access_token:
        return jsonify({"error": "Not authorized"}), 401
    
    try:
        symbol = symbol.upper().strip()
        chain = client.get_option_chain(symbol=symbol, strike_count=10)
        
        if not chain:
            return jsonify({"error": "No data available"}), 404
        
        call_exp_map = chain.get("callExpDateMap", {})
        put_exp_map = chain.get("putExpDateMap", {})
        underlying_price = chain.get("underlyingPrice", 0)
        
        expirations = sorted(call_exp_map.keys()) if call_exp_map else []
        
        calls = []
        puts = []
        
        if expirations:
            first_exp = expirations[0]
            
            # Process calls
            call_strikes = call_exp_map.get(first_exp, {})
            for _strike_price, options_list in sorted(call_strikes.items()):
                for opt in options_list:
                    calls.append({
                        "strike": opt.get("strikePrice", 0),
                        "symbol": opt.get("symbol", ""),
                        "bid": opt.get("bid", 0),
                        "ask": opt.get("ask", 0),
                        "last": opt.get("last", 0),
                        "volume": opt.get("totalVolume", 0),
                        "oi": opt.get("openInterest", 0),
                        "iv": opt.get("volatility", 0),
                    })
            
            # Process puts
            put_strikes = put_exp_map.get(first_exp, {})
            for _strike_price, options_list in sorted(put_strikes.items()):
                for opt in options_list:
                    puts.append({
                        "strike": opt.get("strikePrice", 0),
                        "symbol": opt.get("symbol", ""),
                        "bid": opt.get("bid", 0),
                        "ask": opt.get("ask", 0),
                        "last": opt.get("last", 0),
                        "volume": opt.get("totalVolume", 0),
                        "oi": opt.get("openInterest", 0),
                        "iv": opt.get("volatility", 0),
                    })
        
        return jsonify({
            "symbol": symbol,
            "underlying_price": underlying_price,
            "expiration": expirations[0] if expirations else "N/A",
            "calls": calls,
            "puts": puts,
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logout")
def logout():
    """Clear authorization tokens."""
    client.auth.access_token = None
    client.auth.refresh_token = None
    client.auth.token_expiry = None
    
    # Remove token file if it exists
    if os.path.exists(client.auth.token_file):
        os.remove(client.auth.token_file)
    
    return redirect(url_for("index"))


# API Endpoints for trading operations
@app.route("/api/account/<account_id>")
def get_account(account_id):
    """Get account information."""
    try:
        fields = request.args.get("fields")
        account_info = client.get_account(account_id, fields=fields)
        return account_info
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/api/options/chain")
def get_option_chain():
    """Get option chain."""
    try:
        symbol = request.args.get("symbol", "").upper()
        if not symbol:
            return {"error": "symbol parameter required"}, 400
        
        contract_type = request.args.get("contract_type")
        strike_count = request.args.get("strike_count", type=int)
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")
        
        chain = client.get_option_chain(
            symbol=symbol,
            contract_type=contract_type,
            strike_count=strike_count,
            from_date=from_date,
            to_date=to_date,
        )
        return chain
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/api/orders/<account_id>", methods=["POST"])
def place_order(account_id):
    """Place an options order."""
    try:
        data = request.get_json()
        
        result = client.place_option_order(
            account_id=account_id,
            symbol=data["symbol"],
            option_symbol=data["option_symbol"],
            quantity=data["quantity"],
            instruction=data["instruction"],
            order_type=data.get("order_type", "MARKET"),
            price=data.get("price"),
            duration=data.get("duration", "DAY"),
        )
        return result
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/api/orders/<account_id>/<order_id>")
def get_order_status(account_id, order_id):
    """Get order status."""
    try:
        order = client.get_order(account_id, order_id)
        return order
    except Exception as e:
        return {"error": str(e)}, 500


def open_browser():
    """Open browser after short delay."""
    webbrowser.open("https://127.0.0.1:5000")


if __name__ == "__main__":
    # Open browser automatically after app starts
    Timer(1, open_browser).start()
    
    print("🚀 Starting Schwab Trading API server...")
    print("📍 Server running at: https://127.0.0.1:5000")
    print("📖 Opening browser...")
    print()
    
    # Run with adhoc SSL for local development
    app.run(host="127.0.0.1", port=5000, debug=True, ssl_context="adhoc")
