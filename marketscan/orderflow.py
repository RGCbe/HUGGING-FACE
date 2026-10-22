"""Order flow and footprint charts from trade ticks.

Input is a tick table with ``time``, ``price`` and ``qty`` and, when the feed
provides them, the best ``bid`` and ``ask`` at the time of the trade.

Each trade is labelled as buyer- or seller-initiated:

* quote rule (when bid/ask exist): at or above the ask is a buy, at or below
  the bid is a sell;
* tick rule (otherwise, or between bid and ask): a higher price than the last
  different price is a buy, a lower one a sell.

Trades are then grouped into time bars and price rows. Each cell holds the
volume sold at the bid and bought at the ask, which is what a footprint chart
draws. Free NSE data has no ticks, so this needs a broker feed or a CSV
export; ``synthetic_ticks`` produces demo data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def classify(ticks: pd.DataFrame) -> pd.DataFrame:
    t = ticks.sort_values("time").reset_index(drop=True).copy()
    diff = t["price"].diff()
    tick_side = np.sign(diff).replace(0, np.nan).ffill().fillna(1)
    side = tick_side.copy()
    if {"bid", "ask"} <= set(t.columns):
        side = np.where(t["price"] >= t["ask"], 1, np.where(t["price"] <= t["bid"], -1, tick_side))
    t["side"] = np.asarray(side, dtype=int)
    t["buy_qty"] = np.where(t["side"] > 0, t["qty"], 0)
    t["sell_qty"] = np.where(t["side"] < 0, t["qty"], 0)
    return t


def footprint(ticks: pd.DataFrame, bar: str = "5min", tick_size: float = 0.05, row_ticks: int = 1) -> pd.DataFrame:
    """One row per (bar, price level) with bid/ask volume and delta."""
    t = classify(ticks)
    step = tick_size * row_ticks
    t["bar"] = pd.to_datetime(t["time"]).dt.floor(bar)
    t["level"] = (np.floor(t["price"] / step + 1e-9) * step).round(6)
    fp = t.groupby(["bar", "level"]).agg(bid_vol=("sell_qty", "sum"), ask_vol=("buy_qty", "sum")).reset_index()
    fp["total"] = fp["bid_vol"] + fp["ask_vol"]
    fp["delta"] = fp["ask_vol"] - fp["bid_vol"]
    return fp


def imbalances(fp: pd.DataFrame, ratio: float = 3.0, min_volume: float = 1) -> pd.DataFrame:
    """Diagonal imbalances: ask volume at a price versus bid volume one row lower.

    ``buy_imbalance`` marks aggressive buying, ``sell_imbalance`` aggressive
    selling. Three or more stacked in a row usually mark a strong level.
    """
    out = []
    for bar, g in fp.sort_values("level").groupby("bar"):
        g = g.reset_index(drop=True)
        below_bid = g["bid_vol"].shift(1).fillna(0)
        above_ask = g["ask_vol"].shift(-1).fillna(0)
        g["buy_imbalance"] = (g["ask_vol"] >= min_volume) & (g["ask_vol"] >= ratio * below_bid.clip(lower=1))
        g["sell_imbalance"] = (g["bid_vol"] >= min_volume) & (g["bid_vol"] >= ratio * above_ask.clip(lower=1))
        out.append(g)
    return pd.concat(out, ignore_index=True) if out else fp.assign(buy_imbalance=False, sell_imbalance=False)


def bar_summary(ticks: pd.DataFrame, bar: str = "5min", tick_size: float = 0.05) -> pd.DataFrame:
    """OHLC, volume, delta, cumulative delta and point of control per bar."""
    t = classify(ticks)
    t["bar"] = pd.to_datetime(t["time"]).dt.floor(bar)
    ohlc = t.groupby("bar")["price"].agg(open="first", high="max", low="min", close="last")
    flow = t.groupby("bar").agg(volume=("qty", "sum"), buy=("buy_qty", "sum"), sell=("sell_qty", "sum"))
    out = ohlc.join(flow)
    out["delta"] = out["buy"] - out["sell"]
    out["cum_delta"] = out["delta"].cumsum()
    fp = footprint(ticks, bar, tick_size)
    poc = fp.loc[fp.groupby("bar")["total"].idxmax(), ["bar", "level"]].set_index("bar")["level"]
    out["poc"] = poc
    out["vwap"] = (t["price"] * t["qty"]).groupby(t["bar"]).sum().cumsum() / flow["volume"].cumsum()
    return out.reset_index()


def volume_profile(ticks: pd.DataFrame, tick_size: float = 0.05, row_ticks: int = 4, value_area: float = 0.7) -> dict:
    """Session volume profile with POC and value area (VAH/VAL)."""
    t = classify(ticks)
    step = tick_size * row_ticks
    levels = (np.floor(t["price"] / step + 1e-9) * step).round(6)
    prof = t.groupby(levels).agg(volume=("qty", "sum"), buy=("buy_qty", "sum"), sell=("sell_qty", "sum")).sort_index()
    poc = float(prof["volume"].idxmax())
    order = prof.index.tolist()
    i = lo = hi = order.index(poc)
    covered, target = prof["volume"].iloc[i], prof["volume"].sum() * value_area
    while covered < target and (lo > 0 or hi < len(order) - 1):
        up = prof["volume"].iloc[hi + 1] if hi < len(order) - 1 else -1
        down = prof["volume"].iloc[lo - 1] if lo > 0 else -1
        if up >= down:
            hi += 1
            covered += up
        else:
            lo -= 1
            covered += down
    return {"profile": prof.reset_index(names="level"), "poc": poc, "vah": float(order[hi]), "val": float(order[lo])}


def synthetic_ticks(start: str = "2026-10-21 09:15", minutes: int = 60, price: float = 22800.0, seed: int = 7) -> pd.DataFrame:
    """Random-walk ticks with a bid/ask, for demos and tests."""
    rng = np.random.default_rng(seed)
    n = minutes * 30
    times = pd.Timestamp(start) + pd.to_timedelta(np.sort(rng.uniform(0, minutes * 60, n)), unit="s")
    steps = rng.choice([-0.05, 0, 0.05], size=n, p=[0.32, 0.36, 0.32]) * rng.integers(1, 6, n)
    prices = np.round(price + np.cumsum(steps), 2)
    spread = 0.05
    side = rng.choice([1, -1], n)
    trade = np.round(np.where(side > 0, prices + spread / 2, prices - spread / 2), 2)
    return pd.DataFrame(
        {"time": times, "price": trade, "qty": rng.integers(1, 20, n) * 65, "bid": prices - spread / 2, "ask": prices + spread / 2}
    )
