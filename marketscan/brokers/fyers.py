"""Fyers API v3 connector for live data.

Credentials are read from environment variables and never hard-coded. Set
these on the machine that runs it (for example your VPS), and never commit
them or paste them anywhere:

    FYERS_APP_ID         your app id / client id, e.g. "ABCD1234-100"
    FYERS_ACCESS_TOKEN   the daily access token (expires ~6:30 AM IST)

Optionally, to generate the daily token non-interactively:

    FYERS_SECRET_ID      your app secret
    FYERS_REDIRECT_URI   the redirect URL configured for the app

This module imports the ``fyers_apiv3`` SDK lazily, so the rest of the package
(scanners, tests) works without it installed. Install it on the VPS with
``pip install fyers-apiv3``.

Nothing here logs the token or secret.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd

FYERS_MARKET_TZ = "Asia/Kolkata"


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Export your Fyers credentials in the environment "
            "that runs this (e.g. your VPS); do not hard-code or commit them."
        )
    return value


@dataclass
class FyersClient:
    """Thin wrapper over ``fyers_apiv3.fyersModel.FyersModel``.

    Reads FYERS_APP_ID and FYERS_ACCESS_TOKEN from the environment unless
    passed explicitly. ``app_id`` is the client id; ``token`` the daily token.
    """

    app_id: str | None = None
    token: str | None = None

    def __post_init__(self) -> None:
        self.app_id = self.app_id or _require("FYERS_APP_ID")
        self.token = self.token or _require("FYERS_ACCESS_TOKEN")
        self._model = None

    @property
    def model(self):  # lazy: the SDK is only needed at call time
        if self._model is None:
            from fyers_apiv3 import fyersModel

            self._model = fyersModel.FyersModel(
                client_id=self.app_id, token=self.token, is_async=False, log_path=""
            )
        return self._model

    def profile(self) -> dict:
        """Quick auth check; returns the account profile."""
        return self.model.get_profile()

    def quotes(self, symbols: list[str]) -> pd.DataFrame:
        """Snapshot quotes for Fyers symbols like ``NSE:SBIN-EQ``."""
        resp = self.model.quotes({"symbols": ",".join(symbols)})
        rows = []
        for item in resp.get("d", []):
            v = item.get("v", {})
            rows.append({
                "symbol": item.get("n"), "ltp": v.get("lp"), "open": v.get("open_price"),
                "high": v.get("high_price"), "low": v.get("low_price"), "prev_close": v.get("prev_close_price"),
                "volume": v.get("volume"), "bid": v.get("bid"), "ask": v.get("ask"),
            })
        return pd.DataFrame(rows)

    def option_chain(self, symbol: str, strike_count: int = 10) -> dict:
        """Live option chain for an index/stock, e.g. ``NSE:NIFTY50-INDEX``.

        Returns ``{"underlying": float, "rows": DataFrame}`` where each row has
        the tradable option symbol, strike, option_type (CE/PE) and ltp.
        """
        resp = self.model.optionchain({"symbol": symbol, "strikecount": strike_count, "timestamp": ""})
        data = resp.get("data", {})
        chain = data.get("optionsChain", [])
        rows = []
        underlying = None
        for o in chain:
            otype = o.get("option_type")
            if otype not in ("CE", "PE"):
                underlying = o.get("ltp", underlying)  # the index row carries the spot
                continue
            rows.append({
                "symbol": o.get("symbol"), "strike": o.get("strike_price"), "option_type": otype,
                "ltp": o.get("ltp"), "oi": o.get("oi"), "volume": o.get("volume"), "bid": o.get("bid"), "ask": o.get("ask"),
            })
        df = pd.DataFrame(rows)
        if underlying is None and not df.empty:
            underlying = df["strike"].iloc[(df["strike"] - df["ltp"].mean()).abs().argmin()]
        return {"underlying": underlying, "rows": df}

    def atm_straddle_symbols(self, symbol: str = "NSE:NIFTY50-INDEX", offset: int = 0) -> dict:
        """Pick the ATM call and put from the live chain.

        ``offset`` shifts the strike that many steps from the money.
        """
        chain = self.option_chain(symbol, strike_count=max(5, abs(offset) + 3))
        df, underlying = chain["rows"], chain["underlying"]
        if df.empty or underlying is None:
            raise RuntimeError("Option chain returned no rows; check the symbol and market hours.")
        strikes = sorted(df["strike"].unique())
        atm = min(strikes, key=lambda k: abs(k - underlying))
        idx = strikes.index(atm) + offset
        idx = max(0, min(idx, len(strikes) - 1))
        k = strikes[idx]
        ce = df[(df.strike == k) & (df.option_type == "CE")]["symbol"].iloc[0]
        pe = df[(df.strike == k) & (df.option_type == "PE")]["symbol"].iloc[0]
        return {"underlying": underlying, "strike": k, "call": ce, "put": pe}

    def history(self, symbol: str, resolution: str = "1", days: int = 1) -> pd.DataFrame:
        """Intraday OHLCV bars. ``resolution`` in minutes ("1", "5", ...)."""
        from datetime import date, timedelta

        end = date.today()
        start = end - timedelta(days=days)
        resp = self.model.history({
            "symbol": symbol, "resolution": resolution, "date_format": "1",
            "range_from": start.isoformat(), "range_to": end.isoformat(), "cont_flag": "1",
        })
        candles = resp.get("candles", [])
        df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume"])
        if not df.empty:
            df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(FYERS_MARKET_TZ)
        return df


def data_socket(on_tick, symbols: list[str], app_id: str | None = None, token: str | None = None,
                lite: bool = False):
    """Open the v3 data WebSocket and call ``on_tick(message)`` for each update.

    This blocks on the socket's own loop, so run it in its own process or
    thread. ``lite=True`` streams only last-traded price (less bandwidth).
    """
    from fyers_apiv3.FyersWebsocket import data_ws

    app_id = app_id or _require("FYERS_APP_ID")
    token = token or _require("FYERS_ACCESS_TOKEN")

    def on_open():
        fs.subscribe(symbols=symbols, data_type="SymbolUpdate")
        fs.keep_running()

    fs = data_ws.FyersDataSocket(
        access_token=f"{app_id}:{token}", log_path="", litemode=lite,
        on_connect=on_open, on_message=on_tick, on_error=lambda m: None, on_close=lambda m: None,
    )
    fs.connect()
    return fs


def ticks_to_bars(ticks: pd.DataFrame, bar: str = "1min") -> pd.DataFrame:
    """Aggregate streamed ticks (``time, ltp, volume``) into OHLCV bars.

    ``volume`` from the feed is cumulative for the day, so bar volume is the
    increase within the bar. Feed the result's ``close``/``volume`` to the
    straddle or order-flow functions.
    """
    t = ticks.sort_values("time").copy()
    t["bar"] = pd.to_datetime(t["time"]).dt.floor(bar)
    out = t.groupby("bar").agg(open=("ltp", "first"), high=("ltp", "max"), low=("ltp", "min"),
                               close=("ltp", "last"), cum_volume=("volume", "last")).reset_index()
    out["volume"] = out["cum_volume"].diff().fillna(out["cum_volume"]).clip(lower=0)
    return out.rename(columns={"bar": "time"})[["time", "open", "high", "low", "close", "volume"]]
