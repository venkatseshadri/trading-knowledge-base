# Options and Configurations

Most components rely on their respective configuration files:
- **`matsaya`**: Configured dynamically through `matsaya/config.json`.
- **`new_system`**: Broker relies on `cred.yml` to feed API secrets format.
- **`sandwich`**: Relies heavily on hardcoded internal duckDB paths, configuration handled across `.py` step parameters.
- **`iron_fly_backtest`**: Iterates over pandas arrays reading from `all_configs_full_stats.csv`.

*Reminder: Never check-in `.env`, `cred.yml` or tokens.*