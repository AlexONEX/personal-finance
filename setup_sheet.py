"""setup_sheet.py

Creates three sheet tabs inside an existing Google Spreadsheet:

  • "historic_data" — raw daily values (CER, CCL, …)
                      row 1 = machine-readable metadata (BCRA var ID or source)
                      row 2 = human-readable column names
                      row 3+ = data, populated by the fetch script

  • "market_data"   — monthly end-of-month aggregates, populated by script
                      Δ columns (MoM, 6m, 12m) are formulas that auto-calculate
                      from the raw values written by the script

  • "test"          — monthly income tracking; CER + CCL pulled from
                      market_data via VLOOKUP on Fecha

Run once to initialise, or re-run to reset all three sheets.

Usage:
    uv run setup_sheet.py
"""

import os
import sys

import gspread
from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

# Standard sheets: row 1 = group header, row 2 = col header, row 3+ = data
FIRST_DATA_ROW = 3
MAX_MONTHLY_ROWS = 120  # ~10 years of monthly data

# historic_data: row 1 = metadata, row 2 = col names, row 3+ = daily data
HISTORIC_FIRST_DATA_ROW = 3
HISTORIC_MAX_ROWS = 2000  # covers ~7 years of daily data

HISTORIC_SHEET = "historic_data"
MARKET_SHEET = "market_data"
INCOME_SHEET = "test"
TAX_SHEET = "impuestos"

# ---------------------------------------------------------------------------
# Colors  (RGB 0.0 – 1.0)
# ---------------------------------------------------------------------------
C = {
    "SUELDO": {"red": 0.812, "green": 0.886, "blue": 0.953},
    "AGUINALDO": {"red": 0.851, "green": 0.918, "blue": 0.827},
    "BONO PRODUCTIVIDAD": {"red": 1.000, "green": 0.949, "blue": 0.800},
    "TARJETA EMPRESA": {"red": 0.988, "green": 0.898, "blue": 0.804},
    "TOTAL": {"red": 0.851, "green": 0.824, "blue": 0.914},
    "CCL": {"red": 0.800, "green": 0.902, "blue": 0.902},
    "CER": {"red": 0.957, "green": 0.800, "blue": 0.800},
    "ANÁLISIS REAL": {"red": 0.937, "green": 0.937, "blue": 0.937},
    "_bg": {"red": 0.267, "green": 0.329, "blue": 0.416},
    "_fg": {"red": 1.000, "green": 1.000, "blue": 1.000},
    "_meta_bg": {
        "red": 0.204,
        "green": 0.224,
        "blue": 0.255,
    },  # darker for metadata row
}

# ---------------------------------------------------------------------------
# historic_data definition
#
# Each variable:
#   source_id  — BCRA variable ID (int) if from BCRA API, or string label
#                if from another source. Shown in row 1 (machine-readable).
#   name       — human-readable column name shown in row 2
#   color_key  — key into C dict for column colour
#
# The populate script reads row 1 to decide how to fetch each column:
#   int  → GET /estadisticas/v4.0/Monetarias/{id}  (BCRA API)
#   str  → custom fetcher identified by the label
# ---------------------------------------------------------------------------
HISTORIC_VARIABLES = [
    # (source_id,       name,   color_key)
    (None, "Fecha", None),
    (30, "CER", "CER"),  # BCRA var 30 — CER diario
    ("IOL/dolarapi", "CCL", "CCL"),  # Contado con liquidación
]

