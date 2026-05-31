# BROKEN INDICATORS — Data Capture V3
> deepseek-v4-pro | 2026-05-05 08:56 IST

---

## Test Status

| Test File | Tests | Result | Issue |
|-----------|-------|--------|-------|
| `test_preflight.py` | 8 | **7 PASS**, 1 ERROR | `test_shoonya_search` missing `api` fixture |
| `test_integration.py` | 5 | **5 FAIL** | DuckDB `tempfile.NamedTemporaryFile` creates invalid DB |
| `test_indicators.py` | 2 | **2 ERROR** | Missing `conn` fixture (not defined in conftest) |
| `test_indicator_functions.py` | ? | **1 ERROR** | Imports `varaha.multiframe_supertrend` — module doesn't exist at that path |
| `test_varaha_integration.py` | 9 | **9 PASS** ✅ | Strategy/order tests — unrelated to data capture |
| Capture `__main__` block | — | **NOT TESTED** | `if __name__ == '__main__'` block has arg parsing but no assertions |

**Net: 16 pass, 9 fail/error. No data capture indicator tests are passing.**

---

## Fill Rate Breakdown — May 4 NIFTY (364 rows)

### ✅ WORKING (18 columns, >90% fill)

| Column | Fill % | Warmup bars |
|--------|--------|-------------|
| spot | 100% | 0 |
| futures | 96.2% | ~14 |
| india_vix | 100% | 0 |
| atm_strike | 100% | 0 |
| expiry_* (6 cols) | 100% | 0 |
| intraday_high/low | 100% | 0 |
| buffer_bars | 100% | 0 |
| ema_5 | 97.3% | 10 |
| ema_20 | 90.7% | 34 |
| ema_50 | 82.4% | 64 |
| supertrend_value/direction | 90.7% | 34 |
| adx, atr, rsi | 92.3% | 28 |
| bb_pct_b, bb_width | 90.7% | 34 |
| ema20_slope | 90.7% | 34 |

### ⚠️ PARTIAL (3 columns, >0% but <<90%)

| Column | Fill % | Root Cause |
|--------|--------|------------|
| open_price | 0.5% (2/364) | `get_open_prev_close()` only called once (first bar of day) |
| prev_close | 0.5% (2/364) | Same — stored on bar 1, NULL on bar 2+ |
| gap_pct | 0.5% (2/364) | Depends on open_price + prev_close |

### ❌ BROKEN — DEPENDENCY CHAIN (0% fill)

**Group A: Prev day data — root cause for 16 columns**

| Column | Fill | Dependency |
|--------|------|------------|
| `prev_day_high` | 0% | `get_prev_day_summary()` — only loads on date change (line 784-787) |
| `prev_day_low` | 0% | Same |
| `prev_day_range` | 0% | Same |
| `pivot_pp` | 0% | Needs prev_day_high + prev_day_low |
| `pivot_r1, r2, r3` | 0% | Needs pivots |
| `pivot_s1, s2, s3` | 0% | Needs pivots |
| `fib_0 .. fib_100` | 0% | Needs prev_day_high + prev_day_low |

**Why:** `prev_day_data` starts as `None` (line 763). It's only loaded when `last_date != today` (line 784). On Day 1 of capture, there is no previous date in the DB, so it stays `None` forever. `get_prev_day_summary` queries `WHERE date = '{prev_date}'` — but on first run `last_date` is still `None`, so no query is even attempted.

**Group B: Opening Range (2 columns)**

| Column | Fill | Root Cause |
|--------|------|------------|
| `open_range_high` | 0% | Code at lines 603-609 checks `buf.buf` has exactly 5 bars with `high` fields |
| `open_range_low` | 0% | Same |

**Why:** The logic at line 606-609 slices `bars[:5]` and checks `len(first5) == 5`, but bar dicts use keys `'open', 'high', 'low', 'close'`. However `IndicatorBuffer.append()` at line 737 does `buf.append(spot, spot, spot, spot, v=vol)` — all 4 values are `spot`. So `'high'` = `spot`, which is a float, and `max()` should work. The issue may be that the check `len(first5) == 5` fails because the buffer hasn't accumulated 5 bars yet by the time it's checked on early bars, OR the columns were added to the schema AFTER the data was captured.

**Group C: SMC — ALL 13 COLUMNS (0% fill)**

| Column | Fill | Root Cause |
|--------|------|------------|
| `ob_zone_high, ob_zone_low, ob_strength` | 0% | `compute_smc_indicators(buf)` returning empty dict |
| `fvg_high, fvg_low, fvg_mitigated` | 0% | Same |
| `swing_high, swing_low, liquidity_swept` | 0% | Same |
| `structure_type, structure_confirmed` | 0% | Same |
| `next_target, smc_strength` | 0% | Same |

**Why:** `compute_smc_indicators()` in `varaha_smc_and_logger.py:47` is called at line 564. It's not in a try/except — so if it returned empty, it means either:
1. The SMC function needs a longer buffer warmup than 364 bars (unlikely)
2. The function has internal conditions that never activate (e.g., `if len(buf) < X: return {}`)
3. The function returns populated keys but the INSERT binds `smc.get(key)` which defaults to `None`

Needs code inspection of `varaha_smc_and_logger.py:47` to determine exact root cause.

**Group D: Advanced Indicators (22 columns, 0% fill)**

