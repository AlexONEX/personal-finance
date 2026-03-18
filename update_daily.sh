#!/bin/bash
# update_daily.sh - Actualiza datos de CER, CCL, SPY y REM diariamente
#
# Uso:
#   ./update_daily.sh              # Actualiza desde última fecha en sheet
#   ./update_daily.sh --since 2024-01-01  # Actualiza desde fecha específica
#   ./update_daily.sh --help       # Muestra ayuda

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN:${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Verificar que .env existe
if [ ! -f .env ]; then
    log_error ".env file not found. Run bootstrap.py first."
    exit 1
fi

# Verificar credentials
if [ ! -f token.json ] && [ ! -f service_account.json ]; then
    log_error "No credentials found. Run bootstrap.py first."
    exit 1
fi

log_info "Starting daily data update..."
log_info "Fetching CER (BCRA), CCL (Ambito/dolarapi), SPY (yfinance), REM (BCRA)"

# Ejecutar fetch_data.py
if uv run python fetch_data.py "$@"; then
    log_info "✅ Data update completed successfully"
else
    log_error "❌ Data update failed"
    exit 1
fi

# Mostrar timestamp de última actualización
log_info "Last update: $(date +'%Y-%m-%d %H:%M:%S')"
