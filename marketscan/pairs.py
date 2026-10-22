"""Pair analysis on daily closes.

For two stocks A and B the spread is ``log(A) - beta * log(B)``, with
``beta`` from a least-squares fit. The z-score of the spread says how far the
pair has stretched from its usual relationship:

* z <= -entry: spread unusually low, buy A / sell B;
* z >= +entry: spread unusually high, sell A / buy B;
* |z| <= exit: close the trade.

``adf_stat`` is a plain Augmented Dickey-Fuller statistic (constant, one
lag) used to check that the spread mean-reverts; below about -2.86 is
significant at 5%.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

ADF_5PCT = -2.86


def hedge_ratio(a: pd.Series, b: pd.Series) -> float:
    x, y = np.log(b.values), np.log(a.values)
    x = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(x, y, rcond=None)
    return float(coef[1])


def adf_stat(series: pd.Series) -> float:
    s = series.dropna().values
    if len(s) < 10:
        return float("nan")
    ds = np.diff(s)
    y = ds[1:]
    x = np.column_stack([np.ones(len(y)), s[1:-1], ds[:-1]])
    coef, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ coef
    dof = len(y) - x.shape[1]
    sigma2 = resid @ resid / dof
    cov = sigma2 * np.linalg.inv(x.T @ x)
    return float(coef[1] / np.sqrt(cov[1, 1]))


def half_life(spread: pd.Series) -> float:
    s = spread.dropna()
    lag = s.shift(1).dropna()
    delta = (s - s.shift(1)).dropna()
    x = np.column_stack([np.ones(len(lag)), lag.values])
    coef, *_ = np.linalg.lstsq(x, delta.values, rcond=None)
    return float(-np.log(2) / coef[1]) if coef[1] < 0 else float("inf")


def analyse(a: pd.Series, b: pd.Series, window: int = 20, entry: float = 2.0, exit: float = 0.5) -> tuple[pd.DataFrame, dict]:
    """Spread, z-score and signals for closes ``a`` and ``b`` (indexed by date)."""
    df = pd.concat({"a": a, "b": b}, axis=1).dropna()
    beta = hedge_ratio(df["a"], df["b"])
    df["ratio"] = df["a"] / df["b"]
    df["spread"] = np.log(df["a"]) - beta * np.log(df["b"])
    mean = df["spread"].rolling(window).mean()
    std = df["spread"].rolling(window).std()
    df["zscore"] = (df["spread"] - mean) / std
    df["signal"] = np.select(
        [df["zscore"] <= -entry, df["zscore"] >= entry, df["zscore"].abs() <= exit],
        ["BUY A / SELL B", "SELL A / BUY B", "EXIT"],
        "",
    )
    stats = {
        "beta": beta,
        "correlation": float(np.log(df["a"]).diff().corr(np.log(df["b"]).diff())),
        "adf": adf_stat(df["spread"]),
        "half_life_days": half_life(df["spread"]),
        "zscore_now": float(df["zscore"].iloc[-1]) if len(df) else float("nan"),
    }
    stats["mean_reverting"] = stats["adf"] < ADF_5PCT
    return df, stats


def scan_pairs(closes: pd.DataFrame, min_corr: float = 0.7, window: int = 20) -> pd.DataFrame:
    """Rank every pair of columns in ``closes`` (dates x symbols)."""
    rows = []
    for a, b in itertools.combinations(closes.columns, 2):
        pair = closes[[a, b]].dropna()
        if len(pair) < window + 10:
            continue
        _, st = analyse(pair[a], pair[b], window)
        if st["correlation"] >= min_corr:
            rows.append({"a": a, "b": b, **st})
    out = pd.DataFrame(rows)
    return out.sort_values("adf").reset_index(drop=True) if len(out) else out