# ---------------------------------------------------------------------------
# market_data definition
#
# End-of-month values written by script; Δ columns are Sheets formulas.
# Col indices (1-based VLOOKUP) exposed as comments for cross-sheet refs:
#   B=CER(2)  C=ΔCER MoM(3)  D=ΔCER 6m(4)  E=ΔCER 12m(5)  F=CCL(6)  G=ΔCCL MoM(7)
# ---------------------------------------------------------------------------
MARKET_COLUMNS = [
    ("A", "Fecha", None, None),
    ("B", "CER", "CER", None),
    ("C", "Δ MoM", "CER", '=IFERROR(B{r}/B{r-1}-1,"")'),
    ("D", "Δ 6m", "CER", '=IFERROR(B{r}/OFFSET(B{r},-6,0)-1,"")'),
    ("E", "Δ 12m", "CER", '=IFERROR(B{r}/OFFSET(B{r},-12,0)-1,"")'),
    ("F", "CCL", "CCL", None),
    ("G", "Δ CCL MoM", "CCL", '=IFERROR(F{r}/F{r-1}-1,"")'),
]

MARKET_GROUPS = [
    ("A", "A", ""),
    ("B", "E", "CER"),
    ("F", "G", "CCL"),
]

# ---------------------------------------------------------------------------
# test (income) definition
#
# CCL → VLOOKUP col 6 in market_data
# CER → VLOOKUP col 2 in market_data
# ΔCER MoM → VLOOKUP col 3 in market_data
# ---------------------------------------------------------------------------
_MD = "market_data!$A:$G"

INCOME_COLUMNS = [
    # Deductions auto-calculated from impuestos sheet:
    #   impuestos!$B$2 = Jubilación rate  (row 2)
    #   impuestos!$B$3 = PAMI rate        (row 3)
    #   impuestos!$B$4 = Obra Social rate (row 4)
    #
    # C/D/E = total deductions from sueldo + SAC combined (informational tax view)
    # F     = sueldo neto = B minus sueldo-only deductions (does NOT use C/D/E)
    # H     = SAC neto   = G minus SAC-only deductions
    ("A", "Fecha", None, None),
    ("B", "Bruto", "SUELDO", None),
    (
        "C",
        "Jubilación",
        "SUELDO",
        '=IF(ISBLANK(B{r}),"",ROUND((B{r}+IF(ISBLANK(G{r}),0,G{r}))*impuestos!$B$2,0))',
    ),
    (
        "D",
        "PAMI",
        "SUELDO",
        '=IF(ISBLANK(B{r}),"",ROUND((B{r}+IF(ISBLANK(G{r}),0,G{r}))*impuestos!$B$3,0))',
    ),
    (
        "E",
        "Obra Social",
        "SUELDO",
        '=IF(ISBLANK(B{r}),"",ROUND((B{r}+IF(ISBLANK(G{r}),0,G{r}))*impuestos!$B$4,0))',
    ),
    (
        "F",
        "Neto",
        "SUELDO",
        '=IF(ISBLANK(B{r}),"",B{r}'
        "-ROUND(B{r}*impuestos!$B$2,0)"
        "-ROUND(B{r}*impuestos!$B$3,0)"
        "-ROUND(B{r}*impuestos!$B$4,0))",
    ),
    ("G", "SAC Bruto", "AGUINALDO", None),
    (
        "H",
        "SAC Neto",
        "AGUINALDO",
        '=IF(ISBLANK(G{r}),"",G{r}'
        "-ROUND(G{r}*impuestos!$B$2,0)"
        "-ROUND(G{r}*impuestos!$B$3,0)"
        "-ROUND(G{r}*impuestos!$B$4,0))",
    ),
    ("I", "Bono Neto", "BONO PRODUCTIVIDAD", None),
    ("J", "Comida", "TARJETA EMPRESA", None),
    ("K", "Viajes", "TARJETA EMPRESA", None),
    (
        "L",
        "Total Neto",
        "TOTAL",
        '=IF(ISBLANK(F{r}),"",'
        "F{r}"
        "+IF(ISBLANK(H{r}),0,H{r})"
        "+IF(ISBLANK(I{r}),0,I{r})"
        "+IF(ISBLANK(J{r}),0,J{r})"
        "+IF(ISBLANK(K{r}),0,K{r}))",
    ),
    ("M", "CCL", "CCL", f'=IFERROR(VLOOKUP(A{{r}},{_MD},6,FALSE),"")'),
    ("N", "Sueldo USD", "CCL", '=IFERROR(ROUND(F{r}/M{r},2),"")'),
    ("O", "Δ CCL MoM", "CCL", '=IFERROR(M{r}/M{r-1}-1,"")'),
    ("P", "Δ CER MoM", "ANÁLISIS REAL", f'=IFERROR(VLOOKUP(A{{r}},{_MD},3,FALSE),"")'),
    ("Q", "Δ Sueldo MoM", "ANÁLISIS REAL", '=IFERROR(F{r}/F{r-1}-1,"")'),
    ("R", "Sueldo vs CER", "ANÁLISIS REAL", '=IFERROR((1+Q{r})/(1+P{r})-1,"")'),
    ("S", "Sueldo Real idx", "ANÁLISIS REAL", None),  # special: index=100
]

