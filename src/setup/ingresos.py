"""Setup de la hoja principal de ingresos."""

import gspread

from src.config import SHEET_LIMITS, SHEETS, get_color, lighten_color
from src.setup.utils import apply_formatting, col_idx, get_or_create_worksheet
from src.sheets.structure import COLUMN_FORMATS, INCOME_COLUMNS, INCOME_GROUPS


def setup_ingresos(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja principal de ingresos con 38 columnas.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["INGRESOS"]
    max_rows = SHEET_LIMITS["max_rows"]

    print(f"Configurando {sheet_name}...")
    ws = get_or_create_worksheet(ss, sheet_name, rows=max_rows, cols=60)

    # Row 1: Grupos de columnas
    group_row = [""] * 60
    for start, end, label in INCOME_GROUPS:
        group_row[col_idx(start)] = label
    ws.update(range_name="A1:BH1", values=[group_row])

    # Row 2: Headers de columnas
    header_row = [""] * 60
    for col_let, title, *rest in INCOME_COLUMNS:
        header_row[col_idx(col_let)] = title
    ws.update(range_name="A2:BH2", values=[header_row])

    # Batch update de fórmulas
    formula_updates = []
    for col_let, title, *rest in INCOME_COLUMNS:
        if len(rest) > 0 and rest[0]:
            formula_template = rest[0]
            # Si la fórmula es ARRAYFORMULA, solo va en la fila 3
            if "ARRAYFORMULA" in formula_template:
                formula_updates.append(
                    {"range": f"{col_let}3:{col_let}3", "values": [[formula_template]]}
                )
            else:
                # Fórmulas normales se repiten en cada fila
                col_payload = [
                    [
                        formula_template.replace("{r}", str(r)).replace(
                            "{r-1}", str(r - 1)
                        )
                    ]
                    for r in range(3, max_rows + 1)
                ]
                formula_updates.append(
                    {"range": f"{col_let}3:{col_let}{max_rows}", "values": col_payload}
                )

    if formula_updates:
        ws.batch_update(formula_updates, value_input_option="USER_ENTERED")

    # Formateo
    reqs = [
        # Unmerge any existing merges
        {
            "unmergeCells": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 0,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 60,
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

    # Merge cells y aplicar colores
    for start, end, label in INCOME_GROUPS:
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
            color = get_color(label)
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
    for col_let, fmt_config in COLUMN_FORMATS.items():
        # Skip columns A and B (no format override)
        if col_let in ["A", "B"]:
            continue

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
