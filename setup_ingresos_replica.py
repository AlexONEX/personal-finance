"""setup_ingresos_replica.py

Replica EXACTA de la estructura del sheet "Ingresos" actual.
Crea un sheet de prueba llamado "test_estructura" para validación.

Usage:
    uv run setup_ingresos_replica.py
"""

import os
import sys
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SERVICE_ACCOUNT = "service_account.json"

TEST_SHEET_NAME = "test_estructura"
FIRST_DATA_ROW = 3
MAX_ROWS = 120

# ---------------------------------------------------------------------------
# Estructura exacta del sheet "Ingresos" actual
# ---------------------------------------------------------------------------

# Row 1: Group headers (with merged ranges)
GROUPS = [
    ("A", "A", ""),  # Fecha (sin merge)
    ("B", "F", "SUELDO"),
    ("G", "G", ""),  # SAC Bruto input (sin header en row 1)
    ("H", "H", "AGUINALDO"),
    ("I", "I", "BONOS"),
    ("J", "J", "BENEFICIOS EMPRESA"),
    ("K", "K", "TOTAL"),
    ("L", "N", "CCL"),
    ("O", "P", "CER"),
    ("Q", "X", "ANÁLISIS REAL (Sueldo y Poder Adquisitivo)"),
]

# Row 2: Column headers
COLUMNS = [
    ("A", "Fecha", None),
    ("B", "Bruto", None),
    ("C", "Jubilación", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$2,0))'),
    ("D", "PAMI", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$3,0))'),
    ("E", "Obra Social", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$4,0))'),
    ("F", "Neto", '=IF(ISBLANK(B{r}),"",B{r}-C{r}-D{r}-E{r})'),
    ("G", "", None),  # SAC Bruto (input manual, sin header)
    (
        "H",
        "SAC Neto",
        '=IF(ISBLANK(G{r}),"",G{r}-ROUND(G{r}*impuestos!$B$2,0)-ROUND(G{r}*impuestos!$B$3,0)-ROUND(G{r}*impuestos!$B$4,0))',
    ),
    ("I", "Bono Neto", None),
    ("J", "Comida", None),
    ("K", "Total Neto", '=IFERROR(IF(SUM(F{r}:J{r})=0, "", SUM(F{r}:J{r})), "")'),
    (
        "L",
        "CCL",
        '=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(A{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "")',
    ),
    ("M", "Sueldo USD", '=IFERROR(K{r}/L{r},"")'),
    ("N", "Δ % CCL MoM", '=IFERROR((L{r}-L{r-1})/L{r-1}, "-")'),
    (
        "O",
        "Sueldo Ajustado CER (Base Oct-23)",
        '=IFERROR($K$3 * (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP($A$3, historic_data!$A$4:$B, 2, TRUE)), "")',
    ),
    (
        "P",
        "Δ % CER MoM",
        '=IFERROR((VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(A{r-1}, historic_data!$A$4:$B, 2, TRUE)) - 1, "-")',
    ),
    ("Q", "Δ Sueldo MoM", '=IFERROR(F{r}/F{r-1}-1,"-")'),
    ("R", "Poder Adq. MoM", '=IFERROR((1+Q{r})/(1+P{r})-1,"-")'),
    ("S", "Sueldo Real idx", None),  # Special: primero es 1, resto es formula
    ("T", "CER idx", None),  # Special: primero es =100, resto es formula
    (
        "U",
        "CER Acum. (Total)",
        '=IFERROR((VLOOKUP($A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP($A$3, historic_data!$A$4:$B, 2, TRUE)) - 1, "")',
    ),
    (
        "V",
        "CER Anual (YTD)",
        '=IFERROR((VLOOKUP($A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(DATE(YEAR($A{r}), 1, 1), historic_data!$A$4:$B, 2, TRUE)) - 1, "")',
    ),
    ("W", "Δ % Sueldo USD MoM", '=IFERROR(($M{r}/$M{r-1})-1, "-")'),
    (
        "X",
        "Sueldo USD Anual (YTD)",
        '=IFERROR(($M{r} / IFERROR(VLOOKUP(DATE(YEAR($A{r}), 1, 1), $A$3:$M, 12, TRUE), $M{r})) - 1, "")',
    ),
]

