"""
Run once, manually, to obtain LinkedIn OAuth credentials for .env.
Starts a tiny local server to catch LinkedIn's redirect automatically.
"""

import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import httpx

CLIENT_ID = input("LinkedIn Client ID: ").strip()
CLIENT_SECRET = input("LinkedIn Client Secret: ").strip()
REDIRECT_URI = "http://localhost:8080/callback"

captured_code: dict[str, str] = {}


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
        pass  # silence default request logging


def _run_server_until_code_received():
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    while "code" not in captured_code:
        server.handle_request()


server_thread = threading.Thread(target=_run_server_until_code_received)
server_thread.start()

auth_url = "https://www.linkedin.com/oauth/v2/authorization?" + urlencode(
    {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email w_member_social",
        "state": "linkedin-setup",
    }
)

print(f"\nOpening browser for LinkedIn login...\nIf it doesn't open automatically, visit:\n{auth_url}\n")
webbrowser.open(auth_url)

server_thread.join(timeout=120)

if "code" not in captured_code:
    raise SystemExit("Timed out waiting for LinkedIn's redirect. Did you approve access in the browser?")

code = captured_code["code"]
print("Authorization code captured automatically.")

token_response = httpx.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
token_response.raise_for_status()
tokens = token_response.json()

userinfo_response = httpx.get(
    "https://api.linkedin.com/v2/userinfo",
    headers={"Authorization": f"Bearer {tokens['access_token']}"},
)
userinfo_response.raise_for_status()
person_id = userinfo_response.json()["sub"]

print("\nAdd these to your .env:\n")
print(f"LINKEDIN_CLIENT_ID={CLIENT_ID}")
print(f"LINKEDIN_CLIENT_SECRET={CLIENT_SECRET}")
print(f"LINKEDIN_ACCESS_TOKEN={tokens['access_token']}")
print(f"LINKEDIN_REFRESH_TOKEN={tokens.get('refresh_token', '')}")
print(f"LINKEDIN_PERSON_ID={person_id}")
print("LINKEDIN_API_VERSION=202401")