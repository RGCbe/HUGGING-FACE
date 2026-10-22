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

import os


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} is not set. Export it before running this.")
    return value


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


def main() -> None:
    token = generate()
    print("\nAccess token generated. Export it for the connector:\n")
    print("   export FYERS_ACCESS_TOKEN='<the token below>'\n")
    print(token)
    print("\nKeep it private. It expires around 6:30 AM IST; regenerate each morning.")


if __name__ == "__main__":
    main()