# Colors (RGB 0-1)
C = {
    "SUELDO": {"red": 0.812, "green": 0.886, "blue": 0.953},
    "AGUINALDO": {"red": 0.851, "green": 0.918, "blue": 0.827},
    "BONOS": {"red": 1.000, "green": 0.949, "blue": 0.800},
    "BENEFICIOS EMPRESA": {"red": 0.988, "green": 0.898, "blue": 0.804},
    "TOTAL": {"red": 0.851, "green": 0.824, "blue": 0.914},
    "CCL": {"red": 0.800, "green": 0.902, "blue": 0.902},
    "CER": {"red": 0.957, "green": 0.800, "blue": 0.800},
    "ANÁLISIS REAL (Sueldo y Poder Adquisitivo)": {
        "red": 0.937,
        "green": 0.937,
        "blue": 0.937,
    },
    "_bg": {"red": 0.267, "green": 0.329, "blue": 0.416},
    "_fg": {"red": 1.000, "green": 1.000, "blue": 1.000},
}

# Number formats
_pct = {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}
_ars = {"numberFormat": {"type": "NUMBER", "pattern": "#,##0"}}
_usd = {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}}
_date = {"numberFormat": {"type": "DATE", "pattern": "mmm-yy"}}
_idx = {"numberFormat": {"type": "NUMBER", "pattern": "0.0"}}

COL_FORMATS = {
    "A": _date,
    "B": _ars,
    "C": _ars,
    "D": _ars,
    "E": _ars,
    "F": _ars,
    "G": _ars,  # SAC Bruto
    "H": _ars,
    "I": _ars,
    "J": _ars,
    "K": _ars,
    "L": _usd,
    "M": _usd,
    "N": _pct,
    "O": _ars,
    "P": _pct,
    "Q": _pct,
    "R": _pct,
    "S": _idx,
    "T": _idx,
    "U": _pct,
    "V": _pct,
    "W": _pct,
    "X": _pct,
}

