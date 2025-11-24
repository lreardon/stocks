# Schwab API Project - AI Agent Instructions

## Project Overview

Flask-based web application for executing trades via the Charles Schwab API with focus on options orders. Clean architecture, minimal dependencies, easy to extend.

## Architecture & Components

### Core Modules

- `app.py` - Flask web app with OAuth callbacks and API endpoints
- `schwab_client/auth.py` - OAuth2 authentication, token management, auto-refresh
- `schwab_client/client.py` - Trading operations (place orders, get chains, account info)
- `examples/place_order.py` - Python script examples for direct API usage

### Design Principles

- **Flask-based**: Web interface for OAuth flow and future dashboard features
- **Minimal dependencies**: Flask, requests, python-dotenv
- **Clean separation**: Auth logic separate from trading logic
- **Token persistence**: Tokens saved to `tokens/` (gitignored), auto-refresh before expiry
- **Standard formats**: Option symbols use OCC format (e.g., `AAPL_123456C00150000`)

## Key Development Workflows

### Initial Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your Schwab API credentials to .env
# Get these from https://developer.schwab.com/
# IMPORTANT: Set SCHWAB_REDIRECT_URI=http://127.0.0.1:5000/callback

# 3. Install dependencies (includes Flask)
pip install -e .
```

### Running the Flask App

```bash
# Option 1: Direct Python
python app.py

# Option 2: Bash script
./start_server.sh

# App will:
# - Start on http://127.0.0.1:5000
# - Open browser automatically
# - Handle OAuth flow via web interface
```

### OAuth Authorization Flow

1. Start the Flask app (`python app.py`)
2. Browser opens to `http://127.0.0.1:5000`
3. Click "Authorize with Schwab"
4. Log in to Schwab and authorize
5. Redirects back to app with tokens saved automatically
6. Tokens persist across restarts

### Using the API Programmatically

```python
from schwab_client import SchwabClient

client = SchwabClient()
# Tokens load automatically from file
client.place_option_order(...)
```

### Development Tools

```bash
pip install -e ".[dev]"  # Install dev dependencies
black .                   # Format code
ruff check .              # Lint code
pytest                    # Run tests (when added)
```

## Flask Routes

### Web Interface

- `GET /` - Home page, shows authorization status
- `GET /authorize` - Initiates OAuth flow with Schwab
- `GET /callback` - OAuth callback endpoint (handles authorization code)
- `GET /logout` - Clear tokens and deauthorize

### API Endpoints

- `GET /api/account/<account_id>` - Get account info
  - Query params: `fields` (optional, e.g., "positions")
- `GET /api/options/chain` - Get option chain
  - Query params: `symbol` (required), `contract_type`, `strike_count`, `from_date`, `to_date`
- `POST /api/orders/<account_id>` - Place options order
  - Body: `{"symbol", "option_symbol", "quantity", "instruction", "order_type", "price", "duration"}`
- `GET /api/orders/<account_id>/<order_id>` - Get order status

## Code Conventions

### API Integration Pattern

All API calls go through `SchwabClient._request()` which:

1. Auto-injects Bearer token from `auth.get_access_token()`
2. Refreshes token automatically if expiring soon (< 5 min)
3. Raises exceptions on HTTP errors
4. Returns JSON dict or success indicator

### Authentication Flow

1. **First time**: Visit `/authorize` in Flask app, redirects to Schwab login
2. **After auth**: Tokens saved automatically to `TOKEN_FILE`
3. **Subsequent runs**: Tokens auto-load when creating `SchwabClient()`
4. **Auto-refresh**: Happens in `get_access_token()` when near expiry

### Options Order Structure

Orders use Schwab's exact JSON format:

- `orderType`: MARKET, LIMIT, STOP, STOP_LIMIT
- `instruction`: BUY_TO_OPEN, SELL_TO_OPEN, BUY_TO_CLOSE, SELL_TO_CLOSE
- `duration`: DAY, GTC, etc.
- `orderLegCollection`: List of legs with symbol, quantity, instruction

Example in `client.py` → `place_option_order()`

### Error Handling

- HTTP errors from `requests` raise exceptions immediately
- Flask endpoints catch exceptions and return JSON errors with 500 status
- Validation done early (e.g., LIMIT orders require price)

## External Dependencies

### Schwab API (v1)

- Base URL: `https://api.schwabapi.com/marketdata/v1`
- Auth: OAuth2 with Bearer tokens
- Key endpoints used:
  - `POST /accounts/{id}/orders` - Place orders
  - `GET /accounts/{id}` - Account info
  - `GET /marketdata/chains` - Option chains
  - `GET /accounts/{id}/orders/{orderId}` - Order status

### Environment Variables

See `.env.example` for required vars:

- `SCHWAB_APP_KEY` - OAuth app key
- `SCHWAB_APP_SECRET` - OAuth app secret
- `SCHWAB_REDIRECT_URI` - Must be `http://127.0.0.1:5000/callback` for Flask app
- `TOKEN_FILE` - Where to store tokens (default: `tokens/schwab_token.json`)
- `FLASK_SECRET_KEY` - Flask session secret (optional, auto-generated if not set)

## Security Notes

- Never commit `.env` or `tokens/` directory
- Tokens stored locally with 30-day expiry on refresh tokens
- Use separate app credentials for dev/prod environments
- Flask secret key should be set in production

## Extending the App

The Flask structure makes it easy to add:

- **Web dashboard**: Add routes and templates for viewing positions, orders, etc.
- **Webhooks**: Add POST endpoints for market data alerts
- **Strategy automation**: Add background tasks for algorithmic trading
- **Charts/visualization**: Integrate with charting libraries in web UI
