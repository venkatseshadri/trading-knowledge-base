#!/bin/bash
# BFO Cleanup Script - runs at end of BFO session

echo "=== BFO Cleanup - $(date) ==="

# Kill BFO strategies
pkill -f "strategyCode=s1"
pkill -f "strategyCode=s2"

# Clear positions
> /home/trading_ceo/python-trader/logs/s1/positions.json 2>/dev/null
> /home/trading_ceo/python-trader/logs/s2/positions.json 2>/dev/null

# Clear sessions
> /home/trading_ceo/python-trader/logs/s1/sessions.json 2>/dev/null
> /home/trading_ceo/python-trader/logs/s2/sessions.json 2>/dev/null

# Clear trade calls
> /home/trading_ceo/python-trader/logs/s1/trade_calls.log 2>/dev/null
> /home/trading_ceo/python-trader/logs/s2/trade_calls.log 2>/dev/null

# Clear paper_positions
> /home/trading_ceo/python-trader/orbiter/data/paper_positions.json 2>/dev/null

# Clear lockfile
rm -f /home/trading_ceo/python-trader/orbiter.lock

echo "=== BFO Cleanup Complete ==="
