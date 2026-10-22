"""Live ATM straddle with VWAP from Fyers, printed to the terminal.

Run on the machine that holds your Fyers credentials (your VPS), during
market hours:

    export FYERS_APP_ID=...        # client id
    export FYERS_ACCESS_TOKEN=...  # today's token (see marketscan.brokers.fyers_auth)
    python scripts/fyers_live_straddle.py --symbol NSE:NIFTY50-INDEX

It finds the ATM call and put, streams both, and prints the straddle price
(call + put) with its session VWAP every few seconds. Ctrl-C to stop.

No key is ever written to disk or logged here; everything is read from the
environment.
"""

from __future__ import annotations

import argparse
import threading
import time

import pandas as pd

from marketscan import straddle
from marketscan.brokers import fyers


def main() -> None:
    p = argparse.ArgumentParser(description="Live ATM straddle VWAP via Fyers")
    p.add_argument("--symbol", default="NSE:NIFTY50-INDEX", help="index/stock symbol")
    p.add_argument("--offset", type=int, default=0, help="strikes away from ATM")
    p.add_argument("--bar", default="1min")
    args = p.parse_args()

    client = fyers.FyersClient()
    picked = client.atm_straddle_symbols(args.symbol, args.offset)
    print(f"Underlying {picked['underlying']}  ATM strike {picked['strike']}")
    print(f"Call {picked['call']}   Put {picked['put']}\n")

    latest: dict[str, dict] = {}
    rows: list[dict] = []
    lock = threading.Lock()

    def on_tick(msg: dict) -> None:
        sym = msg.get("symbol")
        if sym not in (picked["call"], picked["put"]):
            return
        with lock:
            latest[sym] = {"ltp": msg.get("ltp"), "volume": msg.get("vol_traded_today") or msg.get("volume") or 0}
            if picked["call"] in latest and picked["put"] in latest:
                rows.append({
                    "time": pd.Timestamp.now(tz=fyers.FYERS_MARKET_TZ),
                    "straddle": latest[picked["call"]]["ltp"] + latest[picked["put"]]["ltp"],
                    "volume": latest[picked["call"]]["volume"] + latest[picked["put"]]["volume"],
                })

    socket = threading.Thread(
        target=fyers.data_socket, args=(on_tick, [picked["call"], picked["put"]]), daemon=True
    )
    socket.start()

    try:
        while True:
            time.sleep(3)
            with lock:
                if not rows:
                    print("waiting for ticks...")
                    continue
                df = pd.DataFrame(rows)
            bars = df.set_index("time").resample(args.bar).agg(straddle=("straddle", "last"), volume=("volume", "last")).dropna().reset_index()
            if bars.empty:
                continue
            pv = (bars["straddle"] * bars["volume"].diff().fillna(bars["volume"]).clip(lower=0)).cumsum()
            vol = bars["volume"].diff().fillna(bars["volume"]).clip(lower=0).cumsum()
            vwap = (pv / vol).iloc[-1] if vol.iloc[-1] else bars["straddle"].iloc[-1]
            last = bars["straddle"].iloc[-1]
            side = "ABOVE VWAP (premium rising)" if last >= vwap else "below VWAP (decaying)"
            print(f"{bars['time'].iloc[-1]:%H:%M}  straddle {last:8.2f}   vwap {vwap:8.2f}   {side}")
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
