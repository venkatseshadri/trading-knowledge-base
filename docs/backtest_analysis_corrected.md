# Backtest Analysis: Iron Butterfly on NIFTY 50 Futures (Corrected Run)

**Source file:** `/home/trading_ceo/backtest_results_corrected.csv`
**Analysis date:** 2026-05-01
**Sample size:** 62 trades (15-Oct-2024 → 28-Oct-2024 entries, expiries from Oct-24 to Jun-25)

---

## 1. Headline Performance

| Metric | Value |
|---|---|
| Trades | 62 |
| Wins | 32 (51.6%) |
| Losses | 30 (48.4%) |
| **Total P&L** | **−2,725.50** |
| Total credit collected | 19,538.15 |
| P&L as % of credit at risk | **−13.95%** |
| Avg P&L per trade | −43.96 |
| Median P&L | +3.06 |
| Stdev P&L | 170.24 |
| Avg winner | +44.68 |
| Avg loser | **−138.51** |
| Largest winner | +387.08 |
| Largest loser | **−722.82** |
| **Profit factor** | **0.344** |

**The headline win rate (51.6%) is misleading.** The strategy loses ~3× more on losers than it makes on winners (`avg_loser / avg_winner = 3.1`). Profit factor of 0.34 means for every ₹1 won, ~₹2.90 is lost. Median trade is barely positive, but the tail of large losses dominates.

The signs in the file are now consistent:

- `entry_cost` is **negative** = credit received (correctly structured short-vol)
- `max_profit` is **positive** = max payout if pinned at body strike
- `max_loss` column equals `|entry_cost|` numerically — this is **not** the true max loss for an iron fly (true max loss = `wing_width − credit`); cosmetic but worth noting.
- `pnl_percent` appears **sign-flipped** vs `pnl` (positive `pnl_percent` = loss, negative = profit). Use the raw `pnl` column for any further work.

---

## 2. The Real Story: Two Strategies Bundled Into One

The 62 trades split cleanly into two very different setups by wing width / credit size:

| Group | Trades | Total P&L | Avg/trade |
|---|---|---|---|
| **Narrow short-dated flies** (wing 50–150 pts, credit < 100) | 36 | **+106.36** | **+2.95** |
| Mid-wing trades (credit 100–500) | 7 | +21.18 | +3.03 |
| **Far-dated wide flies** (wing 1000–2000 pts, credit ≥ 500) | 19 | **−2,853.03** | **−150.16** |

**Almost the entire net loss comes from the 19 far-dated wide-wing trades.** The short-dated narrow iron butterflies — the classic textbook setup — are essentially **breakeven** over this window, slightly positive.

### By wing width

| Call-wing width | Trades | Total P&L | Avg |
|---|---|---|---|
| 50 pts | 40 | +0.38 | +0.01 |
| 100 pts | 4 | −2.95 | −0.74 |
| 150 pts | 1 | +13.14 | +13.14 |
| **1000 pts** | **14** | **−1,539.63** | **−109.97** |
| **2000 pts** | **3** | **−1,196.43** | **−398.81** |

The 17 wide-wing trades (≥1000 pts) account for **−2,736 of the total −2,725 P&L**. Everything else is noise.

### By expiry

| Expiry | Trades | Total P&L | Avg |
|---|---|---|---|
| 05DEC24 | 1 | +31.46 | +31.46 |
| 07NOV24 | 7 | −1.83 | −0.26 |
| 14NOV24 | 5 | −88.21 | −17.64 |
| 17OCT24 | 3 | +14.73 | +4.91 |
| 21NOV24 | 3 | +38.40 | +12.80 |
| 24OCT24 | 6 | +29.48 | +4.91 |
| 26DEC24 | 6 | +100.06 | +16.68 |
| 28NOV24 | 7 | −57.09 | −8.16 |
| 31OCT24 | 7 | −56.44 | −8.06 |
| **24DEC25** | 7 | **−381.23** | −54.46 |
| **27MAR25** | 7 | **−1,158.40** | −165.49 |
| **26JUN25** | 3 | **−1,196.43** | **−398.81** |

