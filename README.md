# spotify-oauth-python

A Python library for authenticating with the Spotify Web API, supporting Authorization Code, Client Credentials, Implicit Grant, and PKCE flows.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Authentication Flows](#authentication-flows)
  - [Authorization Code Flow](#1-authorization-code-flow)
  - [Client Credentials Flow](#2-client-credentials-flow)
  - [Implicit Grant Flow](#3-implicit-grant-flow)
  - [PKCE Flow](#4-pkce-flow)
- [Which Flow Should I Use?](#which-flow-should-i-use)
- [Setup](#setup)
- [Notes](#notes)

---

## Requirements

- Python 3.7+
- Google Chrome + [ChromeDriver](https://chromedriver.chromium.org/) (required for flows that open a browser)
- A [Spotify Developer App](https://developer.spotify.com/dashboard) with a registered redirect URI

Install dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt**
```
selenium
requests
```

---

## Installation

```bash
git clone https://github.com/your-username/spotify-oauth-python.git
cd spotify-oauth-python
pip install -r requirements.txt
```

---

## Authentication Flows

### 1. Authorization Code Flow

Best for server-side applications that need long-lived access and can securely store a client secret.

```python
from OAuth import AuthCodeFlow

auth = AuthCodeFlow(id="your_client_id", secret="your_client_secret")

# Step 1: Get authorization code (opens browser for user login)
response = auth.user_auth(
    redirect_url="http://localhost:8888/callback",
    scope="user-read-private user-read-email"
)
auth_code = response["code"]

# Step 2: Exchange code for access token
token = auth.acs_token(
    redirect_url="http://localhost:8888/callback",
    auth_code=auth_code
)
print(token)
# {"access_token": "...", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "..."}

# Step 3: Refresh the access token when it expires
refreshed = auth.acs_token(
    redirect_url="http://localhost:8888/callback",
    refresh_token=token["refresh_token"]
)
print(refreshed)
```

---

### 2. Client Credentials Flow

Best for server-to-server requests that don't require user authorization (e.g. fetching public playlist data).

```python
from OAuth import ClientCredentials

auth = ClientCredentials(id="your_client_id", secret="your_client_secret")

token = auth.acs_token()
print(token)
# {"access_token": "...", "token_type": "Bearer", "expires_in": 3600}
```

---

### 3. Implicit Grant Flow

> ⚠️ **Deprecated by Spotify.** This flow is no longer recommended. Use the [PKCE Flow](#4-pkce-flow) instead for client-side or mobile applications.

```python
from OAuth import ImplicitGrant

auth = ImplicitGrant(id="your_client_id")

# Opens browser for user login and returns access token directly
response = auth.acs_token(
    redirect_url="http://localhost:8888/callback",
    scope="user-read-private"
)
print(response)
# {"access_token": "...", "token_type": "Bearer", "expires_in": "3600"}
```

---

### 4. PKCE Flow

> ⚠️ **Not yet functional.** This flow is still under development and is not ready for use.

Best for client-side or mobile applications where storing a client secret is not safe. Uses a code verifier and code challenge instead of a secret.

```python
from OAuth import PCKEFlow

auth = PCKEFlow(id="your_client_id")

# Step 1: Generate a code verifier and challenge
code_verifier = auth.gen_random_str(64)   # Length must be between 43–128
code_challenge = auth.hash_str(code_verifier)

# Step 2: Get authorization code (opens browser for user login)
response = auth.usr_auth(
    redirect_url="http://localhost:8888/callback",
    hash_value=code_challenge,
    scope="user-read-private user-read-email"
)
auth_code = response["code"]

# Step 3: Exchange code for access token
auth.acs_token(
    code=auth_code,
    redirect_url="http://localhost:8888/callback",
    random_text=code_verifier
)
```

---

## Which Flow Should I Use?

| Flow | Use Case | Requires Secret |
|---|---|---|
| Authorization Code | Server-side apps, long-lived access | Yes |
| Client Credentials | Server-to-server, no user context | Yes |
| Implicit Grant | ⚠️ Deprecated — avoid | No |
| PKCE | Client-side / mobile apps (⚠️ not yet functional) | No |

---

## Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app.
2. Copy your **Client ID** and **Client Secret**.
3. Add your redirect URI (e.g. `http://localhost:8888/callback`) under the app settings.
4. Store your credentials securely using environment variables:

```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

Then load them in Python:

```python
import os
client_id = os.environ.get("SPOTIFY_CLIENT_ID")
client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
```

> ⚠️ Never hardcode your credentials directly in source code or commit them to version control.

---

## Notes

- Flows that require user login (Authorization Code, Implicit Grant, PKCE) will open a Chrome browser window automatically via Selenium.
- Make sure your ChromeDriver version matches your installed version of Chrome. See [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads).
- The redirect URI used in any method call must exactly match the one registered in your Spotify app settings.
