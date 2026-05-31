# New Modular Trading System

A clean-slate trading system using TA-Lib streaming API for fast indicators.

## Structure

```
new_system/
├── feed/
│   └── datafeed.py      # yfinance + broker quotes
├── indicator/
│   └── indicators.py    # TA-Lib stream functions
├── strategy/
│   └── strategy.py      # Trading strategies
├── broker/
│   └── broker.py        # Shoonya API client
├── trading_engine.py   # Main orchestrator
└── config/             # (reserved)
```

## Usage

```bash
# Single cycle
python3 trading_engine.py --symbol ^NSEI

# Real-time mode
python3 trading_engine.py --symbol ^NSEI --realtime --interval 60
```

## Features

- **Data Feed**: yfinance (primary) + Shoonya (live quotes)
- **Indicators**: TA-Lib streaming API (fast scalar output)
  - SMA, EMA, RSI, ADX, ATR, BBANDS, MACD, SuperTrend
- **Strategies**: SMA Crossover, RSI, ADX Trend, Multi-indicator
- **Broker**: Shoonya OAuth API for order execution

## Testing

```bash
# Test individual modules
python3 -c "from indicator.indicators import IndicatorEngine; print(IndicatorEngine.SMA.__doc__)"
python3 -c "from feed.datafeed import DataFeed; print(DataFeed.__doc__)"
```