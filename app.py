"""Streamlit dashboard: scanners, stock view, straddle VWAP, order flow, pairs.

Run locally with ``streamlit run app.py``.
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from marketscan import data, features, orderflow, pairs, scanners, straddle

st.set_page_config(page_title="Market Scanner", layout="wide")

SCANNER_TITLES = {
    "smart_money": "Smart money (volume + delivery + big trades)",
    "next_day": "Next-day setups (entry, stop, targets)",
    "penny": "Penny movers (Rs 1-50, high risk)",
    "early": "Early setups (quiet build-up before a move)",
    "continuous_delivery": "Continuous delivery (50%+ for 5+ days)",
    "new_high": "New 20-day highs",
    "volume_spike": "Volume spike (2x+ normal)",
    "delivery_spike": "Delivery spike (1.5x+ normal)",
    "bounce": "Bounce from recent low",
    "coiled": "Coiled (breakout from tight 15-day range)",
    "poc_levels": "VWAP levels 5/15/30 days",
    "multi_signal": "Multi-signal (in 2+ lists)",
}


@st.cache_data(show_spinner="Downloading NSE daily files (first run can take a minute)...")
def load_equity(end: date) -> pd.DataFrame:
    return data.equity_history(end, days=75)


@st.cache_data(show_spinner="Computing scanners...")
def load_scans(end: date, scan_day: date) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    snap = features.snapshot(load_equity(end), scan_day)
    return snap, scanners.run_all(snap)


@st.cache_data(show_spinner="Downloading NSE F&O files...")
def load_fo(end: date, days: int, symbol: str) -> pd.DataFrame:
    return data.fo_history(end, days=days, symbol=symbol)


st.sidebar.title("Market Scanner")
picked = st.sidebar.date_input("Scan date", value=date.today(), max_value=date.today())
hist = load_equity(picked)
if hist.empty:
    st.error("No NSE data found for this period. Try an earlier date.")
    st.stop()
trading_days = sorted(hist["date"].dt.date.unique())
scan_day = max(d for d in trading_days if d <= picked)
st.sidebar.caption(f"Using {scan_day:%d %b %Y} - {len(trading_days)} trading days loaded")
page = st.sidebar.radio("View", ["Scanners", "Stock", "Straddle VWAP", "Order flow", "Pairs"])
snap, results = load_scans(picked, scan_day)

if page == "Scanners":
    st.header(f"Scanners - {scan_day:%d %b %Y}")
    st.caption(f"{len(snap):,} stocks scanned. End-of-day NSE data; not investment advice.")
    names = list(SCANNER_TITLES)
    counts = {n: len(results[n]) for n in names}
    choice = st.selectbox("Scanner", names, format_func=lambda n: f"{SCANNER_TITLES[n]} - {counts[n]}")
    df = results[choice]
    st.dataframe(df, width="stretch", hide_index=True, height=600)
    st.download_button("Download CSV", df.to_csv(index=False), file_name=f"{choice}_{scan_day}.csv")

elif page == "Stock":
    sym = st.selectbox("Symbol", sorted(snap.index), index=sorted(snap.index).index("RELIANCE") if "RELIANCE" in snap.index else 0)
    h = features.add_features(hist[hist["symbol"] == sym])
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=h["date"], open=h["open"], high=h["high"], low=h["low"], close=h["close"], name=sym), 1, 1)
    for n, color in ((5, "#e4572e"), (15, "#29335c"), (30, "#a8c686")):
        fig.add_trace(go.Scatter(x=h["date"], y=h[f"vwap{n}"], name=f"VWAP {n}d", line={"color": color, "width": 1.5}), 1, 1)
    fig.add_trace(go.Bar(x=h["date"], y=h["volume"], name="Volume", marker_color="#8d99ae"), 2, 1)
    fig.add_trace(go.Bar(x=h["date"], y=h["deliv_pct"], name="Delivery %", marker_color="#2a9d8f"), 3, 1)
    fig.update_layout(height=720, xaxis_rangeslider_visible=False, legend={"orientation": "h"})
    st.plotly_chart(fig, width="stretch")
    row = snap.loc[sym]
    cols = st.columns(5)
    cols[0].metric("Close", f"{row['close']:.2f}", f"{row['day_change']:+.2f}%")
    cols[1].metric("Volume vs 20d", f"{row['vol_ratio']:.2f}x")
    cols[2].metric("Delivery", f"{row['deliv_pct']:.1f}%", f"{row['deliv_ratio']:.2f}x avg")
    cols[3].metric("Delivery streak (55%+)", f"{int(row['deliv_streak55'])} d")
    parts = scanners.smart_money_parts(row)
    cols[4].metric("Smart-money score", sum(parts.values()))
    st.write({k: v for k, v in parts.items() if v})

elif page == "Straddle VWAP":
    st.header("ATM straddle with VWAP (end of day)")
    c1, c2 = st.columns(2)
    sym = c1.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"])
    days = c2.slider("Calendar days", 10, 90, 30)
    fo = load_fo(scan_day, days, sym)
    if fo.empty:
        st.warning("No F&O data for this range.")
        st.stop()
    dual = straddle.dual_straddle(fo, sym)
    for col in ("date", "expiry_near", "expiry_next"):
        dual[col] = pd.to_datetime(dual[col]).dt.date
    fig = go.Figure()
    for leg, color in (("near", "#e4572e"), ("next", "#29335c")):
        fig.add_trace(go.Scatter(x=dual["date"], y=dual[f"straddle_close_{leg}"], name=f"{leg} expiry close", line={"color": color}))
        fig.add_trace(go.Scatter(x=dual["date"], y=dual[f"straddle_vwap_{leg}"], name=f"{leg} expiry VWAP", line={"color": color, "dash": "dot"}))
    fig.update_layout(height=520, legend={"orientation": "h"}, yaxis_title="Call + put premium")
    st.plotly_chart(fig, width="stretch")
    st.caption("Close above its VWAP means option premiums rose through the day (buyers in control); below means decay "
               "(sellers in control). Each point uses the ATM strike of that day. Intraday charts need a broker feed.")
    st.dataframe(dual, width="stretch", hide_index=True)

elif page == "Order flow":
    st.header("Order flow and footprint")
    st.caption("Free NSE data has no ticks. Upload a tick CSV (time, price, qty, optional bid, ask) or use demo data.")
    up = st.file_uploader("Tick CSV", type="csv")
    ticks = pd.read_csv(up, parse_dates=["time"]) if up else orderflow.synthetic_ticks()
    c1, c2, c3 = st.columns(3)
    bar = c1.selectbox("Bar", ["1min", "5min", "15min"], index=1)
    tick_size = c2.number_input("Tick size", value=0.05, min_value=0.01, step=0.05)
    rows = c3.slider("Ticks per row", 1, 20, 4)
    fp = orderflow.imbalances(orderflow.footprint(ticks, bar, tick_size, rows))
    bars = orderflow.bar_summary(ticks, bar, tick_size)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
    fig.add_trace(go.Heatmap(x=fp["bar"], y=fp["level"], z=fp["delta"], colorscale="RdYlGn", zmid=0,
                             text=fp["bid_vol"].astype(int).astype(str) + " x " + fp["ask_vol"].astype(int).astype(str),
                             hovertemplate="%{x}<br>%{y}<br>bid x ask %{text}<br>delta %{z}<extra></extra>", name="Footprint"), 1, 1)
    fig.add_trace(go.Scatter(x=bars["bar"], y=bars["poc"], mode="markers", marker={"symbol": "line-ew-open", "size": 16, "color": "black"}, name="POC"), 1, 1)
    fig.add_trace(go.Bar(x=bars["bar"], y=bars["delta"], marker_color=["#2a9d8f" if d >= 0 else "#e76f51" for d in bars["delta"]], name="Delta"), 2, 1)
    fig.update_layout(height=720, showlegend=False)
    st.plotly_chart(fig, width="stretch")
    vp = orderflow.volume_profile(ticks, tick_size, rows)
    st.write(f"Session POC {vp['poc']:.2f} - value area {vp['val']:.2f} to {vp['vah']:.2f} - "
             f"stacked buy imbalances {int(fp['buy_imbalance'].sum())}, sell imbalances {int(fp['sell_imbalance'].sum())}")
    st.dataframe(bars, width="stretch", hide_index=True)

elif page == "Pairs":
    st.header("Pair analysis")
    closes = hist.pivot(index="date", columns="symbol", values="close")
    symbols = sorted(closes.columns)
    c1, c2, c3 = st.columns(3)
    a = c1.selectbox("Stock A", symbols, index=symbols.index("HDFCBANK") if "HDFCBANK" in symbols else 0)
    b = c2.selectbox("Stock B", symbols, index=symbols.index("ICICIBANK") if "ICICIBANK" in symbols else 1)
    window = c3.slider("Z-score window", 10, 40, 20)
    df, stats = pairs.analyse(closes[a], closes[b], window)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
    fig.add_trace(go.Scatter(x=df.index, y=df["ratio"], name=f"{a}/{b}"), 1, 1)
    fig.add_trace(go.Scatter(x=df.index, y=df["zscore"], name="z-score"), 2, 1)
    for level in (-2, 0, 2):
        fig.add_hline(y=level, line_dash="dot", row=2, col=1)
    fig.update_layout(height=560, legend={"orientation": "h"})
    st.plotly_chart(fig, width="stretch")
    st.write({k: (round(v, 3) if isinstance(v, float) else v) for k, v in stats.items()})
    st.subheader("Find pairs")
    group = st.text_input("Symbols (comma separated)", "HDFCBANK,ICICIBANK,KOTAKBANK,AXISBANK,SBIN,INDUSINDBK,BANKBARODA,PNB")
    chosen = [s.strip().upper() for s in group.split(",") if s.strip().upper() in closes.columns]
    if len(chosen) >= 2:
        st.dataframe(pairs.scan_pairs(closes[chosen], min_corr=0.3, window=window).round(3), width="stretch", hide_index=True)
