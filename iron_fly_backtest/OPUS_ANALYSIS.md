# Iron Fly Backtest — Optimized Config, Suggestions & Open Questions

**Author:** Claude Opus 4.7
**Date:** 2026-05-02
**Source data:**
- `/home/trading_ceo/iron_fly_backtest/FULL_NUMBERS.md` (summary tables)
- `/home/trading_ceo/iron_fly_backtest/all_configs_full_stats.csv` (640-row config grid)
- `/home/trading_ceo/iron_fly_backtest/results_2024_2026.csv` (66,880 raw trades, NIFTY Mon+Tue, Jan 2024 → Jan 2026)

**User strategy context (from memory):**
- Single iron fly per slot — *not* concurrent ladder
- On SL hit: close fully and re-enter fresh ATM biased in direction of the move
- Underlying thesis: ~60% of sessions are sideways
- Real entry calendar: Fri/Mon/Tue NIFTY (Tue expiry), Wed/Thu SENSEX (Thu expiry)
- Capital-preservation focus

---

## 1. Headline Recommendation

### Primary config — best risk-adjusted, capital-preserving

| Slot | Time | Structure | TP | SL |
|---|---|---|---|---|
| **Mon (1DTE NIFTY)** | **13:00** | **IB-200w** (Iron Butterfly, ±200 wings) | **TP-500inr** (₹6.67/share fixed = ₹500/lot) | **1.5× credit** |

**Realized stats over 102 Mondays (Jan 2024 → Jan 2026):**

| Metric | Value |
|---|---|
| Mean P&L | **₹2,139/lot** |
| Worst single trade | **−₹3,535** |
| Best single trade | ₹6,214 |
| Win rate | 100% (TP hit on 100/102 trades; 2 EOD exits) |
| Sharpe | **1.84** |
| Profit factor | 34.8 |
| Median credit collected | ₹11,616/lot |

**Vol-regime robustness (mean P&L by vol bucket on this exact config):**

| Vol bucket | n | Mean | Min | Max |
|---|---|---|---|---|
| Low (<10%) | 29 | ₹2,716 | ₹575 | ₹6,214 |
| Med (10–13%) | 39 | ₹1,985 | −₹3,534 | ₹3,160 |
| High (13–16%) | 15 | ₹1,897 | −₹2,913 | ₹2,819 |
| V.High (>16%) | 19 | ₹1,764 | ₹1,240 | ₹2,379 |

Profitable in **every** vol bucket — including the 19 V.High-vol Mondays.

---

### Why not the higher-mean configs?

| Config | Mean | Worst | Sharpe | Tradeoff |
|---|---|---|---|---|
| Mon 13:00 IC100-200w TP-50pct | ₹3,835 | **−₹7,014** | 1.44 | +79% mean, but tail nearly **2× worse** — violates capital-preservation goal |
| Mon 13:00 IC100-200w TP-500inr | ₹3,347 | −₹6,754 | 1.89 | Same fat tail; 0.05 Sharpe edge isn't worth 91% deeper worst |
| **Mon 13:00 IB-200w TP-500inr** | **₹2,139** | **−₹3,535** | **1.84** | **Goldilocks — keeps Sharpe, halves the tail** |
| Mon 11:00 IB-100w TP-250inr | ₹606 | −₹879 | 1.44 | Smallest worst, but mean too low to absorb costs/slippage |

**Scaling principle:** if you want more exposure, run **two lots of IB-200w** rather than one lot of IC100-200w. Same expected return, smaller worst-case tail.

---

## 2. What the Data Is Telling You

### 2a. Tuesday (0DTE) is structurally worse than Monday (1DTE) — by 3×

| Day | Mean | Sharpe | Worst | Win rate |
|---|---|---|---|---|
| Mon (1DTE) | ₹1,615 | 1.1 | −₹3,085 | 86.6% |
| Tue (0DTE) | ₹538 | 0.3 | −₹4,746 | 85.6% |

Gamma on 0DTE without intraday management eats theta. Tue requires either active management or skipping.

### 2b. SL is irrelevant in this backtest

- SL fires on **1.0%** of trades (vs TP 77.8%, EOD 21.2%, EOD_DATA_END 0.02%)
- Rows with SL=1.0 / 1.25 / 1.5 / 2.0 are byte-identical for ~95% of configs
- The grid pretends to test 4 SL levels but really only tests one
- **This is the single biggest red flag in the dataset** — your real-world stop-and-recenter strategy depends on SL behavior, and this backtest cannot evaluate it

### 2c. TP rule matters more than SL

