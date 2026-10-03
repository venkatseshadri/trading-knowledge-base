# Variables That Could Turn P&L Positive

**Companion to:** `/home/trading_ceo/backtest_analysis_corrected.md`
**Source data:** `/home/trading_ceo/backtest_results_corrected.csv` (62 trades)
**Date:** 2026-05-02

---

## Context

The corrected backtest shows:

- 62 trades, 51.6% win rate, total P&L **−2,725**
- Avg winner +44.68, avg loser **−138.51** (3.1× asymmetry)
- Profit factor **0.34**
- Loss is concentrated in 19 wide-wing far-dated trades (−2,853); the 36 short-dated narrow trades are essentially breakeven (+106)

The asymmetry between winners and losers — not the win rate — is what's killing this strategy. Any lever that compresses the loser tail or stretches the winner side will move P&L meaningfully.

This document evaluates the four exit/management levers on the table: **TSL, closer hedge, leg shifting, tighter SL** — plus additional variables that should be added to the dataset before drawing further conclusions.

---

## 1. Ranked Impact of the Four Proposed Levers

### Lever 1: Profit Target / Trailing Stop Loss — *Highest expected impact for short-dated narrow flies*

**Mechanism:** Exit when unrealized profit hits, e.g., 25% of max profit (credit received), instead of holding to expiry.

**Why it works on this data:**

- An iron butterfly's P&L curve is concave: peak realized profit in the middle of DTE, then late-cycle gamma erodes gains
- The 36 narrow-fly trades currently average +2.95/trade — they have the right idea, but ride too long and let occasional adverse expiries wipe out a string of small theta wins
- A 25% profit target (or trailing stop activated at, say, 30% of max profit) captures the bulk of theta decay before pin risk kicks in

**Expected effect on this dataset:** Many of the 30 losers among the narrow flies were positions that *had* a profitable mid-trade window before a late-cycle move flipped them. Profit-targeting captures those. Likely turns the narrow-fly subset from breakeven → clearly profitable.

**Tradeoff:** Caps the upside on trades that would have run to full max profit. For an iron fly this is fine — full max profit at expiry is rare and requires pin-perfect closes.

---

### Lever 2: Closer Stop Loss (e.g., 1× credit) — *Biggest impact on the wide-fly tail*

**Mechanism:** Exit when unrealized loss = credit received (or 1.5× / 2× credit, parametrize).

**Why it works on this data:**

- The seven worst trades all came from wide-wing far-dated flies held through a 5% NIFTY move:
  - −722, −472, −408, −402, −378, −359, −297
- Credits collected on those trades were typically 750–1,400. A 1× credit stop would have capped each loss at roughly the credit value (so ~−750 to −1,400), but the realized losses were 2–5× credit because the position was held to expiry
- Even a 1.5× credit stop materially compresses these tails

**Expected effect on this dataset:** Removes the worst single losses, which are the entire reason total P&L is negative. Profit factor moves from 0.34 toward 0.7–1.0+ depending on stop level.

**Tradeoff:** Adds whipsaw risk — some stopped-out trades would have recovered if held. Backtest needs to compare stop levels (1×, 1.5×, 2× credit) to find the sweet spot.

---

### Lever 3: Closer Hedge (Narrower Wings) — *Structural risk reduction*

**Mechanism:** Reduce the distance between sold body strikes and bought wing strikes. E.g., 25-pt wings instead of 50-pt.

**Why it works on this data:**

- Wing-width breakdown:

  | Wing | Trades | Total P&L | Avg |
  |---|---|---|---|
  | 50 pts | 40 | +0.38 | +0.01 |
  | 100 pts | 4 | −2.95 | −0.74 |
  | 150 pts | 1 | +13.14 | +13.14 |
  | **1000 pts** | **14** | **−1,539.63** | **−109.97** |
  | **2000 pts** | **3** | **−1,196.43** | **−398.81** |

- Narrowing wings on the wide-fly trades from 1000 → 200 pts dramatically shrinks max loss
- For short-dated trades the wings are already narrow at 50 pts — limited room to tighten further

**Expected effect on this dataset:** Major reduction in absolute size of worst-case losses. Credit collected also shrinks proportionally, so per-trade theta is smaller — but capital efficiency improves.