Short-dated expiries (Oct/Nov/Dec '24): essentially flat to slightly positive.
Long-dated expiries (Mar/Jun/Dec '25): catastrophic.

---

## 3. Why the Far-Dated Wide Flies Bleed

A 1000–2000 pt wing iron butterfly on NIFTY held for 6–9 months is a different beast from a weekly fly:

1. **Massive directional exposure window.** Over 6–9 months NIFTY easily moves multiple standard deviations. The body strike (e.g. 25000 or 26000) gets blown through, and the position bleeds toward max loss.
2. **Theta is small relative to wing width.** A weekly 50-pt fly captures decay rapidly. A March '25 fly entered in October has tiny daily theta vs the 1000-pt downside it carries.
3. **Vega risk is large.** Long-dated short straddles (the body of the fly) are heavily short vega. Any IV expansion punishes the position before expiry.
4. **NIFTY actually fell ~5% in the test window** (Oct 15 → Oct 28, 2024: 25000 → ~23800). The body strikes at 25000–26000 were left ITM-on-the-put-side, exposing the wide flies to deep losses on the put spread.

**These three losers (-722, -472, -408) are the entire backtest's P&L.** Remove the wide-wing far-dated trades and you have a marginal, mostly flat short-dated iron butterfly book.

---

## 4. Butterfly vs Condor

| Variant | Trades | Total P&L | Avg |
|---|---|---|---|
| True butterfly (`body_ce == body_pe`) | 54 | −2,149.74 | −39.81 |
| Iron condor (split body) | 8 | −575.76 | −71.97 |

Both lose, but the eight split-body "condor" trades all happen to overlap with the wide-wing far-dated set, so this isn't independent of the wing-width issue. Not enough condor trades to draw a separate conclusion.

---

## 5. What This Backtest Is Telling You

1. **The short-dated narrow iron butterfly is, at best, a coinflip in this window.** 51.6% win rate but profit factor 0.34 — wins are too small to pay for the occasional adverse expiry. With more samples it would likely be a slow bleed unless entry timing or exits are tightened.
2. **The far-dated wide-wing variant is unviable as written.** Buying-and-holding a 1000-pt iron fly for 6–9 months on an index that routinely moves 10%+ per quarter is structurally negative-expectancy unless paired with an adjustment regime.
3. **The strategy mixes two regimes that should be evaluated separately.** Reporting one combined P&L hides the fact that the loss is concentrated in a small subset of trades.
4. **Two-week entry window is still tiny.** The market regime over Oct 15–28, 2024 was a ~5% NIFTY drawdown. That's an unfavorable single-regime sample for short-vol structures. Need 12–24 months across IV regimes before drawing strategy conclusions.

---

## 6. Recommended Next Steps

1. **Split the strategy.** Run two separate backtests:
   - Short-dated (≤30 DTE) narrow-wing iron fly
   - Long-dated (≥90 DTE) wide-wing iron fly
   Stop reporting them as one number.
2. **Drop the long-dated wide-wing variant** unless paired with explicit delta-hedging or stop rules. Without those, the math doesn't work.
3. **Fix the data-hygiene issues:**
   - `pnl_percent` is sign-flipped — easy fix, but creates landmines for downstream analysis.
   - `max_loss` is reported as `|entry_cost|`; replace with `wing_width − credit`.
4. **Extend the date range to 12–24 months** spanning trending up, trending down, sideways, and high-IV regimes.
5. **Add per-trade context columns:** spot at entry, IV at entry, DTE at entry, exit reason, exit DTE, MAE/MFE during the trade.
6. **For the short-dated fly** specifically, test exit rules: 25% profit target, 1× credit stop loss, or DTE-based exit (e.g., close at 7 DTE). The current expiry-only exit gives back too much theta to gamma.

---

## 7. Bottom Line

The "corrected" run is genuinely structurally correct now — entries collect credit, signs make sense, and you have a real strategy to evaluate. The verdict on the strategy itself:

- **Short-dated narrow iron butterfly: marginal / breakeven.** Possibly tradeable with tighter exits, but not yet shown to have edge.
- **Far-dated wide iron butterfly: clearly negative-expectancy as configured.** Drop it or redesign with active management.

Without splitting these out, the combined book looks worse than either component deserves credit for, and the wide-wing tail eats everything the narrow trades earn.
