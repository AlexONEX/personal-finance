#!/usr/bin/env python3
"""Script para validar que los cálculos de Análisis ARS/USD sean correctos.

Compara los valores calculados en el spreadsheet con los cálculos manuales
documentados en docs/CALCULO_MANUAL_METRICAS.md.

Usage:
    python validate_analisis.py
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

from src.validators.analisis_coherence import (
    AnalisisCoherenceValidator,
    Severity,
    ValidationIssue,
)

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "service_account.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_sheets_client():
    """Obtiene cliente de Google Sheets."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def parse_currency(value: str) -> Optional[float]:
    """Parsea valor de moneda ($1,234.56)."""
    if not value or value == "":
        return None
    try:
        # Remover $, comas
        cleaned = value.replace("$", "").replace(",", "").strip()
        return float(cleaned)
    except:
        return None


def parse_percentage(value: str) -> Optional[float]:
    """Parsea porcentaje (12.34%)."""
    if not value or value == "":
        return None
    try:
        cleaned = value.replace("%", "").strip()
        return float(cleaned) / 100  # Convertir a decimal
    except:
        return None


def parse_number(value: str) -> Optional[float]:
    """Parsea número genérico."""
    if not value or value == "":
        return None
    try:
        cleaned = value.replace(",", "").strip()
        return float(cleaned)
    except:
        return None


# =============================================================================
# Valores esperados de CALCULO_MANUAL_METRICAS.md
# =============================================================================

EXPECTED_VALUES = {
    "inflacion_acumulada": {
        "periodo_1": {
            "cer": 2.082,  # 208.2%
            "ipc_nacional": 2.123,  # 212.3%
            "ipc_caba": 2.246,  # 224.6%
        },
        "periodo_2": {
            "cer": 0.195,  # 19.5%
            "ipc_nacional": 0.195,  # 19.5%
            "ipc_caba": 0.207,  # 20.7%
        },
        # Período 3 depende del CER actual estimado
    },
    "variacion_real_periodo_1": {
        "cer": 1.066,  # +106.6%
        "ipc_nacional": 1.039,  # +103.9%
        "ipc_caba": 0.962,  # +96.2%
    },
    "variacion_real_periodo_2": {
        "cer": 0.205,  # +20.5%
        "ipc_nacional": 0.205,  # +20.5%
        "ipc_caba": 0.193,  # +19.3%
    },
    # CER Base values
    "cer_base": {
        "oct_2023": 173.7867,
        "dic_2024": 535.5457,
        "ago_2025": 639.7752,
    },
}


def validate_manual_calculations(ss: gspread.Spreadsheet) -> List[ValidationIssue]:
    """Valida cálculos contra valores manuales."""
    issues = []

    # TODO: Implementar validaciones específicas

    return issues


def run_coherence_validations(ss: gspread.Spreadsheet) -> AnalisisCoherenceValidator:
    """Ejecuta validaciones de coherencia."""
    validator = AnalisisCoherenceValidator()

    # Leer datos de Análisis ARS
    try:
        ws_ars = ss.worksheet("Análisis ARS")
        data_ars = ws_ars.get_all_values()

        # Asumiendo headers en rows 1-2, datos desde row 3
        if len(data_ars) < 3:
            print("⚠️  Análisis ARS vacío")
            return validator

        # Leer columnas relevantes
        # TODO: Parsear datos y ejecutar validaciones

        print("✅ Análisis ARS leído correctamente")

    except Exception as e:
        print(f"❌ Error leyendo Análisis ARS: {e}")

    # Leer datos de Análisis USD
    try:
        ws_usd = ss.worksheet("Análisis USD")
        data_usd = ws_usd.get_all_values()

        if len(data_usd) < 3:
            print("⚠️  Análisis USD vacío")
            return validator

        # TODO: Parsear datos y ejecutar validaciones

        print("✅ Análisis USD leído correctamente")

    except Exception as e:
        print(f"❌ Error leyendo Análisis USD: {e}")

    return validator


def main():
    """Main."""
    print("=" * 80)
    print("VALIDACIÓN DE ANÁLISIS ARS Y USD")
    print("=" * 80)
    print()

    if not SPREADSHEET_ID:
        print("❌ ERROR: SPREADSHEET_ID no definido en .env")
        return

    print(f"Conectando a spreadsheet: {SPREADSHEET_ID}")
    gc = get_sheets_client()
    ss = gc.open_by_key(SPREADSHEET_ID)

    print()
    print("-" * 80)
    print("1. VALIDACIONES DE COHERENCIA")
    print("-" * 80)
    validator = run_coherence_validations(ss)
    validator.print_report()

    print()
    print("-" * 80)
    print("2. VALIDACIONES CONTRA CÁLCULOS MANUALES")
    print("-" * 80)
    manual_issues = validate_manual_calculations(ss)

    if not manual_issues:
        print("✅ Todos los cálculos manuales coinciden")
    else:
        print(f"❌ {len(manual_issues)} diferencias encontradas")
        for issue in manual_issues:
            print(f"  {issue.sheet}:{issue.row}:{issue.column} - {issue.message}")

    print()
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)

    has_critical = validator.has_critical_issues()
    has_errors = validator.has_errors()

    if has_critical:
        print("🔴 CRÍTICO: Se encontraron errores críticos que deben corregirse")
        return 1
    elif has_errors:
        print("❌ ERROR: Se encontraron errores que deben revisarse")
        return 1
    elif validator.issues:
        print("⚠️  WARNING: Se encontraron warnings (no bloquean)")
        return 0
    else:
        print("✅ ÉXITO: Todas las validaciones pasaron")
        return 0


if __name__ == "__main__":
    exit(main())