INCOME_GROUPS = [
    ("A", "A", ""),
    ("B", "F", "SUELDO"),
    ("G", "H", "AGUINALDO"),
    ("I", "I", "BONO PRODUCTIVIDAD"),
    ("J", "K", "TARJETA EMPRESA"),
    ("L", "L", "TOTAL"),
    ("M", "O", "CCL"),
    ("P", "S", "ANÁLISIS REAL"),
]

# ---------------------------------------------------------------------------
# Number format presets
# ---------------------------------------------------------------------------
_pct = {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}
_ars = {"numberFormat": {"type": "NUMBER", "pattern": "#,##0"}}
_usd = {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}}
_cer4 = {
    "numberFormat": {"type": "NUMBER", "pattern": "#,##0.0000"}
}  # CER has 4 decimals
_date = {"numberFormat": {"type": "DATE", "pattern": "mmm-yy"}}
_dated = {"numberFormat": {"type": "DATE", "pattern": "dd/mm/yyyy"}}  # daily dates
_idx = {"numberFormat": {"type": "NUMBER", "pattern": "0.0"}}

MARKET_COL_FORMATS = {
    "A": _date,
    "B": _cer4,
    "C": _pct,
    "D": _pct,
    "E": _pct,
    "F": _usd,
    "G": _pct,
}
MARKET_COL_WIDTHS = {
    "A": 70,
    "B": 100,
    "C": 75,
    "D": 75,
    "E": 80,
    "F": 90,
    "G": 80,
}