| Column | Fill | Root Cause |
|--------|------|------------|
| IV group: `iv_current, iv_52w_high, iv_52w_low, iv_rank, iv_regime, iv_short, iv_long, iv_slope` | 0% | `compute_advanced_indicators()` fails silently |
| HV group: `hv_20, hv_60` | 0% | Same |
| Greeks: `agg_delta, agg_gamma, agg_vega, agg_theta, wings_delta, body_delta` | 0% | Same |
| Clusters: `cluster_support, cluster_resistance, distance_to_support, distance_to_resistance` | 0% | Same |
| Session: `session_phase, open_to_current_pct, distance_to_pivot_pct, distance_to_r1_pct, distance_to_s1_pct` | 0% | Same |
| PCR: `pcr_total, pcr_atm` | 0% | Same |
| OI: `sentiment, max_pain_strike, call_oi_concentration, put_oi_concentration, oi_skew` | 0% | Same |

**Why:** Wrapped in try/except at line 612-623 — `compute_advanced_indicators()` raises an exception (silently caught). The module exists (`varaha_advanced_indicators.py`, updated May 5 08:35) but it may:
- Require option data to compute (options were 0 due to symbol bug on May 4)
- Have a parameter mismatch
- Have an internal error (KeyError, TypeError)

**Group E: Multi-Timeframe SuperTrend (5 columns, 0% fill)**

| Column | Fill | Root Cause |
|--------|------|------------|
| `st_5min_value, st_5min_direction, st_15min_value, st_15min_direction, st_consensus` | 0% | `compute_multiframe_supertrend()` fails silently |

**Why:** Wrapped in try/except at line 626-630. Module exists (`varaha_multiframe_supertrend.py`, updated May 5 08:44). Likely same issue — exception caught silently.

**Group F: VWAP (1 column, 0% fill)**

| Column | Fill | Root Cause |
|--------|------|------------|
| `vwap` | 0% | `buf.append(spot,spot,spot,spot,v=vol)` — line 737 |

**Why:** `IndicatorBuffer` at line 83 tracks cumulative volume-price (`_cum_vp`) and cumulative volume (`_cum_vol`). At line 736: `vol = futures_vol if futures_vol and futures_vol > 0 else 1`. The fallback to `vol=1` was added (line 736) but it only applies at the `capture_once` level. Inside `IndicatorBuffer.append()`, the volume parameter `v` is passed but the VWAP calculation at line 121 does `self._cum_vp / self._cum_vol` — if `_cum_vol` is 0, this divides by zero. With `vol=1` as fallback, this SHOULD work now. The issue is this fallback was likely added AFTER May 4 capture. Needs reverification today.

---

## SENSEX DB — Missing 66 columns

SENSEX DB has only 38 columns vs NIFTY's 104. All SMC, advanced, multi-timeframe, pivot, fib, IV, Greeks, PCR, and OI columns are missing from SENSEX schema.

**Why:** `init_schema()` uses DB_PATH which doesn't get overridden for SENSEX in the schema migration code (lines 411-525). The `--db` flag only changes the DB_PATH variable at startup, but `init_schema` creates columns conditionally — SENSEX DB was created with an older schema and migration never added the new columns.

---

## Root Cause Summary Map

```
prev_day_data = None (line 763)
    └── Never loaded on first capture day
        └── prev_day_high/low/range = NULL (3 cols)
            └── pivot_pp/r1-r3/s1-s3 = NULL (7 cols)
            └── fib_0..fib_100 = NULL (7 cols)
                └── distance_to_pivot/r1/s1_pct = NULL (3 cols)

open_range_high/low = NULL (2 cols)
    └── First-5-bar logic broken or warmup issue

compute_smc_indicators() → {} (13 cols)
    └── Function returns empty dict — needs code inspection

compute_advanced_indicators() → silent exception (22 cols)
    └── Needs options data OR has parameter bug

compute_multiframe_supertrend() → silent exception (5 cols)
    └── Needs code inspection

vwap = 0.0 (1 col)
    └── vol=1 fallback added after May 4 capture

SENSEX schema migration (66 cols missing)
    └── init_schema not applying ADD COLUMN migrations for SENSEX
```

---

## What Changed Today (May 5)

| File | Modified | Effect |
|------|----------|--------|
| `varaha_advanced_indicators.py` | 08:35 | Advanced indicators module — should populate Groups D today |
| `varaha_multiframe_supertrend.py` | 08:44 | Multi-timeframe ST — should populate Group E today |
| `varaha_smc_and_logger.py` | Unknown | SMC computation — still 0% fill, needs debugging |
| `data_capture_v3_duckdb.py` | Unknown | Option symbol fix applied — options should flow today |

**Note:** Modules were updated AFTER the May 4 data was captured. Today's reload at 9:14 AM should pick up the new modules. But SMC and prev_day_data fixes are still needed.

---

## Priority Fix Order

| # | Fix | Impact | Effort |
|---|-----|--------|--------|
| 🔴 1 | SMC module — debug `compute_smc_indicators()` returning empty | 13 columns (core S/R engine) | Medium |
| 🔴 2 | Prev day data — load on first run from yfinance fallback | 17 columns (pivots + fibs + distances) | Low |
| 🟡 3 | VWAP — verify `vol=1` fallback works today | 1 column (critical institutional level) | Trivial |
| 🟡 4 | Opening range — fix first-5-bar logic | 2 columns | Low |
| 🟡 5 | SENSEX schema migration — add missing 66 columns | 66 columns on SENSEX | Medium |
| 🟢 6 | Silence try/except blocks — log actual errors | 27 columns (debugging aid) | Trivial |
| 🟢 7 | Fix tests — add conn fixture, fix tempfile usage | 7 failing tests | Medium |
