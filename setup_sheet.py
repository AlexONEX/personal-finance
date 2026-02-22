"""setup_sheet.py

Configura la estructura de las hojas en Google Sheets.
Basado en las definiciones de src/sheets/structure.py.
"""

import os

import gspread
from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.sheets.structure import (
    COLUMN_FORMATS,
    HISTORIC_VARIABLES,
    IMPUESTOS_ROWS,
    INCOME_COLUMNS,
    INCOME_GROUPS,
)

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

FIRST_DATA_ROW = 3
MAX_ROWS = 1000

HISTORIC_FIRST_DATA_ROW = 4
HISTORIC_SHEET = "historic_data"
INCOME_SHEET = "Ingresos"
TAX_SHEET = "impuestos"
REM_SHEET = "REM"
PANEL_SHEET = "Panel"
INVERSIONES_SHEET = "Inversiones"

C = {
    "SUELDO": {"red": 0.8, "green": 0.898, "blue": 1.0},
    "AGUINALDO": {"red": 0.898, "green": 1.0, "blue": 0.898},
    "BONOS": {"red": 1.0, "green": 0.898, "blue": 0.8},
    "BENEFICIOS": {"red": 1.0, "green": 1.0, "blue": 0.8},
    "TOTAL": {"red": 0.898, "green": 0.8, "blue": 1.0},
    "INFLACIÓN (CER)": {"red": 1.0, "green": 0.8, "blue": 0.8},
    "COMPARACION CON ULTIMO AUMENTO ARS": {"red": 0.949, "green": 0.949, "blue": 0.949},
    "PROYECCION REM": {"red": 0.8, "green": 1.0, "blue": 1.0},
    "DÓLAR": {"red": 0.8, "green": 0.898, "blue": 0.898},
    "VS ÚLTIMO AUMENTO USD": {"red": 0.988, "green": 0.898, "blue": 0.804},
    "_bg": {"red": 0.2, "green": 0.3, "blue": 0.4},
    "_fg": {"red": 1.0, "green": 1.0, "blue": 1.0},
}


def col_idx(letter: str) -> int:
    res = 0
    for char in letter.upper():
        res = res * 26 + (ord(char) - ord("A") + 1)
    return res - 1


def get_or_create_worksheet(ss: gspread.Spreadsheet, title: str, rows=1000, cols=60):
    try:
        return ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return ss.add_worksheet(title=title, rows=rows, cols=cols)


def apply_formatting(ss: gspread.Spreadsheet, sheet_id: int, requests: list):
    if requests:
        ss.batch_update({"requests": requests})


def setup_impuestos(ss: gspread.Spreadsheet):
    print(f"Configurando {TAX_SHEET}...")
    ws = get_or_create_worksheet(ss, TAX_SHEET, rows=10, cols=3)
    ws.update(range_name="A1:C1", values=[["Impuesto", "Tasa", "Ley / Descripción"]])
    payload = [[name, rate, ley] for name, rate, ley in IMPUESTOS_ROWS]
    ws.update(
        range_name=f"A2:C{1 + len(payload)}",
        values=payload,
        value_input_option="USER_ENTERED",
    )

    reqs = [
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["_bg"],
                        "textFormat": {"bold": True, "foregroundColor": C["_fg"]},
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


def setup_historic(ss: gspread.Spreadsheet):
    print(f"Configurando {HISTORIC_SHEET}...")
    ws = get_or_create_worksheet(ss, HISTORIC_SHEET, rows=2000, cols=5)
    meta = [f"Source: {v[0]}" if v[0] else "" for v in HISTORIC_VARIABLES]
    headers = [v[1] for v in HISTORIC_VARIABLES]
    ws.update(range_name="A1:D1", values=[meta])
    ws.update(range_name="A2:D2", values=[headers])

    reqs = [
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 2},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["_bg"],
                        "textFormat": {"bold": True, "foregroundColor": C["_fg"]},
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


def setup_rem(ss: gspread.Spreadsheet):
    print(f"Configurando {REM_SHEET}...")
    ws = get_or_create_worksheet(ss, REM_SHEET, rows=100, cols=10)

    # Row 1: Metadata
    ws.update(
        range_name="A1:B1",
        values=[["Última Actualización", ""]],
        value_input_option="USER_ENTERED",
    )

    # Row 2: Empty (spacing)
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

    reqs = [
        # Row 1: Metadata format
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["_bg"],
                        "textFormat": {"bold": True, "foregroundColor": C["_fg"]},
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
                        "backgroundColor": C["_bg"],
                        "textFormat": {"bold": True, "foregroundColor": C["_fg"]},
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        },
    ]
    apply_formatting(ss, ws.id, reqs)


