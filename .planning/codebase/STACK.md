# Technology Stack

**Analysis Date:** Sat Oct 03 2026

## Languages

**Primary:**
- Python 3.10+ - Backend algorithms, ML pipeline, strategies, indicators, execution.

**Secondary:**
- None significant.

## Runtime

**Environment:**
- Python 3.x
- NorenApiPy SDK for Shoonya API

**Package Manager:**
- `pip` inferred (No overarching `requirements.txt` or `poetry`/`Pipenv` setup. Dependency lists found in `Shoonya-API-new/`).
- Lockfile: missing

## Frameworks

**Core:**
- `pandas` & `numpy` - Core dependencies for data manipulation/time-series.
- `scikit-learn` (implied by `pickle` usage in ML models) - `sandwich` ML models.
- `CrewAI` - Mentioned in `AGENTS_AND_SYSTEMS.md` as agent orchestration framework.

**Testing:**
- `pytest` - For TDD in `matsaya` algo.

**Build/Dev:**
- Custom Python scripts (e.g. `runner.py`, `analyzer.py`).

## Key Dependencies

**Critical:**
- `duckdb` - Fast analytical and local database engine used extensively in the `sandwich` pipeline.
- `yfinance` - Sourcing external historical data (observed in `matsaya`).

**Infrastructure:**
- `NorenApiPy` SDK - Essential for interfacing with broker.

## Configuration

**Environment:**
- `cred.yml` - Contains sensitive keys (Shoonya API) and UID.
- `.env` files handling other secrets.

**Build:**
- Ad-hoc scripts (e.g., `main.py`, `trading_engine.py`).

## Platform Requirements

**Development:**
- Need local python installation with dependencies `pandas`, `duckdb`, `yfinance`, `pyyaml`.

**Production:**
- Linux VPS (crontabs configured for daily cron tasks executing `orbiter` and scripts).

---

*Stack analysis: Sat Oct 03 2026*