INCOME_COL_FORMATS = {
    "A": _date,
    "B": _ars,
    "C": _ars,
    "D": _ars,
    "E": _ars,
    "F": _ars,
    "G": _ars,
    "H": _ars,
    "I": _ars,
    "J": _ars,
    "K": _ars,
    "L": _ars,
    "M": _usd,
    "N": _usd,
    "O": _pct,
    "P": _pct,
    "Q": _pct,
    "R": _pct,
    "S": _idx,
}
INCOME_COL_WIDTHS = {
    "A": 70,
    "B": 95,
    "C": 80,
    "D": 60,
    "E": 80,
    "F": 95,
    "G": 95,
    "H": 90,
    "I": 90,
    "J": 85,
    "K": 75,
    "L": 95,
    "M": 80,
    "N": 80,
    "O": 80,
    "P": 75,
    "Q": 85,
    "R": 85,
    "S": 85,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def col_idx(letter: str) -> int:
    return ord(letter.upper()) - ord("A")


def build_formula(template: str, row: int, first_data_row: int) -> str:
    if not template:
        return ""
    # Replace {r-1} BEFORE {r} to avoid partial substitution
    return (
        template.replace("{FD}", str(first_data_row))
        .replace("{r-1}", str(row - 1))
        .replace("{r}", str(row))
    )


def build_idx_formula(col: str, row: int, first_data_row: int) -> str:
    fd = first_data_row
    if row == fd:
        return "=100"
    if col == "S":
        # Sueldo Real idx = (F_current/F_base) / (CER_current/CER_base) * 100
        # CER fetched from market_data col 2 (no raw CER column in test sheet)
        return (
            f"=IFERROR("
            f"(F{row}/F${fd})"
            f"/(VLOOKUP(A{row},market_data!$A:$G,2,FALSE)"
            f"/VLOOKUP(A${fd},market_data!$A:$G,2,FALSE))"
            f'*100,"")'
        )
    return ""


def _recreate_worksheet(
    spreadsheet: gspread.Spreadsheet,
    name: str,
    n_cols: int,
    n_rows: int,
) -> gspread.Worksheet:
    try:
        spreadsheet.del_worksheet(spreadsheet.worksheet(name))
        print(f"  Deleted existing: {name!r}")
    except gspread.exceptions.WorksheetNotFound:
        pass
    ws = spreadsheet.add_worksheet(title=name, rows=n_rows, cols=n_cols + 2)
    print(f"  Created: {name!r}")
    return ws


# ---------------------------------------------------------------------------
# historic_data sheet setup
# ---------------------------------------------------------------------------


def _setup_historic(spreadsheet: gspread.Spreadsheet) -> list[dict]:
    n_vars = len(HISTORIC_VARIABLES)
    ws = _recreate_worksheet(
        spreadsheet,
        HISTORIC_SHEET,
        n_cols=n_vars,
        n_rows=HISTORIC_FIRST_DATA_ROW + HISTORIC_MAX_ROWS,
    )
    sid = ws.id

    # Row 1: metadata (BCRA variable ID or source label)
    meta_row = []
    for source_id, _, _ in HISTORIC_VARIABLES:
        if source_id is None:
            meta_row.append("")
        elif isinstance(source_id, int):
            meta_row.append(f"BCRA var: {source_id}")
        else:
            meta_row.append(str(source_id))

    # Row 2: column names
    name_row = [name for (_, name, _) in HISTORIC_VARIABLES]

    ws.update("A1:C1", [meta_row])
    ws.update("A2:C2", [name_row])

    # Format requests
    reqs: list[dict] = []

    # Freeze 2 rows + col A
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

    # Row 1 (metadata): dark bg, monospace-ish, centered
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": n_vars,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["_meta_bg"],
                        "textFormat": {
                            "bold": True,
                            "fontSize": 9,
                            "foregroundColor": {"red": 0.6, "green": 0.9, "blue": 0.6},
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        }
    )

    # Row 2 (column names): standard dark header
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": n_vars,
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
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        }
    )

    # Colour data columns by variable type
    fd = HISTORIC_FIRST_DATA_ROW
    last_row = fd + HISTORIC_MAX_ROWS
    for i, (_, _, color_key) in enumerate(HISTORIC_VARIABLES):
        if color_key and color_key in C:
            reqs.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sid,
                            "startRowIndex": fd - 1,
                            "endRowIndex": last_row,
                            "startColumnIndex": i,
                            "endColumnIndex": i + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {"backgroundColor": C[color_key]}
                        },
                        "fields": "userEnteredFormat.backgroundColor",
                    }
                }
            )

    # Number formats per column
    historic_col_formats = {"A": _dated, "B": _cer4, "C": _usd}
    for letter, fmt in historic_col_formats.items():
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": fd - 1,
                        "endRowIndex": last_row,
                        "startColumnIndex": col_idx(letter),
                        "endColumnIndex": col_idx(letter) + 1,
                    },
                    "cell": {"userEnteredFormat": fmt},
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    # Column widths
    for letter, width in {"A": 85, "B": 100, "C": 90}.items():
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
    for start_idx, end_idx, height in [(0, 1, 32), (1, 2, 32)]:
        reqs.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sid,
                        "dimension": "ROWS",
                        "startIndex": start_idx,
                        "endIndex": end_idx,
                    },
                    "properties": {"pixelSize": height},
                    "fields": "pixelSize",
                }
            }
        )

    return reqs


