"""Setup de la hoja Análisis USD - Sueldo en dólares nominal y real."""

import gspread

from src.config import SHEET_LIMITS, SHEETS, get_color, lighten_color
from src.setup.utils import apply_formatting, col_idx, get_or_create_worksheet
from src.sheets.structure import (
    ANALISIS_USD_COLUMNS,
    ANALISIS_USD_FORMATS,
    ANALISIS_USD_GROUPS,
)


def setup_analisis_usd(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja de Análisis USD.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["ANALISIS_USD"]
    max_rows = SHEET_LIMITS["max_rows"]

    print(f"Configurando {sheet_name}...")
    ws = get_or_create_worksheet(ss, sheet_name, rows=max_rows, cols=20)

    # Row 1: Grupos de columnas
    group_row = [""] * 20
    for start, end, label in ANALISIS_USD_GROUPS:
        group_row[col_idx(start)] = label
    ws.update(range_name="A1:T1", values=[group_row])

    # Row 2: Headers de columnas
    header_row = [""] * 20
    for col_let, title, *rest in ANALISIS_USD_COLUMNS:
        header_row[col_idx(col_let)] = title
    ws.update(range_name="A2:T2", values=[header_row])

    # Batch update de fórmulas
    formula_updates = []
    for col_let, title, *rest in ANALISIS_USD_COLUMNS:
        if len(rest) > 0 and rest[0]:
            formula_template = rest[0]
            col_payload = [
                [formula_template.replace("{r}", str(r)).replace("{r-1}", str(r - 1))]
                for r in range(3, max_rows + 1)
            ]
            formula_updates.append(
                {"range": f"{col_let}3:{col_let}{max_rows}", "values": col_payload}
            )

    if formula_updates:
        ws.batch_update(formula_updates, value_input_option="USER_ENTERED")

    # Formateo
    reqs = [
        # Unmerge all cells first
        {
            "unmergeCells": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 0,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 20,
                }
            }
        },
        # Freeze header rows and first column
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": ws.id,
                    "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 1},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        },
    ]

    # Merge cells y aplicar colores para grupos
    for start, end, label in ANALISIS_USD_GROUPS:
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

        if label:
            color = get_color(label, default_to_header=True)
            # Header format (Rows 1-2)
            reqs.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": 0,
                            "endRowIndex": 2,
                            "startColumnIndex": col_idx(start),
                            "endColumnIndex": col_idx(end) + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": color,
                                "textFormat": {"bold": True},
                                "horizontalAlignment": "CENTER",
                                "verticalAlignment": "MIDDLE",
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
                    }
                }
            )

            # Data background (Rows 3-MAX_ROWS)
            light_color = lighten_color(color)
            reqs.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": 2,
                            "endRowIndex": max_rows,
                            "startColumnIndex": col_idx(start),
                            "endColumnIndex": col_idx(end) + 1,
                        },
                        "cell": {"userEnteredFormat": {"backgroundColor": light_color}},
                        "fields": "userEnteredFormat.backgroundColor",
                    }
                }
            )

    # Formatos de número
    for col_let, fmt_config in ANALISIS_USD_FORMATS.items():
        gs_format = {}
        if fmt_config["type"] == "DATE":
            gs_format = {"type": "DATE", "pattern": fmt_config["pattern"]}
        elif fmt_config["type"] == "PERCENT":
            gs_format = {"type": "PERCENT", "pattern": fmt_config["pattern"]}
        elif fmt_config["type"] in ["CURRENCY", "NUMBER"]:
            gs_format = {"type": "NUMBER", "pattern": fmt_config["pattern"]}

        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": max_rows,
                        "startColumnIndex": col_idx(col_let),
                        "endColumnIndex": col_idx(col_let) + 1,
                    },
                    "cell": {"userEnteredFormat": {"numberFormat": gs_format}},
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    apply_formatting(ss, ws.id, reqs)
