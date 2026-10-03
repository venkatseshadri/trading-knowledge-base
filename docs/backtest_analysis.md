# Backtest Analysis: "Iron Butterfly" on NIFTY 50 Futures

**Source file:** `/home/trading_ceo/backtest_results.csv`
**Analysis date:** 2026-05-01
**Sample size:** 6 trades (15-Oct-2024 → 28-Oct-2024)

---

## 1. Headline Performance

| Metric | Value |
|---|---|
| Trades | 6 |
| Winners | 0 |
| Losers | 6 |
| Win rate | **0%** |
| Total entry cost | 5.00 |
| Total P&L | -3.24 |
| Avg pnl_percent | **-64.08%** |
| Loss range | -58.16% to -68.60% |

Every single trade lost money, and losses are tightly clustered around -64% of entry cost. The sample window is only **two weeks**, so this is statistically meaningless on its own — but the *uniformity* of the losses points to a structural issue, not just bad luck.

---

## 2. Trade-by-trade

| Date | Expiry | buy_ce | sell_ce | buy_pe | sell_pe | entry_cost | pnl | pnl_% |
|---|---|---|---|---|---|---|---|---|
| 15/10/2024 | 17OCT24 | 27950 | 27850 | 23050 | 23150 | 0.10 | -0.064 | -63.67% |
| 15/10/2024 | 31OCT24 | 27950 | 27850 | 22250 | 22350 | 0.60 | -0.378 | -62.99% |
| 17/10/2024 | 24OCT24 | 27950 | 27850 | 23050 | 23150 | 0.65 | -0.446 | -68.60% |
| 17/10/2024 | 31OCT24 | 27950 | 27850 | 22250 | 22350 | 1.15 | -0.782 | -68.02% |
| 23/10/2024 | 24OCT24 | 27950 | 27850 | 22700 | 22800 | 0.05 | -0.029 | -58.16% |
| 28/10/2024 | 14NOV24 | 26900 | 26600 | 22650 | 22800 | 2.45 | -1.544 | -63.04% |

---

## 3. Structural Red Flags (more important than the P&L)

### 3.1 This is not an Iron Butterfly — it is an Iron Condor

A true iron butterfly has **one body strike** at-the-money: `sell_ce == sell_pe`.

In this data the short strikes are far apart:

- `sell_ce` = 27850 (or 26600 in the last row)
- `sell_pe` = 23150 / 22350 / 22800 / etc.
- Roughly **4,000–5,000 points** between the two short strikes

That payoff profile is an **Iron Condor** (or split-strike short strangle with wings), not a butterfly. The greeks, breakevens, expected win-rate, and risk-of-ruin are all different. Any conclusions framed as "iron butterfly" are mislabeled.

### 3.2 `max_profit` is negative in every row — likely a leg-direction bug

For a correctly constructed short-vol structure you collect a **net credit**:

- `entry_cost` should be **negative** (credit received at entry)
- `max_profit` should be **positive** (= credit received)
- `max_loss` = wing_width − credit

In this CSV:

- `entry_cost` is **positive** (0.05 → 2.45) → you are paying to enter
- `max_profit` is **negative** and equals `-entry_cost` → no theoretical upside

Given the strikes:

- **Call spread:** Buy 27950 CE / Sell 27850 CE. The 27850 is closer to spot → more expensive → selling it should produce a credit.
- **Put spread:** Buy 23050 PE / Sell 23150 PE. The 23150 is closer to spot → more expensive → selling it should produce a credit.

Both spreads *should* contribute net premium received. The positive `entry_cost` therefore suggests one of:

1. The buy/sell columns are **inverted** at order placement (you are actually long the inner strikes and short the outer wings → a long debit fly/condor with no edge unless price pins).
2. `entry_cost` is computed as `|net premium|` and shown as a debit regardless of direction (cosmetic bug, real P&L might still be wrong-signed downstream).
3. `max_profit` is being computed as the P&L if everything expires worthless, not the theoretical maximum payoff.

Until this is resolved, **the P&L numbers cannot be trusted as a measure of strategy edge.**

### 3.3 Market regime during the sample

NIFTY 50 fell from ~25,000 → ~23,800 over this two-week window. The put-side short strikes (23,150 / 22,800 / 22,350) sat directly in that decline path, so even a *correctly structured* short-vol position would have been stressed. A 100% loss rate in a single trending two-week sample says almost nothing about long-run edge.

---

## 4. What's Missing from the Backtest

To draw any real conclusion the backtest needs:

- **At least 12–24 months** of trades spanning trending, ranging, high-IV, and low-IV regimes
- A **sign check on `entry_cost`** — confirm whether the strategy collects or pays premium at entry
- A clear decision on **butterfly vs condor** — and rename the strategy accordingly
- Per-trade columns for: spot/futures at entry, IV at entry, days-to-expiry, exit reason (expiry vs stop vs target)
- Aggregate metrics: max drawdown, Sharpe / Sortino, average winner vs average loser, profit factor
- Regime breakdown: P&L conditional on realized move from entry to expiry

---

## 5. Recommendation

1. **Do not act on these results.** Six trades, all losers, in a single trending fortnight, with a probable leg-direction bug → no signal.
2. **Audit the strategy code first** — specifically the sign of `entry_cost` and which legs are long vs short. If the buy/sell columns are inverted, fixing that single bug may flip the entire P&L distribution.
3. **Decide what you're actually testing** — true ATM iron butterfly (single body strike) or iron condor (split bodies). The current strikes are condor-shaped.
4. **Re-run across a longer window** (multi-year, multi-regime) once the structure is verified.

---

*Caveat: this analysis is based purely on the 6 rows in the CSV. Confirming or refuting the leg-direction concern requires reading the strategy code that produced the file.*
