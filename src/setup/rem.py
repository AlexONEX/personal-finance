"""Setup de la hoja de proyecciones REM."""

import gspread

from src.config import COLORS, SHEETS
from src.setup.utils import apply_formatting, get_or_create_worksheet


def setup_rem(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja de proyecciones REM del BCRA.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["REM"]
    print(f"Configurando {sheet_name}...")

    ws = get_or_create_worksheet(ss, sheet_name, rows=100, cols=2)

    ws.update(
        range_name="A1:B1",
        values=[["Última Actualización", ""]],
        value_input_option="USER_ENTERED",
    )

    headers = ["Mes Reporte", "Próx. 12m (IPC interanual)"]
    ws.update(range_name="A3:B3", values=[headers], value_input_option="USER_ENTERED")

    header_bg = COLORS["header_bg"]
    header_fg = COLORS["header_fg"]

    reqs = [
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": header_bg,
                        "textFormat": {"bold": True, "foregroundColor": header_fg},
                        "horizontalAlignment": "LEFT",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 2,
                    "endRowIndex": 3,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
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
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 3,
                    "endRowIndex": 100,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "PERCENT", "pattern": "0.00%"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        },
    ]
    apply_formatting(ss, ws.id, reqs)
