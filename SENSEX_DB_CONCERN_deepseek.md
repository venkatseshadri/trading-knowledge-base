# SENSEX DB Concern — deepseek

## The Issue

Claude removed `--db varaha/data/varaha_data_sensex.duckdb` from `run_data_capture_sensex.sh`, making SENSEX write to the same `varaha_data.duckdb` as NIFTY.

## Why This Will Break

**DuckDB only allows ONE writer at a time.** Two concurrent Python processes (NIFTY + SENSEX) writing to the same `.duckdb` file will cause lock conflicts:

```
_duckdb.IOException: IO Error: Could not set lock on file
"varaha_data.duckdb": Conflicting lock is held in
/usr/bin/python3.12 (PID 732791) by user root
```

This was already observed today at 10:06 AM — SENSEX crashed on every restart attempt while NIFTY was holding the lock.

## History

This is a **regression**. The separate DB approach was a deliberate fix made on May 4 after discovering the DuckDB concurrency limitation. Previously both processes wrote to the same file and SENSEX consistently failed with lock conflicts. The fix was to give SENSEX its own DB at `varaha_data_sensex.duckdb`.

## SENSEX Option Issue is Separate

The SENSEX option search problem (`search returned None: SENSEX07MAY26C77100 in BFO`) is NOT caused by the DB — it's a Shoonya API issue (wrong exchange, symbol format, or strike grid). Even with the separate DB, SENSEX was failing to find options.

## Recommendation

Do NOT share the DB. Keep `--db varaha/data/varaha_data_sensex.duckdb` in the SENSEX shell script. Fix the SENSEX option search independently (likely needs different exchange code for BFO options or correct symbol format).

Analytical queries across both indices can be done with DuckDB's `ATTACH` statement:
```sql
ATTACH 'varaha/data/varaha_data_sensex.duckdb' AS sensex;
SELECT * FROM sensex.market_data WHERE ...
```
