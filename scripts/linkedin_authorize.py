import webbrowser
from urllib.parse import urlencode

import httpx

CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "https://www.linkedin.com/developers/tools/oauth/redirect"

auth_url = "https://www.linkedin.com/oauth/v2/authorization?" + urlencode(
    {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email w_member_social",
        "state": "linkedin-setup",
    }
)

print(f"\nOpen this URL, approve access, then paste the ?code=... value from the redirected URL:\n{auth_url}\n")
webbrowser.open(auth_url)

code = input("Authorization code: ").strip()

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
