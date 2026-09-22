"""
Run once, manually, to obtain X (Twitter) OAuth 2.0 User Context credentials for .env.
Starts a tiny local server to catch X's redirect automatically.
"""

import base64
import hashlib
import re
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

CLIENT_ID = input("X Client ID: ").strip()
CLIENT_SECRET = input("X Client Secret: ").strip()
REDIRECT_URI = "http://localhost:8081/callback"
SCOPES = "tweet.read tweet.write users.read offline.access"

captured_code: dict[str, str] = {}


def _generate_pkce_pair() -> tuple[str, str]:
    verifier = re.sub(r"[^a-zA-Z0-9]", "", base64.urlsafe_b64encode(secrets.token_bytes(40)).decode())
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    return verifier, challenge


code_verifier, code_challenge = _generate_pkce_pair()


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        code = query.get("code", [None])[0]
        error = query.get("error_description", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if code:
            captured_code["code"] = code
            self.wfile.write(b"<h2>Success! You can close this tab and return to the terminal.</h2>")
        else:
            self.wfile.write(f"<h2>Error: {error or 'no code received'}</h2>".encode())

    def log_message(self, format, *args):
        pass


def _run_server_until_code_received():
    server = HTTPServer(("localhost", 8081), CallbackHandler)
    while "code" not in captured_code:
        server.handle_request()


server_thread = threading.Thread(target=_run_server_until_code_received)
server_thread.start()

auth_url = "https://twitter.com/i/oauth2/authorize?" + urlencode(
    {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": "x-setup",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
)

print(f"\nOpening browser for X login...\nIf it doesn't open automatically, visit:\n{auth_url}\n")
webbrowser.open(auth_url)

server_thread.join(timeout=120)

if "code" not in captured_code:
    raise SystemExit("Timed out waiting for X's redirect. Did you approve access in the browser?")

code = captured_code["code"]
print("Authorization code captured automatically.")

basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

token_response = httpx.post(
    "https://api.x.com/2/oauth2/token",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    },
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {basic_auth}",
    },
)
token_response.raise_for_status()
tokens = token_response.json()

print("\nAdd these to your .env:\n")
print(f"X_CLIENT_ID={CLIENT_ID}")
print(f"X_CLIENT_SECRET={CLIENT_SECRET}")
print(f"X_ACCESS_TOKEN={tokens['access_token']}")
print(f"X_REFRESH_TOKEN={tokens.get('refresh_token', '')}")
