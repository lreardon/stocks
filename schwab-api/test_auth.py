"""Test script to verify Schwab API credentials and authorization flow."""

import os
from dotenv import load_dotenv

load_dotenv()

print("=== Schwab API Configuration Check ===\n")

# Check environment variables
app_key = os.getenv("SCHWAB_APP_KEY")
app_secret = os.getenv("SCHWAB_APP_SECRET")
redirect_uri = os.getenv("SCHWAB_REDIRECT_URI")

print(f"App Key: {app_key[:10]}... (length: {len(app_key) if app_key else 0})")
print(f"App Secret: {'*' * 10}... (length: {len(app_secret) if app_secret else 0})")
print(f"Redirect URI: {redirect_uri}")

if not all([app_key, app_secret, redirect_uri]):
    print("\n❌ ERROR: Missing credentials in .env file")
    exit(1)

# Build authorization URL
auth_url = (
    f"https://api.schwabapi.com/v1/oauth/authorize"
    f"?client_id={app_key}"
    f"&redirect_uri={redirect_uri}"
    f"&response_type=code"
)

print(f"\n=== Authorization Instructions ===\n")
print("1. Copy this URL and open it in your browser:")
print(f"\n{auth_url}\n")
print("2. Log in with your Schwab credentials")
print("3. Authorize the app")
print("4. After redirect, copy the FULL URL from your browser")
print("   (It will look like: https://127.0.0.1:8080/callback?code=...)")
print("5. The page won't load - that's OK! Just copy the URL from the address bar")
print("\nNote: If you get an error when logging in, your account may need")
print("API access enabled. Contact Schwab support to enable it.")
