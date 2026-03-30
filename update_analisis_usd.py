#!/usr/bin/env python3
"""Actualiza Análisis USD para usar columna de ascensos de Ingresos."""

import os

from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.setup.analisis_usd import setup_analisis_usd

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def main():
    """Actualiza Análisis USD."""
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return

    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    print("=" * 80)
    print("ACTUALIZANDO ANÁLISIS USD")
    print("=" * 80)
    print()

    setup_analisis_usd(ss)

    print()
    print("=" * 80)
    print("✅ Análisis USD actualizado correctamente")
    print()
    print(f"Ver sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print("=" * 80)


if __name__ == "__main__":
    main()
