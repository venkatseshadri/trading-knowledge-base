# Integration Rules

## Core Broker (Shoonya API)
1. Ensure `Shoonya_oAuth_API.py` wrapper library works. Needs `api_helper.NorenApiPy`.
2. Connect with `cred.yml` referencing `UID` and `Access_token`. `NorenApiPy` uses `.set_session(uid, token)`.
3. Do **not** commit `cred.yml` to the repository.

## DuckDB Access
1. Do not lock databases via parallel write instances.
2. Read-only pipelines must pass `read_only=True` to `duckdb.connect(str(DB_PATH))`.

## Models / Signals
1. `SandwichSignalEngine` ML pipelines expect pandas DataFrames.
2. Ensure Pickled (`.pkl`) models are pre-generated within `sandwich/data/`.