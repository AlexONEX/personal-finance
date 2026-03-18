"""Setup de la hoja de inversiones."""

import gspread

from src.config import (
    COLORS,
    INVERSIONES_COLORS,
    INVERSIONES_COLUMN_FORMATS,
    INVERSIONES_GROUPS,
    SHEETS,
    lighten_color,
)
from src.setup.utils import apply_formatting, col_idx


def setup_inversiones(ss: gspread.Spreadsheet) -> None:
    """Aplica formato a la sheet Inversiones.

    La sheet ya debe tener datos y headers (creados por upload_to_inversiones.py).

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["INVERSIONES"]
    print(f"Configurando {sheet_name}...")

    try:
        ws = ss.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(
            f"  ⚠️  Sheet {sheet_name} no existe. Ejecuta upload_to_inversiones.py primero."
        )
        return

    # Grupos y formatos desde configuración centralizada
    inversiones_groups = INVERSIONES_GROUPS
    column_formats = INVERSIONES_COLUMN_FORMATS

    header_bg = COLORS["header_bg"]
    header_fg = COLORS["header_fg"]

    reqs = [
        # Unmerge any existing merges first
        {
            "unmergeCells": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 0,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 30,
                }
            }
        },
        # Freeze header rows 1-2 only
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": ws.id,
                    "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 0},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        },
        # Row 1: Group titles background
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": header_bg,
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": header_fg,
                            "fontSize": 11,
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        },
        # Row 2: Column headers background
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 1, "endRowIndex": 2},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": header_bg,
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": header_fg,
                            "fontSize": 9,
                        },
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        },
    ]

    # Merge cells for group titles in row 1
    for start, end, label in inversiones_groups:
        if start != end:
            reqs.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": col_idx(start),
                            "endColumnIndex": col_idx(end) + 1,
                        },
                        "mergeType": "MERGE_ALL",
                    }
                }
            )

    # Apply group colors to data rows (row 3+) - 1000 rows
    for start, end, label in inversiones_groups:
        color = INVERSIONES_COLORS.get(label, header_bg)
        light_color = lighten_color(color)
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": 1002,
                        "startColumnIndex": col_idx(start),
                        "endColumnIndex": col_idx(end) + 1,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": light_color}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )

    # Apply number formats to data rows (row 3+) - 1000 rows
    for col_let, fmt_config in column_formats.items():
        gs_format = {}
        if fmt_config["type"] == "DATE":
            gs_format = {"type": "DATE", "pattern": fmt_config["pattern"]}
        elif fmt_config["type"] == "PERCENT":
            gs_format = {"type": "PERCENT", "pattern": fmt_config["pattern"]}
        elif fmt_config["type"] == "NUMBER":
            gs_format = {"type": "NUMBER", "pattern": fmt_config["pattern"]}

        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": 1002,
                        "startColumnIndex": col_idx(col_let),
                        "endColumnIndex": col_idx(col_let) + 1,
                    },
                    "cell": {"userEnteredFormat": {"numberFormat": gs_format}},
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    apply_formatting(ss, ws.id, reqs)
    print(f"Formato aplicado a {sheet_name}")
