import numpy as np
import pandas as pd
import pytest

from marketscan import features


def test_volume_ratio_uses_prior_20_rows(history):
    f = features.add_features(history)
    a = f[f.symbol == "AAA"].reset_index(drop=True)
    i = 25
    expected = a.loc[i, "volume"] / a.loc[i - 20 : i - 1, "volume"].mean()
    assert a.loc[i, "vol_ratio"] == pytest.approx(expected)
    assert np.isnan(a.loc[19, "vol_ratio"])  # fewer than 20 prior rows


def test_windows_do_not_cross_symbols(history):
    f = features.add_features(history)
    b = f[f.symbol == "BBB"].reset_index(drop=True)
    assert b.loc[:19, "vol_avg20"].isna().all()
    assert b.loc[0, "rows_before"] == 0


def test_delivery_streak_and_ratio(history):
    h = history.copy()
    a = h.symbol == "AAA"
    idx = h[a].index
    h.loc[idx[-6:], "deliv_pct"] = 90.0  # last six days high delivery
    f = features.add_features(h)
    last = f[f.symbol == "AAA"].iloc[-1]
    assert last["deliv_streak55"] == 6
    assert last["deliv_streak50"] == 6
    prior = h.loc[idx[-21:-1], "deliv_pct"].mean()
    assert last["deliv_ratio"] == pytest.approx(90 / prior)


def test_breakout_and_bounce_levels(history):
    f = features.add_features(history)
    a = f[f.symbol == "AAA"].reset_index(drop=True)
    i = 30
    assert a.loc[i, "high20_prior"] == pytest.approx(a.loc[i - 20 : i - 1, "high"].max())
    assert a.loc[i, "low10_prior"] == pytest.approx(a.loc[i - 10 : i - 1, "low"].min())
    age = a.loc[i, "low10_age"]
    assert a.loc[i - age, "low"] == pytest.approx(a.loc[i, "low10_prior"])


def test_vwap_is_volume_weighted_typical_price(history):
    f = features.add_features(history)
    a = f[f.symbol == "AAA"].reset_index(drop=True)
    w = a.loc[25:29]
    tp = (w["high"] + w["low"] + w["close"]) / 3
    assert a.loc[29, "vwap5"] == pytest.approx((tp * w["volume"]).sum() / w["volume"].sum())


def test_snapshot_limits_lookback(history):
    day = history["date"].max()
    snap = features.snapshot(history, day)
    assert set(snap.index) == {"AAA", "BBB"}
    assert (snap["rows_before"] == 30).all()
    assert (snap["date"] == pd.Timestamp(day)).all()
