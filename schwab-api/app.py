"""Flask app for Schwab trading API."""

import os
import webbrowser
from threading import Timer
# from urllib.parse import parse_qs, urlparse

from flask import Flask, redirect, render_template_string, request, url_for
from dotenv import load_dotenv

from schwab_client import SchwabClient

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

# Global client instance
client = SchwabClient()


@app.route("/")
def index():
    """Home page - redirect to dashboard if authorized, otherwise show login."""
    is_authorized = client.auth.access_token is not None
    
    if is_authorized:
        return redirect(url_for("dashboard"))
    
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Schwab Trading API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #00a0dc; }
                .status { padding: 15px; border-radius: 5px; margin: 20px 0; }
                .unauthorized { background: #f8d7da; color: #721c24; }
                .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                         text-decoration: none; border-radius: 5px; margin: 10px 5px; }
                .button:hover { background: #0088bb; }
                .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>Schwab Trading API</h1>
            
            <div class="status unauthorized">
                <strong>⚠ Not Authorized</strong><br>
                You need to authorize with Schwab to use the trading API.
            </div>
            
            <div class="info">
                <h3>What you'll be able to do:</h3>
                <ul>
                    <li>Place options orders</li>
                    <li>Get account information</li>
                    <li>Fetch option chains</li>
                    <li>Check order status</li>
                </ul>
            </div>
            
            <a href="/authorize" class="button">Authorize with Schwab</a>
            
        </body>
        </html>
        """
    )


@app.route("/dashboard")
def dashboard():
    """Dashboard page for authorized users."""
    if not client.auth.access_token:
        return redirect(url_for("index"))
    
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - Schwab Trading API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 20px auto; padding: 20px; }
                h1 { color: #00a0dc; }
                .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
                .status { padding: 15px; border-radius: 5px; margin: 20px 0; background: #d4edda; color: #155724; }
                .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                         text-decoration: none; border-radius: 5px; margin: 5px; }
                .button:hover { background: #0088bb; }
                .button.logout { background: #dc3545; }
                .button.logout:hover { background: #c82333; }
                .section { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; 
                          box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .api-endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; 
                               font-family: monospace; font-size: 14px; }
                .method { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; 
                         font-weight: bold; margin-right: 10px; }
                .get { background: #28a745; }
                .post { background: #007bff; }
                ul { line-height: 1.8; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Trading Dashboard</h1>
                <div>
                    <a href="/test-connection" class="button">Test Connection</a>
                    <a href="/options-chain" class="button">Options Chain</a>
                    <a href="/logout" class="button logout">Logout</a>
                </div>
            </div>
            
            <div class="status">
                <strong>✓ Connected to Schwab API</strong><br>
                Token expires: {{ expiry }}<br>
                <small>Tokens auto-refresh when needed</small>
            </div>
            
            <div class="section">
                <h2>🔌 API Endpoints</h2>
                <p>Use these endpoints with your account hash ID from Schwab:</p>
                
                <h3>Account Information</h3>
                <div class="api-endpoint">
                    <span class="method get">GET</span>
                    /api/account/&lt;account_id&gt;?fields=positions
                </div>
                
                <h3>Options Chain</h3>
                <div class="api-endpoint">
                    <span class="method get">GET</span>
                    /api/options/chain?symbol=AAPL&contract_type=CALL&strike_count=5
                </div>
                
                <h3>Place Order</h3>
                <div class="api-endpoint">
                    <span class="method post">POST</span>
                    /api/orders/&lt;account_id&gt;
                </div>
                <p style="margin-left: 20px; color: #666;">
                    Body: <code>{"symbol": "AAPL", "option_symbol": "...", "quantity": 1, 
                    "instruction": "BUY_TO_OPEN", "order_type": "LIMIT", "price": 5.50}</code>
                </p>
                
                <h3>Order Status</h3>
                <div class="api-endpoint">
                    <span class="method get">GET</span>
                    /api/orders/&lt;account_id&gt;/&lt;order_id&gt;
                </div>
            </div>
            
            <div class="section">
                <h2>🐍 Python Client Usage</h2>
                <pre style="background: #282c34; color: #abb2bf; padding: 15px; border-radius: 5px; overflow-x: auto;">
<span style="color: #c678dd;">from</span> schwab_client <span style="color: #c678dd;">import</span> SchwabClient

<span style="color: #5c6370;"># Client automatically loads saved tokens</span>
client = SchwabClient()

<span style="color: #5c6370;"># Place an options order</span>
order = client.place_option_order(
    account_id=<span style="color: #98c379;">"your_account_hash"</span>,
    symbol=<span style="color: #98c379;">"AAPL"</span>,
    option_symbol=<span style="color: #98c379;">"AAPL_123456C00150000"</span>,
    quantity=<span style="color: #d19a66;">1</span>,
    instruction=<span style="color: #98c379;">"BUY_TO_OPEN"</span>,
    order_type=<span style="color: #98c379;">"LIMIT"</span>,
    price=<span style="color: #d19a66;">5.50</span>
)
                </pre>
            </div>
            
            <div class="section">
                <h2>📚 Next Steps</h2>
                <ul>
                    <li>Get your account hash ID from Schwab API or account info endpoint</li>
                    <li>Use the API endpoints above or the Python client to execute trades</li>
                    <li>Check <code>examples/place_order.py</code> for more examples</li>
                    <li>See <code>README.md</code> for full documentation</li>
                </ul>
            </div>
            
        </body>
        </html>
        """,
        expiry=client.auth.token_expiry,
    )


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
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authorization Failed</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Authorization Failed</h1>
                    <p>Error: {{ error }}</p>
                    <p>Description: {{ error_description }}</p>
                </div>
                <a href="/" class="button">Back to Home</a>
            </body>
            </html>
            """,
            error=error,
            error_description=request.args.get("error_description", "Unknown error"),
        ), 400
    
    if not auth_code:
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authorization Failed</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Authorization Failed</h1>
                    <p>No authorization code received.</p>
                </div>
                <a href="/" class="button">Back to Home</a>
            </body>
            </html>
            """
        ), 400
    
    try:
        # Exchange code for tokens
        client.auth._get_tokens(auth_code)
        
        # Redirect to dashboard after successful authorization
        return redirect(url_for("dashboard"))
    except Exception as e:
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authorization Error</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>Authorization Error</h1>
                    <p>{{ error }}</p>
                </div>
                <a href="/" class="button">Back to Home</a>
            </body>
            </html>
            """,
            error=str(e),
        ), 500


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
        
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Connection Test - Schwab API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 1000px; margin: 20px auto; padding: 20px; }
                    h1 { color: #00a0dc; }
                    .success { background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin: 20px 0; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 10px 5px; }
                    .button:hover { background: #0088bb; }
                    .account { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; 
                              border-left: 4px solid #00a0dc; }
                    .hash-id { font-family: monospace; background: white; padding: 5px; border-radius: 3px; 
                              display: inline-block; margin-top: 5px; }
                    pre { background: #282c34; color: #abb2bf; padding: 15px; border-radius: 5px; 
                         overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1>✅ Connection Test Successful!</h1>
                
                <div class="success">
                    <strong>Your application is authorized and ready to trade!</strong><br>
                    Successfully retrieved {{ account_count }} account(s) from Schwab API.
                </div>
                
                <h2>📋 Your Accounts</h2>
                {% for acc in accounts %}
                <div class="account">
                    <strong>Account {{ loop.index }}</strong><br>
                    Account Number: {{ acc.number }}<br>
                    Type: {{ acc.type }}<br>
                    <strong>Hash ID:</strong> <span class="hash-id">{{ acc.hash_id }}</span>
                    <p style="color: #666; font-size: 14px;">
                        ℹ️ Use this hash ID in your API calls
                    </p>
                </div>
                {% endfor %}
                
                <h2>🐍 Example Usage</h2>
                <pre>
from schwab_client import SchwabClient

client = SchwabClient()

# Use your account hash ID
account_id = "{{ accounts[0].hash_id if accounts else 'YOUR_HASH_ID' }}"

# Get account details
account = client.get_account(account_id, fields="positions")
print(account)
                </pre>
                
                <a href="/dashboard" class="button">Back to Dashboard</a>
                
            </body>
            </html>
            """,
            account_count=account_count,
            accounts=account_info,
        )
        
    except Exception as e:
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Connection Test Failed</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>❌ Connection Test Failed</h1>
                    <p>Error: {{ error }}</p>
                </div>
                <a href="/dashboard" class="button">Back to Dashboard</a>
            </body>
            </html>
            """,
            error=str(e),
        ), 500


@app.route("/options-chain")
def options_chain_page():
    """Display option chain page with symbol input."""
    if not client.auth.access_token:
        return redirect(url_for("index"))
    
    # Get symbol from query parameter
    symbol = request.args.get("symbol", "").upper().strip()
    
    # If no symbol provided, show the input form
    if not symbol:
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Option Chain - Schwab API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    h1 { color: #00a0dc; }
                    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 5px; border: none; cursor: pointer; }
                    .button:hover { background: #0088bb; }
                    .form-section { background: white; padding: 30px; border-radius: 8px; 
                                   box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                    .input-group { margin: 20px 0; }
                    label { display: block; font-weight: bold; margin-bottom: 8px; color: #333; }
                    input[type="text"] { width: 100%; padding: 12px; font-size: 18px; border: 2px solid #ddd; 
                                        border-radius: 5px; text-transform: uppercase; }
                    input[type="text"]:focus { outline: none; border-color: #00a0dc; }
                    .quick-symbols { margin: 20px 0; }
                    .quick-symbol { display: inline-block; padding: 8px 15px; background: #e7f3ff; 
                                   color: #00a0dc; border-radius: 5px; margin: 5px; cursor: pointer; 
                                   border: 1px solid #00a0dc; }
                    .quick-symbol:hover { background: #00a0dc; color: white; }
                    .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; }
                </style>
                <script>
                    function loadSymbol(symbol) {
                        document.getElementById('symbolInput').value = symbol;
                        document.getElementById('symbolForm').submit();
                    }
                </script>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Option Chain Viewer</h1>
                    <a href="/dashboard" class="button">Back to Dashboard</a>
                </div>
                
                <div class="form-section">
                    <form id="symbolForm" method="get" action="/options-chain">
                        <div class="input-group">
                            <label for="symbolInput">Enter Symbol:</label>
                            <input type="text" id="symbolInput" name="symbol" placeholder="e.g., AAPL, SPY, QQQ" 
                                   autofocus required>
                        </div>
                        <button type="submit" class="button" style="width: 100%; font-size: 16px;">
                            📈 View Option Chain
                        </button>
                    </form>
                    
                    <div class="quick-symbols">
                        <strong>Quick Select:</strong><br>
                        <span class="quick-symbol" onclick="loadSymbol('SPY')">SPY</span>
                        <span class="quick-symbol" onclick="loadSymbol('QQQ')">QQQ</span>
                        <span class="quick-symbol" onclick="loadSymbol('AAPL')">AAPL</span>
                        <span class="quick-symbol" onclick="loadSymbol('TSLA')">TSLA</span>
                        <span class="quick-symbol" onclick="loadSymbol('MSFT')">MSFT</span>
                        <span class="quick-symbol" onclick="loadSymbol('NVDA')">NVDA</span>
                        <span class="quick-symbol" onclick="loadSymbol('AMD')">AMD</span>
                        <span class="quick-symbol" onclick="loadSymbol('META')">META</span>
                    </div>
                    
                    <div class="info">
                        <strong>💡 Tip:</strong> The option chain will automatically refresh every 5 seconds 
                        to show real-time price updates. You can pause/resume auto-refresh at any time.
                    </div>
                </div>
            </body>
            </html>
            """
        )
    
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
        
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ symbol }} Option Chain - Schwab API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 1400px; margin: 20px auto; padding: 20px; }
                    h1 { color: #00a0dc; }
                    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 5px; }
                    .button:hover { background: #0088bb; }
                    .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .options-container { display: flex; gap: 20px; margin-top: 20px; }
                    .options-table { flex: 1; overflow-x: auto; }
                    table { width: 100%; border-collapse: collapse; font-size: 14px; }
                    th { background: #00a0dc; color: white; padding: 10px; text-align: left; position: sticky; top: 0; }
                    td { padding: 8px; border-bottom: 1px solid #ddd; }
                    tr:hover { background: #f8f9fa; }
                    .calls th { background: #28a745; }
                    .puts th { background: #dc3545; }
                    .strike { font-weight: bold; text-align: right; }
                    .price { text-align: right; }
                    .symbol { font-family: monospace; font-size: 12px; }
                    .atm { background: #fff3cd; }
                    .status { font-size: 12px; color: #666; margin-top: 10px; }
                    .refreshing { color: #00a0dc; }
                    .symbol-input { display: flex; gap: 10px; align-items: center; margin-bottom: 15px; }
                    .symbol-input input { padding: 8px 12px; font-size: 16px; border: 2px solid #ddd; 
                                         border-radius: 5px; text-transform: uppercase; width: 150px; }
                    .symbol-input input:focus { outline: none; border-color: #00a0dc; }
                    .symbol-input button { padding: 8px 20px; background: #28a745; color: white; 
                                          border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
                    .symbol-input button:hover { background: #218838; }
                </style>
                <script>
                    let refreshInterval;
                    let countdown = 5;
                    
                    function updateCountdown() {
                        document.getElementById('countdown').textContent = countdown;
                        countdown--;
                        if (countdown < 0) {
                            countdown = 5;
                            location.reload();
                        }
                    }
                    
                    function startAutoRefresh() {
                        refreshInterval = setInterval(updateCountdown, 1000);
                    }
                    
                    function stopAutoRefresh() {
                        if (refreshInterval) {
                            clearInterval(refreshInterval);
                            refreshInterval = null;
                        }
                        document.getElementById('countdown').textContent = 'paused';
                    }
                    
                    function toggleAutoRefresh() {
                        const btn = document.getElementById('toggleBtn');
                        if (refreshInterval) {
                            stopAutoRefresh();
                            btn.textContent = '▶️ Resume Auto-Refresh';
                            btn.style.background = '#28a745';
                        } else {
                            countdown = 5;
                            startAutoRefresh();
                            btn.textContent = '⏸️ Pause Auto-Refresh';
                            btn.style.background = '#ffc107';
                        }
                    }
                    
                    function changeSymbol() {
                        const newSymbol = document.getElementById('newSymbol').value.trim().toUpperCase();
                        if (newSymbol) {
                            window.location.href = '/options-chain?symbol=' + newSymbol;
                        }
                    }
                    
                    function handleKeyPress(event) {
                        if (event.key === 'Enter') {
                            changeSymbol();
                        }
                    }
                    
                    // Start auto-refresh on page load
                    window.onload = startAutoRefresh;
                </script>
            </head>
            <body>
                <div class="header">
                    <h1>📊 {{ symbol }} Option Chain</h1>
                    <div>
                        <button id="toggleBtn" onclick="toggleAutoRefresh()" class="button" style="background: #ffc107;">⏸️ Pause Auto-Refresh</button>
                        <a href="/options-chain" class="button">Change Symbol</a>
                        <a href="/dashboard" class="button">Back to Dashboard</a>
                    </div>
                </div>
                
                <div class="symbol-input">
                    <label><strong>Quick Switch:</strong></label>
                    <input type="text" id="newSymbol" placeholder="Enter symbol" onkeypress="handleKeyPress(event)" value="{{ symbol }}">
                    <button onclick="changeSymbol()">Load</button>
                </div>
                
                <div class="info">
                    <strong>Underlying Price:</strong> ${{ "%.2f"|format(underlying_price) }}<br>
                    <strong>Expiration:</strong> {{ expiration }}<br>
                    <strong>Total Expirations Available:</strong> {{ total_expirations }}<br>
                    <small>Showing nearest expiration with {{ calls|length }} call strikes and {{ puts|length }} put strikes</small>
                    <div class="status">🔄 Auto-refreshing in <span id="countdown">5</span> seconds</div>
                </div>
                
                <div class="options-container">
                    <div class="options-table calls">
                        <h2>📈 Calls</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Strike</th>
                                    <th>Symbol</th>
                                    <th>Bid</th>
                                    <th>Ask</th>
                                    <th>Last</th>
                                    <th>Volume</th>
                                    <th>OI</th>
                                    <th>IV</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for call in calls %}
                                <tr {% if call.strike <= underlying_price and calls[loop.index0 + 1].strike > underlying_price %}class="atm"{% endif %}>
                                    <td class="strike price">${{ "%.2f"|format(call.strike) }}</td>
                                    <td class="symbol">{{ call.symbol }}</td>
                                    <td class="price">${{ "%.2f"|format(call.bid) }}</td>
                                    <td class="price">${{ "%.2f"|format(call.ask) }}</td>
                                    <td class="price">${{ "%.2f"|format(call.last) }}</td>
                                    <td class="price">{{ call.volume }}</td>
                                    <td class="price">{{ call.oi }}</td>
                                    <td class="price">{{ "%.1f"|format(call.iv) }}%</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="options-table puts">
                        <h2>📉 Puts</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Strike</th>
                                    <th>Symbol</th>
                                    <th>Bid</th>
                                    <th>Ask</th>
                                    <th>Last</th>
                                    <th>Volume</th>
                                    <th>OI</th>
                                    <th>IV</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for put in puts %}
                                <tr {% if put.strike <= underlying_price and puts[loop.index0 + 1].strike > underlying_price %}class="atm"{% endif %}>
                                    <td class="strike price">${{ "%.2f"|format(put.strike) }}</td>
                                    <td class="symbol">{{ put.symbol }}</td>
                                    <td class="price">${{ "%.2f"|format(put.bid) }}</td>
                                    <td class="price">${{ "%.2f"|format(put.ask) }}</td>
                                    <td class="price">${{ "%.2f"|format(put.last) }}</td>
                                    <td class="price">{{ put.volume }}</td>
                                    <td class="price">{{ put.oi }}</td>
                                    <td class="price">{{ "%.1f"|format(put.iv) }}%</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                
            </body>
            </html>
            """,
            symbol=symbol,
            underlying_price=underlying_price,
            expiration=expirations[0] if expirations else "N/A",
            total_expirations=len(expirations),
            calls=calls,
            puts=puts,
        )
        
    except Exception as e:
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }
                    .button { display: inline-block; padding: 10px 20px; background: #00a0dc; color: white; 
                             text-decoration: none; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>❌ Error Fetching Option Chain</h1>
                    <p>Symbol: {{ symbol }}</p>
                    <p>Error: {{ error }}</p>
                </div>
                <a href="/dashboard" class="button">Back to Dashboard</a>
            </body>
            </html>
            """,
            symbol=symbol,
            error=str(e),
        ), 500


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
