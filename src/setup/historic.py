"""Setup de la hoja de datos históricos (CER, CCL, SPY)."""

import gspread

from src.config import COLORS, SHEETS
from src.setup.utils import apply_formatting, get_or_create_worksheet
from src.sheets.structure import HISTORIC_VARIABLES


def setup_historic(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja de datos históricos.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["HISTORIC"]
    print(f"Configurando {sheet_name}...")

    ws = get_or_create_worksheet(ss, sheet_name, rows=2000, cols=len(HISTORIC_VARIABLES))

    # Row 1: Metadata (source)
    meta = [f"Source: {v[0]}" if v[0] else "" for v in HISTORIC_VARIABLES]
    ws.update(range_name="A1:F1", values=[meta])

    # Row 2: Headers
    headers = [v[1] for v in HISTORIC_VARIABLES]
    ws.update(range_name="A2:F2", values=[headers])

    header_bg = COLORS["header_bg"]
    header_fg = COLORS["header_fg"]

    reqs = [
        # Rows 1-2: Headers
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 2},
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
        # Column A: Date format
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 3,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "DATE", "pattern": "dd/mm/yyyy"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        },
    ]
    apply_formatting(ss, ws.id, reqs)