# ---------------------------------------------------------------------------
# Standard sheet setup (market_data and test)
# ---------------------------------------------------------------------------


def _build_formula_rows(
    columns: list[tuple],
    first_data_row: int,
    max_rows: int,
    idx_cols: set[str] | None = None,
) -> list[list[str]]:
    idx_cols = idx_cols or set()
    rows = []
    for row in range(first_data_row, first_data_row + max_rows):
        row_data = []
        for letter, _, _, formula_tmpl in columns:
            if letter in idx_cols:
                row_data.append(build_idx_formula(letter, row, first_data_row))
            elif formula_tmpl:
                row_data.append(build_formula(formula_tmpl, row, first_data_row))
            else:
                row_data.append("")
        rows.append(row_data)
    return rows


def _write_standard_content(
    ws: gspread.Worksheet,
    columns: list[tuple],
    groups: list[tuple],
    first_data_row: int,
    max_rows: int,
    idx_cols: set[str] | None = None,
) -> None:
    n = len(columns)
    last_col = chr(ord("A") + n - 1)
    last_row = first_data_row + max_rows - 1

    group_row = [""] * n
    for start, _, label in groups:
        if label:
            group_row[col_idx(start)] = label

    header_row = [h for (_, h, _, _) in columns]
    formula_rows = _build_formula_rows(columns, first_data_row, max_rows, idx_cols)

    ws.update(f"A1:{last_col}1", [group_row])
    ws.update(f"A2:{last_col}2", [header_row])
    ws.update(
        f"A{first_data_row}:{last_col}{last_row}",
        formula_rows,
        value_input_option="USER_ENTERED",
    )


def _format_requests(
    sheet_id: int,
    columns: list[tuple],
    groups: list[tuple],
    col_formats: dict[str, dict],
    col_widths: dict[str, int],
    first_data_row: int,
    max_rows: int,
) -> list[dict]:
    last_data_row = first_data_row + max_rows
    n = len(columns)
    reqs: list[dict] = []

    reqs.append(
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 1},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        }
    )

    for start, end, label in groups:
        if label and start != end:
            reqs.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": col_idx(start),
                            "endColumnIndex": col_idx(end) + 1,
                        },
                        "mergeType": "MERGE_ALL",
                    }
                }
            )

    for start, end, label in groups:
        if not label:
            continue
        color = C.get(label, C["_bg"])
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
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

    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": n,
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

    for start, end, label in groups:
        if not label or label not in C:
            continue
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": first_data_row - 1,
                        "endRowIndex": last_data_row,
                        "startColumnIndex": col_idx(start),
                        "endColumnIndex": col_idx(end) + 1,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": C[label]}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )

    for letter, fmt in col_formats.items():
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": first_data_row - 1,
                        "endRowIndex": last_data_row,
                        "startColumnIndex": col_idx(letter),
                        "endColumnIndex": col_idx(letter) + 1,
                    },
                    "cell": {"userEnteredFormat": fmt},
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    for letter, width in col_widths.items():
        reqs.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": col_idx(letter),
                        "endIndex": col_idx(letter) + 1,
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }
        )

    for start_idx, end_idx, height in [(0, 1, 35), (1, 2, 48)]:
        reqs.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": start_idx,
                        "endIndex": end_idx,
                    },
                    "properties": {"pixelSize": height},
                    "fields": "pixelSize",
                }
            }
        )

    return reqs


# ---------------------------------------------------------------------------
# impuestos sheet  (static config — edit rates here, test sheet reads them)
# ---------------------------------------------------------------------------

# Rows 2-N: (name, rate, ley)
# Rate stored as decimal (0.11) formatted as % — user sees 11%
# test sheet references: $B$2=Jubilación, $B$3=PAMI, $B$4=Obra Social, $B$5=Otro
IMPUESTOS_ROWS = [
    ("Jubilación", 0.11, "Ley 24241"),
    ("PAMI", 0.03, "Ley 19032"),
    ("Obra Social", 0.03, "Ley 23660"),
    ("Otro", 0.00, "—"),
]


