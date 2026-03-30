"""Setup de la hoja Dashboard - Métricas para negociación salarial."""

import gspread

from src.config import SHEET_LIMITS, SHEETS, get_color
from src.setup.utils import apply_formatting, col_idx, get_or_create_worksheet
from src.sheets.structure import DASHBOARD_ROWS, DASHBOARD_SECTIONS


def setup_dashboard(ss: gspread.Spreadsheet) -> None:
    """Configura la hoja Dashboard con métricas clave.

    Args:
        ss: Spreadsheet de gspread
    """
    sheet_name = SHEETS["DASHBOARD"]

    print(f"Configurando {sheet_name}...")
    ws = get_or_create_worksheet(ss, sheet_name, rows=50, cols=5)

    # Escribir todas las filas
    for row_num, col_let, label, formula in DASHBOARD_ROWS:
        cell = f"{col_let}{row_num}"
        if formula:
            ws.update(range_name=cell, values=[[formula]], value_input_option="USER_ENTERED")
        else:
            ws.update(range_name=cell, values=[[label]], value_input_option="USER_ENTERED")

    # Formateo visual
    reqs = []

    # Header general
    header_bg = {"red": 0.2, "green": 0.3, "blue": 0.4}
    header_fg = {"red": 1.0, "green": 1.0, "blue": 1.0}

    # Row 1: Título principal
    ws.update(range_name="A1", values=[["DASHBOARD DE NEGOCIACIÓN SALARIAL"]], value_input_option="USER_ENTERED")
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": header_bg,
                        "textFormat": {"bold": True, "fontSize": 14, "foregroundColor": header_fg},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        }
    )

    # Merge título
    reqs.append(
        {
            "mergeCells": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5,
                },
                "mergeType": "MERGE_ALL",
            }
        }
    )

    # Secciones
    section_colors = {
        "RESUMEN EJECUTIVO": {"red": 1.0, "green": 0.8, "blue": 0.8},
        "PODER ADQUISITIVO": {"red": 0.8, "green": 0.898, "blue": 1.0},
        "COMPARATIVAS": {"red": 0.898, "green": 1.0, "blue": 0.898},
        "ÚLTIMO MES": {"red": 1.0, "green": 1.0, "blue": 0.8},
        "TARGETS/OBJETIVOS": {"red": 0.898, "green": 0.8, "blue": 1.0},
    }

    for section_name, start_row, end_row in DASHBOARD_SECTIONS:
        color = section_colors.get(section_name, header_bg)

        # Header de sección
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": start_row - 1,
                        "endRowIndex": start_row,
                        "startColumnIndex": 0,
                        "endColumnIndex": 3,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": color,
                            "textFormat": {"bold": True, "fontSize": 11},
                            "horizontalAlignment": "CENTER",
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                }
            }
        )

        # Background suave para datos de la sección
        light_color = {
            "red": min(1.0, color["red"] + (1 - color["red"]) * 0.7),
            "green": min(1.0, color["green"] + (1 - color["green"]) * 0.7),
            "blue": min(1.0, color["blue"] + (1 - color["blue"]) * 0.7),
        }
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row + 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 3,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": light_color}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )

    # Formatos de número para columna B
    # Rows con porcentajes
    percent_rows = [3, 5, 12, 15, 16, 17, 21, 22, 27, 28, 29]
    for r in percent_rows:
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": r - 1,
                        "endRowIndex": r,
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

    # Rows con moneda
    currency_rows = [9, 10, 11, 15, 16, 17, 30]
    for r in currency_rows:
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": r - 1,
                        "endRowIndex": r,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    # Número simple para meses
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 3,
                    "endRowIndex": 4,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "NUMBER", "pattern": "0"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        }
    )

    # Ancho de columnas
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "properties": {"pixelSize": 350},
                "fields": "pixelSize",
            }
        }
    )
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": 2,
                },
                "properties": {"pixelSize": 150},
                "fields": "pixelSize",
            }
        }
    )
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 2,
                    "endIndex": 3,
                },
                "properties": {"pixelSize": 100},
                "fields": "pixelSize",
            }
        }
    )

    apply_formatting(ss, ws.id, reqs)
