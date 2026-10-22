# Scanner rules

All scanners run on NSE's free end-of-day equity file (`sec_bhavdata_full`),
EQ series only. Windows count each stock's own trading rows. "Prior 20" means
the 20 rows before the scan date; "last 5" includes the scan date. A stock
needs 20 prior rows to be scanned, and at most 30 prior rows are used.

## Building blocks

| Name | Formula |
|---|---|
| Volume x (buzz) | today's volume / mean volume of the prior 20 rows |
| Delivery % | NSE `DELIV_PER` |
| Delivery ratio | delivery % / mean delivery % of the prior 20 rows |
| Delivery streak | rows in a row, ending today, with delivery % >= 55 (or 50, 40 where noted) |
| Trade size x | (turnover / trades) / mean of the same over the prior 20 rows |
| Close position | (close - low) / (high - low) |
| 20-day high | highest high of the prior 20 rows |
| VWAP n | sum(typical price x volume) / sum(volume) over the last n rows, typical = (H+L+C)/3 |

## Smart money

Points from eight parts, summed (maximum 125, listed from 50):

| Part | Points |
|---|---|
| Volume x | >= 4: 20, >= 3: 15, >= 2.5: 10, >= 2: 5 |
| Delivery % | >= 80: 20, >= 70: 15, >= 60: 10, >= 50: 5 |
| Delivery ratio | >= 2: 15, >= 1.5: 8 |
| Delivery streak (55%) | >= 7: 20, >= 5: 12, >= 3: 5 |
| Trade size x | >= 2.5: 15, >= 2: 10, >= 1.5: 5 |
| Quiet buying | 12 when the price moved less than 1% with delivery >= 60% |
| Strong close | 8 when close position >= 0.85 and the day's gain >= 1% |
| New 20-day high | 15 with volume x >= 2, otherwise 8 |

Listed only with volume >= 50,000 shares, turnover >= Rs 1 crore and volume x >= 1.3.
Grade: A+ >= 90, A >= 80, B+ >= 70, B >= 60, C+ otherwise.
Action: below 60 WATCH; 60-69 ACCUMULATE; 70+ on a down day ACCUMULATE, else BUY (STRONG BUY from 80).

## Lists

| Scanner | Rule | Order |
|---|---|---|
| Volume spike | volume x >= 2 | volume x, top 100 |
| Delivery spike | delivery % >= 50 and delivery ratio >= 1.5 | ratio, top 100 |
| New high | close above the 20-day high | breakout %, top 100 |
| Coiled | prior-15-row range under 5% and close above its high (volume ratio shown over the prior 15 rows) | tightest first |
| Continuous delivery | delivery >= 50% for 5+ rows in a row (shown up to 10) | streak, then average delivery over it |
| Bounce | green up-day (close > open, day change >= 1%), close position >= 0.7, 3%+ off a prior-10-row low that is also the 20-day low (a genuine bottom) | bounce % |

## VWAP levels (5, 15, 30 days)

Close compared with VWAP 5, 15 and 30. "Near" = within 2%.

| Above 5 / 15 / 30 | Trend |
|---|---|
| yes / yes / yes | STRONG BULLISH |
| no / no / no | STRONG BEARISH |
| yes / no / no | REVERSAL POSSIBLE |
| no / yes / yes | PULLBACK |
| yes / yes / no | STRONG REVERSAL |
| no / no / yes | CORRECTION |
| no / yes / no | CONSOLIDATION |
| yes / no / yes | MILD BULLISH |

Stack: rising when VWAP5 > VWAP15 > VWAP30, falling when reversed, mixed otherwise.

## Penny movers (Rs 1-50)

Turnover >= Rs 10 lakh and volume >= 20,000. Listed from 40 points.

| Part | Points |
|---|---|
| Day's gain | >= 10%: 30, >= 5%: 20, >= 3%: 10 |
| Volume x | >= 5: 30, >= 3: 20, >= 2: 10 |
| Delivery % | >= 60: 20, >= 45: 10 |
| Delivery streak (40%) | >= 5: 20, >= 3: 10 |
| Above 20-day high | 15 |
| 5-day return | >= 15%: 15, >= 10%: 10 |
| Close position >= 0.8 | 10 |

Risk: under Rs 5 very high, under Rs 20 high, otherwise medium.

## Early setups

Turnover >= Rs 50 lakh, listed from 60 points.

| Part | Points |
|---|---|
| 5-row range under 5% and narrower than the 5 rows before | 25; narrower but up to 8%: 15 |
| 5-row delivery up 10%+ on the previous 5 rows and >= 45% | 25; otherwise >= 55%: 15 |
| 5-row volume / 20-row volume | < 0.6: 20, < 0.8: 10 |
| Volume returning: volume x (20 incl. today) >= 1.2 while 5-row volume < 0.9 | 15 |
| Higher lows in the last 5 rows | 4 of 4: 20, 3 of 4: 10 |
| Close vs VWAP 20 | 0 to +3% on an up day: 20; within 3%: 10 |
| Close position >= 0.8 on an up day | 10 |
| Day's change between -1% and +3% | 10 |

## Next-day setups

First match wins:

| Setup | Condition | Entry | Stop | Targets |
|---|---|---|---|---|
| Breakout ready | within 2% of the 20-day high | close | higher of entry - 1.5% and 5-row low - 1% | +3.5%, +6% |
| Squeeze | 5-row range under 3% | today's low | lower of entry - 1.5% and 3-row low | +4%, +7% |
| Support bounce | within 2% of VWAP 20 after a down day | today's low | lower of entry - 1.5% and today's low - 1% | +3%, +5% |
| Momentum | up 2%+ with SMA5 above SMA20 | close | higher of entry - 1.5% and 5-row low - 1% | +3.5%, +6% |

Score = 40 + good delivery 25 + volume confirming 20 + strong close 15 +
delivery rising 15 + above averages 15 + higher lows 10 + near support 10.

## Multi-signal

Stocks in two or more lists above, plus "VWAP bullish" (strong bullish and near VWAP 5).

## Straddle VWAP

From NSE's F&O file: for each day, the strike nearest the underlying for the
nearest (and next) expiry. Straddle = call + put close. Daily straddle VWAP =
each leg's `TtlTrfVal / (TtlTradgVol x lot) - strike`, summed (NSE reports
option turnover as (strike + premium) x quantity).

## Order flow

Trades are buyer-initiated at or above the ask and seller-initiated at or
below the bid; otherwise the tick rule decides. Footprint cells hold bid
(sell) and ask (buy) volume per bar and price row. Diagonal imbalance = ask
volume at a price >= 3x bid volume one row lower (and the reverse for selling).
Value area covers 70% of the session's volume around the POC.

## Pairs

Spread = log(A) - beta x log(B), beta from least squares. Z-score over a
rolling window (default 20). Entry at |z| >= 2, exit at |z| <= 0.5.
Mean reversion is checked with an ADF statistic (below -2.86 at 5%) and the
half-life of the spread.

## Validation

These rules were reverse-engineered black-box (clean-room): only the numbers a
public page shows plus NSE's own free files, never any site's source code or
private endpoints. Checked against 31 trading days of public end-of-day
results, the smart-money, volume-spike, delivery-spike, new-high, coiled and
penny lists reproduce the published lists at roughly 90-100%, and the smart,
POC, high-buzz and new-high column values are exact or near-exact. The bounce,
next-day and early-setup *selections* are our own definitions: their published
column values match, but the exact stock-selection rule for those three is not
reproduced, so those lists are built from the documented rules above rather
than claimed to match any site.
