#!/bin/bash
# Weekly Cleanup Script - runs Sunday noon

echo "=== Weekly Cleanup - $(date) ==="

LOG_DIR="/home/trading_ceo/python-trader/logs"
TEMP_DIR="/tmp"

# Archive and compress old orbiter logs (keep last 7 days)
echo "Archiving old logs..."
find $LOG_DIR -name "orbiter_*.log" -type f -mtime +1 -exec gzip {} \; 2>/dev/null

# Delete old archived logs (older than 30 days)
echo "Deleting old archives..."
find $LOG_DIR -name "orbiter_*.log.gz" -type f -mtime +30 -delete 2>/dev/null

# Clean system debug.log
echo "Cleaning system debug.log..."
> $LOG_DIR/system/debug.log 2>/dev/null

# Clean INFO and TRACE orbiter logs
echo "Cleaning INFO/TRACE logs..."
find /home/trading_ceo/python-trader/INFO -name "orbiter_*.log" -type f -mtime +7 -delete 2>/dev/null
find /home/trading_ceo/python-trader/TRACE -name "orbiter_*.log" -type f -mtime +7 -delete 2>/dev/null

# Clean NFO temp files
echo "Cleaning NFO temp files..."
find $TEMP_DIR -name "orbiter_n*.log" -type f -mtime +7 -delete 2>/dev/null
find $TEMP_DIR -name "nfo_*.log" -type f -mtime +7 -delete 2>/dev/null

# Clean BFO temp files
echo "Cleaning BFO temp files..."
find $TEMP_DIR -name "orbiter_s*.log" -type f -mtime +7 -delete 2>/dev/null
find $TEMP_DIR -name "bfo_*.log" -type f -mtime +7 -delete 2>/dev/null

# Clean MCX temp files
echo "Cleaning MCX temp files..."
find $TEMP_DIR -name "orbiter_m*.log" -type f -mtime +7 -delete 2>/dev/null
find $TEMP_DIR -name "mcx_*.log" -type f -mtime +7 -delete 2>/dev/null

# Clean pycache
echo "Cleaning pycache..."
find /home/trading_ceo/python-trader -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Clear old health check logs
echo "Clearing old health check logs..."
find /tmp -name "health_check*.log" -type f -mtime +7 -delete 2>/dev/null

echo "=== Weekly Cleanup Complete ==="
