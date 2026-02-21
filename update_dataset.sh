#!/bin/bash
# update_dataset.sh
#
# Actualiza el dataset de mercado (CER, CCL, REM) desde la última fecha registrada.
# Llena automáticamente todos los datos faltantes hasta hoy.
#
# Usage:
#   ./update_dataset.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/logs/update_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "============================================" | tee -a "$LOG_FILE"
echo "Ingresos Dataset Update - $(date)" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "Actualizando datos de mercado..." | tee -a "$LOG_FILE"
if uv run fetch_data.py 2>&1 | tee -a "$LOG_FILE"; then
    echo "✓ Dataset actualizado" | tee -a "$LOG_FILE"
else
    echo "✗ Actualización fallida" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "✓ Actualización completa" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"
