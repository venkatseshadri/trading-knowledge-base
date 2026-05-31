#!/bin/bash
# Run Orbiter with specified strategy
# Usage: ./run_strategy.sh <strategy_folder> [screen_name]

STRATEGY=$1
SCREEN_NAME=${2:-orbiter_$STRATEGY}

if [ -z "$STRATEGY" ]; then
    echo "Usage: $0 <strategy_folder> [screen_name]"
    exit 1
fi

STRATEGY_PATH="strategies/${STRATEGY}/strategy.json"

# Update session.json
cd /home/trading_ceo/python-trader/orbiter
python3 -c "
import json
with open('config/session.json', 'r') as f:
    session = json.load(f)
session['active_strategy_path'] = '$STRATEGY_PATH'
with open('config/session.json', 'w') as f:
    json.dump(session, f, indent=2)
print(f'Switched to strategy: $STRATEGY_PATH')
"

# Kill existing screen if running
screen -S $SCREEN_NAME -X kill 2>/dev/null

# Start in screen with --strategyCode parameter (matches health_check.sh)
screen -dmS $SCREEN_NAME
screen -S $SCREEN_NAME -p 0 -X stuff "cd /home/trading_ceo/python-trader && python3 -m orbiter --strategyCode=$STRATEGY 2>&1\n"

echo "Started $STRATEGY in screen session: $SCREEN_NAME"
