#!/bin/bash
# MCX Session Summary Script
# Uses actual log paths from your trading system
# Location: /home/trading_ceo/mcx_session_summary.sh

LOG_DIR="/home/trading_ceo/python-trader/logs"
SYSTEM_LOG_DIR="$LOG_DIR/system"
PAPER_STATE="/home/trading_ceo/python-trader/orbiter/utils/margin/paper_trade_state.json"
TODAY=$(date +%Y%m%d)

echo "========================================="
echo "  MCX SESSION SUMMARY - $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo ""

# Find today's latest orbiter log
LATEST_LOG=$(ls -t "$SYSTEM_LOG_DIR"/orbiter_${TODAY}_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "⚠️  No trade logs found for today: $TODAY"
    # Try to find yesterday's log
    YESTERDAY=$(date -d "yesterday" +%Y%m%d)
    LATEST_LOG=$(ls -t "$SYSTEM_LOG_DIR"/orbiter_${YESTERDAY}_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "📂 Using yesterday's log: $(basename $LATEST_LOG)"
    else
        exit 0
    fi
else
    echo "📂 Log: $(basename $LATEST_LOG)"
fi

echo ""
echo "--- 📊 Trades Executed (Last 30) ---"

# Extract trade orders from log
grep "trade.place_future_order" "$LATEST_LOG" | tail -30 | while read line; do
    timestamp=$(echo "$line" | cut -d'|' -f1 | xargs)
    # Extract fields from JSON-like params
    symbol=$(echo "$line" | grep -oP "'symbol': '[^']+'" | cut -d"'" -f4)
    side=$(echo "$line" | grep -oP "'side': '[^']+'" | cut -d"'" -f4)
    qty=$(echo "$line" | grep -oP "'qty': \d+" | grep -oP "\d+")
    remark=$(echo "$line" | grep -oP "'remark': '[^']+'" | cut -d"'" -f4)
    
    if [ "$side" = "BUY" ]; then
        emoji="🟢"
    else
        emoji="🔴"
    fi
    
    echo "  $emoji $side $symbol | Qty: $qty | Strategy: $remark"
done

echo ""
echo "--- 📈 Symbols Traded Today ---"

# Get unique symbols
grep "trade.place_future_order" "$LATEST_LOG" | grep -oP "'symbol': '[^']+'" | cut -d"'" -f4 | sort | uniq -c | while read count symbol; do
    echo "  • $symbol: $count orders"
done

echo ""
echo "--- 💰 Position Summary ---"

# Check paper trade state
if [ -f "$PAPER_STATE" ]; then
    cash=$(grep -oP '"cash":\s*\d+' "$PAPER_STATE" | grep -oP "\d+" | head -1)
    used_margin=$(grep -oP '"used_margin":\s*\d+' "$PAPER_STATE" | grep -oP "\d+" | head -1)
    mtm=$(grep -oP '"mtm":\s*-?\d+' "$PAPER_STATE" | grep -oP "\d+" | head -1)
    positions=$(grep -oP '"positions":\s*\[]' "$PAPER_STATE" >/dev/null && echo "0 open positions" || cat "$PAPER_STATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d.get(\"positions\",[]))} open positions')" 2>/dev/null)
    
    echo "  Cash: ₹${cash:-0}"
    echo "  Used Margin: ₹${used_margin:-0}"
    echo "  MTM: ₹${mtm:-0}"
    echo "  Open Positions: ${positions:-0}"
else
    echo "  (No position file found)"
fi

echo ""
echo "--- 🛑 Session End ---"

# Check shutdown reason
shutdown_reason=$(grep "EOD Shutdown\|Manual\|Error" "$LATEST_LOG" | tail -1 | grep -oP "EOD|Manual|Error" | tail -1)
if [ "$shutdown_reason" = "EOD" ]; then
    echo "  Normal EOD shutdown"
else
    echo "  Session ended: $shutdown_reason"
fi

echo ""
echo "========================================="
