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

# Step 1: Fetch new historic data (incremental)
echo "" | tee -a "$LOG_FILE"
echo "[1/2] Fetching latest CER + CCL data..." | tee -a "$LOG_FILE"
if uv run fetch_historic.py 2>&1 | tee -a "$LOG_FILE"; then
    echo "✓ Fetch complete" | tee -a "$LOG_FILE"
else
    echo "✗ Fetch failed" | tee -a "$LOG_FILE"
    exit 1
fi

# Step 2: Fetch latest REM projections
echo "" | tee -a "$LOG_FILE"
echo "[2/2] Fetching latest REM projections..." | tee -a "$LOG_FILE"
if uv run fetch_rem.py 2>&1 | tee -a "$LOG_FILE"; then
    echo "✓ REM fetch complete" | tee -a "$LOG_FILE"
else
    echo "✗ REM fetch failed" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "✓ Daily update complete" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"