def _setup_impuestos(spreadsheet: gspread.Spreadsheet) -> list[dict]:
    ws = _recreate_worksheet(
        spreadsheet,
        TAX_SHEET,
        n_cols=3,
        n_rows=2 + len(IMPUESTOS_ROWS),
    )
    sid = ws.id

    ws.update("A1:C1", [["Impuesto", "Tasa", "Ley / Descripción"]])
    ws.update(
        f"A2:C{1 + len(IMPUESTOS_ROWS)}",
        [[name, rate, ley] for name, rate, ley in IMPUESTOS_ROWS],
        value_input_option="USER_ENTERED",
    )

    reqs: list[dict] = []

    # Freeze row 1
    reqs.append(
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sid,
                    "gridProperties": {"frozenRowCount": 1},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        }
    )

    # Header row style
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 3,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["_bg"],
                        "textFormat": {
                            "bold": True,
                            "fontSize": 10,
                            "foregroundColor": C["_fg"],
                        },
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        }
    )

    # Format col B (Tasa) as percentage
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sid,
                    "startRowIndex": 1,
                    "endRowIndex": 1 + len(IMPUESTOS_ROWS),
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

    # Column widths
    for i, width in enumerate([160, 80, 160]):
        reqs.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sid,
                        "dimension": "COLUMNS",
                        "startIndex": i,
                        "endIndex": i + 1,
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }
        )

    return reqs


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def setup() -> None:
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID not set in .env", file=sys.stderr)
        sys.exit(1)

    client = get_sheets_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    all_requests: list[dict] = []

    # ── impuestos (config) ────────────────────────────────────────────────────
    print(f"\nSetting up {TAX_SHEET!r}...")
    all_requests += _setup_impuestos(spreadsheet)

    # ── historic_data ─────────────────────────────────────────────────────────
    print(f"\nSetting up {HISTORIC_SHEET!r}...")
    all_requests += _setup_historic(spreadsheet)

    # ── market_data ───────────────────────────────────────────────────────────
    print(f"\nSetting up {MARKET_SHEET!r}...")
    ws_market = _recreate_worksheet(
        spreadsheet,
        MARKET_SHEET,
        n_cols=len(MARKET_COLUMNS),
        n_rows=FIRST_DATA_ROW + MAX_MONTHLY_ROWS,
    )
    _write_standard_content(
        ws_market,
        MARKET_COLUMNS,
        MARKET_GROUPS,
        FIRST_DATA_ROW,
        MAX_MONTHLY_ROWS,
    )
    all_requests += _format_requests(
        ws_market.id,
        MARKET_COLUMNS,
        MARKET_GROUPS,
        MARKET_COL_FORMATS,
        MARKET_COL_WIDTHS,
        FIRST_DATA_ROW,
        MAX_MONTHLY_ROWS,
    )

    # ── test (income) ─────────────────────────────────────────────────────────
    print(f"\nSetting up {INCOME_SHEET!r}...")
    ws_income = _recreate_worksheet(
        spreadsheet,
        INCOME_SHEET,
        n_cols=len(INCOME_COLUMNS),
        n_rows=FIRST_DATA_ROW + MAX_MONTHLY_ROWS,
    )
    _write_standard_content(
        ws_income,
        INCOME_COLUMNS,
        INCOME_GROUPS,
        FIRST_DATA_ROW,
        MAX_MONTHLY_ROWS,
        idx_cols={"S"},
    )
    all_requests += _format_requests(
        ws_income.id,
        INCOME_COLUMNS,
        INCOME_GROUPS,
        INCOME_COL_FORMATS,
        INCOME_COL_WIDTHS,
        FIRST_DATA_ROW,
        MAX_MONTHLY_ROWS,
    )

    spreadsheet.batch_update({"requests": all_requests})
    print(f"\nDone → https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")


if __name__ == "__main__":
    setup()
