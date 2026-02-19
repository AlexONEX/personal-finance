#!/bin/bash
# automation/install.sh
#
# Installs launchd job for daily automatic updates.
#
# Usage:
#   ./automation/install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_TEMPLATE="$SCRIPT_DIR/com.ingresos.daily-update.plist.template"
PLIST_DEST="$HOME/Library/LaunchAgents/com.ingresos.daily-update.plist"

echo "============================================"
echo "Ingresos - Install Daily Automation"
echo "============================================"
echo ""

# Create LaunchAgents directory if needed
mkdir -p "$HOME/Library/LaunchAgents"

# Replace PROJECT_DIR placeholder with actual path
echo "Creating plist at: $PLIST_DEST"
sed "s|PROJECT_DIR|$PROJECT_DIR|g" "$PLIST_TEMPLATE" > "$PLIST_DEST"
echo "✓ Plist created"

# Load the job
echo ""
echo "Loading launchd job..."
launchctl unload "$PLIST_DEST" 2>/dev/null || true  # unload if already loaded
launchctl load "$PLIST_DEST"
echo "✓ Job loaded"

echo ""
echo "============================================"
echo "✓ Installation complete!"
echo "============================================"
echo ""
echo "The daily update will run at 9:00 AM every day."
echo ""
echo "Useful commands:"
echo "  # Check job status"
echo "  launchctl list | grep ingresos"
echo ""
echo "  # Run manually now (for testing)"
echo "  launchctl start com.ingresos.daily-update"
echo ""
echo "  # View logs"
echo "  tail -f $PROJECT_DIR/logs/launchd-stdout.log"
echo ""
echo "  # Uninstall"
echo "  ./automation/uninstall.sh"
echo ""
