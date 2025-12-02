"""Authentication module for Schwab API OAuth2 flow."""

import json
import os
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv

load_dotenv()


class SchwabAuth:
    """Handles OAuth2 authentication for Schwab API."""

    BASE_AUTH_URL = "https://api.schwabapi.com/v1/oauth"
    TOKEN_URL = f"{BASE_AUTH_URL}/token"
    AUTHORIZE_URL = f"{BASE_AUTH_URL}/authorize"

    def __init__(self, token_file: str = None):
        """Initialize auth handler.

        Args:
            token_file: Path to store/load tokens. Defaults to TOKEN_FILE env var.
        """
        self.app_key = os.getenv("SCHWAB_APP_KEY")
        self.app_secret = os.getenv("SCHWAB_APP_SECRET")
        self.redirect_uri = os.getenv("SCHWAB_REDIRECT_URI")
        self.token_file = token_file or os.getenv("TOKEN_FILE", "tokens/schwab_token.json")

        if not all([self.app_key, self.app_secret, self.redirect_uri]):
            raise ValueError("Missing required environment variables. Check .env file.")

        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

        # Load existing token if available
        self._load_token()

    def _load_token(self):
        """Load token from file if it exists."""
        if not Path(self.token_file).exists():
            return

        with open(self.token_file, "r") as f:
            data = json.load(f)
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            expiry_str = data.get("expiry")
            if expiry_str:
                self.token_expiry = datetime.fromisoformat(expiry_str)

    def _save_token(self):
        """Save token to file."""
        Path(self.token_file).parent.mkdir(parents=True, exist_ok=True)

        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expiry": self.token_expiry.isoformat() if self.token_expiry else None,
        }

        with open(self.token_file, "w") as f:
            json.dump(data, f, indent=2)

    def authorize(self):
        """Start OAuth2 authorization flow. Opens browser for user login."""
        auth_url = (
            f"{self.AUTHORIZE_URL}"
            f"?client_id={self.app_key}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
        )

        print("Opening browser for authorization...")
        print(f"If browser doesn't open, visit: {auth_url}")
        webbrowser.open(auth_url)

        # Get authorization code from user
        callback_url = input("\nPaste the full callback URL here: ").strip()
        auth_code = parse_qs(urlparse(callback_url).query).get("code", [None])[0]

        if not auth_code:
            raise ValueError("No authorization code found in callback URL")

        # Exchange code for tokens
        self.get_tokens(auth_code)
        print("Authorization successful!")

    def get_tokens(self, auth_code: str):
        """Exchange authorization code for access and refresh tokens."""
        # Use Basic Authentication (standard OAuth2 pattern)
        from base64 import b64encode
        
        credentials = f"{self.app_key}:{self.app_secret}"
        encoded_credentials = b64encode(credentials.encode()).decode()
        
        response = requests.post(
            self.TOKEN_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}",
            },
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
            },
        )
        
        # Better error handling
        if not response.ok:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = f"{error_json.get('error', 'Unknown')}: {error_json.get('error_description', error_detail)}"
            except:
                pass
            raise Exception(f"Token exchange failed: {response.status_code} - {error_detail}")
        
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        expires_in = data["expires_in"]
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

        self._save_token()

    def refresh_access_token(self):
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            raise ValueError("No refresh token available. Run authorize() first.")

        # Use Basic Authentication
        from base64 import b64encode
        
        credentials = f"{self.app_key}:{self.app_secret}"
        encoded_credentials = b64encode(credentials.encode()).decode()
        
        response = requests.post(
            self.TOKEN_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]
        expires_in = data["expires_in"]
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

        self._save_token()

    def get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary.

        Returns:
            Valid access token string.
        """
        if not self.access_token:
            raise ValueError("Not authorized. Run authorize() first.")

        # Refresh if token expires in less than 5 minutes
        if self.token_expiry and datetime.now() >= self.token_expiry - timedelta(minutes=5):
            self.refresh_access_token()

        return self.access_token