COL_WIDTHS = {
    "A": 70,
    "B": 95,
    "C": 80,
    "D": 60,
    "E": 80,
    "F": 95,
    "G": 95,  # SAC Bruto
    "H": 90,
    "I": 90,
    "J": 85,
    "K": 95,
    "L": 80,
    "M": 80,
    "N": 80,
    "O": 120,
    "P": 75,
    "Q": 85,
    "R": 85,
    "S": 85,
    "T": 75,
    "U": 95,
    "V": 90,
    "W": 90,
    "X": 110,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def col_idx(letter: str) -> int:
    """A=0, B=1, ..., Z=25, AA=26, ..."""
    result = 0
    for char in letter:
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result - 1


def build_formula(template: str, row: int) -> str:
    """Replace {r} and {r-1} placeholders."""
    if not template:
        return ""
    return template.replace("{r-1}", str(row - 1)).replace("{r}", str(row))


def build_special_formula(col: str, row: int) -> str:
    """Special formulas for S (Sueldo Real idx) and T (CER idx)."""
    if row == FIRST_DATA_ROW:
        if col == "S":
            return "1"
        if col == "T":
            return "=100"
    # Rows after first
    if col == "S":
        # No formula en estructura actual (valor manual o dejado en blanco)
        return ""
    if col == "T":
        # T tiene formula solo en la primera fila (=100)
        return ""
    return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID not set in .env", file=sys.stderr)
        sys.exit(1)

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # Delete existing test sheet if present
    try:
        existing = spreadsheet.worksheet(TEST_SHEET_NAME)
        spreadsheet.del_worksheet(existing)
        print(f"✓ Deleted existing '{TEST_SHEET_NAME}'")
    except gspread.exceptions.WorksheetNotFound:
        pass

    # Create new test sheet
    n_cols = len(COLUMNS)
    ws = spreadsheet.add_worksheet(
        title=TEST_SHEET_NAME,
        rows=FIRST_DATA_ROW + MAX_ROWS,
        cols=n_cols,
    )
    print(f"✓ Created sheet '{TEST_SHEET_NAME}' ({n_cols} cols)")

    sid = ws.id

    # ─── Write content ───────────────────────────────────────────────────────

    # Row 1: Group headers
    row1 = [""] * n_cols
    for start, end, label in GROUPS:
        if label:
            row1[col_idx(start)] = label

    # Row 2: Column headers
    row2 = [header for (_, header, _) in COLUMNS]

    # Rows 3+: Formulas
    formula_rows = []
    for row in range(FIRST_DATA_ROW, FIRST_DATA_ROW + MAX_ROWS):
        row_data = []
        for col_letter, _, formula_tmpl in COLUMNS:
            if col_letter in ("S", "T"):
                row_data.append(build_special_formula(col_letter, row))
            elif formula_tmpl:
                row_data.append(build_formula(formula_tmpl, row))
            else:
                row_data.append("")
        formula_rows.append(row_data)

    # Write all at once
    last_col = chr(ord("A") + n_cols - 1)
    ws.update(f"A1:{last_col}1", [row1])
    ws.update(f"A2:{last_col}2", [row2])
    ws.update(
        f"A{FIRST_DATA_ROW}:{last_col}{FIRST_DATA_ROW + MAX_ROWS - 1}",
        formula_rows,
        value_input_option="USER_ENTERED",
    )
    print("✓ Content written")

    # ─── Formatting ─────────────────────────────────────────────────────────

    reqs = []

    # Freeze 2 rows + 1 col
    reqs.append(
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sid,
                    "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 1},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        }
    )

    # Merge cells in row 1
    for start, end, label in GROUPS:
        if label and start != end:
            reqs.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": col_idx(start),
                            "endColumnIndex": col_idx(end) + 1,
                        },
                        "mergeType": "MERGE_ALL",
                    }
                }
            )

    # Row 1: background colors + centered text
    for start, end, label in GROUPS:
        if not label:
            continue
        color = C.get(label, C["_bg"])
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": col_idx(start),
                        "endColumnIndex": col_idx(end) + 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": color,
                            "textFormat": {
                                "bold": True,
                                "fontSize": 10,
                                "foregroundColor": C["_bg"],
                            },
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
                }
            }
        )

    # Row 2: dark header
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": n_cols,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["_bg"],
                        "textFormat": {
                            "bold": True,
                            "fontSize": 9,
                            "foregroundColor": C["_fg"],
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "wrapStrategy": "WRAP",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)",
            }
        }
    )

    # Data rows: column colors by group
    for start, end, label in GROUPS:
        if not label or label not in C:
            continue
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": FIRST_DATA_ROW - 1,
                        "endRowIndex": FIRST_DATA_ROW + MAX_ROWS,
                        "startColumnIndex": col_idx(start),
                        "endColumnIndex": col_idx(end) + 1,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": C[label]}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )

    # Number formats
    for letter, fmt in COL_FORMATS.items():
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": FIRST_DATA_ROW - 1,
                        "endRowIndex": FIRST_DATA_ROW + MAX_ROWS,
                        "startColumnIndex": col_idx(letter),
                        "endColumnIndex": col_idx(letter) + 1,
                    },
                    "cell": {"userEnteredFormat": fmt},
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    # Column widths
    for letter, width in COL_WIDTHS.items():
        reqs.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sid,
                        "dimension": "COLUMNS",
                        "startIndex": col_idx(letter),
                        "endIndex": col_idx(letter) + 1,
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }
        )

    # Row heights
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sid,
                    "dimension": "ROWS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "properties": {"pixelSize": 35},
                "fields": "pixelSize",
            }
        }
    )
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sid,
                    "dimension": "ROWS",
                    "startIndex": 1,
                    "endIndex": 2,
                },
                "properties": {"pixelSize": 48},
                "fields": "pixelSize",
            }
        }
    )

    # Apply all formatting
    spreadsheet.batch_update({"requests": reqs})
    print("✓ Formatting applied")

    print(f"\n✅ Done! Check sheet '{TEST_SHEET_NAME}' in your spreadsheet:")
    print(f"   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")


if __name__ == "__main__":
    main()
