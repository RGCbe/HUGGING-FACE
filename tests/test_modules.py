import numpy as np
import pandas as pd
import pytest

from marketscan import data, orderflow, pairs, straddle

EQUITY_CSV = b"""SYMBOL, SERIES, DATE1, PREV_CLOSE, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, LAST_PRICE, CLOSE_PRICE, AVG_PRICE, TTL_TRD_QNTY, TURNOVER_LACS, NO_OF_TRADES, DELIV_QTY, DELIV_PER
GTPL, EQ, 21-Oct-2026, 54.70, 54.12, 55.90, 54.12, 54.40, 54.38, 54.78, 457104, 250.40, 310, 448969, 98.22
ABC, BE, 21-Oct-2026, 10, 10, 11, 9, 10.5, 10.5, 10.2, 100, 0.01, 2, -, -
"""


def test_parse_equity_csv():
    df = data.parse_equity_csv(EQUITY_CSV)
    g = df.iloc[0]
    assert g["symbol"] == "GTPL" and g["series"] == "EQ"
    assert g["date"] == pd.Timestamp("2026-10-21")
    assert g["deliv_pct"] == 98.22 and g["volume"] == 457104
    assert df.iloc[1]["deliv_pct"] == 0  # "-" becomes 0


def test_stale_file_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("MARKETSCAN_CACHE", str(tmp_path))
    monkeypatch.setattr(data, "_get", lambda url: EQUITY_CSV)  # always serves 21-Oct
    assert data.equity_day("2026-10-21") is not None
    assert data.equity_day("2026-10-22") is None
    assert not (tmp_path / "eq_20261022.csv").exists()


def fo_chain(day, underlying, expiry, strikes, ce, pe, lot=65):
    rows = []
    for k, c, p in zip(strikes, ce, pe):
        for typ, px in (("CE", c), ("PE", p)):
            rows.append(dict(date=pd.Timestamp(day), instrument="IDO", symbol="NIFTY", expiry=pd.Timestamp(expiry), strike=k,
                             option_type=typ, open=px, high=px, low=px, close=px, underlying=underlying, settle=px, oi=1000,
                             oi_change=0, contracts=10, notional=(k + px + 1) * 10 * lot, trades=5, lot_size=lot))
    return rows


def test_eod_straddle_picks_atm_and_vwap():
    fo = pd.DataFrame(fo_chain("2026-10-21", 22811, "2026-10-27", [22700, 22800, 22900], [200, 150, 100], [90, 140, 190]))
    st = straddle.eod_straddles(fo, "NIFTY")
    assert st.loc[0, "strike"] == 22800
    assert st.loc[0, "straddle_close"] == 290
    # notional was (strike + premium + 1) per unit, so each leg's VWAP is premium + 1
    assert st.loc[0, "straddle_vwap"] == pytest.approx(292)


def test_intraday_straddle_vwap_resets_daily():
    t = pd.to_datetime(["2026-10-21 09:15", "2026-10-21 09:20", "2026-10-22 09:15"])
    call = pd.DataFrame({"time": t, "close": [100, 110, 50], "volume": [10, 30, 5]})
    put = pd.DataFrame({"time": t, "close": [100, 90, 50], "volume": [10, 10, 5]})
    s = straddle.intraday_straddle(call, put)
    assert list(s["straddle"]) == [200, 200, 100]
    assert s.loc[1, "vwap"] == pytest.approx(200)
    assert s.loc[2, "vwap"] == pytest.approx(100)


def test_classify_quote_and_tick_rules():
    ticks = pd.DataFrame({"time": pd.date_range("2026-10-21 09:15", periods=4, freq="s"), "price": [100, 100.05, 100.0, 100.0],
                          "qty": [1, 2, 3, 4], "bid": [99.95, 100.0, 100.0, 99.95], "ask": [100.0, 100.05, 100.05, 100.05]})
    c = orderflow.classify(ticks)
    assert list(c["side"]) == [1, 1, -1, -1]  # at ask, at ask, at bid, between -> tick rule (down)


def test_footprint_and_profile_totals():
    ticks = orderflow.synthetic_ticks(minutes=10)
    fp = orderflow.footprint(ticks, "5min", 0.05)
    assert fp["total"].sum() == ticks["qty"].sum()
    bars = orderflow.bar_summary(ticks, "5min")
    assert bars["cum_delta"].iloc[-1] == fp["delta"].sum()
    vp = orderflow.volume_profile(ticks)
    assert vp["val"] <= vp["poc"] <= vp["vah"]
    im = orderflow.imbalances(fp)
    assert {"buy_imbalance", "sell_imbalance"} <= set(im.columns)


def test_pairs_detects_mean_reversion():
    rng = np.random.default_rng(3)
    n = 250
    b = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, n))))
    noise = np.zeros(n)
    for i in range(1, n):
        noise[i] = 0.7 * noise[i - 1] + rng.normal(0, 0.01)
    a = pd.Series(np.exp(0.5 + 1.5 * np.log(b) + noise))
    df, st = pairs.analyse(a, b)
    assert st["beta"] == pytest.approx(1.5, abs=0.1)
    assert st["mean_reverting"]
    assert st["half_life_days"] < 10
    assert {"spread", "zscore", "signal"} <= set(df.columns)
    ranked = pairs.scan_pairs(pd.DataFrame({"A": a, "B": b, "C": b * 0 + rng.normal(100, 1, n)}), min_corr=0.5)
    assert list(ranked[["a", "b"]].iloc[0]) == ["A", "B"]
