"""setup_sheet.py

Configura la estructura de las hojas en Google Sheets.
Basado en las definiciones de src/sheets/structure.py.

Actualizado para:
  - No borrar hojas existentes (evita romper fórmulas #REF!).
  - No sobrescribir datos manuales (Columnas A, B, G, etc. en Ingresos).
  - Usar nombres de hojas correctos ('Ingresos' en lugar de 'test').
"""

import os

import gspread
from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client
from src.sheets.structure import (
    INCOME_GROUPS,
    INCOME_COLUMNS,
    COLUMN_FORMATS,
    IMPUESTOS_ROWS,
    HISTORIC_VARIABLES,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

FIRST_DATA_ROW = 3
MAX_MONTHLY_ROWS = 120  # ~10 años

HISTORIC_FIRST_DATA_ROW = 4  # Metadata(1) + Headers(2) + Spacer(3)?
# Wait, in structure.py VLOOKUPs use $A$4:$B. So first data row is 4.
HISTORIC_SHEET = "historic_data"
INCOME_SHEET = "Ingresos"
TAX_SHEET = "impuestos"
REM_SHEET = "REM"

# Colors (RGB 0.0 – 1.0) - Reutilizamos los del código original o similares
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def col_idx(letter: str) -> int:
    """Convierte letra de columna a índice 0-based."""
    res = 0
    for char in letter.upper():
        res = res * 26 + (ord(char) - ord("A") + 1)
    return res - 1


def get_or_create_worksheet(ss: gspread.Spreadsheet, title: str, rows=100, cols=20):
    try:
        return ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return ss.add_worksheet(title=title, rows=rows, cols=cols)


def apply_formatting(ss: gspread.Spreadsheet, sheet_id: int, requests: list):
    if requests:
        ss.batch_update({"requests": requests})


# ---------------------------------------------------------------------------
# Setup Logic
# ---------------------------------------------------------------------------


def setup_impuestos(ss: gspread.Spreadsheet):
    print(f"Configurando {TAX_SHEET}...")
    ws = get_or_create_worksheet(ss, TAX_SHEET, rows=10, cols=3)

    # Header
    ws.update(range_name="A1:C1", values=[["Impuesto", "Tasa", "Ley / Descripción"]])

    # Data
    payload = [[name, rate, ley] for name, rate, ley in IMPUESTOS_ROWS]
    ws.update(
        range_name=f"A2:C{1 + len(payload)}",
        values=payload,
        value_input_option="USER_ENTERED",
    )

    # Formatting
    reqs = []
    # Header format
    reqs.append(
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
        }
    )
    # Percent format for col B
    reqs.append(
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
        }
    )
    apply_formatting(ss, ws.id, reqs)


def setup_historic(ss: gspread.Spreadsheet):
    print(f"Configurando {HISTORIC_SHEET}...")
    ws = get_or_create_worksheet(ss, HISTORIC_SHEET, rows=2000, cols=5)

    # Row 1: Metadata
    meta = []
    for src, name, _ in HISTORIC_VARIABLES:
        meta.append(f"Source: {src}" if src else "")
    ws.update(range_name="A1:C1", values=[meta])

    # Row 2: Headers
    headers = [v[1] for v in HISTORIC_VARIABLES]
    ws.update(range_name="A2:C2", values=[headers])

    # Note: Row 3 is empty or spacer in some designs, but structure.py says $A$4.
    # We leave row 3 empty.

    reqs = []
    # Header formats
    reqs.append(
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
        }
    )
    # Date format col A
    reqs.append(
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
        }
    )
    apply_formatting(ss, ws.id, reqs)


def setup_ingresos(ss: gspread.Spreadsheet):
    print(f"Configurando {INCOME_SHEET}...")
    ws = get_or_create_worksheet(ss, INCOME_SHEET, rows=200, cols=40)

    # 1. Group Headers (Row 1)
    group_row = [""] * 40
    for start, end, label in INCOME_GROUPS:
        group_row[col_idx(start)] = label
    ws.update(range_name="A1:AN1", values=[group_row])

    # 2. Column Headers (Row 2)
    header_row = [""] * 40
    for col_let, title, *rest in INCOME_COLUMNS:
        header_row[col_idx(col_let)] = title
    ws.update(range_name="A2:AN2", values=[header_row])

    # 3. Formulas (Rows 3+)
    # IMPORTANTE: Solo escribimos en las columnas que tienen fórmula.
    # No tocamos A, B, G, I, J, K etc.

    print("  Actualizando fórmulas (sin tocar datos manuales)...")
    formula_updates = []
    for col_let, title, *rest in INCOME_COLUMNS:
        if len(rest) > 0 and rest[0]:  # Tiene fórmula
            formula_template = rest[0]
            col_payload = []
            for r in range(3, 3 + MAX_MONTHLY_ROWS):
                # {r} y {r-1} replacement
                f = formula_template.replace("{r}", str(r)).replace("{r-1}", str(r - 1))
                col_payload.append([f])

            # Preparamos el update para esta columna
            range_label = f"{col_let}3:{col_let}{3 + MAX_MONTHLY_ROWS - 1}"
            formula_updates.append({"range": range_label, "values": col_payload})

    if formula_updates:
        ws.batch_update(formula_updates, value_input_option="USER_ENTERED")

    # 4. Formatting
    reqs = []
    # Unmerge headers first to avoid conflicts
    reqs.append(
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
        }
    )
    # Freeze 2 rows
    reqs.append(
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": ws.id,
                    "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 1},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        }
    )
    # Group merges
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

    # Column formats
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


def setup_rem(ss: gspread.Spreadsheet):
    print(f"Configurando {REM_SHEET}...")
    ws = get_or_create_worksheet(ss, REM_SHEET, rows=50, cols=10)

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

    reqs = []
    # Header format
    reqs.append(
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
    )
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

    print(
        f"\n✓ Setup completo: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"
    )


if __name__ == "__main__":
    main()
