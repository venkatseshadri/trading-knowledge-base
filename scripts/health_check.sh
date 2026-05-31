#!/bin/bash
# Health check - restarts orbiter with given strategy if not running
# Usage: ./health_check.sh <strategyCode>
# Example: ./health_check.sh n1

# Telegram config
TELEGRAM_BOT_TOKEN="8608054593:AAGDM9-x7TmjMO8Trpn-bPUBqqwQDFv-pcc"
TELEGRAM_CHAT_ID="8317944043"

STRATEGY=${1:-m1}

# Determine market based on strategy code
case "$STRATEGY" in
    n1|n2|s1|s2) MARKET="nfo" ;;   # NSE & BSE F&O (same holidays)
    m1)          MARKET="mcx" ;;   # MCX Commodities
    *)           MARKET="nfo" ;;    # default to nfo
esac

# Get today's date in YYYY-MM-DD format
TODAY=$(date +%Y-%m-%d)

# 🔍 CHECK HOLIDAY - Line 19-27
HOLIDAY_FILE="/home/trading_ceo/python-trader/orbiter/data/$MARKET/holidays.json"

if [ -f "$HOLIDAY_FILE" ]; then
    # Check if today's date exists in holidays array
    if grep -q "$TODAY" "$HOLIDAY_FILE"; then
        MSG="⛔ SKIPPED - $MARKET market is closed (Holiday: $TODAY)"
        echo "[$(date)] $MSG"
        
        # Send Telegram alert
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d chat_id="$TELEGRAM_CHAT_ID" \
            -d text="$MSG" 2>/dev/null
        
        exit 0
    fi
fi

# Check if orbiter is already running
if pgrep -f "strategyCode=$STRATEGY" > /dev/null; then
    MSG="✅ Already running: $STRATEGY"
    echo "[$(date)] $MSG"
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="$MSG" 2>/dev/null
    exit 0
fi

# Start orbiter
cd /home/trading_ceo/python-trader && nohup /home/trading_ceo/python-trader/dist/orbiter-4.6.1 --strategyCode=$STRATEGY --caller=cron > /tmp/orbiter_$STRATEGY.log 2>&1

MSG="🚀 Started: $STRATEGY ($MARKET market)"
echo "[$(date)] $MSG"

# Send Telegram alert
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d chat_id="$TELEGRAM_CHAT_ID" \
    -d text="$MSG" 2>/dev/null