**Tradeoff:** Lower credit per trade, tighter breakevens (so the body needs to stay closer to spot at expiry), and win rate may drop slightly. Best applied **in combination with** Levers 1 and 2 rather than as a substitute.

---

### Lever 4: Shifting / Rolling the Unchallenged Side — *High skill, regime-dependent*

**Mechanism:** When one side of the fly gets tested by a directional move, roll the *unchallenged* side closer to spot to collect more credit and re-center the position.

**Why it's complicated:**

- Works beautifully in choppy / mean-reverting markets — extra credit cushions the tested side, position re-centers around the new spot
- **Backfires in trending markets** — you keep chasing the trend, taking losses on each roll
- Backtesting honestly requires a regime classifier or rule for "is this a trend or noise" — which is exactly the question you can't answer in advance
- The Oct 2024 sample window was a 5% trending decline → most rolls in this window would have lost money

**Recommendation:** Test this *after* Levers 1 and 2 are in place. The base strategy needs positive expectancy first; rolling is an enhancement, not a fix.

**Tradeoff:** Adds rule complexity, transaction costs, and regime sensitivity. Easy to overfit in a backtest.

---

## 2. Other Variables That Should Be in the Dataset

The current CSV is missing the variables that probably explain most of the P&L variance. Adding these will let you answer "what predicts a winner vs loser" cleanly:

| Variable | Why it matters |
|---|---|
| **DTE at entry** | Short-dated and long-dated flies have completely different greeks. Probably the single most predictive variable for this strategy. |
| **IV / IV-rank at entry** | Short premium has positive expectancy primarily in elevated-IV regimes. Filter entries to IV-rank > 30 and the strategy's economics change. |
| **Body delta** (not just strike) | The body strike vs spot determines whether you're truly ATM or skewed. Some trades in this CSV have body strikes drifting far from spot. |
| **Spot / futures at entry & exit** | Required to compute realized move and decompose P&L into directional vs vol vs theta. |
| **Realized move from entry to exit** | Lets you bucket P&L by move size — short-vol structures should make money in small moves and lose in large ones. Confirms the strategy is doing what it's supposed to. |
| **Exit reason** (expiry / target / stop / time) | Tags each trade with how it closed. Without this, you can't evaluate exit rules independently. |
| **MAE / MFE during the trade** | Maximum adverse / favorable excursion. Tells you what stop levels and profit targets *would have* triggered. |

---

## 3. Recommended Experiment Sequence

Run these as separate variants, comparing P&L, profit factor, and Sharpe to baseline:

1. **Baseline + 25% profit target** (Lever 1 alone)
   - Expected: narrow-fly subset moves clearly profitable; wide-fly subset largely unchanged
2. **Baseline + 1× credit stop loss** (Lever 2 alone)
   - Expected: wide-fly losses capped; narrow-fly subset roughly unchanged
3. **Baseline + 25% profit target + 1× credit stop** (Levers 1 + 2 combined)
   - Expected: most likely path to a positive overall P&L. This is the core test.
4. **Variant 3 + DTE filter** (only enter trades with 7–30 DTE)
   - Removes the wide-fly far-dated trades structurally; expected to be the cleanest profitable strategy
5. **Variant 4 + IV-rank filter** (only enter when IV-rank > 30)
   - Expected: fewer trades but higher per-trade edge
6. **Optional: add unchallenged-side roll** at, e.g., 1.5× credit MTM loss
   - Only test after #3 is in place. Compare to the simple stop loss.

---

## 4. Bottom Line

The two highest-leverage, lowest-complexity changes are:

- **Add a profit target** (rescues the breakeven narrow-fly subset)
- **Add a hard stop loss** (caps the wide-fly tail that's currently eating everything)

Together these target the exact asymmetry visible in the current numbers: average loser is 3× average winner. Compress the loser side and stretch the winner side, and a 51.6% win-rate strategy turns from −13.95% on credit to clearly positive.

Wing tightening and leg rolling are second-order optimizations that should be evaluated only after the base profit-target + stop-loss strategy is shown to have edge. And before any of this, the dataset needs DTE, IV, spot at entry/exit, MAE/MFE, and exit-reason columns — without those, the next iteration of the backtest will be just as hard to interpret as this one.
