# Integration Guide: Advanced Research Indicators

## Overview

This guide integrates **24 new research indicators** into `data_capture_v3_duckdb.py` to support multi-strategy research (Iron Fly, directional, volatility, etc.).

**Code file:** `/home/trading_ceo/varaha_advanced_indicators.py`

---

## What Gets Added

### 1. Advanced Indicators (24 new columns in market_data table)

```sql
-- IV Metrics (for entry timing)
iv_current DOUBLE,              -- Current india_vix
iv_52w_high DOUBLE,             -- 52-week VIX high
iv_52w_low DOUBLE,              -- 52-week VIX low
iv_rank DOUBLE,                 -- IV percentile (0-100)
iv_regime VARCHAR,              -- 'low' | 'mid' | 'high'

-- IV Term Structure
iv_short DOUBLE,                -- Short-term IV (weekly expiry)
iv_long DOUBLE,                 -- Long-term IV (monthly expiry)
iv_slope DOUBLE,                -- Contango (positive) vs backwardation

-- Historical Volatility
hv_20 DOUBLE,                   -- 20-day realized volatility
hv_60 DOUBLE,                   -- 60-day realized volatility

-- Greeks (Iron Fly Position)
agg_delta DOUBLE,               -- Net directional exposure (should ≈0)
agg_gamma DOUBLE,               -- Curvature risk (negative for short)
agg_vega DOUBLE,                -- IV sensitivity (negative for short)
agg_theta DOUBLE,               -- Daily time decay
wings_delta DOUBLE,             -- Long wing hedge delta
body_delta DOUBLE,              -- Short ATM straddle delta

-- Multi-day Support/Resistance
cluster_support DOUBLE,         -- Nearest support from pivot clusters
cluster_resistance DOUBLE,      -- Nearest resistance from pivot clusters
distance_to_support DOUBLE,     -- Gap to support (points)
distance_to_resistance DOUBLE,  -- Gap to resistance (points)

-- Session Phase & Structure
session_phase VARCHAR,          -- 'pre' | 'early' | 'mid' | 'late'
open_to_current_pct DOUBLE,     -- (spot - open) / open * 100
distance_to_pivot_pct DOUBLE,   -- Distance to pivot_pp (%)
distance_to_r1_pct DOUBLE,      -- Distance to pivot_r1 (%)
distance_to_s1_pct DOUBLE,      -- Distance to pivot_s1 (%)

-- Put-Call Sentiment
pcr_total DOUBLE,               -- Total OI put/call ratio
pcr_atm DOUBLE,                 -- ATM put/call ratio
sentiment VARCHAR,              -- 'bullish' | 'neutral' | 'bearish'

-- Open Interest Analysis
max_pain_strike INTEGER,        -- Highest OI strike
call_oi_concentration DOUBLE,   -- % of total OI in calls
put_oi_concentration DOUBLE,    -- % of total OI in puts
oi_skew DOUBLE                  -- Put/Call OI ratio
```

---

## Integration Steps

### Step 1: Add Database Columns to init_schema()

In `init_schema()` function, find the CREATE TABLE market_data statement and add these columns (around line 380):

```sql
-- IV Metrics
iv_current DOUBLE,
iv_52w_high DOUBLE,
iv_52w_low DOUBLE,
iv_rank DOUBLE,
iv_regime VARCHAR,
iv_short DOUBLE,
iv_long DOUBLE,
iv_slope DOUBLE,

-- Historical Volatility
hv_20 DOUBLE,
hv_60 DOUBLE,

-- Greeks
agg_delta DOUBLE,
agg_gamma DOUBLE,
agg_vega DOUBLE,
agg_theta DOUBLE,
wings_delta DOUBLE,
body_delta DOUBLE,

-- Support/Resistance Clusters
cluster_support DOUBLE,
cluster_resistance DOUBLE,
distance_to_support DOUBLE,
distance_to_resistance DOUBLE,

-- Session Metrics
session_phase VARCHAR,
open_to_current_pct DOUBLE,
distance_to_pivot_pct DOUBLE,
distance_to_r1_pct DOUBLE,
distance_to_s1_pct DOUBLE,

-- PCR Sentiment
pcr_total DOUBLE,
pcr_atm DOUBLE,
sentiment VARCHAR,

-- OI Analysis
max_pain_strike INTEGER,
call_oi_concentration DOUBLE,
put_oi_concentration DOUBLE,
oi_skew DOUBLE,
```

### Step 2: Import at Top of File

Add to imports (around line 1-40):

```python
from varaha_advanced_indicators import compute_advanced_indicators
```

### Step 3: Call compute_advanced_indicators() in capture_once()

