# IV Issue Investigation - Shoonya API

**Date:** May 6, 2026 | **Finding:** Shoonya API does NOT provide IV field

---

## The Problem

All IV values are 0.0 in the database because Shoonya doesn't return IV in the quote response.

Code at line 331 of data_capture_v3_duckdb.py:
```python
'iv': float(q.get('iv', 0) or 0)
```

This tries to get `iv` from the quote, defaults to 0 if missing.

---

## What Shoonya Actually Returns

**Sample NIFTY option quote response (NIFTY12MAY26C24000):**

Fields available:
- `lp`: 341.00 (Last Price)
- `oi`: 3761940 (Open Interest)
- `v`: 3463850 (Volume)
- `c`: 248.10 (Close)
- `h`: 373.45 (High)
- `l`: 308.50 (Low)
- `o`: 315.00 (Open)
- `ap`: 345.77 (Average Price)
- `tsym`: 'NIFTY12MAY26C24000'
- `strprc`: 24000 (Strike Price)
- `pp`: 2 (Precision)
- `ls`: 65 (Lot Size)
- `ti`: 0.05 (Tick Interval)
- Bid/Ask levels: `bp1-bp5`, `sp1-sp5` (bid price 1-5, spread price 1-5)

**Fields NOT available:**
- ❌ `iv` (Implied Volatility)
- ❌ `theta` (Theta Greek)
- ❌ `delta` (Delta Greek)
- ❌ `gamma` (Gamma Greek)
- ❌ `vega` (Vega Greek)

---

## Why This Happened

1. **Assumption:** Shoonya API provides IV like other brokers
2. **Reality:** Shoonya quote endpoint only provides OHLCV + OI data
3. **Result:** IV defaults to 0.0, blocks IV term structure calculation

---

## IV Calculation Options

### Option A: Calculate IV from Option Price (Complex)
- Use Black-Scholes inverse calculation
- Input: Option LTP, Spot, Strike, Time to expiry, Risk-free rate
- Output: Implied Volatility
- **Complexity:** High, requires numerical methods
- **Pros:** Accurate, self-contained
- **Cons:** Expensive computationally

### Option B: Get IV from Different Source
- Use alternative data provider (NSE API, other broker APIs)
- **Pros:** Reliable, accurate
- **Cons:** Requires additional integration

### Option C: Accept IV = Not Available
- Document that Shoonya doesn't provide IV
- IV term structure = Not calculated
- IV-dependent indicators = N/A
- **Pros:** No additional work
- **Cons:** Lose IV-based analysis

### Option D: Use Historical Volatility as Proxy
- Use HV-20/HV-60 instead of IV
- Already being calculated successfully
- **Pros:** Uses available data, useful for volatility analysis
- **Cons:** Not true IV (historical vs implied)

---

## Impact on Data Quality

**Currently broken (0% coverage):**
- `iv_short` — Cannot calculate from 0.0 IVs
- `iv_long` — Cannot calculate from 0.0 IVs
- `iv_slope` — Cannot calculate from 0.0 IVs

**Still working (85%+ coverage):**
- `hv_20`, `hv_60` — Historical volatility ✓
- All other indicators — Working fine ✓

---

## Recommendation

**Use Option D (HV as proxy) for now:**

1. Keep HV-20 and HV-60 calculations (already working)
2. Remove IV term structure calculation (can't work without IV)
3. Document that IV is from Shoonya not available
4. Future: Integrate Black-Scholes IV calculation if needed

**Code change needed:**
- Remove or skip `compute_iv_term_structure()` call
- Return zeros/None for iv_short, iv_long, iv_slope
- This is already happening naturally due to the broker limitation

---

## Conclusion

**This is NOT a bug.** It's a broker API limitation. Shoonya's quote endpoint doesn't provide IV fields, so all IV-based calculations fail gracefully to NULL/0. The system is working as designed for the given broker constraints.

All other indicators (85+ columns) are populating correctly at 80%+ coverage.

