"""Command line: ``python -m marketscan scan`` / ``python -m marketscan straddle``."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from . import data, features, scanners, straddle


def _day(text: str | None) -> date:
    if text:
        return datetime.strptime(text, "%Y-%m-%d").date()
    day = data.latest_trading_day()
    if day is None:
        raise SystemExit("No NSE file found in the last 10 days.")
    return day


def cmd_scan(args: argparse.Namespace) -> None:
    day = _day(args.date)
    snap = features.snapshot(data.equity_history(day, days=75), day)
    if snap.empty:
        raise SystemExit(f"No NSE data for {day}.")
    results = scanners.run_all(snap)
    out = Path(args.out) / f"{day:%Y-%m-%d}"
    out.mkdir(parents=True, exist_ok=True)
    print(f"{day}: {len(snap)} stocks scanned -> {out}")
    for name, df in results.items():
        df.to_csv(out / f"{name}.csv", index=False)
        print(f"  {name:20s} {len(df):5d}")
    if len(results["smart_money"]):
        print("\nTop smart-money stocks:")
        print(results["smart_money"][["symbol", "score", "grade", "action", "volume_x", "delivery_pct"]].head(10).to_string(index=False))


def cmd_straddle(args: argparse.Namespace) -> None:
    day = _day(args.date)
    fo = data.fo_history(day, days=args.days, symbol=args.symbol)
    if fo.empty:
        raise SystemExit("No F&O data found.")
    df = straddle.dual_straddle(fo, args.symbol)
    cols = ["date", "strike_near", "straddle_close_near", "straddle_vwap_near", "strike_next", "straddle_close_next", "straddle_vwap_next"]
    out = df[cols].copy()
    out["date"] = out["date"].dt.date
    print(out.round(2).to_string(index=False))


def main() -> None:
    p = argparse.ArgumentParser(prog="marketscan", description="NSE end-of-day scanners")
    sub = p.add_subparsers(required=True)
    s = sub.add_parser("scan", help="run every scanner and save CSVs")
    s.add_argument("--date", help="YYYY-MM-DD (default: latest trading day)")
    s.add_argument("--out", default="output")
    s.set_defaults(func=cmd_scan)
    t = sub.add_parser("straddle", help="near and next expiry ATM straddle with VWAP")
    t.add_argument("--symbol", default="NIFTY")
    t.add_argument("--date")
    t.add_argument("--days", type=int, default=30)
    t.set_defaults(func=cmd_straddle)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
