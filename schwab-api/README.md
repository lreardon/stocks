# Schwab API Trading Client

A clean, minimal Flask web application for executing trades via the Charles Schwab API, with focus on options orders.

## Setup

1. **Get Schwab API Credentials**
   - Register at https://developer.schwab.com/
   - Create an app to get your App Key and Secret
   - Set redirect URI to: `http://127.0.0.1:5000/callback`

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Install Dependencies**
   ```bash
   pip install -e .
   ```

4. **Start the App**
   ```bash
   python app.py
   # or
   ./start_server.sh
   ```

5. **Authorize**
   - Browser opens automatically to http://127.0.0.1:5000
   - Click "Authorize with Schwab"
   - Log in and approve
   - You'll be redirected to the Dashboard

## Usage

### Web Dashboard

After authorization, the dashboard shows:
- API endpoint documentation
- Python client usage examples
- Your token status

### Python Client

```python
from schwab_client import SchwabClient

# Initialize client (loads saved tokens automatically)
client = SchwabClient()

# Place an options order
order = client.place_option_order(
    account_id="your_account_id",
    symbol="AAPL",
    option_symbol="AAPL_123456C00150000",  # Standard OCC format
    quantity=1,
    instruction="BUY_TO_OPEN",
    order_type="LIMIT",
    price=5.50
)
```

### API Endpoints

The Flask app exposes REST endpoints:

- `GET /api/account/<account_id>?fields=positions`
- `GET /api/options/chain?symbol=AAPL&contract_type=CALL`
- `POST /api/orders/<account_id>` - Place order
- `GET /api/orders/<account_id>/<order_id>` - Check status

## Project Structure

```
schwab-api/
├── schwab_client/
│   ├── __init__.py
│   ├── auth.py          # OAuth2 authentication
│   ├── client.py        # Main trading client
│   └── models.py        # Data models for orders
├── examples/
│   └── place_order.py   # Example usage
├── .env.example         # Environment template
└── pyproject.toml       # Project config
```

## Architecture

- **auth.py**: Handles OAuth2 flow, token refresh, and credential management
- **client.py**: Core API client with methods for placing options orders
- **models.py**: Clean data structures for order construction

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Format code
black .

# Lint
ruff check .

# Run tests
pytest
```

## Security Notes

- Never commit `.env` or token files
- Tokens are stored locally in `tokens/` (gitignored)
- Use environment variables for all credentials
