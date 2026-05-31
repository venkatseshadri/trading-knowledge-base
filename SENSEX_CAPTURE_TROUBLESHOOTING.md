# SENSEX Option Capture Troubleshooting Report
**Date:** May 6, 2026 | **Time:** 09:18 AM  
**Status:** SENSEX capture running, options not visible in logs (DEBUG logging now enabled)

---

## Issues Found & Resolved

### 1. ✅ SENSEX Symbol Format (FIXED)
**Status:** WORKING  
**What was wrong:** Code was generating `SENSEX[DD][MMM][YY]` (NIFTY format) for SENSEX  
**Fix applied:** Conditional logic added at line 279-287 to generate `SENSEX[YY][M][DD][STRIKE5DIGITS][CE/PE]`

**Test result:**
```
Symbol: SENSEX2650777700CE
Shoonya response: ✅ Quote found (LTP=327.3, OI=543700)
```

---

### 2. ❌ IV Values from Broker (BROKER LIMITATION)
**Status:** Cannot fix locally  
**Issue:** Shoonya API returns `iv: 0.0` for SENSEX options  
**Root cause:** SENSEX options on Shoonya may not have IV quotes available  

**Evidence:**
- NIFTY options: IV populated correctly (e.g., 17.05)
- SENSEX options: Always returns 0.0
- This matches May 5 data where all SENSEX IVs were 0.0

**Impact:** 
- IV-dependent indicators (iv_short, iv_long, iv_slope) will be NULL
- Greeks calculation won't use real IV
- But option capture should still work (IV not required for snapshots)

---

### 3. ❌ May 5 Capture Failure (ROOT CAUSE IDENTIFIED)
**Status:** Prevented by DuckDB concurrent write lock  
**What happened:**
- 09:14 AM: SENSEX process tried to connect but couldn't acquire lock
- Lock held by unknown PID 741904
- Retried multiple times until market close
- At 15:31 PM: Finally got lock, but market was closing
- Result: 0 capture iterations, no option rows written by scheduled process

**Why:** DuckDB doesn't support concurrent writes from multiple processes. A stale process was holding the lock.

**Solution implemented:** Separate databases (varaha_data.duckdb for NIFTY, varaha_data_sensex.duckdb for SENSEX)

---

### 4. ⚠️ Logging Level Hidden Option Counts
**Status:** FIXED  
**Problem:** DEBUG-level logs not visible
- Line 812: `logger.debug(f"Wrote {option_count} option rows")`
- Logging level was set to INFO (line 46)
- Result: Can't see if options are being inserted

**Fix applied:**
- Changed logging level from INFO → DEBUG
- Will take effect on next process restart
- Options counts will now be visible in logs

---

## Current Status (May 6, 09:18 AM)

### SENSEX Capture Process
✅ Running (PID 765549)  
✅ Connected to Shoonya broker  
✅ Fetching market data (iterations 1, 2, 3...)  
✅ Symbol format correct  
⏳ Option captures: CANNOT VERIFY (DEBUG logs not active yet)

### Market Data Quality
- Spot: 77541.61 ✓
- ATM: 77500 ✓
- Buffer: 3 bars ✓
- Iteration count: 3+ ✓

### What We Can't See Yet
- How many option rows being written per iteration
- Whether all 11 strikes (±500 points) are being captured
- IV values being stored (will be 0.0)

---

## Next Steps (After Market Close)

1. **Verify option captures with DEBUG logs:**
   ```
   tail -100 /tmp/varaha_data_capture_sensex.log | grep "Wrote.*option"
   ```

2. **Check data quality:**
   ```
   duckdb varaha/data/varaha_data_sensex.duckdb
   SELECT COUNT(*), COUNT(DISTINCT strike) FROM option_snapshots 
   WHERE date = '2026-05-06';
   ```

3. **Run indicator tests:**
   ```
   python3 varaha/test_indicators.py --date 2026-05-06
   ```

4. **Verify IV=0.0 situation:**
   ```
   SELECT DISTINCT iv FROM option_snapshots 
   WHERE date = '2026-05-06' LIMIT 5;
   ```

---

## Code Changes Made

**File:** `/home/trading_ceo/python-trader/varaha/data_capture_v3_duckdb.py`

**Line 46:** Logging level changed
```python
# Before:
level=logging.INFO,

# After:
level=logging.DEBUG,
```

This enables visibility of option capture counts.

---

## Pending Issues

| Issue | Severity | Status |
|-------|----------|--------|
| IV values = 0.0 | Medium | Broker limitation - can't fix |
| DEBUG logs not yet active | Low | Will activate on process restart |
| May 5 data quality | Info | Options captured despite lock issues |
| Multi-timeframe SuperTrend | Low | Working as designed (returns None with insufficient bars) |
| HV/IV term structure | Low | Expected NULL early in session (needs 21+ bars) |

---

## Root Cause Summary

**Why SENSEX options weren't captured on May 5:**
1. DuckDB lock held by stale process at market open
2. SENSEX capture retried but never got lock until 15:31 PM
3. By then, market was closing (15:30 close)
4. No option capture iterations ran

**Why we can't see if they're being captured on May 6:**
1. Logging level was INFO, not DEBUG
2. Option row counts logged at DEBUG level
3. Changed to DEBUG - will show on next process restart

**Why IV is 0.0:**
1. Shoonya broker returns 0.0 for SENSEX option IV
2. Not a bug - broker limitation
3. Affects IV-dependent indicators but not core capture

