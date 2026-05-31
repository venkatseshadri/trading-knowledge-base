#!/bin/bash
# Cleanup script for Orbiter - run daily via cron
# Clears old logs, stale lockfiles, trade_calls.log

ORBITER_DIR="/home/trading_ceo/python-trader"
LOG_DIR="$ORBITER_DIR/logs/system"
TRADE_LOGS="$ORBITER_DIR/logs"
ORBITER_CORE="$ORBITER_DIR/orbiter"

echo "=== Orbiter Cleanup - $(date) ==="

# 1. Truncate trade_calls.log files (keep file, clear content)
echo "Cleaning trade_calls.log files..."
find $TRADE_LOGS -name "trade_calls.log" -type f -exec truncate -s 0 {} \;

# 2. Archive and truncate old orbiter logs (keep last 3 days)
echo "Archiving old logs..."
find $LOG_DIR -name "orbiter_*.log" -type f -mtime +1 -exec gzip {} \; 2>/dev/null

# 3. Delete archived logs older than 7 days
echo "Deleting old archives..."
find $LOG_DIR -name "orbiter_*.log.gz" -type f -mtime +7 -delete

# 4. Delete old mcx.log files (not the current one)
echo "Cleaning MCX logs..."
find $ORBITER_CORE -name "mcx.log*" -type f -mtime +1 -delete 2>/dev/null

# 5. Delete stale lockfiles (older than 1 day)
echo "Cleaning stale lockfiles..."
find $ORBITER_CORE -name "*.lock" -type f -mtime +1 -delete 2>/dev/null

# 6. Clean up pycache
echo "Cleaning pycache..."
find $ORBITER_DIR -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "=== Cleanup complete ==="
