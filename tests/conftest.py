import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def make_history(symbols=("AAA", "BBB"), days=40, seed=1) -> pd.DataFrame:
    """Synthetic equity history in the shape ``data.equity_history`` returns."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2026-08-03", periods=days)
    rows = []
    for sym in symbols:
        close = 100.0
        for d in dates:
            prev = close
            close = round(prev * (1 + rng.normal(0, 0.01)), 2)
            high = round(max(prev, close) * 1.01, 2)
            low = round(min(prev, close) * 0.99, 2)
            vol = int(rng.integers(90_000, 110_000))
            deliv = float(rng.uniform(30, 45))
            trades = int(rng.integers(900, 1100))
            rows.append({
                "symbol": sym, "series": "EQ", "date": d, "prev_close": prev, "open": prev, "high": high, "low": low,
                "last": close, "close": close, "avg_price": (high + low + close) / 3, "volume": vol,
                "turnover_lacs": vol * close / 1e5, "trades": trades, "deliv_qty": vol * deliv / 100, "deliv_pct": deliv,
            })
    return pd.DataFrame(rows)


@pytest.fixture
def history():
    return make_history()
