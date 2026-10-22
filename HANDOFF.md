# Handoff

Context for continuing this project in another session (e.g. local Claude Code
with VPS access). Branch: `ccr-6784e06b-dhsdvg` (PR #3, open draft, 4 commits
ahead of `main`).

## What this repo is

`marketscan/` — end-of-day scanners for NSE stocks, built only from NSE's free
daily files, plus straddle VWAP, order flow / footprint, pair analysis, a
Streamlit dashboard (`app.py`), a CLI (`python -m marketscan ...`), and a Fyers
live-data connector. The scanner rules were worked out black-box (clean-room):
only numbers a public page shows plus NSE's own files — no site's source code,
no private endpoints, no login. Rules are in `docs/scanner-rules.md`.

## Done and tested offline (45 pytest tests pass)

- `marketscan/data.py` — download/cache NSE equity + F&O daily files; skip
  stale (holiday) files by checking the date inside.
- `marketscan/features.py` — per-stock volume/delivery/trade-size/range/VWAP
  features over each stock's own rows.
- `marketscan/scanners.py` — 12 scanners with scores/grades/actions.
- `marketscan/straddle.py`, `orderflow.py`, `pairs.py` — analysis modules.
- `marketscan/brokers/fyers.py` + `fyers_auth.py` — Fyers API v3 connector,
  daily token (interactive and automated), token cache.
- `scripts/fyers_live_straddle.py`, `scripts/fyers_runner.py` — live straddle
  VWAP and a hands-off runner.
- `deploy/` — `fyers.env.example` and a systemd unit for a set-and-forget
  service. See `docs/live-data.md`.

## Open items — need a LIVE run on the VPS to confirm

These could not be tested from the cloud session (no key, needs market hours):

1. **WebSocket field names.** `scripts/fyers_live_straddle.py` reads `ltp` and
   `vol_traded_today`/`volume` from each tick (`on_tick`). Confirm against the
   actual `FyersDataSocket` `on_message` payload for your SDK version; adjust
   if different.
2. **Option-chain response shape.** `FyersClient.option_chain` parses
   `data.optionsChain` with `symbol`/`strike_price`/`option_type`/`ltp` and
   reads the spot from the index row. Confirm the keys.
3. **Automated login endpoints.** `fyers_auth.auto_token()` drives Fyers'
   internal `vagator/v2` + `api/v3/token` flow with FY_ID / PIN / TOTP. These
   are not part of the public API and can change; verify or fall back to the
   interactive token.

## How to run live (on the VPS)

```bash
pip install fyers-apiv3 pyotp
cp deploy/fyers.env.example deploy/fyers.env   # fill in real secrets, chmod 600
# semi-auto: python -m marketscan.brokers.fyers_auth  (log in once/day)
# full-auto: set FYERS_AUTO_LOGIN=1 and use the systemd service
python scripts/fyers_live_straddle.py --symbol NSE:NIFTY50-INDEX
```

## Security (do not skip)

- Fyers secrets (app id, secret, FY_ID, PIN, TOTP seed, tokens) live only on
  the VPS, in `deploy/fyers.env` (chmod 600) or the environment. They are
  git-ignored. Never commit them, log them, or paste them into any chat.
- A token/PIN/TOTP leak = account takeover (trading, not just data). Keep the
  VPS locked down.

## Not to publish

The repo is public and intentionally contains **no** reference to the site the
scanner rules were derived from. A separate private report (delivered to the
owner, not in this repo) holds the full third-party breakdown. Do not add third
-party names, their obfuscated code, or paid-product internals to this repo —
those were deliberately left out (login-gated and paid content were off-limits).

## Tests

```bash
pip install pytest && python -m pytest       # 45 pass, no network/keys needed
```
