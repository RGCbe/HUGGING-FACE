# Live data with Fyers (runs on your VPS)

The scanners are end-of-day. For live intraday straddle VWAP and order flow,
connect a broker feed. This repo ships a Fyers API v3 connector. Run it on the
machine that holds your Fyers credentials (your VPS) — the key stays there and
is read from the environment, never from the code.

## 1. Install the SDK (on the VPS)

```bash
pip install fyers-apiv3
```

## 2. Set your credentials in the environment

Copy `.env.example` to `.env` and fill it in, or export the variables. `.env`
is git-ignored; never commit it or paste the values anywhere.

```bash
export FYERS_APP_ID="ABCD1234-100"       # your client id
export FYERS_SECRET_ID="xxxxxxxx"        # only for token generation
export FYERS_REDIRECT_URI="https://127.0.0.1/"
```

## 3. Generate today's access token

Fyers tokens expire around 6:30 AM IST, so refresh each morning:

```bash
python -m marketscan.brokers.fyers_auth
# open the printed URL, log in, paste back the auth_code
export FYERS_ACCESS_TOKEN="<the token it prints>"
```

## 4. Use it

Live ATM straddle VWAP for NIFTY:

```bash
python scripts/fyers_live_straddle.py --symbol NSE:NIFTY50-INDEX
```

In your own code:

```python
from marketscan.brokers import fyers

client = fyers.FyersClient()                 # reads the env vars
print(client.profile())                      # auth check
chain = client.option_chain("NSE:NIFTY50-INDEX")
atm = client.atm_straddle_symbols("NSE:NIFTY50-INDEX")
bars = client.history("NSE:SBIN-EQ", resolution="1", days=1)
```

Stream live ticks and turn them into bars for the straddle or order-flow
functions:

```python
from marketscan.brokers import fyers

ticks = []
def on_tick(msg):
    ticks.append({"time": msg["timestamp"], "ltp": msg["ltp"], "volume": msg.get("vol_traded_today", 0)})

fyers.data_socket(on_tick, ["NSE:NIFTY50-INDEX"])   # blocks; run in a thread/process
# later:
bars = fyers.ticks_to_bars(pd.DataFrame(ticks), "1min")
```

## What goes live, and what stays end-of-day

| Feature | Live with Fyers |
|---|---|
| Straddle VWAP (intraday) | Yes — ATM call + put streamed, VWAP per session |
| Order flow / footprint | Approximate — built from streamed ticks (lite mode is LTP only; full mode adds depth) |
| Volume-based scanners | Yes, using volume so far vs the normal pace |
| Smart-money / delivery scanners | No — NSE publishes delivery only after close; run these each evening |

## Security

- The token lets someone act on your account. Keep it on the VPS, in the
  environment or a file only you can read. Do not commit it, log it, or paste
  it into any chat.
- Regenerate the token daily; an old one simply stops working.
- The connector and auth helper never print the secret or token except the
  one line the auth helper outputs for you to copy.