def setup_ingresos(ss: gspread.Spreadsheet):
    print(f"Configurando {INCOME_SHEET}...")
    ws = get_or_create_worksheet(ss, INCOME_SHEET, rows=MAX_ROWS, cols=60)

    group_row = [""] * 60
    for start, end, label in INCOME_GROUPS:
        group_row[col_idx(start)] = label
    ws.update(range_name="A1:BH1", values=[group_row])

    header_row = [""] * 60
    for col_let, title, *rest in INCOME_COLUMNS:
        header_row[col_idx(col_let)] = title
    ws.update(range_name="A2:BH2", values=[header_row])

    formula_updates = []
    for col_let, title, *rest in INCOME_COLUMNS:
        if len(rest) > 0 and rest[0]:
            formula_template = rest[0]
            col_payload = [
                [formula_template.replace("{r}", str(r)).replace("{r-1}", str(r - 1))]
                for r in range(3, MAX_ROWS + 1)
            ]
            formula_updates.append(
                {"range": f"{col_let}3:{col_let}{MAX_ROWS}", "values": col_payload}
            )

    if formula_updates:
        ws.batch_update(formula_updates, value_input_option="USER_ENTERED")

    reqs = [
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
            color = C.get(label, C["_bg"])
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
            # Create a lighter version for data background
            light_color = {
                "red": min(1.0, color["red"] + (1 - color["red"]) * 0.85),
                "green": min(1.0, color["green"] + (1 - color["green"]) * 0.85),
                "blue": min(1.0, color["blue"] + (1 - color["blue"]) * 0.85),
            }
            reqs.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": 2,
                            "endRowIndex": MAX_ROWS,
                            "startColumnIndex": col_idx(start),
                            "endColumnIndex": col_idx(end) + 1,
                        },
                        "cell": {"userEnteredFormat": {"backgroundColor": light_color}},
                        "fields": "userEnteredFormat.backgroundColor",
                    }
                }
            )

    for col_let, fmt_config in COLUMN_FORMATS.items():
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
                        "startColumnIndex": col_idx(col_let),
                        "endColumnIndex": col_idx(col_let) + 1,
                    },
                    "cell": {"userEnteredFormat": {"numberFormat": gs_format}},
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    apply_formatting(ss, ws.id, reqs)


