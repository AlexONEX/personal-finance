"""setup_sheet.py

Configura la estructura de las hojas en Google Sheets.
Orquesta los módulos de setup individuales.
"""

import os

from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.setup import (
    setup_analisis_ars,
    setup_analisis_usd,
    setup_cpi,
    setup_historic,
    setup_impuestos,
    setup_ingresos,
    setup_inversiones,
    setup_rem,
    setup_simulador,
)

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def setup_all():
    """Ejecuta el setup completo de todas las hojas."""
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return

    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    # Configurar cada hoja
    setup_impuestos(ss)
    setup_historic(ss)
    setup_rem(ss)
    setup_cpi(ss)
    setup_ingresos(ss)
    setup_inversiones(ss)
    setup_analisis_ars(ss)
    setup_analisis_usd(ss)
    setup_simulador(ss)

    print(
        f"\nSetup completo: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"
    )


if __name__ == "__main__":
    setup_all()
