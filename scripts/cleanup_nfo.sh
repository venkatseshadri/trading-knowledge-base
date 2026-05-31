#!/bin/bash
# NFO Cleanup Script - runs at end of NFO session

echo "=== NFO Cleanup - $(date) ==="

# Kill NFO strategies
pkill -f "strategyCode=n1"
pkill -f "strategyCode=n2"

# Clear positions
> /home/trading_ceo/python-trader/logs/n1/positions.json 2>/dev/null
> /home/trading_ceo/python-trader/logs/n2/positions.json 2>/dev/null

# Clear sessions
> /home/trading_ceo/python-trader/logs/n1/sessions.json 2>/dev/null
> /home/trading_ceo/python-trader/logs/n2/sessions.json 2>/dev/null

# Clear trade calls
> /home/trading_ceo/python-trader/logs/n1/trade_calls.log 2>/dev/null
> /home/trading_ceo/python-trader/logs/n2/trade_calls.log 2>/dev/null

# Clear paper_positions
> /home/trading_ceo/python-trader/orbiter/data/paper_positions.json 2>/dev/null

# Clear lockfile
rm -f /home/trading_ceo/python-trader/orbiter.lock

echo "=== NFO Cleanup Complete ==="
