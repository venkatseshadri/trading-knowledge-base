# Research Agent End-of-Session Checklist

Updated: 2026-05-29 | All tunable parameters from today's fixes

## Parameters to Evaluate from Trade Outcomes

### 1. EMA Weights (entry_weights.json → trend.ema_weights)
```
Current:   EMA5=0.25  EMA20=1.00  EMA50=0.75  EMA100=0.00  EMA200=0.00
Question:  Does EMA20 at 1.0× actually predict direction better than EMA50 at 0.75×?
Metric:    For each EMA, compare accuracy of its isolated signal vs actual trade P&L.
           Adjust weight proportional to historical win rate.
```

### 2. TF Weights (entry_tools.py → traffic light)
```
Current:   1m=0.25  5m=0.50  15m=0.75  30m=1.00  60m=1.25  240m=2.00  1440m=3.00
Question:  Does weighting higher TFs at 12× the 1m produce better trade outcomes?
Metric:    Compare TL confidence vs actual trade direction accuracy.
           If TL at 40% conf delivers 60% accuracy → weights are good.
           If TL at 40% conf delivers 30% accuracy → weights are inflated.
```

### 3. Pattern Scores (entry_weights.json → traffic_light.patterns)
```
Current:  MOMENTUM_PEAK=0  BEARISH_CONTINUATION=-8  DEAD_CAT_BOUNCE=-6  etc.
Question: Do these scores predict actual price direction?
Metric:   For each pattern, track what % of trades moved in the predicted direction.
          If MOMENTUM_PEAK (score=0, neutral) → 70% of times price reversed next hour
          → increase bullish score. If 50/50 → leave at 0.
```

### 4. Confidence Thresholds
```
Current:  bullish=0.50  bearish=-0.50 (trend)
          bullish=3.00  bearish=-3.00 (traffic light)
Question: At what score does the signal become profitable?
Metric:   Bucket scores into bands (±0.25 increments). Track P&L per band.
          If -0.30 to -0.50 score trades lose money → tighten threshold.
          If -0.50+ score trades make money → correct.
```

### 5. Slope Threshold (0.01% per 60min bar)
```
Current:  slope_factor = min(|slope| / 0.0001, 1.0)
Question: Is 0.01% the right minimum slope for a trending EMA?
Metric:   Track if trades with slope_factor < 0.5 underperform vs > 0.5.
```

### 6. Completion Threshold (implicit in weighted completion)
```
Current:  No hard floor. 2% conf at open naturally drops TL to near-zero.
Question: At what weighted completion does TL signal become useful?
Metric:   Track entry_check confidence vs actual trade accuracy by session time.
          09:15-09:30 vs 10:00+ accuracy rates should diverge.
```

### 7. ADX Gate (pass-through, future evaluation)
```
Current:  ADX flows through but does not block entry.
Question: Does adding ADX < 20 SKIP or ADX < 25 CAUTION improve trade outcomes?
Metric:   Compare trade P&L when ADX < 20 (would have blocked) vs > 20 (allowed).
          If blocked trades would have been losers → add gate.
          If blocked trades would have been winners → keep pass-through.
```

### 8. Confidence Ceiling & PCR Boundary
```
Current:  confidence = min(confidence, 100)
          PCR <= 0.85 (was PCR < 0.85)
Question: Does the ceiling clamp ever fire? If so, was the pre-clamp trade profitable?
Metric:   Track how often confidence hits 100%. If it happens and trade profits
          → ceiling is correct. If it profits but gets clamped lower and blocks
          a good trade → increase ceiling or remove.
```

### 9. Gap Boost Weights
```
Current:  gap_weight=0.20  gap_boost=+/-1.5-2.0  gap_conf=+/-10-20
Question: Does the gap direction predict the next 60 min?
Metric:   For each gap direction × pattern combination, track if the boosted
          confidence aligns with actual price movement.
```

### 10. Research Override (ChromaDB consensus)
```
Current:  Neutral consensus → Iron Butterfly at 40% confidence
Question: Does the research override at market open improve or harm P&L?
Metric:   Compare overridden trades vs trades that would have fired naturally.
          Today's override put on an IRON_BUTTERFLY at 09:16 — P&L is the metric.
```

## How to Evaluate (per-session)

```python
# For each trade taken:
{
    "trade_id": "TRD-20260529...",
    "entry_signal": "BEARISH",
    "entry_confidence": 79,
    "trend_score": -0.50,
    "tl_pattern": "MIXED",
    "ema5_slope": -0.00154,
    "ema20_slope": -0.00049,
    "ema50_slope": +0.00020,
    "vix": 14.9,
    "adx": 12.77,
    "pcr": 0.85,
    "gap": "RED",
    
    # What the research agent computes:
    "outcome": "PROFIT" / "LOSS",
    "pnl": +₹X / -₹Y,
    "direction_correct": true/false,  # did price move in predicted direction?
    "time_to_tp": N,  # minutes until TP hit (or None)
    "time_to_sl": M,  # minutes until SL hit (or None)
    "max_favorable": +Z,  # max favorable move before exit
    "max_adverse": -W,    # max adverse move before exit
}
```

## Weight Update Logic

Each parameter gets a score based on its contribution accuracy:

```
if parameter_predicted_direction == actual_direction:
    parameter.score += 1
else:
    parameter.score -= 1

weight_new = weight_old + learning_rate × (parameter.score / total_trade_count)
```

Research agent runs post-market (15:40), reads all trades from state.db,
adjusts weights in entry_weights.json, commits with rationale.
