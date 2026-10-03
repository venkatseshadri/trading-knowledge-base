# Codebase Structure

**Analysis Date:** Sat Oct 03 2026

## Directory Layout

```
/home/trading_ceo/projects/trading-knowledge-base/
├── iron_fly_backtest/   # Scripts testing variations of Iron Fly option legs
├── matsaya/             # Clean boilerplate framework, structured with tests
├── new_system/          # Consolidated Trading Engine for real-time dispatch
├── sandwich/            # DuckDB-powered Machine Learning prediction API
├── Shoonya-API-new/     # External Broker SDK dependencies
└── scripts/             # Arbitrary utility commands
```

## Directory Purposes

**`matsaya/`:**
- Purpose: Best practice (test-driven) environment using historical data.
- Contains: Clean modules: `data`, `indicators`, `signals`, `trades`.
- Key files: `matsaya/main.py`, `matsaya/config.json`.

**`new_system/`:**
- Purpose: Aggregator of strategies over real broker. 
- Contains: Broker clients, live data feed objects, execution engine.
- Key files: `new_system/trading_engine.py`.

**`sandwich/`:**
- Purpose: Multi-step data orchestration and feature output.
- Contains: Pipeline scripts mapping data -> labels -> correlations -> pickles.
- Key files: `sandwich/steps/step03_features.py`, `sandwich/signal_api.py`.

## Key File Locations

**Entry Points:**
- `matsaya/main.py`: Bootstraps indicators scanner.
- `new_system/trading_engine.py`: Runs main production integration execution.

**Configuration:**
- `cred.yml`: Excluded locally, critical for broker credentials.
- `matsaya/config.json`: Algorithm params.

**Core Logic:**
- `sandwich/signal_api.py`: Exposes `SandwichSignalEngine`.

## Where to Add New Code

**New Trading Strategies:**
- Implementation: `new_system/strategy/strategy.py`

**New Machine Learning Features:**
- Implementation: `sandwich/steps/step03_features.py`

**New Broker Integrations:**
- Implementation: `new_system/broker/broker.py`

---

*Structure analysis: Sat Oct 03 2026*