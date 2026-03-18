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

    ws = get_or_create_worksheet(ss, sheet_name, rows=100, cols=10)

    # Row 1: Metadata
    ws.update(
        range_name="A1:B1",
        values=[["Última Actualización", ""]],
        value_input_option="USER_ENTERED",
    )

    # Row 3: Headers
    headers = [
        "Mes Reporte",
        "Mes M",
        "Mes M+1",
        "Mes M+2",
        "Mes M+3",
        "Mes M+4",
        "Mes M+5",
        "Mes M+6",
        "Próx. 12m",
    ]
    ws.update(range_name="A3:I3", values=[headers], value_input_option="USER_ENTERED")

    header_bg = COLORS["header_bg"]
    header_fg = COLORS["header_fg"]

    reqs = [
        # Row 1: Metadata format
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
        # Row 3: Headers format
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 2, "endRowIndex": 3},
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
    ]
    apply_formatting(ss, ws.id, reqs)