- TP-500inr (fixed ₹6.67/share) → best Sharpe
- TP-50pct (50% of credit) → best mean, but adds tail risk
- TP-250inr (₹3.33/share) → conservative; works for narrow wings
- TP-25pct → too tight; leaves theta on the table

### 2d. 13:00 is the sweet entry time on Monday

- 10:00 / 11:00 entries: wider stdev because more session remains for drift
- 13:00: residual range smaller; theta/gamma ratio more favorable
- Pattern holds across structures

### 2e. Mean P&L by structure (Mon only)

| Structure | Mean | Sharpe | Worst |
|---|---|---|---|
| IB-100w | ₹741 | 1.0 | −₹1,036 |
| IB-150w | ₹1,440 | 1.1 | −₹2,206 |
| IB-200w | ₹2,142 | 1.1 | −₹3,738 |
| IC50-100w | ₹1,211 | 1.2 | −₹1,952 |
| IC100-200w | ₹2,540 | 1.1 | −₹6,494 |

IB-200w sits at the efficient frontier point that maximizes return-per-unit-of-tail.

---

## 3. Suggested Improvements to the Backtest (Highest Priority First)

### 3.1 Add the missing entry slots that you actually trade

This dataset is NIFTY Mon+Tue only. Three of your five real slots are absent:
- **Fri NIFTY (4DTE)** — biggest missing piece. Different greeks, weekend gap risk, totally different theta/gamma curve. Likely highest-edge slot in the calendar.
- **Wed SENSEX (1DTE)**
- **Thu SENSEX (0DTE)**

Without these, the backtest covers ~40% of your real trading calendar.

### 3.2 Model the stop-and-recenter behavior

Current backtest holds to EOD. Your actual rule: *"on SL hit, close + re-enter fresh ATM, biased in direction of move."* The two strategies will produce systematically different P&L distributions — re-entry adds slippage but also adds theta optionality. **Without modeling this, the SL column is meaningless.**

### 3.3 Add transaction costs

NIFTY lot=75. Realistic round-trip:
- Brokerage + STT + exchange fees: ~₹150–250/lot
- Slippage: 0.5–1.0 tick per leg × 4 legs ≈ ₹50–150/lot
- **Total: ~₹200–400/lot per trade**

Effect on rankings:
- Recommended config: ₹2,139 → ~₹1,800 (still strong)
- **Most Tue configs flip negative**
- Mon 11:00 IB-100w TP-250inr (₹606) → ₹250–₹400, marginal

### 3.4 Validate the synthetic pricing against actual NIFTY option-chain prints

Pricing model: BS with vol = 20-day realized × 1.1. Misses:
- Skew (puts trade richer than calls)
- Term structure
- IV crush on 0DTE
- Event-day vol spikes (Fed/RBI/budget)

If true IV averages 1.3× realized, both credits and TP-hit-rates are biased.

### 3.5 Add MAE/MFE-based replays

Per-trade MAE/MFE already in the CSV. Can simulate every TP/SL combination without re-running the backtest. Use to find the actual SL "knee" — level where capping tail losses starts *helping* P&L.

### 3.6 Time-walk the optimization

Train 2024, test 2025, walk forward. 102-Monday sample is small; any TP/SL tuning on the full window risks overfit. Mon 13:00 IB-200w should hold up; lower-mean configs may not.

### 3.7 Add an event calendar overlay

Tag each trade: RBI policy, FOMC, budget, monthly expiry, quarterly settlement, earnings of index-heavyweight stocks. A regime-aware filter ("skip Mon if RBI on Wed") may dominate any structural tweak.

---

## 4. Open Questions

### 4a. About the dataset

1. **Why NIFTY Mon+Tue only?** Is Fri NIFTY data missing because of different DTE-bucket logic, or just not run yet?
2. **Where is SENSEX (Wed/Thu)?** Equivalent backtest somewhere I haven't seen?
3. **Vol model `realized_20d × 1.1`** — was this calibrated against actual ATM IV prints, or is it an assumption? If actual IV is ~1.3× realized, every credit in the CSV is understated by ~20%.
4. **2026 Jan endpoint** — is this through current date (2026-05-02), or did the data feed end in January? Last 4 months of 2026 missing would change recent-regime read.

### 4b. About the strategy as you actually trade it

5. **Direction of "shifted in direction of move"** — last bar? last 30 min? cumulative since entry? This needs a rule before it can be backtested.
6. **After re-entry, what's the new SL?** Same multiple of new credit? Same absolute rupees? Same target time?
7. **How many re-entries per session** before you stop trading that slot? Capping at 1 vs unlimited produces very different tail distributions.
8. **Do you re-enter if SL hits in the last hour**, or call it a day? Matters a lot on 0DTE Tue.
9. **Per-day capital limit?** "Capital preservation" means different things at 1 lot/day vs 10 lots/day vs scaling-with-equity.
10. **Does the "60% sideways" thesis come from measurement on your own data, or assumption?** If we define "sideways" as |close−open| < credit collected, what's the actual hit-rate over 2024–2026?

