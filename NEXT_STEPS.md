# Next Steps — NGT Data Capture System

1. **Restart SENSEX capture process**
   - Kill old shell wrapper if running
   - Remove stale lock `/tmp/varaha_data_capture_sensex.lock`
   - Let watchdog restart or manually start with:
     ```
     cd /home/trading_ceo/python-trader && python3 varaha/data_capture_v3_duckdb.py --index SENSEX --db varaha/data/varaha_data_sensex.duckdb
     ```

2. **Verify SENSEX options flow**
   - Correct format: `SENSEX26{M}{DD}{STRIKE5DIGITS}{CE/PE}` (single-digit month)
   - Code at `varaha/data_capture_v3_duckdb.py:279-285` has the `month_map` fix
   - If process still shows old errors, clear `__pycache__` and restart

3. **Fix multi-timeframe SuperTrend**
   - `compute_multiframe_supertrend` crashes silently (line 626-630)
   - Module `varaha_multiframe_supertrend.py` exists but raises exception

4. **Check IV/HV/Clusters** (9 columns NULL)
   - `iv_short`, `iv_long`, `iv_slope`, `hv_20`, `hv_60`
   - `iv_cluster`, `hv_cluster`, `strike_density`, `option_flow`
   - May need separate debugging or warmup

5. **Run indicator fill check** (after 14+ bars)
   ```
   python3 varaha/test_indicators.py --date 2026-05-05
   ```

6. **Verify full pipeline** (after market close)
   ```
   pytest varaha/test_indicators.py varaha/test_integration.py varaha/test_preflight.py varaha/test_indicator_functions.py test_varaha_integration.py
   ```

**Key:** NIFTY options work (66 rows/min, Greeks populating). SENSEX option format is the last major blocker — fix is in code but process needs restart.
