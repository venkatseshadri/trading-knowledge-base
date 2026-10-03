# Penguin Data Pipeline Architecture

Updated: 2026-06-03 | Status: Production (NIFTY, SENSEX, MCX)

## Overview

Penguin is a per-instrument data pipeline built on SQLite (WAL-mode), Redis pub/sub, and
process separation. It replaces the legacy v3.1 + v4 DuckDB path with a modular
feed → consumer → enricher chain. Each stage runs as an independent process; failures
in one stage do not cascade.

## Pipeline Stages

```
 Stage 1: FEED                    Stage 2: CONSUMER                Stage 3: ENRICHER
 ┌──────────────────┐            ┌───────────────────┐           ┌────────────────────┐
 │ antariksh/feed.py│            │ antariksh/consumers│           │ antariksh/enrichers│
 │                  │            │ /instrument_       │           │ /instrument_       │
 │ Shoonya WebSocket│───────────>│ consumer.py        │──────────>│ enricher.py        │
 │                  │ LPUSH Redis│                    │PUBLISH    │                    │
 │ normalize() →    │ feed:{INST}│ MinuteBuffer →     │bars:{INST}│ Enricher.enrich_   │
 │ JSON bar         │            │ 1-min OHLCV →      │:{1..1440} │ bar() → 104 cols   │
 │                  │            │ market_data (SQL)  │           │ → market_data_     │
 │                  │            │ BarAggregator →    │           │   enriched (SQL)   │
 │                  │            │ market_data_multitf│           │                    │
 │                  │            │ (SQLite)           │           │                    │
 └──────────────────┘            └───────────────────┘           └────────────────────┘
                                                                        │
                                                         Redis bridge (NEW)
                                                         v3_ohlcv_queue_{INST}
                                                                        │
                                                                        ▼
 Stage 4: CONSUMERS                                           ┌────────────────┐
                                                              │ entry_check.py │
 ┌──────────────────────────┐                                │ v4_aggregator  │
 │ Brahmand Agents          │                                │ data_health.py │
 │                          │                                └────────────────┘
 │ duckdb_tool.py           │
 │   _connect_sqlite()──────┤  ← reads Penguin SQLite directly during market hours
 │   LEFT JOIN enriched     │
 │                          │
 │ trading_desk.py          │
 │   _read_penguin_sqlite()─┤  ← direct SQLite query
 │                          │
 │ entry_check_tool.py      │
 │   _query_penguin_sqlite()┤  ← direct SQLite query
 └──────────────────────────┘
```

## Databases

All at `/home/trading_ceo/python-trader/varaha/data/`:

| File | Tables | Writer | Purpose |
|------|--------|--------|---------|
| `capture_nifty.sqlite` | market_data | consumer.py | 1-min OHLCV bars |
| | market_data_multitf | consumer.py | 5/15/30/60/240/1440 min OHLCV |
| | market_data_enriched | enricher.py | 104 columns per bar |
| | consumer_state | both | Resumption checkpoints |
| `capture_sensex.sqlite` | same schema | same | SENSEX data |
| `capture_mcx.sqlite` | same schema | same | MCX data |

Schema definitions: `antariksh/config/sqlite_schema.py`

## Pub/Sub Channels

| Channel | Publisher | Subscriber(s) | Purpose |
|---------|-----------|---------------|---------|
| `feed:{INST}` (Redis LIST via LPUSH) | feed.py | consumer.py (LRANGE) | Raw WebSocket ticks |
| `bars:{INST}:1` (Redis pub/sub) | consumer.py | enricher.py | 1-min completed OHLCV |
| `bars:{INST}:5` | consumer.py | (available) | 5-min bucket |
| `bars:{INST}:15` | consumer.py | (available) | 15-min bucket |
| `bars:{INST}:30` | consumer.py | (available) | 30-min bucket |
| `bars:{INST}:60` | consumer.py | (available) | 60-min bucket |
| `bars:{INST}:240` | consumer.py | (available) | 4H bucket |
| `bars:{INST}:1440` | consumer.py | (available) | Daily bucket |

## 104 Enriched Columns

The enricher computes per bar:

| Category | Columns |
|----------|---------|
| **Metadata** | timestamp, date, time, trading_day, index_name, data_source |
| **Price** | open_price, spot, futures, prev_close, atm_strike |
| **Expiry** | expiry_weekly, days_to_weekly, expiry_next_weekly, expiry_monthly, days_to_monthly |
| **Moving Averages** | ema_5, ema_20, ema_50, ema20_slope |
| **Technical** | supertrend_value/direction, adx(14), atr(14), rsi(14), vwap, bb_pct_b, bb_width |
| **VIX** | india_vix |
| **Gap/Prev Day** | gap_pct, prev_day_high, prev_day_low, prev_day_range |
| **Intraday** | intraday_high, intraday_low |
| **Open Range** | open_range_high, open_range_low |
| **Pivot Points** | pivot_pp, pivot_r1/r2/r3, pivot_s1/s2/s3 |
| **Fibonacci** | fib_0/236/382/50/618/786/100 |
| **SMC (12)** | ob_zone_high/low, ob_strength, fvg_high/low/mitigated, swing_high/low, liquidity_swept, structure_type/confirmed, next_target, smc_strength |
| **IV Analysis** | iv_current, iv_52w_high/low, iv_rank, iv_regime, iv_short/long/slope |
| **HV** | hv_20, hv_60 |
| **Aggregate Greeks** | agg_delta/gamma/vega/theta, wings_delta, body_delta |
| **Pivot Clusters** | cluster_support/resistance, distance_to_support/resistance |
| **Session Metrics** | session_phase, open_to_current_pct, distance_to_pivot/r1/s1_pct |
| **PCR & Sentiment** | pcr_total, pcr_atm, sentiment, max_pain_strike, call_oi_concentration, put_oi_concentration, oi_skew |
| **Multi-TF SuperTrend** | st_5min_value/direction, st_15min_value/direction, st_consensus |

