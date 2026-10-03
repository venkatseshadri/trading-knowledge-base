# Next-Gen Trader (NGT) — Latest Changes Summary

## Goal

Build a comprehensive intraday options trading system called "Next-Gen Trader" (NGT) for NIFTY and SENSEX weekly options. The system needs to capture 1-minute market data with full indicator coverage, detect smart money concepts (SMC), and eventually feed a strategy engine that uses Fibonacci wings, VIX scaling, and multi-exit logic.

## Instructions

- Think like a professional trader whose life depends on making money
- All research must be data-backed
- Document everything in `__NGT_STRATEGY_deepseek_v4__.md`
- Broker tokens must be refreshed daily via cron
- Use `talib.set_compatibility(1)` for Metastock Wilder smoothing
- Capture both NIFTY (Tuesday weekly expiry) and SENSEX (Thursday weekly expiry)
- Add SMC support/resistance data (pivots, Fibonacci, order blocks, FVGs, swing levels)
- Add CSV export for accessibility

## Discoveries

### Option Symbol Construction Bug (CRITICAL)
The Shoonya option ticker format was wrong in 5 files:
- **Wrong:** `NIFTY07MA2624300CE` (2-char month 'MA', strike before type, 'CE' not 'C')
- **Correct:** `NIFTY07MAY26C24300` (3-char month 'MAY', type 'C'/'P' before strike)
- This caused **zero options captured** on the first day (May 4)

### Searchscrip First-Result Bug
`get_index_spot()` used `searchscrip('NSE', 'NIFTY')` and blindly took `result['values'][0]`. First result was Nifty Next 50 (~70K), not Nifty 50 (~24K). Same for SENSEX — first result was SENSEX50 (~25K), not BSE SENSEX (~77K). Fixed by using pre-configured tokens directly (NIFTY=26000, SENSEX=1).

### Weekly Expiry Bug
`get_expiry_info()` was hardcoded to find next Thursday. NIFTY weekly options expire on **Tuesdays**, SENSEX on **Thursdays**. Added holiday-aware logic that shifts back to previous trading day if expiry falls on a holiday.

### DuckDB Concurrency
DuckDB uses single-writer locking. Two concurrent capture processes (NIFTY + SENSEX) writing to the same DB caused lock conflicts. Fixed by giving SENSEX its own DB (`varaha_data_sensex.duckdb`).

### Market Hours Exit Bug
Capture processes looped forever after 15:30 instead of exiting. Fixed: exit after 15:31 when market is closed.

## Accomplished

### File: `varaha/data_capture_v3_duckdb.py` (main capture engine)

| Fix | Details |
|-----|---------|
| Option symbol format | `{prefix}{DD}{MMM}{YY}{C/P}{strike}` — 3-char month, type before strike, C/P not CE/PE |
| Dict access fix | `result['values'][0]['token']` instead of `result[0]['token']` |
| get_spot() fix | Uses pre-configured tokens directly instead of broken `get_index_spot()` |
| get_futures() fix | Cached token lookup with tsym discriminator |
| get_vix() fix | Hardcoded token 26017 instead of searchscrip |
| Weekly expiry day | NIFTY=Tuesday, SENSEX=Thursday with holiday shift |
| Market hours exit | Exit after 15:31 instead of looping forever |
| Shell retry | 5 attempts × 30s delay in `run_data_capture.sh` and `run_data_capture_sensex.sh` |
| Watchdog | Every 5 min via cron, restarts dead capture processes |
| SENSEX DB split | `--db varaha/data/varaha_data_sensex.duckdb` |
| VWAP bug | Identified — `buf.append(spot,spot,spot,spot)` with `v=0` means `_cum_vol` stays 0, VWAP never computed (not yet fixed) |

### New indicators added (66 total columns)

| Batch | Columns | Source |
|-------|---------|--------|
| Pivot points (7) | `pivot_pp`, `pivot_r1-r3`, `pivot_s1-s3` | Prev day H/L/C |
| Fibonacci (7) | `fib_0`, `fib_236`, `fib_382`, `fib_50`, `fib_618`, `fib_786`, `fib_100` | Prev day H→L range |
| Opening range (2) | `open_range_high`, `open_range_low` | First 5 bars of day |
| SMC (13) | `ob_zone_high/low/strength`, `fvg_high/low/mitigated`, `swing_high/low`, `liquidity_swept`, `structure_type/confirmed/next_target`, `smc_strength` | 50-bar rolling window on IndicatorBuffer |

