"""The twelve end-of-day scanners.

Every scanner takes the feature snapshot for one date (from
``features.snapshot``) and returns a DataFrame sorted best-first. Rules are
documented in ``docs/scanner-rules.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FULL_HISTORY = 20  # rows a stock needs before the scan date


def _tier(value: float, steps: list[tuple[float, int]]) -> int:
    if pd.isna(value):
        return 0
    for threshold, points in steps:
        if value >= threshold:
            return points
    return 0


def _ready(snap: pd.DataFrame) -> pd.DataFrame:
    return snap[snap["rows_before"] >= FULL_HISTORY]


# --------------------------------------------------------------- smart money

SMART_LABELS = {
    "volume_spike": {20: "Volume 4x+", 15: "Volume 3x+", 10: "Volume 2.5x+", 5: "Volume 2x+"},
    "delivery_level": {20: "Delivery 80%+", 15: "Delivery 70%+", 10: "Delivery 60%+", 5: "Delivery 50%+"},
    "delivery_spike": {15: "Delivery 2x normal", 8: "Delivery 1.5x normal"},
    "accumulation": {20: "Delivery streak 7d+", 12: "Delivery streak 5d+", 5: "Delivery streak 3d+"},
    "large_trades": {15: "Trade size 2.5x+", 10: "Trade size 2x+", 5: "Trade size 1.5x+"},
    "quiet_accumulation": {12: "Quiet buying"},
    "price_strength": {8: "Strong close"},
    "breakout_volume": {15: "New 20D high on volume", 8: "New 20D high"},
}


def smart_money_parts(row: pd.Series) -> dict[str, int]:
    new_high = row["breakout_pct"] > 0
    return {
        "volume_spike": _tier(row["vol_ratio"], [(4, 20), (3, 15), (2.5, 10), (2, 5)]),
        "delivery_level": _tier(row["deliv_pct"], [(80, 20), (70, 15), (60, 10), (50, 5)]),
        "delivery_spike": _tier(row["deliv_ratio"], [(2, 15), (1.5, 8)]),
        "accumulation": _tier(row["deliv_streak55"], [(7, 20), (5, 12), (3, 5)]),
        "large_trades": _tier(row["trade_size_ratio"], [(2.5, 15), (2, 10), (1.5, 5)]),
        "quiet_accumulation": 12 if abs(row["day_change"]) < 1 and row["deliv_pct"] >= 60 else 0,
        "price_strength": 8 if row["close_position"] >= 0.85 and row["day_change"] >= 1 else 0,
        "breakout_volume": (15 if row["vol_ratio"] >= 2 else 8) if new_high else 0,
    }


def grade(score: float) -> str:
    for cut, g in ((90, "A+"), (80, "A"), (70, "B+"), (60, "B")):
        if score >= cut:
            return g
    return "C+"


def action(score: float, day_change: float) -> str:
    if score < 60:
        return "WATCH"
    if score < 70 or day_change < 0:
        return "ACCUMULATE"
    return "STRONG BUY" if score >= 80 else "BUY"


def smart_money(snap: pd.DataFrame, min_score: int = 50) -> pd.DataFrame:
    s = _ready(snap)
    s = s[(s["volume"] >= 50_000) & (s["turnover_lacs"] >= 100) & (s["vol_ratio"] >= 1.3)]
    rows = []
    for sym, r in s.iterrows():
        parts = smart_money_parts(r)
        score = sum(parts.values())
        if score < min_score:
            continue
        signals = [SMART_LABELS[k][v] for k, v in parts.items() if v]
        rows.append(
            {
                "symbol": sym,
                "score": score,
                "grade": grade(score),
                "action": action(score, r["day_change"]),
                "close": r["close"],
                "chg_pct": r["day_change"],
                "volume_x": r["vol_ratio"],
                "delivery_pct": r["deliv_pct"],
                "delivery_streak": int(r["deliv_streak55"]),
                "trade_size_x": r["trade_size_ratio"],
                "signals": ", ".join(signals),
                **{f"pts_{k}": v for k, v in parts.items()},
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values(["score", "volume_x"], ascending=False).reset_index(drop=True) if len(out) else out


# ------------------------------------------------------------- simple lists


def volume_spike(snap: pd.DataFrame, min_ratio: float = 2.0, limit: int = 100) -> pd.DataFrame:
    s = _ready(snap)
    s = s[s["vol_ratio"] >= min_ratio].sort_values("vol_ratio", ascending=False).head(limit)
    return s.reset_index()[["symbol", "close", "day_change", "volume", "vol_avg20", "vol_ratio", "deliv_pct"]]


def delivery_spike(snap: pd.DataFrame, min_ratio: float = 1.5, min_delivery: float = 50, limit: int = 100) -> pd.DataFrame:
    s = _ready(snap)
    s = s[(s["deliv_ratio"] >= min_ratio) & (s["deliv_pct"] >= min_delivery)]
    s = s.sort_values("deliv_ratio", ascending=False).head(limit)
    return s.reset_index()[["symbol", "close", "day_change", "deliv_pct", "deliv_avg20", "deliv_ratio", "volume"]]


def new_highs(snap: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    s = _ready(snap)
    s = s[s["close"] > s["high20_prior"]].sort_values("breakout_pct", ascending=False).head(limit)
    return s.reset_index()[["symbol", "close", "day_change", "high20_prior", "breakout_pct", "volume", "deliv_pct"]]


def bounces(snap: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    """Up 2%+ on volume, closing strong, off a 10-day low made in the last 3
    sessions after a fall of 10%+ from the 20-day high."""
    s = _ready(snap)
    drop = (1 - s["low10_prior"] / s["high20_prior"]) * 100
    s = s[(s["day_change"] >= 2) & (s["bounce_pct"] >= 3) & (s["low10_age"] <= 3) & (drop >= 10)
          & (s["close_position"] >= 0.6) & (s["vol_ratio"] >= 1.2)]
    s = s.sort_values("bounce_pct", ascending=False).head(limit)
    return s.reset_index()[["symbol", "close", "day_change", "low10_prior", "bounce_pct", "deliv_pct"]]


def coiled(snap: pd.DataFrame, max_range: float = 5.0, limit: int = 100) -> pd.DataFrame:
    """Breaking above a tight 15-day range."""
    s = _ready(snap)
    s = s[(s["range15_pct"] < max_range) & (s["close"] > s["high15_prior"])].copy()
    s["breakout_pct"] = (s["close"] / s["high15_prior"] - 1) * 100
    s = s.sort_values("range15_pct").head(limit)
    return s.reset_index()[["symbol", "close", "day_change", "range15_pct", "breakout_pct", "vol_ratio", "deliv_pct"]]


def continuous_delivery(snap: pd.DataFrame, min_days: int = 5, limit: int = 100) -> pd.DataFrame:
    """Delivery of 50%+ for ``min_days``+ sessions in a row (streak shown up to 10)."""
    s = _ready(snap)
    s = s[s["deliv_streak50"] >= min_days].copy()
    s["streak"] = s["deliv_streak50"].clip(upper=10).astype(int)
    s = s.sort_values(["streak", "deliv_streak_avg"], ascending=False).head(limit)
    return s.reset_index()[["symbol", "close", "day_change", "streak", "deliv_pct", "deliv_streak_avg"]]


# ---------------------------------------------------------------- POC levels

TRENDS = {
    (True, True, True): "STRONG BULLISH",
    (False, False, False): "STRONG BEARISH",
    (True, False, False): "REVERSAL POSSIBLE",
    (False, True, True): "PULLBACK",
    (True, True, False): "STRONG REVERSAL",
    (False, False, True): "CORRECTION",
    (False, True, False): "CONSOLIDATION",
    (True, False, True): "MILD BULLISH",
}


def poc_levels(snap: pd.DataFrame, near_pct: float = 2.0) -> pd.DataFrame:
    """Price versus volume-weighted typical price over 5, 15 and 30 sessions."""
    s = snap.dropna(subset=["vwap5", "vwap15", "vwap30"]).copy()
    for n in (5, 15, 30):
        s[f"vs_{n}d_pct"] = (s["close"] / s[f"vwap{n}"] - 1) * 100
        s[f"near_{n}d"] = s[f"vs_{n}d_pct"].abs() <= near_pct
    above = [s["close"] > s[f"vwap{n}"] for n in (5, 15, 30)]
    s["trend"] = [TRENDS[k] for k in zip(*above)]
    rising = (s["vwap5"] > s["vwap15"]) & (s["vwap15"] > s["vwap30"])
    falling = (s["vwap5"] < s["vwap15"]) & (s["vwap15"] < s["vwap30"])
    s["stack"] = np.select([rising, falling], ["rising", "falling"], "mixed")
    cols = ["close", "day_change", "vol_ratio", "vwap5", "vwap15", "vwap30", "vs_5d_pct", "vs_15d_pct", "vs_30d_pct",
            "near_5d", "near_15d", "near_30d", "trend", "stack"]
    return s.reset_index()[["symbol", *cols]]


# ------------------------------------------------------------- penny movers


def penny_parts(r: pd.Series) -> dict[str, int]:
    return {
        "move": _tier(r["day_change"], [(10, 30), (5, 20), (3, 10)]),
        "volume": _tier(r["vol_ratio"], [(5, 30), (3, 20), (2, 10)]),
        "delivery": _tier(r["deliv_pct"], [(60, 20), (45, 10)]),
        "streak": _tier(r["deliv_streak40"], [(5, 20), (3, 10)]),
        "breakout": 15 if r["breakout_pct"] > 0 else 0,
        "run_5d": _tier(r["return_5d"], [(15, 15), (10, 10)]),
        "strong_close": 10 if r["close_position"] >= 0.8 else 0,
    }


def penny(snap: pd.DataFrame, min_score: int = 40, limit: int = 100) -> pd.DataFrame:
    s = _ready(snap)
    s = s[(s["close"] >= 1) & (s["close"] <= 50) & (s["turnover_lacs"] >= 10) & (s["volume"] >= 20_000)]
    rows = []
    for sym, r in s.iterrows():
        parts = penny_parts(r)
        score = sum(parts.values())
        if score < min_score:
            continue
        if r["day_change"] >= 5 and r["vol_ratio"] >= 2:
            category = "Rocket"
        elif parts["breakout"]:
            category = "Breakout"
        elif r["vol_ratio"] >= 3:
            category = "Volume"
        elif parts["delivery"] or parts["streak"]:
            category = "Accumulation"
        else:
            category = "Active"
        risk = "Very High" if r["close"] < 5 else "High" if r["close"] < 20 else "Medium"
        rows.append({"symbol": sym, "score": score, "category": category, "risk": risk, "close": r["close"],
                     "chg_pct": r["day_change"], "volume_x": r["vol_ratio"], "delivery_pct": r["deliv_pct"],
                     "return_5d": r["return_5d"], **{f"pts_{k}": v for k, v in parts.items()}})
    out = pd.DataFrame(rows)
    return out.sort_values("score", ascending=False).head(limit).reset_index(drop=True) if len(out) else out


# --------------------------------------------------------------- early setups


def early_parts(r: pd.Series) -> dict[str, int]:
    poc_gap = (r["close"] / r["vwap20"] - 1) * 100
    tightening = r["range5_pct"] < r["range5_prev_pct"]
    rising_delivery = r["deliv_avg5"] > 1.1 * r["deliv_avg5_prev"] and r["deliv_avg5"] >= 45
    return {
        "range": 25 if r["range5_pct"] < 5 and tightening else 15 if tightening and r["range5_pct"] <= 8 else 0,
        "delivery": 25 if rising_delivery else 15 if r["deliv_avg5"] >= 55 else 0,
        "volume_dry": 20 if r["vol_avg5_ratio"] < 0.6 else 10 if r["vol_avg5_ratio"] < 0.8 else 0,
        "volume_return": 15 if r["vol_ratio_incl"] >= 1.2 and r["vol_avg5_ratio"] < 0.9 else 0,
        "higher_lows": _tier(r["higher_lows5"], [(4, 20), (3, 10)]),
        "poc": 20 if 0 < poc_gap <= 3 and r["day_change"] > 0 else 10 if abs(poc_gap) <= 3 else 0,
        "strong_close": 10 if r["close_position"] >= 0.8 and r["day_change"] > 0 else 0,
        "quiet_strength": 10 if -1 < r["day_change"] < 3 else 0,
    }


def early_setups(snap: pd.DataFrame, min_score: int = 60, limit: int = 100) -> pd.DataFrame:
    s = _ready(snap)
    s = s[(s["turnover_lacs"] >= 50) & s["vwap20"].notna()]
    rows = []
    for sym, r in s.iterrows():
        parts = early_parts(r)
        score = sum(parts.values())
        if score < min_score:
            continue
        if parts["range"] == 25 and parts["volume_dry"]:
            pattern = "Coiling"
        elif parts["delivery"] == 25:
            pattern = "Silent accumulation"
        else:
            pattern = "Ready to move"
        rows.append({"symbol": sym, "score": score, "pattern": pattern, "close": r["close"], "chg_pct": r["day_change"],
                     "range5_pct": r["range5_pct"], "delivery5_pct": r["deliv_avg5"], "volume_x": r["vol_ratio_incl"],
                     "vs_vwap20_pct": (r["close"] / r["vwap20"] - 1) * 100, **{f"pts_{k}": v for k, v in parts.items()}})
    out = pd.DataFrame(rows)
    return out.sort_values("score", ascending=False).head(limit).reset_index(drop=True) if len(out) else out


# --------------------------------------------------------- next-day setups


def next_day_setups(snap: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    """Entry, stop-loss and two targets for the next session.

    Setups (first match wins): breakout ready (within 2% of the 20-day high),
    squeeze (5-day range under 3%), support bounce (within 2% of the 20-day
    VWAP after a down day) and momentum (up 2%+ with SMA5 above SMA20).
    """
    s = _ready(snap)
    s = s[(s["turnover_lacs"] >= 100) & s["vwap20"].notna()]
    rows = []
    for sym, r in s.iterrows():
        dist_high = (r["high20_prior"] / r["close"] - 1) * 100
        vwap_gap = (r["close"] / r["vwap20"] - 1) * 100
        if -2 <= dist_high <= 2:
            setup, entry, t1, t2 = "Breakout ready", r["close"], 3.5, 6
            stop = max(entry * 0.985, r["low5_incl"] * 0.99)
        elif r["range5_pct"] < 3:
            setup, entry, t1, t2 = "Squeeze", r["low"], 4, 7
            stop = min(entry * 0.985, r["low3_incl"])
        elif abs(vwap_gap) <= 2 and r["day_change"] <= 0:
            setup, entry, t1, t2 = "Support bounce", r["low"], 3, 5
            stop = min(entry * 0.985, r["low"] * 0.99)
        elif r["day_change"] >= 2 and r["sma5"] > r["sma20"]:
            setup, entry, t1, t2 = "Momentum", r["close"], 3.5, 6
            stop = max(entry * 0.985, r["low5_incl"] * 0.99)
        else:
            continue
        if stop >= entry:
            continue
        reasons = {
            "Good delivery": 25 if r["deliv_pct"] >= 50 else 0,
            "Volume confirming": 20 if r["vol_ratio"] >= 1.5 else 0,
            "Strong close": 15 if r["close_position"] >= 0.75 else 0,
            "Delivery rising": 15 if r["deliv_avg5"] > r["deliv_avg5_prev"] else 0,
            "Above averages": 15 if r["close"] > r["sma5"] > r["sma20"] else 0,
            "Higher lows": 10 if r["higher_lows5"] >= 3 else 0,
            "Near support": 10 if abs(vwap_gap) <= 2 else 0,
        }
        score = 40 + sum(reasons.values())
        risk = (entry - stop) / entry * 100
        rows.append({"symbol": sym, "score": score, "setup": setup, "close": r["close"], "entry": entry, "stop_loss": stop,
                     "target1": entry * (1 + t1 / 100), "target2": entry * (1 + t2 / 100), "risk_pct": risk,
                     "reward_risk": t1 / risk if risk else np.nan, "why": ", ".join(k for k, v in reasons.items() if v)})
    out = pd.DataFrame(rows)
    return out.sort_values("score", ascending=False).head(limit).reset_index(drop=True) if len(out) else out


# --------------------------------------------------------------- run all

SCANNERS = {
    "smart_money": smart_money,
    "next_day": next_day_setups,
    "penny": penny,
    "early": early_setups,
    "continuous_delivery": continuous_delivery,
    "new_high": new_highs,
    "volume_spike": volume_spike,
    "delivery_spike": delivery_spike,
    "bounce": bounces,
    "coiled": coiled,
}


def run_all(snap: pd.DataFrame) -> dict[str, pd.DataFrame]:
    results = {name: fn(snap) for name, fn in SCANNERS.items()}
    poc = poc_levels(snap)
    results["poc_levels"] = poc
    results["multi_signal"] = multi_signal(results, poc)
    return results


def multi_signal(results: dict[str, pd.DataFrame], poc: pd.DataFrame | None = None, min_lists: int = 2) -> pd.DataFrame:
    """Stocks that appear in two or more scanner lists."""
    hits: dict[str, list[str]] = {}
    for name, df in results.items():
        if name in ("poc_levels", "multi_signal") or df is None or df.empty:
            continue
        for sym in df["symbol"]:
            hits.setdefault(sym, []).append(name)
    if poc is not None and not poc.empty:
        for sym in poc.loc[(poc["trend"] == "STRONG BULLISH") & poc["near_5d"], "symbol"]:
            hits.setdefault(sym, []).append("poc_bullish")
    rows = [{"symbol": s, "count": len(v), "lists": " + ".join(v)} for s, v in hits.items() if len(v) >= min_lists]
    out = pd.DataFrame(rows, columns=["symbol", "count", "lists"])
    return out.sort_values("count", ascending=False).reset_index(drop=True)
