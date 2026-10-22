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

## Fully automated (no daily login, no babysitting)

If you'd rather not log in each morning, the runner can generate the token by
itself and only stream during market hours. This means storing your Fyers
login id, PIN and TOTP seed on the VPS — read the Security note below first.

1. Put the secrets in `deploy/fyers.env` (git-ignored) and lock it down:

   ```bash
   cp deploy/fyers.env.example deploy/fyers.env
   nano deploy/fyers.env      # fill in app id, secret, redirect, fy_id, pin, totp_secret
   chmod 600 deploy/fyers.env
   ```

   The `FYERS_TOTP_SECRET` is the text seed shown when you set up the
   authenticator app for Fyers (the same one that generates the 6-digit code).

2. Install and start it as a service so it survives reboots and runs daily:

   ```bash
   pip install fyers-apiv3 pyotp
   sed -i "s/CHANGE_ME/$USER/g" deploy/fyers-straddle.service
   sudo cp deploy/fyers-straddle.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now fyers-straddle
   journalctl -u fyers-straddle -f        # watch it
   ```

   From then on it refreshes the token each morning, waits for the open,
   streams the straddle VWAP all session, and idles overnight and on weekends.
   No daily action from you.

   Prefer not to use systemd? Run it in `tmux`/`screen` instead:
   `set -a; source deploy/fyers.env; set +a; python scripts/fyers_runner.py`.

The automated login drives Fyers' own login endpoints, which are not part of
the public API and can change. If a morning login fails, the service keeps
retrying and logs the error; fall back to the interactive token (step 3 above)
until it's sorted.

## Security

- The token lets someone act on your account. Keep it on the VPS, in the
  environment or a file only you can read. Do not commit it, log it, or paste
  it into any chat.
- Regenerate the token daily; an old one simply stops working.
- The connector and auth helper never print the secret or token except the
  one line the auth helper outputs for you to copy.
