# Architecture Diagram: Trading Knowledge Base

```mermaid
graph TD
    A[trading-knowledge-base] --> B[new_system: Live Trading Engine]
    A --> C[matsaya: TDD Algo Sandbox]
    A --> D[sandwich: ML Signal Engine]
    A --> E[iron_fly_backtest: Strategy Analytics]

    B --> F[Broker/Data Feeds: Shoonya API]
    C --> G[yfinance API]
    D --> H[(DuckDB local analytics)]
    E --> I[Options Backtest Logic]
```

This repository operates as an ensemble of distinct trading pipelines running autonomously on crontab (`crontab.txt`) against external services API and local Data Warehouses (`duckdb`).