#!/usr/bin/env python3
"""Crea/actualiza solo la hoja Dashboard."""

import os

from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.setup.dashboard import setup_dashboard

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def main():
    """Actualiza Dashboard."""
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return

    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    print("=" * 80)
    print("CREANDO DASHBOARD DE NEGOCIACIÓN SALARIAL")
    print("=" * 80)
    print()

    setup_dashboard(ss)

    print()
    print("=" * 80)
    print("✅ Dashboard creado correctamente")
    print()
    print(f"Ver sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print("=" * 80)


if __name__ == "__main__":
    main()