### CSV Logger
- Daily CSVs at `/home/trading_ceo/data/csv/YYYY-MM-DD_{market,options}.csv`
- Auto-gzip compression of yesterday's files
- Auto-cleanup after 14 days
- Module: `varaha/varaha_smc_and_logger.py`

### Other files fixed
- `varaha/data_capture.py` — option symbol format
- `varaha/data_capture_v2.py` — option symbol format
- `varaha/strategist_90_hitrate.py` — option symbol format (NIFTY + SENSEX)

### Cron schedule
```
12 9 * * 1-5  refresh_broker_tokens.sh
14 9 * * 1-5  run_data_capture.sh (NIFTY)
14 9 * * 1-5  run_data_capture_sensex.sh (SENSEX)
*/5 9-15 * * 1-5  watchdog_capture.sh
```

### Test status: 6/6 pass

## Current State

- **Both capture processes stopped** — old PIDs killed, waiting for cron restart at 9:14 AM today (Tuesday May 5)
- **May 4 data:** 364 NIFTY rows + 360 SENSEX rows captured (spot only, no options due to symbol bug)
- **Bad rows deleted:** 11 NIFTY + 14 SENSEX wrong-spot rows purged
- **Flattrade token refresh:** Fails with HTTPS timeout (Flattrade API issue) — doesn't block Shoonya
- **VWAP:** Still 0% fill rate (known bug, needs volume data or price-only approximation)
- **Today's expiry:** NIFTY weekly = 05-MAY-2026 (today!), SENSEX weekly = 07-MAY-2026

## Next Steps (for next agent)

1. **At 9:14 AM** — verify cron restarts both capture processes
2. **At 9:15-9:20 AM** — verify option snapshots flowing (should see ~22 rows/min in `option_snapshots` table)
3. **Verify SMC columns** populate after 5+ bars of data
4. **Verify CSV files** at `/home/trading_ceo/data/csv/` are growing
5. **Fix VWAP** — need either 1-min volume data from broker or price-only TWAP approximation
6. **After 7-14 days of live data** — run `deep_research.py`, `smc_research.py`, `strategy_optimizer.py` against captured real data (OI, IV, Greeks)

## Relevant Files

| Path | Purpose | Status |
|------|---------|--------|
| `varaha/data_capture_v3_duckdb.py` | Main capture engine (1283 lines, 66 columns) | Active, awaiting 9:14 restart |
| `varaha/varaha_smc_and_logger.py` | SMC analysis + CSV logger module | Active, imported |
| `varaha/run_data_capture.sh` | NIFTY capture wrapper (retry + lock) | Ready |
| `varaha/run_data_capture_sensex.sh` | SENSEX capture wrapper (retry + lock, --db split) | Ready |
| `varaha/watchdog_capture.sh` | Every-5-min liveness check | Running via cron |
| `varaha/refresh_broker_tokens.sh` | Daily Shoonya/Flattrade OAuth refresh | Shoonya OK, Flattrade fails |
| `varaha/data/varaha_data.duckdb` | NIFTY DB (38→66 cols, May 4 data) | Ready |
| `varaha/data/varaha_data_sensex.duckdb` | SENSEX DB (May 4 data) | Ready |
| `/home/trading_ceo/data/csv/` | Daily CSV output | Created |
| `varaha/ngt_strategy.py` | Strategy engine | Not yet run (needs live data) |
| `varaha/deep_research.py` | VIX/DTE/debit spread sweeps | Not yet run |
| `varaha/smc_research.py` | SMC/Fibonacci S/R analysis | Not yet run |
| `varaha/strategy_optimizer.py` | Entry time × filter × wing sweep | Not yet run |
| `varaha/__NGT_STRATEGY_deepseek_v4__.md` | Master strategy blueprint | Needs update with capture fixes |
| `varaha/data_capture.py` | Legacy capture (option symbol fixed) | Deprecated |
| `varaha/data_capture_v2.py` | Legacy capture (option symbol fixed) | Deprecated |
| `varaha/strategist_90_hitrate.py` | Legacy strategist (option symbol fixed) | Deprecated |
| `varaha_auth.py` | Broker auth (3 bugs fixed, SENSEX routing added) | Active |
| `/home/trading_ceo/INTEGRATION_GUIDE_SMC_LOGGER.md` | Integration guide | Reference |
| `/tmp/varaha_data_capture.log` | NIFTY capture log | Watch |
| `/tmp/varaha_data_capture_sensex.log` | SENSEX capture log | Watch |
| `/tmp/varaha_watchdog.log` | Watchdog log | Watch |
| `/tmp/varaha_token_refresh.log` | Token refresh log | Flattrade fails |
