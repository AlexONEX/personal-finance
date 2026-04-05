"""Setup de la hoja Simulador Inflación."""

import gspread

from src.config import COLORS, SHEETS
from src.setup.utils import apply_formatting, get_or_create_worksheet
from src.sheets.structure import SIMULADOR_INFLACION_ROWS


def setup_simulador(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja de simulador de inflación.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["SIMULADOR_INFLACION"]
    print(f"Configurando {sheet_name}...")

    ws = get_or_create_worksheet(ss, sheet_name, rows=20, cols=5)

    # Row 1: Header
    ws.update(range_name="A1:D1", values=[SIMULADOR_INFLACION_ROWS[0]])
    
    # Row 3: Ejemplo/Placeholder (dejamos la fila 2 vacía por estética)
    # El usuario debería llenar A3, B3, C3
    placeholder = [3, 2026, 0.029, "Pendiente de ejecutar script"]
    ws.update(range_name="A3:D3", values=[[3, 2026, 0.029, "Esperando script..."]])

    header_bg = COLORS["header_bg"]
    header_fg = COLORS["header_fg"]

    reqs = [
        # Headers Row 1
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 4},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": header_bg,
                        "textFormat": {"bold": True, "foregroundColor": header_fg},
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        },
        # Input format for Inflation (Column C)
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 2, "endRowIndex": 3, "startColumnIndex": 2, "endColumnIndex": 3},
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "PERCENT", "pattern": "0.0%"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        },
        # Border for input cells
        {
            "updateBorders": {
                "range": {"sheetId": ws.id, "startRowIndex": 2, "endRowIndex": 3, "startColumnIndex": 0, "endColumnIndex": 3},
                "bottom": {"style": "SOLID", "width": 1},
                "top": {"style": "SOLID", "width": 1},
                "left": {"style": "SOLID", "width": 1},
                "right": {"style": "SOLID", "width": 1},
            }
        }
    ]
    apply_formatting(ss, ws.id, reqs)
