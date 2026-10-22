"""Download and cache NSE's free end-of-day files.

Two public NSE archives are used:

* ``sec_bhavdata_full_DDMMYYYY.csv`` - every equity's OHLC, volume, trades and
  delivery for one day.
* ``BhavCopy_NSE_FO_0_0_0_YYYYMMDD_F_0000.csv.zip`` - every F&O contract for
  one day.

NSE sometimes answers a request for a holiday (or a day it has not published
yet) with the *previous* day's file. Those stale files are detected by
checking the date inside the file and are skipped, so a day never appears
twice in the history.
"""

from __future__ import annotations

import io
import os
import time
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

ARCHIVE = "https://nsearchives.nseindia.com"
EQUITY_URL = ARCHIVE + "/products/content/sec_bhavdata_full_{d:%d%m%Y}.csv"
FO_URL = ARCHIVE + "/content/fo/BhavCopy_NSE_FO_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/141.0 Safari/537.36"
)

EQUITY_COLUMNS = {
    "SYMBOL": "symbol",
    "SERIES": "series",
    "DATE1": "date",
    "PREV_CLOSE": "prev_close",
    "OPEN_PRICE": "open",
    "HIGH_PRICE": "high",
    "LOW_PRICE": "low",
    "LAST_PRICE": "last",
    "CLOSE_PRICE": "close",
    "AVG_PRICE": "avg_price",
    "TTL_TRD_QNTY": "volume",
    "TURNOVER_LACS": "turnover_lacs",
    "NO_OF_TRADES": "trades",
    "DELIV_QTY": "deliv_qty",
    "DELIV_PER": "deliv_pct",
}


def cache_dir() -> Path:
    path = Path(os.environ.get("MARKETSCAN_CACHE", "data/cache"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get(url: str, retries: int = 3) -> bytes | None:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        except requests.RequestException:
            time.sleep(2**attempt)
            continue
        if resp.status_code == 404:
            return None
        if resp.ok:
            return resp.content
        time.sleep(2**attempt)
    return None


def _as_date(d: date | str) -> date:
    return d if isinstance(d, date) else datetime.strptime(str(d), "%Y-%m-%d").date()


def _mark_missing(marker: Path, d: date) -> None:
    # Recent days may simply not be published yet, so only remember older gaps.
    if d < date.today() - timedelta(days=3):
        marker.touch()


def parse_equity_csv(raw: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(raw), skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns=EQUITY_COLUMNS)[list(EQUITY_COLUMNS.values())]
    for col in ("symbol", "series", "date"):
        df[col] = df[col].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y")
    numeric = [c for c in EQUITY_COLUMNS.values() if c not in ("symbol", "series", "date")]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    df[["deliv_qty", "deliv_pct"]] = df[["deliv_qty", "deliv_pct"]].fillna(0)
    return df


def equity_day(d: date | str, refresh: bool = False) -> pd.DataFrame | None:
    """One day's equity file, or None for holidays, missing or stale files."""
    d = _as_date(d)
    if d.weekday() >= 5:
        return None
    path = cache_dir() / f"eq_{d:%Y%m%d}.csv"
    miss = cache_dir() / f"eq_{d:%Y%m%d}.missing"
    if miss.exists() and not refresh:
        return None
    if not path.exists() or refresh:
        raw = _get(EQUITY_URL.format(d=d))
        if raw is None or not raw.lstrip().startswith(b"SYMBOL"):
            _mark_missing(miss, d)
            return None
        path.write_bytes(raw)
    df = parse_equity_csv(path.read_bytes())
    if df.empty or df["date"].iloc[0].date() != d:
        # NSE served another day's data for this date: treat as unavailable.
        _mark_missing(miss, d)
        path.unlink(missing_ok=True)
        return None
    return df


def equity_history(end: date | str, days: int = 70, series: str = "EQ") -> pd.DataFrame:
    """Equity rows for roughly ``days`` calendar days up to ``end`` (inclusive)."""
    end = _as_date(end)
    frames = []
    for i in range(days, -1, -1):
        df = equity_day(end - timedelta(days=i))
        if df is not None:
            frames.append(df[df["series"] == series] if series else df)
    if not frames:
        return pd.DataFrame(columns=list(EQUITY_COLUMNS.values()))
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values(["symbol", "date"]).reset_index(drop=True)


def parse_fo_zip(raw: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        df = pd.read_csv(z.open(z.namelist()[0]))
    df = df.rename(
        columns={
            "TradDt": "date",
            "FinInstrmTp": "instrument",
            "TckrSymb": "symbol",
            "XpryDt": "expiry",
            "StrkPric": "strike",
            "OptnTp": "option_type",
            "OpnPric": "open",
            "HghPric": "high",
            "LwPric": "low",
            "ClsPric": "close",
            "UndrlygPric": "underlying",
            "SttlmPric": "settle",
            "OpnIntrst": "oi",
            "ChngInOpnIntrst": "oi_change",
            "TtlTradgVol": "contracts",
            "TtlTrfVal": "notional",
            "TtlNbOfTxsExctd": "trades",
            "NewBrdLotQty": "lot_size",
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df["expiry"] = pd.to_datetime(df["expiry"])
    return df


def fo_day(d: date | str, refresh: bool = False) -> pd.DataFrame | None:
    """One day's F&O file, or None when NSE has none for that date."""
    d = _as_date(d)
    if d.weekday() >= 5:
        return None
    path = cache_dir() / f"fo_{d:%Y%m%d}.zip"
    miss = cache_dir() / f"fo_{d:%Y%m%d}.missing"
    if miss.exists() and not refresh:
        return None
    if not path.exists() or refresh:
        raw = _get(FO_URL.format(d=d))
        if raw is None or not raw.startswith(b"PK"):
            _mark_missing(miss, d)
            return None
        path.write_bytes(raw)
    df = parse_fo_zip(path.read_bytes())
    if df.empty or df["date"].iloc[0].date() != d:
        _mark_missing(miss, d)
        path.unlink(missing_ok=True)
        return None
    return df


def fo_history(end: date | str, days: int = 30, symbol: str | None = None) -> pd.DataFrame:
    end = _as_date(end)
    frames = []
    for i in range(days, -1, -1):
        df = fo_day(end - timedelta(days=i))
        if df is not None:
            frames.append(df[df["symbol"] == symbol] if symbol else df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def latest_trading_day(start: date | None = None, lookback: int = 10) -> date | None:
    start = start or date.today()
    for i in range(lookback):
        d = start - timedelta(days=i)
        if equity_day(d) is not None:
            return d
    return None