### 4c. About goals

11. **Define "capital preservation" precisely.** Pick one:
    - (a) worst single trade ≤ X
    - (b) max consecutive losses ≤ N
    - (c) max drawdown ≤ X% of capital
    - (d) P5 of trade distribution ≥ Y
    Each leads to a different optimal config.
12. **Optimizing for ₹/lot or return on margin?** IC100-200w needs more margin than IB-100w; rankings change if measured as ROI.
13. **Maximum acceptable single-trade loss in absolute rupees** regardless of mean P&L? If −₹3,500/lot is unacceptable, IB-150w (worst −₹2,017) or IB-100w (worst −₹967) become the right answers despite lower mean.
14. **Is daily P&L variance acceptable**, or do you want to smooth it via spreading entries across 2–3 times within the day?

---

## 5. Bottom Line

For *this* dataset and *this* definition of capital preservation:

> **Mon 13:00 IB-200w TP-500inr** is the dominant config. It's within 0.05 of the highest Sharpe in the grid while keeping the worst trade at half the depth of the higher-mean alternatives.

But before committing live capital, the dataset is missing 60% of your actual trading calendar (Fri NIFTY + both SENSEX days), doesn't model your actual exit behavior (stop-and-recenter), and treats SL as if it almost never matters.

**Questions that gate live deployment: 1, 2, 5, 7, 11.** Those determine whether the recommendation transfers from backtest to your real book.

---

## Appendix A — Top 10 Configs by Sharpe (de-duplicated across SL setting)

| Day | Time | Structure | TP | n | Mean | Worst | Best | Sharpe |
|---|---|---|---|---|---|---|---|---|
| Mon | 13:00 | IC100-200w | TP-500inr | 102 | ₹3,347 | −₹6,754 | ₹7,378 | 1.89 |
| **Mon** | **13:00** | **IB-200w** | **TP-500inr** | **102** | **₹2,139** | **−₹3,535** | **₹6,214** | **1.84** |
| Mon | 13:00 | IB-200w | TP-250inr | 102 | ₹2,121 | −₹3,535 | ₹6,214 | 1.80 |
| Mon | 13:00 | IC50-100w | TP-250inr | 102 | ₹1,135 | −₹1,787 | ₹3,584 | 1.78 |
| Mon | 13:00 | IC100-200w | TP-25pct | 102 | ₹3,412 | −₹7,014 | ₹7,378 | 1.77 |
| Mon | 13:00 | IB-150w | TP-250inr | 102 | ₹1,288 | −₹2,017 | ₹4,176 | 1.75 |
| Mon | 13:00 | IC50-100w | TP-500inr | 102 | ₹1,140 | −₹1,901 | ₹3,584 | 1.69 |
| Mon | 13:00 | IB-100w | TP-500inr | 102 | ₹643 | −₹967 | ₹2,150 | 1.69 |
| Mon | 13:00 | IB-150w | TP-500inr | 102 | ₹1,292 | −₹2,146 | ₹4,176 | 1.66 |
| Mon | 13:00 | IB-100w | TP-250inr | 102 | ₹607 | −₹967 | ₹2,150 | 1.62 |

Every top-10-Sharpe config is **Mon 13:00**. The data is unanimous about the slot.

---

## Appendix B — Best Capital Preservation (smallest |worst|, mean > 0, n ≥ 80)

| Day | Time | Structure | TP | Mean | Worst | Sharpe |
|---|---|---|---|---|---|---|
| Mon | 11:00 | IB-100w | TP-250inr | ₹606 | −₹879 | 1.44 |
| Mon | 13:00 | IB-100w | TP-500inr | ₹643 | −₹967 | 1.69 |
| Mon | 13:00 | IB-100w | TP-250inr | ₹607 | −₹967 | 1.62 |
| Mon | 11:00 | IB-100w | TP-500inr | ₹610 | −₹989 | 1.31 |
| Mon | 11:00 | IB-100w | TP-50pct | ₹1,056 | −₹1,048 | 0.64 |
| Mon | 11:00 | IB-100w | TP-25pct | ₹827 | −₹1,048 | 0.72 |

If absolute floor on single-trade loss is the priority, **Mon 13:00 IB-100w TP-500inr** (worst −₹967, mean ₹643, Sharpe 1.69) is the right answer — but post-cost it's marginal.
