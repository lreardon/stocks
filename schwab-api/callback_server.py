#!/usr/bin/env python3
"""Simple local callback server for OAuth flow."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback and display the authorization code."""

    def do_GET(self):
        """Handle GET request with authorization code."""
        # Parse the query string
        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params:
            auth_code = params["code"][0]
            # Send success page with the code
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = f"""
            <html>
            <head><title>Authorization Successful</title></head>
            <body style="font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
                <h1 style="color: #00a0dc;">✅ Authorization Successful!</h1>
                <p>Authorization code received:</p>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; word-break: break-all; font-family: monospace;">
                    {auth_code}
                </div>
                <p style="color: #666; margin-top: 20px;">
                    You can close this window and return to your terminal.
                </p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            print(f"\n✅ Authorization code received: {auth_code[:30]}...")
            print("   (Displayed in browser)")
        else:
            # Send error page
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            error_html = """
            <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: Arial, sans-serif; padding: 40px;">
                <h1 style="color: #dc3545;">Authorization Failed</h1>
                <p>No authorization code received in the callback.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
            print("\nNo authorization code received")

    def log_message(self, format, *args):
        """Custom logging."""
        return  # Suppress default logging


def start_server(host="127.0.0.1", port=8080):
    """Start the callback server."""
    server = HTTPServer((host, port), CallbackHandler)
    print(f"🚀 Callback server running on http://{host}:{port}")
    print(f"📍 Callback URL: http://{host}:{port}/callback")
    print()
    print("⏳ Waiting for OAuth callback...")
    print("   (Complete the authorization in your browser)")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        server.shutdown()


if __name__ == "__main__":
    start_server()
