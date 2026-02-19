#!/bin/bash
# automation/uninstall.sh
#
# Uninstalls launchd job for daily automatic updates.
#
# Usage:
#   ./automation/uninstall.sh

set -euo pipefail

PLIST_FILE="$HOME/Library/LaunchAgents/com.ingresos.daily-update.plist"

echo "============================================"
echo "Ingresos - Uninstall Daily Automation"
echo "============================================"
echo ""

if [ ! -f "$PLIST_FILE" ]; then
    echo "No installation found at: $PLIST_FILE"
    echo "Nothing to uninstall."
    exit 0
fi

echo "Unloading launchd job..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
echo "✓ Job unloaded"

echo ""
echo "Removing plist..."
rm "$PLIST_FILE"
echo "✓ Plist removed"

echo ""
echo "============================================"
echo "✓ Uninstallation complete!"
echo "============================================"
echo ""
