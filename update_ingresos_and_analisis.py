#!/usr/bin/env python3
"""Actualiza Ingresos (con columna ¿Ascenso?) y Análisis ARS."""

import os

from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.setup.ingresos import setup_ingresos
from src.setup.analisis_ars import setup_analisis_ars

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def main():
    """Actualiza Ingresos y Análisis ARS."""
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return

    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    print("=" * 80)
    print("ACTUALIZANDO INGRESOS Y ANÁLISIS ARS")
    print("=" * 80)
    print()

    # Actualizar Ingresos (ahora con columna Q = ¿Ascenso?)
    setup_ingresos(ss)

    print()

    # Actualizar Análisis ARS (sin columna E local, usa Ingresos!Q)
    setup_analisis_ars(ss)

    print()
    print("=" * 80)
    print("✅ Sheets actualizadas correctamente")
    print()
    print(f"Ver sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print()
    print("PRÓXIMO PASO: Ejecutar mark_ascensos.py para marcar los 2 ascensos")
    print("=" * 80)


if __name__ == "__main__":
    main()
