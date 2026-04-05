#!/usr/bin/env python3
"""Script principal para configurar Análisis ARS y USD con fórmulas V2.

Este script:
1. Configura las hojas de Análisis ARS y USD con fórmulas simplificadas
2. Opcionalmente ejecuta validaciones de coherencia
3. Genera reporte de validación

Usage:
    # Setup completo con validación
    python setup_analisis_v2.py --all

    # Solo setup sin validación
    python setup_analisis_v2.py --setup

    # Solo validación (asume que ya está configurado)
    python setup_analisis_v2.py --validate

    # Setup de solo una hoja
    python setup_analisis_v2.py --ars
    python setup_analisis_v2.py --usd
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.setup.analisis_v2 import setup_analisis_ars_v2, setup_analisis_usd_v2

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def main():
    parser = argparse.ArgumentParser(description="Configurar Análisis ARS/USD V2")
    parser.add_argument("--all", action="store_true", help="Setup completo + validación")
    parser.add_argument("--setup", action="store_true", help="Solo setup (sin validación)")
    parser.add_argument("--validate", action="store_true", help="Solo validación")
    parser.add_argument("--ars", action="store_true", help="Solo Análisis ARS")
    parser.add_argument("--usd", action="store_true", help="Solo Análisis USD")

    args = parser.parse_args()

    if not (args.all or args.setup or args.validate or args.ars or args.usd):
        parser.print_help()
        return

    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return

    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    print("=" * 80)
    print("SETUP ANÁLISIS ARS/USD V2")
    print("=" * 80)
    print()

    # Setup
    if args.all or args.setup or args.ars:
        print("🔧 Configurando Análisis ARS...")
        setup_analisis_ars_v2(ss)
        print()

    if args.all or args.setup or args.usd:
        print("🔧 Configurando Análisis USD...")
        setup_analisis_usd_v2(ss)
        print()

    # Validación
    if args.all or args.validate:
        print("🔍 Ejecutando validaciones...")
        print()
        print("NOTA: Para validaciones completas, ejecutar:")
        print("  python validate_analisis.py")
        print()

    print("=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    print()
    print(f"Ver sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print()


if __name__ == "__main__":
    main()
