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

C = {
    "SUELDO": {"red": 0.8, "green": 0.9, "blue": 1.0},
    "AGUINALDO": {"red": 0.9, "green": 1.0, "blue": 0.9},
    "BONOS": {"red": 1.0, "green": 0.9, "blue": 0.8},
    "BENEFICIOS": {"red": 1.0, "green": 1.0, "blue": 0.8},
    "TOTAL": {"red": 0.9, "green": 0.8, "blue": 1.0},
    "INFLACIÓN (CER)": {"red": 1.0, "green": 0.8, "blue": 0.8},
    "VS ÚLTIMO AUMENTO": {"red": 0.95, "green": 0.95, "blue": 0.95},
    "ANÁLISIS TOTAL": {"red": 0.9, "green": 0.9, "blue": 0.9},
    "PROYECCIONES REM": {"red": 0.8, "green": 1.0, "blue": 1.0},
    "DÓLARES (CCL)": {"red": 0.8, "green": 0.9, "blue": 0.9},
    "VS ÚLTIMO AUMENTO USD": {"red": 0.85, "green": 0.85, "blue": 0.85},
    "_bg": {"red": 0.2, "green": 0.3, "blue": 0.4},
    "_fg": {"red": 1.0, "green": 1.0, "blue": 1.0},
}


def col_idx(letter: str) -> int:
    res = 0
    for char in letter.upper():
        res = res * 26 + (ord(char) - ord("A") + 1)
    return res - 1


def get_or_create_worksheet(ss: gspread.Spreadsheet, title: str, rows=1000, cols=40):
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
    ws.update(range_name="A1:C1", values=[meta])
    ws.update(range_name="A2:C2", values=[headers])

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
    ws.update(range_name="A3", values=[headers], value_input_option="USER_ENTERED")
    reqs = [
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
        }
    ]
    apply_formatting(ss, ws.id, reqs)


def setup_ingresos(ss: gspread.Spreadsheet):
    print(f"Configurando {INCOME_SHEET}...")
    ws = get_or_create_worksheet(ss, INCOME_SHEET, rows=MAX_ROWS, cols=40)

    group_row = [""] * 40
    for start, end, label in INCOME_GROUPS:
        group_row[col_idx(start)] = label
    ws.update(range_name="A1:AN1", values=[group_row])

    header_row = [""] * 40
    for col_let, title, *rest in INCOME_COLUMNS:
        header_row[col_idx(col_let)] = title
    ws.update(range_name="A2:AN2", values=[header_row])

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
                    "endColumnIndex": 40,
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
            reqs.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": col_idx(start),
                            "endColumnIndex": col_idx(end) + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": color,
                                "textFormat": {"bold": True},
                                "horizontalAlignment": "CENTER",
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
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


def setup_panel(ss: gspread.Spreadsheet):
    print(f"Configurando {PANEL_SHEET}...")
    ws = get_or_create_worksheet(ss, PANEL_SHEET, rows=20, cols=10)
    ws.clear()
    content = [
        ["PANEL DE CONTROL"],
        [""],
        ["Instrucciones para Sincronización Interna (JavaScript):"],
        ["1. Arriba en el menú de Google Sheets, ve a 'Extensiones' -> 'Apps Script'"],
        ["2. Copia el contenido del archivo 'apps_script.js' del repositorio"],
        ["3. Pégalo en el editor de Google y guarda (Ctrl+S)"],
        ["4. Recarga esta página"],
        ["5. Aparecerá un menú arriba llamado 'Tracker' para actualizar CER y CCL"],
        [""],
        ["Nota: El REM (Proyecciones) sigue requiriendo el script de Python."],
        [""],
        ["Links útiles:"],
        ["- BCRA API (CER): https://api.bcra.gob.ar"],
        ["- Ambito (CCL): https://mercados.ambito.com"],
    ]
    ws.update(range_name="A1", values=content)
    reqs = [
        {
            "repeatCell": {
                "range": {"sheetId": ws.id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True, "fontSize": 14},
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(textFormat,horizontalAlignment)",
            }
        }
    ]
    apply_formatting(ss, ws.id, reqs)


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
    setup_panel(ss)
    print(
        f"\nSetup completo: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"
    )


if __name__ == "__main__":
    main()
