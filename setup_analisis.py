#!/usr/bin/env python3
"""Script principal para configurar Análisis ARS y USD.

Este script configura las hojas de Análisis ARS y USD con fórmulas simplificadas.

Usage:
    # Setup completo
    python setup_analisis.py --all

    # Setup de solo una hoja
    python setup_analisis.py --ars
    python setup_analisis.py --usd
"""

import argparse
import os

from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.setup.analisis import setup_analisis_ars, setup_analisis_usd

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def main():
    parser = argparse.ArgumentParser(description="Configurar Análisis ARS/USD")
    parser.add_argument("--all", action="store_true", help="Setup completo")
    parser.add_argument("--ars", action="store_true", help="Solo Análisis ARS")
    parser.add_argument("--usd", action="store_true", help="Solo Análisis USD")

    args = parser.parse_args()

    if not (args.all or args.ars or args.usd):
        parser.print_help()
        return

    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return

    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    print("=" * 80)
    print("SETUP ANÁLISIS ARS/USD")
    print("=" * 80)
    print()

    if args.all or args.ars:
        print("Configurando Análisis ARS...")
        setup_analisis_ars(ss)
        print()

    if args.all or args.usd:
        print("Configurando Análisis USD...")
        setup_analisis_usd(ss)
        print()

    print("=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    print()
    print(f"Ver sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print()


if __name__ == "__main__":
    main()
