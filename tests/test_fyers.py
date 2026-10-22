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