After SMC calculation (around line 490), add:

```python
# Calculate advanced research indicators
advanced = compute_advanced_indicators(
    db, ds, timestamp, date_str, spot,
    buf, prev_day_data,
    atm_strike, india_vix,
    open_price, pivot_pp, pivot_r1, pivot_s1,
    expiries['weekly'], expiries['monthly'],
    index=ds.index
)
```

### Step 4: Add Advanced Indicators to Database INSERT

Update the INSERT INTO market_data statement column list (around line 547-551):

**In the column list, add:**
```python
iv_current, iv_52w_high, iv_52w_low, iv_rank, iv_regime,
iv_short, iv_long, iv_slope,
hv_20, hv_60,
agg_delta, agg_gamma, agg_vega, agg_theta, wings_delta, body_delta,
cluster_support, cluster_resistance, distance_to_support, distance_to_resistance,
session_phase, open_to_current_pct, distance_to_pivot_pct, distance_to_r1_pct, distance_to_s1_pct,
pcr_total, pcr_atm, sentiment,
max_pain_strike, call_oi_concentration, put_oi_concentration, oi_skew,
```

**Add 32 more `?` placeholders in VALUES:**
```python
?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
```

### Step 5: Add Parameter Values to INSERT

In the parameter list (around line 571-576), add:

```python
advanced.get('iv_current'), advanced.get('iv_52w_high'), advanced.get('iv_52w_low'),
advanced.get('iv_rank'), advanced.get('iv_regime'),
advanced.get('iv_short'), advanced.get('iv_long'), advanced.get('iv_slope'),
advanced.get('hv_20'), advanced.get('hv_60'),
advanced.get('agg_delta'), advanced.get('agg_gamma'), advanced.get('agg_vega'),
advanced.get('agg_theta'), advanced.get('wings_delta'), advanced.get('body_delta'),
advanced.get('cluster_support'), advanced.get('cluster_resistance'),
advanced.get('distance_to_support'), advanced.get('distance_to_resistance'),
advanced.get('session_phase'), advanced.get('open_to_current_pct'),
advanced.get('distance_to_pivot_pct'), advanced.get('distance_to_r1_pct'),
advanced.get('distance_to_s1_pct'),
advanced.get('pcr_total'), advanced.get('pcr_atm'), advanced.get('sentiment'),
advanced.get('max_pain_strike'), advanced.get('call_oi_concentration'),
advanced.get('put_oi_concentration'), advanced.get('oi_skew'),
```

### Step 6: Update CSV Export

The CSV export in `varaha_smc_and_logger.py` needs to include the new columns. Update the `export_to_csv()` function around line 400:

**In the SELECT statement, add all advanced indicator columns:**
```python
, iv_current, iv_52w_high, iv_52w_low, iv_rank, iv_regime,
  iv_short, iv_long, iv_slope,
  hv_20, hv_60,
  agg_delta, agg_gamma, agg_vega, agg_theta, wings_delta, body_delta,
  cluster_support, cluster_resistance, distance_to_support, distance_to_resistance,
  session_phase, open_to_current_pct, distance_to_pivot_pct, distance_to_r1_pct, distance_to_s1_pct,
  pcr_total, pcr_atm, sentiment,
  max_pain_strike, call_oi_concentration, put_oi_concentration, oi_skew
```

**In the columns list, add:**
```python
'iv_current', 'iv_52w_high', 'iv_52w_low', 'iv_rank', 'iv_regime',
'iv_short', 'iv_long', 'iv_slope',
'hv_20', 'hv_60',
'agg_delta', 'agg_gamma', 'agg_vega', 'agg_theta', 'wings_delta', 'body_delta',
'cluster_support', 'cluster_resistance', 'distance_to_support', 'distance_to_resistance',
'session_phase', 'open_to_current_pct', 'distance_to_pivot_pct', 'distance_to_r1_pct', 'distance_to_s1_pct',
'pcr_total', 'pcr_atm', 'sentiment',
'max_pain_strike', 'call_oi_concentration', 'put_oi_concentration', 'oi_skew',
```

---

## Indicator Descriptions

### IV Metrics (IV Rank, IV Term Structure)
- **Use case**: Entry timing. Sell premium when IV rank > 67 (high IV), avoid short vol when IV rank < 33
- **iv_rank**: Percentile of current IV vs 252-day range. 0-100 scale
- **iv_regime**: Categorical version (low/mid/high)
- **iv_slope**: Positive = contango (normal), negative = backwardation (crisis)

