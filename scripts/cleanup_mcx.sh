#!/bin/bash
# MCX Cleanup Script - runs at end of MCX session

echo "=== MCX Cleanup - $(date) ==="

# Kill MCX strategy
pkill -f "strategyCode=m1"

# Clear positions
> /home/trading_ceo/python-trader/logs/m1/positions.json 2>/dev/null

# Clear sessions
> /home/trading_ceo/python-trader/logs/m1/sessions.json 2>/dev/null

# Clear trade calls
> /home/trading_ceo/python-trader/logs/m1/trade_calls.log 2>/dev/null

# Clear paper_positions
> /home/trading_ceo/python-trader/orbiter/data/paper_positions.json 2>/dev/null

# Clear lockfile
rm -f /home/trading_ceo/python-trader/orbiter.lock

echo "=== MCX Cleanup Complete ==="
