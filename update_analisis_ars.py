#!/usr/bin/env python3
"""Actualiza solo la hoja Análisis ARS con la nueva columna ¿Ascenso?"""

import os

from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.setup.analisis_ars import setup_analisis_ars

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def main():
    """Actualiza solo la hoja Análisis ARS."""
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return

    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    print("=" * 80)
    print("ACTUALIZANDO ANÁLISIS ARS CON NUEVA COLUMNA '¿ASCENSO?'")
    print("=" * 80)
    print()

    setup_analisis_ars(ss)

    print()
    print("=" * 80)
    print("✅ Análisis ARS actualizado correctamente")
    print()
    print(f"Ver sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid=...")
    print()
    print("PRÓXIMO PASO: Ejecutar mark_ascensos.py para marcar los ascensos reales")
    print("=" * 80)


if __name__ == "__main__":
    main()
