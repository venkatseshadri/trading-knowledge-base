#!/bin/bash
LOG_FILE="/tmp/clear_paper_positions.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting daily position cleanup" >> $LOG_FILE

# 1. Kill MCX agent (m1)
pkill -f "strategyCode=m1" && echo "$(date) - MCX (m1) stopped" >> $LOG_FILE || echo "$(date) - MCX not running" >> $LOG_FILE

# 2. Clear paper positions file
PAPER_POS_FILE="/home/trading_ceo/python-trader/orbiter/data/paper_positions.json"
if [ -f "$PAPER_POS_FILE" ]; then
    echo "[]" > "$PAPER_POS_FILE"
    echo "$(date) - Paper positions cleared" >> $LOG_FILE
fi

# 3. Reset margin state
MARGIN_STATE="/home/trading_ceo/python-trader/orbiter/utils/margin/paper_trade_state.json"
if [ -f "$MARGIN_STATE" ]; then
    python3 -c "
import json
with open(, 'r') as f:
    data = json.load(f)
data['used_margin'] = 0
data['mtm'] = 0
data['positions'] = []
data['daily_pnl'] = 0
data['trade_count'] = 0
with open(, 'w') as f:
    json.dump(data, f, indent=2)
" && echo "$(date) - Margin state reset" >> $LOG_FILE
fi

echo "$(date) - Daily cleanup complete" >> $LOG_FILE
