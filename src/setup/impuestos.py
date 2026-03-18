"""Setup de la hoja de impuestos."""

import gspread

from src.config import COLORS, SHEETS
from src.setup.utils import apply_formatting, get_or_create_worksheet
from src.sheets.structure import IMPUESTOS_ROWS


def setup_impuestos(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja de impuestos con tasas y leyes.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["IMPUESTOS"]
    print(f"Configurando {sheet_name}...")

    ws = get_or_create_worksheet(ss, sheet_name, rows=10, cols=3)
    ws.update(range_name="A1:C1", values=[["Impuesto", "Tasa", "Ley / Descripción"]])

    payload = [[name, rate, ley] for name, rate, ley in IMPUESTOS_ROWS]
    ws.update(
        range_name=f"A2:C{1 + len(payload)}",
        values=payload,
        value_input_option="USER_ENTERED",
    )

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
                    "startRowIndex": 1,
                    "endRowIndex": 10,
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
