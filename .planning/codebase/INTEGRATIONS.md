# External Integrations

**Analysis Date:** Sat Oct 03 2026

## APIs & External Services

**Brokerage & Execution:**
- Finvasia Shoonya - Trading execution, login, order management format.
  - SDK/Client: `Shoonya_oAuth_API.py` -> `NorenApiPy`
  - Auth: Handled via `cred.yml` (UID, Access_token).

**Market Data:**
- Yahoo Finance - Historical tick and daily data retrieval.
  - SDK/Client: `yfinance` 

## Data Storage

**Databases:**
- DuckDB
  - Connection: Hardcoded Paths e.g., `/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb`
  - Client: `duckdb` (Python library).

**File Storage:**
- Local filesystem only (.parquet, .csv, json reports).

**Caching:**
- None detected explicitly beyond DuckDB memory processing.

## Authentication & Identity

**Auth Provider:**
- Custom / Shoonya API Auth Token
  - Implementation: Reading `cred.yml`, passing keys via NorenApi set_session.

## Monitoring & Observability

**Error Tracking:**
- Standard Python logging and cron log files (`nohup.out`, `/tmp/*.log`).

**Logs:**
- Files written locally via `logging` module.

## CI/CD & Deployment

**Hosting:**
- Raw Virtual Private Server / Cron instances.

**CI Pipeline:**
- None detected.

## Environment Configuration

**Required env vars:**
- Access_token, UID, etc. (mostly configured via files like `cred.yml` and `config.json`).

**Secrets location:**
- `.env` files and `cred.yml` (which isn't tracked in git, `cred.yml.CAN_BE_DELETED` acts as sample).

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: Sat Oct 03 2026*