### Historical Volatility (HV-20, HV-60)
- **Use case**: Compare realized vs implied. HV > IV = volatility compression
- **Calculation**: Annualized std dev of 1-min log returns
- **hv_20**: Last 20 bars (≈20 minutes of trading)
- **hv_60**: Last 60 bars (≈60 minutes)

### Greeks (Delta, Gamma, Vega, Theta)
- **Use case**: Position risk monitoring. Validate hedge ratio, monitor decay
- **agg_delta**: Should ≈ 0 for balanced iron fly (long wings hedge short body)
- **agg_gamma**: Negative = short vega risk (unprofitable if IV spikes)
- **agg_vega**: Negative = short vega (profits if IV drops)
- **agg_theta**: Positive daily decay. Target ₹1,000–₹1,200/day

### Multi-day Pivot Clusters
- **Use case**: Define "sideways" zone. If spot within cluster ± ATR, no trend
- **cluster_support/resistance**: Levels where 2+ daily pivots cluster
- **distance_to_***: Gap in points (for breakout detection)

### Session Phase
- **Use case**: Entry timing within day. Early session = fresh algo, late = liquidation
- **session_phase**: 'early' (9:15–10:45), 'mid' (10:45–2:30 PM), 'late' (2:30–3:30 PM)
- **distance_to_pivot_pct**: % move from pivot (|move| < 0.5% = sideways)

### PCR (Put-Call Ratio) & Sentiment
- **Use case**: Market sentiment bias. PCR > 1.0 = fear, < 0.8 = greed
- **pcr_total**: All strikes. Usually 0.8–1.2 in normal markets
- **pcr_atm**: ATM only. Better for directional bias
- **sentiment**: Categorical (bullish/neutral/bearish)

### OI Analysis
- **Use case**: Gamma zones, max pain, support levels where MMs hedge
- **max_pain_strike**: Where max OI concentrates (likely close at expiry)
- **oi_skew**: Put/call OI ratio. > 1.0 = fear, < 1.0 = confidence
- **call_oi_concentration**: % of total OI in calls. > 60% = bullish bias

---

## Performance Impact

- **Advanced calculations:** 15–25ms per minute (Greeks are the heavy ones)
- **DB lookups:** 5–8ms per minute (IV rank, clusters, PCR queries)
- **Total overhead:** ~30–35ms per minute
- **Daily impact:** 360 min × 33ms ≈ 12 seconds (acceptable for research)

---

## Storage Impact

- **32 new columns:** ~3–4 KB per row (doubles from 2 KB to 5–6 KB)
- **14-day rolling CSV:** 180–220 MB (uncompressed) / 45–60 MB (compressed)
- **No limit on research quality** — storage stays constant (rolling window)

---

## Testing

After integration, verify with a dry run:

```bash
python3 varaha/data_capture_v3_duckdb.py --once --no-broker
```

Check:
1. ✅ DuckDB has all 32 new columns populated
2. ✅ IV rank values are 0-100
3. ✅ Greeks are non-zero for expiries
4. ✅ PCR values are > 0
5. ✅ CSV files include all new columns
6. ✅ No performance degradation (< 60ms overhead per minute)

---

## Quick Reference

| Metric | Range | Interpretation | Use Case |
|--------|-------|-----------------|----------|
| IV Rank | 0-100 | Low = cheap IV, High = rich IV | Entry timing |
| IV Slope | -∞ to +∞ | Pos = contango, Neg = backwardation | Expiry structure |
| HV % | 0-100+ | HV > IV = compression, HV < IV = expansion | Volatility regime |
| Agg Delta | -1 to +1 | Should ≈ 0 for iron fly | Hedge check |
| Agg Gamma | -∞ to +∞ | Negative = short gamma risk | Curve risk |
| Agg Theta | 0+ | ₹1,000–₹1,200/day target | P&L tracking |
| PCR | 0-∞ | > 1.0 = bearish, < 0.8 = bullish | Sentiment |
| Session Phase | early/mid/late | Different entry strategies per phase | Timing |

---

## Questions for Deepseek

Provide this document + `/home/trading_ceo/varaha_advanced_indicators.py` to Deepseek with:

> "Integrate 24 advanced research indicators into data_capture_v3_duckdb.py following the 6-step guide in INTEGRATION_GUIDE_ADVANCED_INDICATORS.md. The code is ready in varaha_advanced_indicators.py. This adds IV rank, Greeks, PCR, OI analysis, and session metrics for multi-strategy research. Test with --once flag after integration."

---

## Notes on scipy Dependency

The Greeks calculation uses `scipy.stats.norm` for the CDF. If scipy is not installed:

```bash
pip install scipy
```

If scipy is unavailable at runtime, Greeks fall back to zero values (doesn't break the capture).

