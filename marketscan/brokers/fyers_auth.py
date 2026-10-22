"""Generate a Fyers v3 daily access token.

The token expires about 6:30 AM IST each day, so you refresh it each morning.
Run this on the machine that holds your credentials (your VPS). It reads the
app id, secret and redirect URI from the environment and prints only the token
— it never logs the secret.

    export FYERS_APP_ID="ABCD1234-100"
    export FYERS_SECRET_ID="xxxxxxxx"
    export FYERS_REDIRECT_URI="https://127.0.0.1/"
    python -m marketscan.brokers.fyers_auth

It prints a login URL. Open it, log in, and paste the `auth_code` from the
redirected URL back in. The resulting token can be exported as
FYERS_ACCESS_TOKEN for the connector, or saved to a file only you can read.
"""

from __future__ import annotations

import base64
import json
import os
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse

VAGATOR = "https://api-t2.fyers.in/vagator/v2"
TOKEN_API = "https://api-t1.fyers.in/api/v3/token"


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} is not set. Export it before running this.")
    return value


def token_path() -> Path:
    """Where the daily token is cached (override with FYERS_TOKEN_FILE)."""
    return Path(os.environ.get("FYERS_TOKEN_FILE", str(Path.home() / ".fyers_token.json")))


def cached_token() -> str | None:
    """Return today's saved token, or None if missing or stale."""
    path = token_path()
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if data.get("date") == date.today().isoformat() and data.get("token"):
        return data["token"]
    return None


def save_token(token: str) -> None:
    path = token_path()
    path.write_text(json.dumps({"date": date.today().isoformat(), "token": token}))
    try:
        path.chmod(0o600)  # owner-only; it can trade on your account
    except OSError:
        pass


def _b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def generate(auth_code: str | None = None) -> str:
    from fyers_apiv3 import fyersModel

    session = fyersModel.SessionModel(
        client_id=_require("FYERS_APP_ID"),
        secret_key=_require("FYERS_SECRET_ID"),
        redirect_uri=_require("FYERS_REDIRECT_URI"),
        response_type="code",
        grant_type="authorization_code",
    )
    if auth_code is None:
        print("1. Open this URL, log in, and copy the auth_code from the redirected URL:\n")
        print("   " + session.generate_authcode() + "\n")
        auth_code = input("2. Paste auth_code here: ").strip()
    session.set_token(auth_code)
    resp = session.generate_token()
    token = resp.get("access_token")
    if not token:
        raise SystemExit(f"Token generation failed: {resp}")
    return token


def auto_token() -> str:
    """Generate the daily token with no browser, using stored login secrets.

    Needs these in the environment (keep them on the VPS only):

        FYERS_APP_ID         client id, e.g. "ABCD1234-100"
        FYERS_SECRET_ID      app secret
        FYERS_REDIRECT_URI   the app's redirect URL
        FYERS_FY_ID          your Fyers login id
        FYERS_PIN            your 4-digit app PIN
        FYERS_TOTP_SECRET    the TOTP seed from your authenticator setup

    This drives Fyers' own login endpoints. They are not part of the public
    API contract and can change; if a step fails, fall back to the interactive
    ``generate()`` or a maintained helper. Nothing here logs a secret.
    """
    import pyotp
    import requests
    from fyers_apiv3 import fyersModel

    fy_id = _require("FYERS_FY_ID")
    s = requests.Session()
    r = s.post(f"{VAGATOR}/send_login_otp_v2", json={"fy_id": _b64(fy_id), "app_id": "2"})
    r.raise_for_status()
    request_key = r.json()["request_key"]

    otp = pyotp.TOTP(_require("FYERS_TOTP_SECRET")).now()
    r = s.post(f"{VAGATOR}/verify_otp", json={"request_key": request_key, "otp": otp})
    r.raise_for_status()
    request_key = r.json()["request_key"]

    r = s.post(f"{VAGATOR}/verify_pin", json={
        "request_key": request_key, "identity_type": "pin", "identifier": _b64(_require("FYERS_PIN"))})
    r.raise_for_status()
    bearer = r.json()["data"]["access_token"]

    app_id = _require("FYERS_APP_ID")
    base_app, app_type = (app_id.split("-") + ["100"])[:2]
    r = s.post(TOKEN_API, headers={"authorization": f"Bearer {bearer}"}, json={
        "fyers_id": fy_id, "app_id": base_app, "redirect_uri": _require("FYERS_REDIRECT_URI"),
        "appType": app_type, "code_challenge": "", "state": "sample", "scope": "",
        "nonce": "", "response_type": "code", "create_cookie": True})
    r.raise_for_status()
    auth_code = parse_qs(urlparse(r.json()["Url"]).query)["auth_code"][0]

    session = fyersModel.SessionModel(
        client_id=app_id, secret_key=_require("FYERS_SECRET_ID"), redirect_uri=_require("FYERS_REDIRECT_URI"),
        response_type="code", grant_type="authorization_code")
    session.set_token(auth_code)
    resp = session.generate_token()
    token = resp.get("access_token")
    if not token:
        raise SystemExit(f"Token exchange failed: {resp}")
    return token


def ensure_token(auto: bool = True) -> str:
    """Return a valid token for today, generating and caching one if needed.

    Order: a cached token from today, then FYERS_ACCESS_TOKEN from the
    environment, then (if ``auto``) a fresh automated login.
    """
    token = cached_token()
    if token:
        return token
    token = os.environ.get("FYERS_ACCESS_TOKEN")
    if token:
        save_token(token)
        return token
    if auto:
        token = auto_token()
        save_token(token)
        return token
    raise SystemExit("No valid token. Run `python -m marketscan.brokers.fyers_auth` first.")


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Generate and cache a Fyers daily token")
    p.add_argument("--auto", action="store_true", help="log in automatically using stored secrets")
    args = p.parse_args()
    token = auto_token() if args.auto else generate()
    save_token(token)
    print(f"\nToken saved to {token_path()} (today only; regenerate each morning).")
    if not args.auto:
        print("For the connector in this shell you can also:  export FYERS_ACCESS_TOKEN='<token>'")


if __name__ == "__main__":
    main()
