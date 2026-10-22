"""Per-stock features computed over each stock's own trading rows.

Windows count the stock's own rows (days it traded), not calendar days.
"Prior N" windows end the day before the scan date; "last N" windows include
the scan date itself.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _streak(flags: pd.Series, groups: pd.Series) -> pd.Series:
    """Length of the run of True values ending at each row, per group."""
    flags = flags.astype(bool)
    breaks = (~flags).groupby(groups).cumsum()
    return flags.astype(int).groupby([groups, breaks]).cumsum()


def _rising_count(s: pd.Series, groups: pd.Series, window: int) -> pd.Series:
    """How many of the last ``window - 1`` steps went up (within one group)."""
    prev = s.groupby(groups).shift(1)
    up = (s > prev).astype(float).where(prev.notna())
    r = up.groupby(groups, sort=False).rolling(window - 1, min_periods=window - 1).sum()
    return r.reset_index(level=0, drop=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return ``df`` (one row per stock per day) with scanner features added."""
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    g = df.groupby("symbol", sort=False)
    sym = df["symbol"]

    def roll(values: pd.Series, n: int, how: str) -> pd.Series:
        r = values.groupby(sym, sort=False).rolling(n, min_periods=n)
        return getattr(r, how)().reset_index(level=0, drop=True)

    def prior(col: str, n: int, how: str) -> pd.Series:
        return roll(g[col].shift(1), n, how)

    def last(col: str, n: int, how: str) -> pd.Series:
        return roll(df[col], n, how)

    df["rows_before"] = g.cumcount()
    df["day_change"] = (df["close"] / df["prev_close"] - 1) * 100
    span = (df["high"] - df["low"]).replace(0, np.nan)
    df["close_position"] = ((df["close"] - df["low"]) / span).fillna(0.5)

    # Volume ("buzz") and delivery ("confidence").
    df["vol_avg20"] = prior("volume", 20, "mean")
    df["vol_ratio"] = df["volume"] / df["vol_avg20"]
    df["vol_avg20_incl"] = last("volume", 20, "mean")
    df["vol_ratio_incl"] = df["volume"] / df["vol_avg20_incl"]
    df["vol_avg5_ratio"] = last("volume", 5, "mean") / df["vol_avg20_incl"]
    df["deliv_avg20"] = prior("deliv_pct", 20, "mean")
    df["deliv_ratio"] = df["deliv_pct"] / df["deliv_avg20"].replace(0, np.nan)
    df["deliv_avg5"] = last("deliv_pct", 5, "mean")
    df["deliv_avg5_prev"] = roll(g["deliv_pct"].shift(5), 5, "mean")
    df["deliv_streak55"] = _streak(df["deliv_pct"] >= 55, sym)
    df["deliv_streak50"] = _streak(df["deliv_pct"] >= 50, sym)
    df["deliv_streak40"] = _streak(df["deliv_pct"] >= 40, sym)
    # Average delivery over the current >=50% streak, looking back at most 10 rows.
    k = df["deliv_streak50"].clip(upper=10)
    csum = g["deliv_pct"].cumsum()
    df["deliv_streak_avg"] = np.nan
    for n in range(1, 11):
        back = csum.groupby(sym).shift(n).fillna(0)
        df.loc[k == n, "deliv_streak_avg"] = ((csum - back) / n)[k == n]

    # Average trade value compared with normal: big tickets hint at large players.
    df["trade_value"] = df["turnover_lacs"] / df["trades"].replace(0, np.nan)
    df["trade_value_avg20"] = prior("trade_value", 20, "mean")
    df["trade_size_ratio"] = df["trade_value"] / df["trade_value_avg20"]

    # Price levels.
    df["high20_prior"] = prior("high", 20, "max")
    df["breakout_pct"] = (df["close"] / df["high20_prior"] - 1) * 100
    df["low10_prior"] = prior("low", 10, "min")
    df["bounce_pct"] = (df["close"] / df["low10_prior"] - 1) * 100
    # Sessions since the prior-10-day low (1 = yesterday).
    df["low10_age"] = np.nan
    for n in range(10, 0, -1):
        df.loc[g["low"].shift(n) == df["low10_prior"], "low10_age"] = n
    df["high15_prior"] = prior("high", 15, "max")
    df["low15_prior"] = prior("low", 15, "min")
    df["range15_pct"] = (df["high15_prior"] - df["low15_prior"]) / df["low15_prior"] * 100
    df["range5_pct"] = (last("high", 5, "max") - last("low", 5, "min")) / last("low", 5, "min") * 100
    hi_prev5 = roll(g["high"].shift(5), 5, "max")
    lo_prev5 = roll(g["low"].shift(5), 5, "min")
    df["range5_prev_pct"] = (hi_prev5 - lo_prev5) / lo_prev5 * 100
    df["low5_incl"] = last("low", 5, "min")
    df["low3_incl"] = last("low", 3, "min")
    df["return_5d"] = (df["close"] / g["close"].shift(5) - 1) * 100
    df["higher_lows5"] = _rising_count(df["low"], sym, 5)
    df["sma5"] = last("close", 5, "mean")
    df["sma20"] = last("close", 20, "mean")

    # Volume-weighted average of the typical price (High+Low+Close)/3.
    df["_tpv"] = (df["high"] + df["low"] + df["close"]) / 3 * df["volume"]
    for n in (5, 15, 20, 30):
        df[f"vwap{n}"] = last("_tpv", n, "sum") / last("volume", n, "sum")
    df = df.drop(columns="_tpv")
    return df


def snapshot(history: pd.DataFrame, day, rows: int = 31) -> pd.DataFrame:
    """Features for one scan date, indexed by symbol.

    Only each stock's last ``rows`` rows up to ``day`` are used, so streaks and
    averages look back at most 30 trading days before the scan date.
    """
    day = pd.Timestamp(day)
    upto = history[history["date"] <= day]
    upto = upto.groupby("symbol", sort=False).tail(rows)
    feats = add_features(upto)
    return feats[feats["date"] == day].set_index("symbol")
