# Iron Fly/Condor Permutation Backtest — Results

**Period:** 2024-01-01 to 2026-01-20 (209 entry days)
**Trades simulated:** 66,880 across 320 configurations × 209 days
**Date:** 2026-05-02

## Methodology Caveats

- **Pricing**: Black-Scholes with 20-day realized vol × 1.1 as IV proxy (no real IV data available)
- **Strikes**: 50pt grid (NIFTY standard)
- **Lot size**: 75 (post Nov 2024 reduction)
- **Entry days**: Monday + Tuesday only (per iron_fly_entry_calendar memory)
- **Expiry**: Next Tuesday (NIFTY weekly)
- **Exit**: SL/TP hit or 3:00 PM EOD
- **NOT modeled**: Bid-ask slippage, brokerage, IV smile, IV crush events
- **Implication**: Absolute P&L is optimistic. RELATIVE rankings between variables are reliable.

---

## Ranked Variable Impact

| Variable | Best Level | Best ₹/lot | Worst Level | Worst ₹/lot | Spread |
|---|---|---|---|---|---|
| **TP Rule** | TP-50pct | 1,671 | TP-250inr | 524 | **₹1,147** |
| **Day of Week** | Monday | 1,615 | Tuesday | 519 | **₹1,096** |
| **Structure** | IC100-200w | 1,469 | IB-100w | 572 | **₹898** |
| Entry Time | 11:00 AM | 1,126 | 09:30 AM | 974 | ₹152 |
| **SL %** | 1.25× | 1,054 | 2.0× | 1,053 | **₹2** |

### Random Forest Feature Importance (P&L variance explained)

| Feature | Importance |
|---|---|
| **vol_estimate** (exogenous) | **42.3%** |
| TP rule | 17.2% |
| Structure | 16.0% |
| Day of week | 15.0% |
| DTE | 5.0% |
| Entry time | 4.6% |
| **SL %** | **0.0%** |

---

## Top 5 Findings

### 1. TP Rule is the #1 controllable lever

| TP Rule | Mean ₹/lot | Win Rate | Avg Win | Avg Loss |
|---|---|---|---|---|
| TP-50pct (50% credit) | **1,671** | 73% | ₹3,013 | -₹2,030 |
| TP-25pct (25% credit) | 1,187 | 81% | ₹1,957 | -₹2,065 |
| TP-500inr | 833 | 93% | ₹1,081 | -₹2,562 |
| TP-250inr | 524 | 96% | ₹669 | -₹2,623 |

**Insight**: Quick small TPs (₹250) hit 96% win rate but capture pennies. Letting trades run to **50% of credit** captures the meat of theta and dominates expectancy.

### 2. Tuesday Entry is Structurally Bad

| Day | Mean ₹/lot | Profit Factor | Worst Trade |
|---|---|---|---|
| Monday (1 DTE → Tue exp) | **1,615** | 8.1 | -₹7,014 |
| Tuesday (0 DTE — same-day exp) | 519 | 2.4 | -₹9,987 |

**Insight**: Tuesday entries face pin risk on same-day expiry. Worst losses are ~40% larger. **Monday is structurally superior** for weekly entries.

### 3. Wider Wings Win

| Structure | Mean ₹/lot | Win Rate | Sharpe |
|---|---|---|---|
| IB-200w (Iron Fly, 200pt wings) | **1,409** | 88% | 0.6 |
| IC100-200w (Iron Condor, 100/200) | **1,469** | 93% | 0.6 |
| IB-150w | 1,014 | 83% | 0.5 |
| IC50-100w | 804 | 86% | 0.6 |
| IB-100w | 572 | 78% | 0.5 |

**Insight**: Wider hedges = more credit = more theta to capture. The narrow IB-100w is the worst of all 5 structures by ₹500-900/lot.

### 4. SL % Doesn't Matter (At These Structure Sizes)

For structures with hedge_distance ≤ 200pts, **structural max loss is bounded** at ~(wing - credit). Even a 100% credit SL almost never triggers because TP or EOD fires first. SL hits were <1% of trades across all 66k simulations.

**Implication**: Don't waste time tuning SL — focus on the 3 levers above.

### 5. Vol Regime Drives 42% of P&L

The single biggest predictor isn't a controllable knob — it's the **volatility environment** at entry. This strongly suggests:
- **Add an IV-rank filter**: only enter when IV is elevated (proxy: realized vol > 12%)
- Lower vol = lower credits = lower expectancy regardless of strategy

---

## OPTIMAL CONFIGURATION (from data)

```
Entry:    Monday 11:00 AM
Structure: IB-200w (Iron Fly, 200pt wings)
SL:       1.5× credit (rarely triggers; pick anything 1.0–2.0)
TP:       50% of credit collected
Avg P&L:  ₹2,608/lot per trade
Win rate: 77.5%
```

**Top 10 configurations all share:**
- TP rule = TP-50pct (every single one)
- Structure = IB-200w or IC100-200w
- Entry time = 09:30, 10:00, or 11:00 (afternoon performs marginally worse)

**Bottom 10 configurations all share:**
- TP rule = TP-250inr (every single one)
- Structure = IC100-200w (this structure is highly TP-sensitive)

---

## What's Missing & Should Be Added

1. **More structures**: Asymmetric (1:2 ratio adds), pure condor with 200pt body
2. **Adjustment rules**: When down -X%, add a leg / roll a side / shift strike
3. **IV-rank filter**: Real IV data (NSE bhavcopy) instead of realized-vol proxy
4. **Brokerage + slippage**: Subtract ₹150-200/trade for realistic P&L
5. **Friday entries**: Currently testing Mon+Tue only; Fri (Mon entry equivalent for liquidity)
6. **Longer DTE**: All trades here are 0-1 DTE; test 2-7 DTE entries
7. **Live trade logging**: Capture actual fills to compare BS prices vs reality

---

## Action Items

**Immediate (this week)**:
1. **Default config for Monday May 5 launch**: IB-200w, Monday entry at 10:00-11:00, TP at 50% credit, SL 1.5×
2. **Stop debating SL %**: It doesn't move the needle at these structure sizes
3. **Skip Tuesday entries** until we understand the same-day expiry dynamics better

**Phase 2 (after 100+ live trades)**:
1. Replace BS prices with actual fills
2. Add IV-rank filter using NSE bhavcopy data
3. Test asymmetric leg adds (1:2 on favourable side) in simulator
4. Test adjustments — leg shifts, rolls, recentering

**Phase 3 (after 6 months of live data)**:
1. Re-run RF importance with real-fill P&L
2. Build IV-regime classifier (not just realized vol)
3. Add Black-Scholes-Merton with skew (puts trade at premium to calls — affects PE leg pricing)