## Redis Bridge (v3_ohlcv_queue compat)

The enricher pushes a subset of enriched data to `v3_ohlcv_queue_{INST}` on every bar for backward
compatibility with entry_check.py and the v4 aggregator:

```json
{
    "timestamp": "...", "index": "NIFTY",
    "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...,
    "ema5": ..., "ema20": ..., "ema50": ...,
    "rsi": ..., "atr": ..., "adx": ...,
    "st_direction": "...", "bb_pct_b": ...
}
```

`data_health.py` reads this queue during market hours (lock-free). `entry_check.py` uses it
for trend + traffic light scoring. This bridge eliminates the need for the legacy
`data_capture_combined.py` systemd services.

## Process Management

| Process | Trigger | PID Guard | Restart Strategy |
|---------|---------|-----------|-----------------|
| feed.py | Manual (09:14 launch) | pgrep | Watchdog cron |
| consumer.py | Manual per instrument | pgrep | Watchdog cron |
| enricher.py | Manual per instrument | pgrep | Resumes from consumer_state checkpoint |
| v4_aggregator.py | Cron `*/5 9-15 * * 1-5` | pgrep | Cron respawns every 5 min |
| pattern_enricher.py | Cron `*/5 9-15 * * 1-5` | pgrep | Cron respawns |
| data_health.py | Cron `*/5 9-15 * * 1-5` | — | Every 5 min |

## EOD Bridge

After market close (15:40 IST), `tools/eod_etl.py` copies SQLite data into
DuckDB warehouse files at `research/{date}/nifty.duckdb`. Brahmand agents
read the warehouse for backtests and post-market analysis.

## What Was Removed

| Legacy Component | Reason |
|-----------------|--------|
| `data_capture_combined.py` (systemd) | Redundant — Penguin consumer + enricher handle 1-min + multi-TF |
| `data_capture_v3.1_duckdb.py` (cron) | Dead — could never start due to DuckDB lock |
| `run_data_capture_with_v4.sh` (watchdog) | Redundant — cron handles v4, systemd removed |
| `instrument_consumer.py` Redis dual-write | Removed — was polluting v3_ohlcv_queue with indicator-less bars |
| `varaha_data.duckdb` (v3.1 capture) | Replaced by Penguin SQLite + EOD warehouse |

## MCX — Multi-Instrument Feed (Known Issue)

Unlike NIFTY/SENSEX which deliver one 1-min OHLCV bar per minute, the MCX feed
carries **~6-7 instruments per tick** (different commodity contracts in the same
WebSocket feed). Each gets its own row in `market_data`:

```
NIFTY/SENSEX:  1 row per minute → 1 enriched row per minute → clean 1.0x ratio
MCX:           6-7 rows per minute → 855 enriched rows (with gaps + corrupt values)
```

**Impact:** The enricher does NOT separate MCX by instrument/contract. It computes
indicators across mixed scrips, producing nonsensical values (e.g., `spot=317.8`
yet `open_price=156,316`, `gap_pct=42,749%`). The raw `market_data` capture is
correct — only the enriched layer is broken.

**Fix needed:** Instrument-level separation before enrichment, or feed change to
emit per-contract 1-min bars.

## Enricher Coverage Gaps (measured Jun 1, 477 rows NIFTY)

| Column group | Coverage | Status |
|---|---|---|
| spot, ema_5/20/50, rsi, adx, atr, vwap, atm_strike | 91-100% | ✅ Working |
| india_vix, agg_delta/greeks, iv_current | ~29% | ⚠️ Option chain fetch path mostly failing |
| expiry_weekly, pivot_pp, pcr_total, sentiment | 0% → now fixed | ✅ Pivots + expiry fixed 2026-06-03 |
| PCR/sentiment/VIX/greeks/IV | Option-chain-gated at 0-29% | ⚠️ Needs live-hours market-open debugging |

## Varaha DuckDB Migration — Current State

The migration repoints Brahmand agents from the dead `varaha_data.duckdb` to
Penguin SQLite + EOD DuckDB warehouse. See `brahmand/docs/PENGUIN_REPOINT_LOG.md`.

| Status | Count | Components |
|--------|-------|-----------|
| ✅ Repointed | 1 | `ema_backfill.py` |
| ⬜ Pending simple repoints | 5 | `margin_capture.py`, `entry_signal_broker.py`, `research_agents_full_db.py`, `nightly_research_scheduler.py`, `data_health.py` |
| 🔒 HELD (risk/option) | 2 | `wing_optimizer.py`, `risk_tools.py` |
| 🚫 BLOCKED | 1 | `research_agents.py` (needs `market_data_patterns`/`trade_outcomes`) |
| 🔗 Collateral | 1 | `pattern_enricher.py` (reads from varaha_data.duckdb, chained dep) |

**Key blockers:**
- No `option_snapshots` equivalent in Penguin (only per-strike LTP)
- Pattern/trade_outcome tables are chained — must migrate the writer first
- Multi-TF duplication: consumer + v4 aggregator both produce multi-TF OHLCV
