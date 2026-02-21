#!/bin/bash
# update_daily.sh
#
# Daily update script for Ingresos tracker.
# Fetches latest CER + CCL data, then recomputes monthly aggregates.
#
# Usage:
#   ./update_daily.sh
#
# For automation, see: automation/README.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/logs/update_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================" | tee -a "$LOG_FILE"
echo "Ingresos Daily Update - $(date)" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"

# Step 1: Fetch all data (CER, CCL, REM)
echo "" | tee -a "$LOG_FILE"
echo "[1/1] Fetching all market data..." | tee -a "$LOG_FILE"
if uv run fetch_data.py 2>&1 | tee -a "$LOG_FILE"; then
    echo "✓ Update complete" | tee -a "$LOG_FILE"
else
    echo "✗ Update failed" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "✓ Daily update complete" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"
