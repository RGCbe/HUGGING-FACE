"""Hands-off live runner: ensure a token, wait for market open, then stream.

Meant to be started once (by cron, systemd, or by hand) and left alone. It
refreshes the token automatically when stale, waits until the NSE session is
open, runs the live straddle, and idles outside market hours.

Run on the machine that holds your Fyers secrets (your VPS):

    export FYERS_AUTO_LOGIN=1          # allow automated daily login
    export FYERS_APP_ID=... FYERS_SECRET_ID=... FYERS_REDIRECT_URI=...
    export FYERS_FY_ID=... FYERS_PIN=... FYERS_TOTP_SECRET=...
    python scripts/fyers_runner.py --symbol NSE:NIFTY50-INDEX

Nothing here logs a secret.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
OPEN, CLOSE = dtime(9, 15), dtime(15, 30)


def market_open(now: datetime | None = None) -> bool:
    now = now or datetime.now(IST)
    return now.weekday() < 5 and OPEN <= now.time() <= CLOSE


def wait_seconds(now: datetime | None = None) -> int:
    """How long to sleep while closed: until today's open if it's still ahead,
    otherwise re-check in 15 minutes (keeps the loop simple and robust)."""
    now = now or datetime.now(IST)
    if now.weekday() < 5 and now.time() < OPEN:
        return max(60, int((now.replace(hour=OPEN.hour, minute=OPEN.minute, second=0, microsecond=0) - now).total_seconds()))
    return 15 * 60


def main() -> None:
    p = argparse.ArgumentParser(description="Hands-off live straddle runner")
    p.add_argument("--symbol", default="NSE:NIFTY50-INDEX")
    p.add_argument("--offset", type=int, default=0)
    args = p.parse_args()

    from marketscan.brokers import fyers_auth

    while True:
        if not market_open():
            wait = wait_seconds()
            print(f"{datetime.now(IST):%Y-%m-%d %H:%M} IST - market closed; sleeping {wait // 60} min")
            time.sleep(wait)
            continue

        # Make sure today's token exists before the stream starts.
        try:
            fyers_auth.ensure_token(auto=True)
        except SystemExit as e:
            print(f"token error: {e}; retrying in 5 min")
            time.sleep(300)
            continue

        print(f"{datetime.now(IST):%H:%M} IST - market open; starting live straddle")
        proc = subprocess.Popen(
            [sys.executable, "scripts/fyers_live_straddle.py", "--symbol", args.symbol, "--offset", str(args.offset)]
        )
        # Run until the close, then stop and loop back to the waiting state.
        while market_open() and proc.poll() is None:
            time.sleep(30)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        print(f"{datetime.now(IST):%H:%M} IST - session ended")


if __name__ == "__main__":
    main()
