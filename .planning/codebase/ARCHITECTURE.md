<!-- refreshed: Sat Oct 03 2026 -->
# Architecture

**Analysis Date:** Sat Oct 03 2026

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                 Trading Knowledge Base Root                 │
├──────────────────┬──────────────────┬───────────────────────┤
│   [matsaya]      │  [new_system]    │    [sandwich]         │
│  TDD Framework   │  Orchestrator    │    ML Pipeline        │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Integrations & Storage                      │
│     Shoonya API SDK | duckDB | yfinance                     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                       Market Execution                      │
│                  NSE / External API Endpoints               │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `matsaya` | Modern, clean TDD environment handling indicators and order flows using YAHOO | `matsaya/main.py` |
| `new_system` | Production trading engine orchestration interacting with Shoonya | `new_system/trading_engine.py` |
| `sandwich` | Feature engineering and ML prediction engine over local Duckdb storage | `sandwich/signal_api.py` |
| `iron_fly_backtest` | Simulator for complex option hedging/income strategies (Iron fly) | `iron_fly_backtest/runner.py` |

## Pattern Overview

**Overall:** Modular / Monorepo Ensemble

**Key Characteristics:**
- Represents an evolution of different trading agent paradigms (from scripting, ML steps pipeline, to object-oriented trading engines).
- Extensive use of Pandas/Numpy matrices for fast vectorized evaluation before sending single orders.
- Heavy reliance on local DBs (DuckDB).

## Layers

**Trading Engine Layer:**
- Purpose: Execute algorithms based on live ticks.
- Location: `new_system/trading_engine.py`
- Contains: Broker loops, initialization modules.
- Depends on: `NorenApiPy`.

**Data / Feature Extraction Layer:**
- Purpose: Cleansing data, predicting probabilities. 
- Location: `sandwich/steps/`
- Contains: sequential python scripts processing data tables.
- Depends on: `duckdb`, `pandas`, `sklearn`.

## Data Flow

### Primary Execution Path (new_system)

1. Trading Engine initialization (`new_system/trading_engine.py`)
2. Start DataFeed for live ticks fetching (`new_system/feed/datafeed.py`)
3. Compute indicators / execute strategies (`new_system/strategy/strategy.py`)
4. Submit via Broker (`new_system/broker/broker.py`)

## Key Abstractions

**NorenApiPy Client Wrapper:**
- Purpose: Safe session wrapping and API token execution.
- Examples: `new_system/broker/broker.py`
- Pattern: Object wrapper logging states.

## Entry Points

**Matsaya entry:**
- Location: `matsaya/main.py`
- Triggers: CLI invocation
- Responsibilities: End to end fetch and scan indicators demo.

**Sandwich Pipeline:**
- Location: `sandwich/signal_api.py`
- Triggers: Called by other bots to evaluate ML probabilities.
- Responsibilities: Wraps pickled model into a single `.predict(features)` call.

## Architectural Constraints

- **Local Data Coupling:** DuckDB paths are absolute inside `sandwich` e.g., `/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb`.
- **Global state:** Several ML models rely on pre-trained serialized `.pkl` in nested folders.
- **Threading:** Some models are completely synchronous loops on crontab (`crontab.txt`).

## Anti-Patterns

### Hardcoded File Paths in Production

**What happens:** Hardcoding absolute local Linux paths for DuckDB.
**Why it's wrong:** Breaks modularity and deployment elsewhere.
**Do this instead:** Rely on Environment variables (`.env`) for configuring `DB_PATH`.

## Error Handling

**Strategy:** Try block exception printing. Standard logging output file routing.

---

*Architecture analysis: Sat Oct 03 2026*