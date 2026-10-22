"""Tests for the Fyers connector's pure helpers.

These never need the fyers_apiv3 SDK, a network, or real credentials — only the
parts that transform data or read the environment.
"""

import os

import pandas as pd
import pytest

from marketscan.brokers import fyers


def test_missing_credentials_raise_clear_error(monkeypatch):
    monkeypatch.delenv("FYERS_APP_ID", raising=False)
    monkeypatch.delenv("FYERS_ACCESS_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="FYERS_APP_ID"):
        fyers.FyersClient()


def test_client_reads_env(monkeypatch):
    monkeypatch.setenv("FYERS_APP_ID", "TEST-100")
    monkeypatch.setenv("FYERS_ACCESS_TOKEN", "tok")
    c = fyers.FyersClient()
    assert c.app_id == "TEST-100" and c.token == "tok"


def test_ticks_to_bars_uses_cumulative_volume_delta():
    ticks = pd.DataFrame({
        "time": pd.to_datetime([
            "2026-10-22 09:15:10", "2026-10-22 09:15:40", "2026-10-22 09:16:05", "2026-10-22 09:16:50",
        ]),
        "ltp": [100.0, 101.0, 102.0, 101.5],
        "volume": [500, 900, 1400, 1800],  # cumulative for the day
    })
    bars = fyers.ticks_to_bars(ticks, "1min")
    assert list(bars["close"]) == [101.0, 101.5]
    assert list(bars["high"]) == [101.0, 102.0]
    # first bar volume = last cumulative in bar (900); second = 1800 - 900 = 900
    assert list(bars["volume"]) == [900, 900]


def test_atm_straddle_symbol_selection(monkeypatch):
    monkeypatch.setenv("FYERS_APP_ID", "TEST-100")
    monkeypatch.setenv("FYERS_ACCESS_TOKEN", "tok")
    c = fyers.FyersClient()
    chain = {
        "underlying": 22811.0,
        "rows": pd.DataFrame([
            {"symbol": "NSE:NIFTY-22700CE", "strike": 22700, "option_type": "CE", "ltp": 200},
            {"symbol": "NSE:NIFTY-22700PE", "strike": 22700, "option_type": "PE", "ltp": 90},
            {"symbol": "NSE:NIFTY-22800CE", "strike": 22800, "option_type": "CE", "ltp": 140},
            {"symbol": "NSE:NIFTY-22800PE", "strike": 22800, "option_type": "PE", "ltp": 130},
            {"symbol": "NSE:NIFTY-22900CE", "strike": 22900, "option_type": "CE", "ltp": 95},
            {"symbol": "NSE:NIFTY-22900PE", "strike": 22900, "option_type": "PE", "ltp": 185},
        ]),
    }
    monkeypatch.setattr(c, "option_chain", lambda symbol, strike_count=10: chain)
    picked = c.atm_straddle_symbols("NSE:NIFTY50-INDEX")
    assert picked["strike"] == 22800
    assert picked["call"] == "NSE:NIFTY-22800CE"
    assert picked["put"] == "NSE:NIFTY-22800PE"
    # one strike above the money
    assert c.atm_straddle_symbols("NSE:NIFTY50-INDEX", offset=1)["strike"] == 22900


def test_token_cache_roundtrip(tmp_path, monkeypatch):
    from datetime import date
    from marketscan.brokers import fyers_auth

    monkeypatch.setenv("FYERS_TOKEN_FILE", str(tmp_path / "tok.json"))
    assert fyers_auth.cached_token() is None
    fyers_auth.save_token("abc123")
    assert fyers_auth.cached_token() == "abc123"
    # a token saved for a different day is treated as stale
    (tmp_path / "tok.json").write_text(f'{{"date": "2000-01-01", "token": "old"}}')
    assert fyers_auth.cached_token() is None


def test_ensure_token_prefers_cache_then_env(tmp_path, monkeypatch):
    from marketscan.brokers import fyers_auth

    monkeypatch.setenv("FYERS_TOKEN_FILE", str(tmp_path / "tok.json"))
    monkeypatch.setenv("FYERS_ACCESS_TOKEN", "fromenv")
    assert fyers_auth.ensure_token(auto=False) == "fromenv"      # env used and cached
    monkeypatch.delenv("FYERS_ACCESS_TOKEN")
    assert fyers_auth.ensure_token(auto=False) == "fromenv"      # now served from cache


def test_b64_encoding():
    from marketscan.brokers import fyers_auth
    import base64

    assert fyers_auth._b64("1234") == base64.b64encode(b"1234").decode()


def test_market_hours_logic():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    import importlib.util, pathlib

    spec = importlib.util.spec_from_file_location("fyers_runner", pathlib.Path("scripts/fyers_runner.py"))
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    ist = ZoneInfo("Asia/Kolkata")
    assert runner.market_open(datetime(2026, 10, 22, 10, 0, tzinfo=ist))      # Thursday 10:00
    assert not runner.market_open(datetime(2026, 10, 22, 8, 0, tzinfo=ist))   # before open
    assert not runner.market_open(datetime(2026, 10, 22, 16, 0, tzinfo=ist))  # after close
    assert not runner.market_open(datetime(2026, 10, 24, 10, 0, tzinfo=ist))  # Saturday
    assert runner.wait_seconds(datetime(2026, 10, 22, 9, 0, tzinfo=ist)) == 15 * 60
