#!/bin/bash
# Kubera Validation Script - Check Claude Remote Execution
# Run this 5 minutes after 03:05 AM to verify the job completed
# Usage: ./validate_remote.sh [RESPONSE_FILE]

RESPONSE_FILE="${1:-/home/trading_ceo/__RESPONSE__.MD}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "🔍 Kubera Validation Check - $TIMESTAMP"
echo "====================================="
echo "Checking: $RESPONSE_FILE"

if [ ! -f "$RESPONSE_FILE" ]; then
    echo "❌ FAILURE: Response file does not exist!"
    echo "⚠️  Remote execution may have failed to start."
    exit 1
fi

FILE_SIZE=$(stat -c%s "$RESPONSE_FILE" 2>/dev/null || stat -f%z "$RESPONSE_FILE" 2>/dev/null)

if [ "$FILE_SIZE" -eq 0 ]; then
    echo "❌ FAILURE: Response file is empty (0 bytes)!"
    echo "⚠️  The pipe likely failed - Claude may be waiting for stdin."
    exit 1
fi

echo "✅ SUCCESS: Response file exists and has content."
echo "   Size: $FILE_SIZE bytes"

# Show last 10 lines for quick verification
echo ""
echo "--- Last 10 lines of response ---"
tail -10 "$RESPONSE_FILE"

exit 0