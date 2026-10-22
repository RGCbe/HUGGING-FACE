import pandas as pd
import pytest

from marketscan import features, scanners


def row(**kw):
    base = dict(vol_ratio=1.0, deliv_pct=40.0, deliv_ratio=1.0, deliv_streak55=0, trade_size_ratio=1.0, day_change=0.5,
                close_position=0.5, breakout_pct=-1.0)
    base.update(kw)
    return pd.Series(base)


def test_smart_money_points_table():
    r = row(vol_ratio=7.85, deliv_pct=98.22, deliv_ratio=1.51, deliv_streak55=9, trade_size_ratio=15.6, day_change=-0.59,
            close_position=0.15)
    parts = scanners.smart_money_parts(r)
    assert parts == {"volume_spike": 20, "delivery_level": 20, "delivery_spike": 8, "accumulation": 20, "large_trades": 15,
                     "quiet_accumulation": 12, "price_strength": 0, "breakout_volume": 0}
    assert sum(parts.values()) == 95


@pytest.mark.parametrize("ratio,points", [(1.99, 0), (2.0, 5), (2.5, 10), (3.0, 15), (4.0, 20)])
def test_volume_tiers(ratio, points):
    assert scanners.smart_money_parts(row(vol_ratio=ratio))["volume_spike"] == points


def test_new_high_needs_volume_for_full_points():
    assert scanners.smart_money_parts(row(breakout_pct=1, vol_ratio=2.1))["breakout_volume"] == 15
    assert scanners.smart_money_parts(row(breakout_pct=1, vol_ratio=1.9))["breakout_volume"] == 8


@pytest.mark.parametrize("score,g", [(95, "A+"), (90, "A+"), (85, "A"), (75, "B+"), (61, "B"), (50, "C+")])
def test_grade(score, g):
    assert scanners.grade(score) == g


@pytest.mark.parametrize("score,chg,a", [(55, 1, "WATCH"), (65, 1, "ACCUMULATE"), (75, -1, "ACCUMULATE"), (75, 0.5, "BUY"),
                                         (85, 0.5, "STRONG BUY")])
def test_action(score, chg, a):
    assert scanners.action(score, chg) == a


def test_trend_labels_cover_every_position():
    assert len(scanners.TRENDS) == 8
    assert scanners.TRENDS[(True, True, True)] == "STRONG BULLISH"
    assert scanners.TRENDS[(False, False, False)] == "STRONG BEARISH"


def test_penny_points():
    r = pd.Series(dict(day_change=11, vol_ratio=5.5, deliv_pct=62, deliv_streak40=6, breakout_pct=2, return_5d=16,
                       close_position=0.9))
    assert sum(scanners.penny_parts(r).values()) == 30 + 30 + 20 + 20 + 15 + 15 + 10


def test_run_all_on_synthetic_history(history):
    h = history.copy()
    last = h["date"].max()
    spike = (h.symbol == "AAA") & (h.date == last)
    h.loc[spike, ["volume", "deliv_pct", "turnover_lacs"]] = [600_000, 92.0, 600.0]
    snap = features.snapshot(h, last)
    res = scanners.run_all(snap)
    assert set(res) == set(scanners.SCANNERS) | {"poc_levels", "multi_signal"}
    assert "AAA" in set(res["volume_spike"]["symbol"])
    assert "AAA" in set(res["delivery_spike"]["symbol"])
    sm = res["smart_money"]
    assert list(sm["symbol"]) == ["AAA"]
    assert sm.loc[0, "score"] >= 50
    assert "AAA" in set(res["multi_signal"]["symbol"])


def test_next_day_levels_are_consistent(history):
    snap = features.snapshot(history, history["date"].max())
    snap["turnover_lacs"] = 500
    out = scanners.next_day_setups(snap)
    for _, r in out.iterrows():
        assert r["stop_loss"] < r["entry"] < r["target1"] < r["target2"]


def test_bounce_rows_meet_documented_conditions(history):
    # Every bounce row must be a green up-day closing strong off a 20-day bottom.
    snap = features.snapshot(history, history["date"].max())
    out = scanners.bounces(snap)
    for _, r in out.iterrows():
        assert r["day_change"] >= 1
        assert r["close_position"] >= 0.7
        assert r["bounce_pct"] >= 3


def test_coiled_reports_prior_15_volume_ratio(history):
    snap = features.snapshot(history, history["date"].max())
    out = scanners.coiled(snap, max_range=100)  # loose range so rows appear
    assert "vol_ratio15" in out.columns
