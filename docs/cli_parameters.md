# CLI Parameters

**Analysis Date:** Sat Oct 03 2026

The repository does not expose a traditional command‑line interface package. However, operational scripts are invoked via crontab and manual execution:

- `sandwich/steps/*.py` – executable Python scripts for data preparation, model training, and reporting. They are run directly with `python <script>.py`.
- `iron_fly_backtest/runner.py` – launches back‑testing runs.
- `matsaya/main.py` – entry point for the Matsaya sandbox; can be executed with `python -m matsaya.main`.
- `new_system/trading_engine.py` – can be started using `python new_system/trading_engine.py` with a configuration file path passed via `--config <path>` (custom argument parsed inside the script).

**Typical invocation pattern:**
```bash
python new_system/trading_engine.py --config matsaya/config.json
```

**Note:** No dedicated CLI argument parser (e.g., argparse) is present for most scripts; parameters are hard‑coded or read from JSON/YAML config files.
