"""Setup V2 para hojas de Análisis ARS y USD con fórmulas simplificadas.

Esta versión usa fórmulas individuales por fila en lugar de ARRAYFORMULA,
facilitando debugging y validación.
"""

import gspread
from typing import List, Dict, Tuple

from src.config import SHEET_LIMITS, SHEETS, get_color, lighten_color
from src.setup.utils import apply_formatting, col_idx, get_or_create_worksheet
from src.sheets.structure import (
    ANALISIS_ARS_COLUMNS,
    ANALISIS_ARS_FORMATS,
    ANALISIS_ARS_GROUPS,
    ANALISIS_USD_COLUMNS,
    ANALISIS_USD_FORMATS,
    ANALISIS_USD_GROUPS,
    get_formula_for_row,
    is_column_hidden,
)


def generate_formulas_for_sheet(
    columns: List[Tuple],
    start_row: int = 3,
    end_row: int = 1000,
) -> Dict[str, List[str]]:
    """Genera fórmulas para todas las filas de un sheet.

    Args:
        columns: Lista de definiciones de columnas
        start_row: Primera fila de datos
        end_row: Última fila de datos

    Returns:
        Dict con letra de columna -> lista de fórmulas
    """
    formulas_by_col = {}

    for col_def in columns:
        col_letter = col_def[0]
        formulas = []

        for row_num in range(start_row, end_row + 1):
            formula = get_formula_for_row(col_def, row_num)
            formulas.append(formula if formula else "")

        formulas_by_col[col_letter] = formulas

    return formulas_by_col


def get_hidden_columns(columns: List[Tuple]) -> List[str]:
    """Obtiene lista de letras de columnas que deben ocultarse.

    Args:
        columns: Lista de definiciones de columnas

    Returns:
        Lista de letras de columnas a ocultar
    """
    hidden = []
    for col_def in columns:
        if is_column_hidden(col_def):
            hidden.append(col_def[0])
    return hidden


def setup_analisis_ars(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja de Análisis ARS con fórmulas V2.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["ANALISIS_ARS"]
    max_rows = SHEET_LIMITS["max_rows"]
    start_row = 3

    print(f"Configurando {sheet_name} V2...")
    ws = get_or_create_worksheet(ss, sheet_name, rows=max_rows, cols=30)

    # Row 1: Grupos de columnas
    group_row = [""] * 30
    for start, end, label in ANALISIS_ARS_GROUPS:
        group_row[col_idx(start)] = label
    ws.update(range_name="A1:AD1", values=[group_row])

    # Row 2: Headers de columnas
    header_row = [""] * 30
    for col_let, title, *rest in ANALISIS_ARS_COLUMNS:
        header_row[col_idx(col_let)] = title
    ws.update(range_name="A2:AD2", values=[header_row])

    print(f"Limpiando fórmulas viejas en {sheet_name}...")
    ws.batch_clear([f"A3:AD{max_rows}"])

    print("Generando fórmulas por fila...")
    formulas_by_col = generate_formulas_for_sheet(
        ANALISIS_ARS_COLUMNS, start_row=start_row, end_row=max_rows
    )

    # Batch update de fórmulas por columna
    formula_updates = []
    for col_letter, formulas in formulas_by_col.items():
        # Filtrar solo fórmulas no vacías
        non_empty_formulas = [(i, f) for i, f in enumerate(formulas) if f]

        if not non_empty_formulas:
            continue

        # Agrupar fórmulas consecutivas para optimizar requests
        current_start = None
        current_formulas = []

        for i, formula in non_empty_formulas:
            row_num = start_row + i

            if current_start is None:
                current_start = row_num
                current_formulas = [formula]
            elif row_num == current_start + len(current_formulas):
                # Consecutivo
                current_formulas.append(formula)
            else:
                # Gap, hacer update del grupo anterior
                if current_formulas:
                    formula_updates.append(
                        {
                            "range": f"{col_letter}{current_start}:{col_letter}{current_start + len(current_formulas) - 1}",
                            "values": [[f] for f in current_formulas],
                        }
                    )
                current_start = row_num
                current_formulas = [formula]

        # Update del último grupo
        if current_formulas:
            formula_updates.append(
                {
                    "range": f"{col_letter}{current_start}:{col_letter}{current_start + len(current_formulas) - 1}",
                    "values": [[f] for f in current_formulas],
                }
            )

    print(f"Aplicando {len(formula_updates)} bloques de fórmulas...")
    if formula_updates:
        # Batch en grupos de 100 para evitar límites de API
        batch_size = 100
        for i in range(0, len(formula_updates), batch_size):
            batch = formula_updates[i : i + batch_size]
            ws.batch_update(batch, value_input_option="USER_ENTERED")
            print(
                f"  Aplicado batch {i // batch_size + 1}/{(len(formula_updates) + batch_size - 1) // batch_size}"
            )

    # Formateo
    print("Aplicando formatos...")
    reqs = [
        # Unmerge all cells first
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
        # Freeze header rows and first column
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": ws.id,
                    "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 2},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        },
    ]

    # Merge cells y aplicar colores para grupos
    for start, end, label in ANALISIS_ARS_GROUPS:
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
    for col_let, fmt_config in ANALISIS_ARS_FORMATS.items():
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

    # Ocultar columnas auxiliares
    hidden_cols = get_hidden_columns(ANALISIS_ARS_COLUMNS)
    for col_letter in hidden_cols:
        idx = col_idx(col_letter)
        reqs.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": idx,
                        "endIndex": idx + 1,
                    },
                    "properties": {"hiddenByUser": True},
                    "fields": "hiddenByUser",
                }
            }
        )
        print(f"  Ocultando columna {col_letter}")

    apply_formatting(ss, ws.id, reqs)
    print(f"✅ {sheet_name} V2 configurado correctamente")


