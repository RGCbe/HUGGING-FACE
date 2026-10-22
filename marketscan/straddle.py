"""Straddle price and straddle VWAP.

A straddle is one call plus one put at the same strike. Its price is
``call + put``; its VWAP weights that price by the traded volume.

* ``eod_straddles`` builds a daily history from NSE's free F&O file: for each
  day it picks the at-the-money strike of an expiry and reports the straddle
  close and the straddle's daily VWAP (each leg's traded value divided by its
  traded quantity, net of the strike, because NSE reports option turnover as
  ``(strike + premium) x quantity``).
* ``intraday_straddle`` works on intraday bars from any source (a broker
  feed later) and returns the running straddle price with its session VWAP.
"""

from __future__ import annotations

import pandas as pd


def _atm_strike(chain: pd.DataFrame, underlying: float) -> float:
    strikes = chain["strike"].unique()
    return float(min(strikes, key=lambda k: abs(k - underlying)))


def leg_vwap(row: pd.Series) -> float:
    qty = row["contracts"] * row["lot_size"]
    if not qty:
        return float("nan")
    return row["notional"] / qty - row["strike"]


def eod_straddles(fo: pd.DataFrame, symbol: str = "NIFTY", expiry_rank: int = 0, strike_offset: int = 0) -> pd.DataFrame:
    """Daily ATM straddle for ``symbol``.

    ``expiry_rank`` 0 is the nearest expiry, 1 the next one. ``strike_offset``
    moves the strike that many steps above (+) or below (-) the ATM strike.
    """
    opts = fo[(fo["symbol"] == symbol) & fo["option_type"].isin(["CE", "PE"])]
    rows = []
    for day, chain in opts.groupby("date"):
        expiries = sorted(e for e in chain["expiry"].unique() if e >= day)
        if len(expiries) <= expiry_rank:
            continue
        exp = expiries[expiry_rank]
        c = chain[chain["expiry"] == exp]
        underlying = float(c["underlying"].iloc[0])
        strikes = sorted(c["strike"].unique())
        atm = _atm_strike(c, underlying)
        idx = strikes.index(atm) + strike_offset
        if not 0 <= idx < len(strikes):
            continue
        k = strikes[idx]
        ce = c[(c["strike"] == k) & (c["option_type"] == "CE")]
        pe = c[(c["strike"] == k) & (c["option_type"] == "PE")]
        if ce.empty or pe.empty:
            continue
        ce, pe = ce.iloc[0], pe.iloc[0]
        rows.append(
            {
                "date": day,
                "expiry": exp,
                "underlying": underlying,
                "strike": k,
                "call_close": ce["close"],
                "put_close": pe["close"],
                "straddle_close": ce["close"] + pe["close"],
                "straddle_open": ce["open"] + pe["open"],
                "straddle_vwap": leg_vwap(ce) + leg_vwap(pe),
                "call_oi": ce["oi"],
                "put_oi": pe["oi"],
                "pcr_oi": pe["oi"] / ce["oi"] if ce["oi"] else float("nan"),
            }
        )
    out = pd.DataFrame(rows)
    if len(out):
        out["above_vwap"] = out["straddle_close"] > out["straddle_vwap"]
    return out


def dual_straddle(fo: pd.DataFrame, symbol: str = "NIFTY") -> pd.DataFrame:
    """Near-expiry and next-expiry ATM straddles side by side."""
    near = eod_straddles(fo, symbol, expiry_rank=0).set_index("date")
    nxt = eod_straddles(fo, symbol, expiry_rank=1).set_index("date")
    return near.join(nxt, lsuffix="_near", rsuffix="_next", how="inner").reset_index()


def intraday_straddle(call_bars: pd.DataFrame, put_bars: pd.DataFrame) -> pd.DataFrame:
    """Combine call and put bars (``time, close, volume``) into a straddle with VWAP.

    The VWAP restarts each session, uses the combined volume of both legs and
    is cumulative within the day, as on a standard intraday VWAP chart.
    """
    m = call_bars.merge(put_bars, on="time", suffixes=("_call", "_put"))
    m["straddle"] = m["close_call"] + m["close_put"]
    m["volume"] = m["volume_call"] + m["volume_put"]
    session = pd.to_datetime(m["time"]).dt.date
    pv = (m["straddle"] * m["volume"]).groupby(session).cumsum()
    vol = m["volume"].groupby(session).cumsum()
    m["vwap"] = pv / vol
    m["signal"] = (m["straddle"] < m["vwap"]).map({True: "below VWAP (premium decaying)", False: "above VWAP (premium rising)"})
    return m[["time", "close_call", "close_put", "straddle", "volume", "vwap", "signal"]]
