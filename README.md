---
title: Market Scanner
emoji: 📈
colorFrom: green
colorTo: blue
sdk: streamlit
app_file: app.py
pinned: false
---

# Market Scanner

End-of-day scanners for NSE stocks, built only on NSE's free daily files.
The front matter above lets this repo run as a Hugging Face Space.

* **12 scanners**: smart money, next-day setups (entry/stop/targets), penny
  movers, early setups, continuous delivery, new 20-day highs, volume spike,
  delivery spike, bounce, coiled, VWAP levels (5/15/30 days), multi-signal.
* **Straddle VWAP**: near and next expiry ATM straddle with VWAP for NIFTY,
  BANKNIFTY, FINNIFTY and MIDCPNIFTY (daily, from the F&O file).
* **Order flow / footprint**: bid x ask volume per price, delta, cumulative
  delta, imbalances, POC and value area from tick data (CSV upload or demo
  data; free NSE data has no ticks).
* **Pair analysis**: hedge ratio, spread z-score, ADF test, half-life and a
  pair finder.

The exact rules are in [docs/scanner-rules.md](docs/scanner-rules.md).

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py                         # dashboard
python -m marketscan scan                    # latest day -> output/<date>/*.csv
python -m marketscan scan --date 2026-10-21
python -m marketscan straddle --symbol BANKNIFTY
```

The first run downloads about 75 days of NSE files into `data/cache/`
(set `MARKETSCAN_CACHE` to change it). Later runs reuse them.

## Tests

```bash
pip install pytest
python -m pytest
```

## Data notes

* NSE sometimes serves the previous day's file for a holiday; those files are
  detected by their date and skipped.
* Everything above is end of day. For **live intraday** straddle VWAP and order
  flow, connect a broker feed. A **Fyers API v3** connector is included
  (`marketscan/brokers/fyers.py`); run it on the machine that holds your key —
  credentials are read from the environment, never the code. See
  [docs/live-data.md](docs/live-data.md). `straddle.intraday_straddle` and
  `orderflow.footprint` accept the live bars and ticks it produces.

Not investment advice.