def setup_analisis_usd(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja de Análisis USD con fórmulas V2.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["ANALISIS_USD"]
    max_rows = SHEET_LIMITS["max_rows"]
    start_row = 3

    print(f"Configurando {sheet_name} V2...")
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

    print(f"Limpiando fórmulas viejas en {sheet_name}...")
    ws.batch_clear([f"A3:T{max_rows}"])

    print("Generando fórmulas por fila...")
    formulas_by_col = generate_formulas_for_sheet(
        ANALISIS_USD_COLUMNS, start_row=start_row, end_row=max_rows
    )

    # Batch update de fórmulas por columna
    formula_updates = []
    for col_letter, formulas in formulas_by_col.items():
        non_empty_formulas = [(i, f) for i, f in enumerate(formulas) if f]

        if not non_empty_formulas:
            continue

        current_start = None
        current_formulas = []

        for i, formula in non_empty_formulas:
            row_num = start_row + i

            if current_start is None:
                current_start = row_num
                current_formulas = [formula]
            elif row_num == current_start + len(current_formulas):
                current_formulas.append(formula)
            else:
                if current_formulas:
                    formula_updates.append(
                        {
                            "range": f"{col_letter}{current_start}:{col_letter}{current_start + len(current_formulas) - 1}",
                            "values": [[f] for f in current_formulas],
                        }
                    )
                current_start = row_num
                current_formulas = [formula]

        if current_formulas:
            formula_updates.append(
                {
                    "range": f"{col_letter}{current_start}:{col_letter}{current_start + len(current_formulas) - 1}",
                    "values": [[f] for f in current_formulas],
                }
            )

    print(f"Aplicando {len(formula_updates)} bloques de fórmulas...")
    if formula_updates:
        batch_size = 100
        for i in range(0, len(formula_updates), batch_size):
            batch = formula_updates[i : i + batch_size]
            ws.batch_update(batch, value_input_option="USER_ENTERED")
            print(
                f"  Aplicado batch {i // batch_size + 1}/{(len(formula_updates) + batch_size - 1) // batch_size}"
            )

    # Formateo
    print("Aplicando formatos...")
    reqs = [
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
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": ws.id,
                    "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 2},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        },
    ]

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
    print(f"✅ {sheet_name} V2 configurado correctamente")
