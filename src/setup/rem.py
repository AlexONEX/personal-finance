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

    ws = get_or_create_worksheet(ss, sheet_name, rows=100, cols=11)

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
        "Índice REM",
    ]
    ws.update(range_name="A3:J3", values=[headers], value_input_option="USER_ENTERED")

    # Column J: Índice REM acumulado usando M+1
    # J4 = 1 (base), J5+ = J(n-1) * (1 + C(n-1))
    index_formulas = [["1"]]  # J4 = 1
    for r in range(5, 101):
        index_formulas.append([f"=J{r - 1}*(1+C{r - 1})"])
    ws.update(
        range_name="J4:J100", values=index_formulas, value_input_option="USER_ENTERED"
    )

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
        # Row 3: Headers format (extended to J)
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 2,
                    "endRowIndex": 3,
                    "startColumnIndex": 0,
                    "endColumnIndex": 10,
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
        # Column J: Índice REM format (4 decimals)
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 3,
                    "endRowIndex": 100,
                    "startColumnIndex": 9,
                    "endColumnIndex": 10,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "NUMBER", "pattern": "0.0000"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        },
    ]
    apply_formatting(ss, ws.id, reqs)
