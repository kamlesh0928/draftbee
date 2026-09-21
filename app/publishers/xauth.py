import base64
import hashlib
import multiprocessing
import os
import re
import time
from threading import Timer

from flask import Flask, redirect, request, session
from requests_oauthlib import OAuth2Session
from werkzeug.serving import run_simple

from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("xauth")

# Constants for configuration
FLASK_PORT = 5001
X_REDIRECT_URI = f"http://localhost:{FLASK_PORT}/oauth/callback"  # Must be set in X Developer Console
X_AUTH_URL = "https://twitter.com/i/oauth2/authorize"
X_TOKEN_URL = "https://api.x.com/2/oauth2/token"
X_SCOPES = ["tweet.read", "users.read", "tweet.write", "offline.access"]

def run_token_server(q: multiprocessing.Queue,
                     client_id: str,
                     client_secret: str,
                     redirect_uri: str,
                     auth_url: str,
                     token_url: str,
                     scopes: list,
                     port: int) -> None:
    """Run a minimal Flask server that captures the token and puts it on a queue."""
    app = Flask(__name__)
    app.secret_key = os.urandom(50)

    def _generate_pkce():
        """Generate a PKCE code verifier and challenge."""
        code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
        code_verifier = re.sub(r"[^a-zA-Z0-9]+", "", code_verifier)
        challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(challenge).decode("utf-8").replace("=", "")
        return code_verifier, code_challenge

    @app.route("/")
    def auth_start():
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
        code_verifier, code_challenge = _generate_pkce()
        authorization_url, state = oauth.authorization_url(
            auth_url,
            code_challenge=code_challenge,
            code_challenge_method="S256"
        )
        # Store PKCE values in session
        session["oauth_state"] = state
        session["code_verifier"] = code_verifier
        return redirect(authorization_url)

    @app.route("/oauth/callback")
    def auth_callback():
        code = request.args.get("code")
        if not code:
            return "Error: No code provided", 400

        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
        token = oauth.fetch_token(
            token_url,
            client_secret=client_secret,
            code_verifier=session.get("code_verifier"),
            code=code
        )
        token["expires_at"] = time.time() + token["expires_in"]

        # Put the token on the queue so the main process can receive it.
        q.put(token)

        # Return a response first so the browser sees a success message.
        response = "Authentication successful! You can now close this window."
        
        # Schedule a delayed shutdown of the server to allow the response to be sent.
        Timer(1.0, lambda: os._exit(0)).start()
        return response, 200

    run_simple("localhost", port, app)

class XAuth:
    def __init__(self):
        self.client_id = settings.X_CLIENT_ID
        self.client_secret = settings.X_CLIENT_SECRET
        self.redirect_uri = X_REDIRECT_URI

        self.auth_url = X_AUTH_URL
        self.token_url = X_TOKEN_URL
        self.scopes = X_SCOPES


    def _make_oauth_session(self):
        return OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scopes
        )

    def get_access_token(self):
        """
        Get a valid access token. If no token is stored, start the token server
        in a separate process to capture the token from the OAuth callback.
        """
        token = None
        if not token:
            logger.info("No token found. Starting authentication using multiprocessing...")
            q = multiprocessing.Queue()
            p = multiprocessing.Process(
                target=run_token_server,
                args=(
                    q,
                    self.client_id,
                    self.client_secret,
                    self.redirect_uri,
                    self.auth_url,
                    self.token_url,
                    self.scopes,
                    FLASK_PORT
                )
            )
            p.start()
            print(f"Visit http://localhost:{FLASK_PORT} to authorize your app.")
            print("Access token", token["access_token"])
            return token["access_token"]

        if time.time() >= token.get("expires_at", 0):
            logger.info("Token expired. Refreshing...")
            token = self._refresh_token()

        print("Access token", token["access_token"])
        return token["access_token"] if token else None