def setup_inversiones(ss: gspread.Spreadsheet):
    """
    Aplica formato a la sheet Inversiones.
    La sheet ya debe tener datos y headers (creados por upload_to_inversiones.py).
    """
    print(f"Configurando {INVERSIONES_SHEET}...")

    try:
        ws = ss.worksheet(INVERSIONES_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        print(f"  ⚠️  Sheet {INVERSIONES_SHEET} no existe. Ejecuta upload_to_inversiones.py primero.")
        return

    # Grupos de columnas para formato (row 1 groups + data colors)
    inversiones_groups = [
        ("A", "I", "INPUTS"),              # Datos raw de IEB
        ("J", "K", "GANANCIAS"),           # Ganancias calculadas
        ("L", "R", "RENDIMIENTO ARS"),     # Rendimiento ARS vs CER
        ("S", "Y", "RENDIMIENTO USD"),     # Rendimiento USD vs SPY
        ("Z", "AC", "CCL"),                # CCL y conversión
    ]

    # Colores para los grupos
    group_colors = {
        "INPUTS": {"red": 0.8, "green": 0.898, "blue": 1.0},
        "GANANCIAS": {"red": 1.0, "green": 1.0, "blue": 0.8},
        "RENDIMIENTO ARS": {"red": 1.0, "green": 0.8, "blue": 0.8},
        "RENDIMIENTO USD": {"red": 0.898, "green": 1.0, "blue": 0.898},
        "CCL": {"red": 0.988, "green": 0.898, "blue": 0.804},
    }

    # Formatos por columna
    column_formats = {
        "A": {"type": "DATE", "pattern": "dd/mm/yyyy"},
        # INPUTS - ARS
        "B": {"type": "NUMBER", "pattern": "#,##0.00"},
        "C": {"type": "NUMBER", "pattern": "#,##0.00"},
        "D": {"type": "NUMBER", "pattern": "#,##0.00"},
        "E": {"type": "NUMBER", "pattern": "#,##0.00"},
        # INPUTS - USD
        "F": {"type": "NUMBER", "pattern": "#,##0.00"},
        "G": {"type": "NUMBER", "pattern": "#,##0.00"},
        "H": {"type": "NUMBER", "pattern": "#,##0.00"},
        "I": {"type": "NUMBER", "pattern": "#,##0.00"},
        # GANANCIAS
        "J": {"type": "NUMBER", "pattern": "#,##0.00"},
        "K": {"type": "NUMBER", "pattern": "#,##0.00"},
        # RENDIMIENTO ARS
        "L": {"type": "PERCENT", "pattern": "0.00%"},
        "M": {"type": "PERCENT", "pattern": "0.00%"},
        "N": {"type": "NUMBER", "pattern": "#,##0.00"},
        "O": {"type": "NUMBER", "pattern": "#,##0.00"},
        "P": {"type": "PERCENT", "pattern": "0.00%"},
        "Q": {"type": "PERCENT", "pattern": "0.00%"},
        "R": {"type": "PERCENT", "pattern": "0.00%"},
        # RENDIMIENTO USD
        "S": {"type": "PERCENT", "pattern": "0.00%"},
        "T": {"type": "PERCENT", "pattern": "0.00%"},
        "U": {"type": "NUMBER", "pattern": "#,##0.00"},
        "V": {"type": "NUMBER", "pattern": "#,##0.00"},
        "W": {"type": "PERCENT", "pattern": "0.00%"},
        "X": {"type": "PERCENT", "pattern": "0.00%"},
        "Y": {"type": "PERCENT", "pattern": "0.00%"},
        # CCL
        "Z": {"type": "NUMBER", "pattern": "#,##0.00"},
        "AA": {"type": "NUMBER", "pattern": "#,##0.00"},
        "AB": {"type": "PERCENT", "pattern": "0.00%"},
        "AC": {"type": "NUMBER", "pattern": "#,##0.00"},
    }

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
        # Freeze header rows 1-2 only (no frozen columns to allow merging)
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
                        "backgroundColor": C["_bg"],
                        "textFormat": {"bold": True, "foregroundColor": C["_fg"], "fontSize": 11},
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
                        "backgroundColor": C["_bg"],
                        "textFormat": {"bold": True, "foregroundColor": C["_fg"], "fontSize": 9},
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
        color = group_colors.get(label, C["_bg"])
        # Create lighter version for data rows
        light_color = {
            "red": min(1.0, color["red"] + (1 - color["red"]) * 0.85),
            "green": min(1.0, color["green"] + (1 - color["green"]) * 0.85),
            "blue": min(1.0, color["blue"] + (1 - color["blue"]) * 0.85),
        }
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 2,
                        "endRowIndex": 1002,  # 1000 rows of data
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
                        "endRowIndex": 1002,  # 1000 rows of data
                        "startColumnIndex": col_idx(col_let),
                        "endColumnIndex": col_idx(col_let) + 1,
                    },
                    "cell": {"userEnteredFormat": {"numberFormat": gs_format}},
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    apply_formatting(ss, ws.id, reqs)
    print(f"  ✅ Formato aplicado a {INVERSIONES_SHEET}")


def main():
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID no definido en .env")
        return
    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)
    setup_impuestos(ss)
    setup_historic(ss)
    setup_rem(ss)
    setup_ingresos(ss)
    setup_inversiones(ss)
    print(
        f"\nSetup completo: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"
    )


if __name__ == "__main__":
    main()
