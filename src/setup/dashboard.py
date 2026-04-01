"""Setup de la hoja Dashboard - Métricas para negociación salarial."""

import time
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
    ws = get_or_create_worksheet(ss, sheet_name, rows=70, cols=8)

    # Preparar datos para batch update
    batch_data = []
    for row_num, col_let, label, formula in DASHBOARD_ROWS:
        cell = f"{col_let}{row_num}"
        value = formula if formula else label
        batch_data.append({
            'range': cell,
            'values': [[value]]
        })

    # Batch update (máximo 50 por batch para evitar rate limit)
    batch_size = 50
    for i in range(0, len(batch_data), batch_size):
        batch = batch_data[i:i + batch_size]
        ws.batch_update(batch, value_input_option="USER_ENTERED")
        # Pequeño delay para evitar rate limiting
        if i + batch_size < len(batch_data):
            time.sleep(2)

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
                    "endColumnIndex": 8,
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
                    "endColumnIndex": 8,
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
        "IMPACTO ECONÓMICO": {"red": 1.0, "green": 0.7, "blue": 0.7},
        "CONTEXTO HISTÓRICO": {"red": 0.8, "green": 1.0, "blue": 0.8},
        "PROYECCIONES INTELIGENTES": {"red": 0.9, "green": 0.9, "blue": 1.0},
        "ALERTAS Y URGENCIA": {"red": 1.0, "green": 0.9, "blue": 0.7},
        "VISUALIZACIÓN TENDENCIA": {"red": 0.95, "green": 0.95, "blue": 0.95},
        "COMPARATIVA VISUAL": {"red": 0.9, "green": 1.0, "blue": 0.95},
        "SIMULADOR DE AUMENTOS": {"red": 1.0, "green": 0.95, "blue": 0.85},
    }

    for section_data in DASHBOARD_SECTIONS:
        # Manejar tanto (name, start, end) como (name, start, end, col)
        if len(section_data) == 4:
            section_name, start_row, end_row, start_col = section_data
            # Convertir letra a índice
            start_col_idx = ord(start_col.upper()) - ord('A')
            end_col_idx = start_col_idx + 3  # 3 columnas para secciones laterales
        else:
            section_name, start_row, end_row = section_data
            start_col_idx = 0
            end_col_idx = 3

        color = section_colors.get(section_name, header_bg)

        # Header de sección
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": start_row - 1,
                        "endRowIndex": start_row,
                        "startColumnIndex": start_col_idx,
                        "endColumnIndex": end_col_idx,
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
                        "startColumnIndex": start_col_idx,
                        "endColumnIndex": end_col_idx,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": light_color}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )

    # Formatos de número para columna B
    # Rows con porcentajes
    percent_rows = [3, 5, 12, 15, 16, 17, 21, 22, 23, 24, 25, 27, 28, 29, 41, 42, 45, 51, 52, 54]
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

    # Rows con moneda (columna B)
    currency_rows_b = [9, 10, 11, 30, 33, 34, 35, 36, 47, 48, 55, 56]
    for r in currency_rows_b:
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

    # Número simple para meses, días y contadores
    number_rows = [4, 37, 38, 43, 44, 53]
    for r in number_rows:
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
                            "numberFormat": {"type": "NUMBER", "pattern": "0.0"}
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    # Formatos para columna C (contexto adicional)
    # Número en columna C (avg meses)
    reqs.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 49,  # Row 50 (0-indexed)
                    "endRowIndex": 50,
                    "startColumnIndex": 2,  # Columna C
                    "endColumnIndex": 3,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "NUMBER", "pattern": "0.0"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        }
    )
    # Moneda en columna C
    currency_rows_c = [9, 10, 15, 16, 17, 47, 48, 51, 52, 56]
    for r in currency_rows_c:
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": r - 1,
                        "endRowIndex": r,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {"type": "CURRENCY", "pattern": "$#,##0"}
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )

    # Fechas en columna C (contexto histórico)
    date_rows_c = [41, 42, 55]
    for r in date_rows_c:
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": r - 1,
                        "endRowIndex": r,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3,
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

    # Formatos para columnas del simulador (columna F)
    # Porcentajes en simulador
    percent_sim_rows = [25, 29, 34, 35, 36, 37]
    for r in percent_sim_rows:
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": r - 1,
                        "endRowIndex": r,
                        "startColumnIndex": 5,  # Columna F
                        "endColumnIndex": 6,
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

    # Moneda en simulador
    currency_sim_rows = [28, 10, 11, 12]
    for r in currency_sim_rows:
        reqs.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": r - 1,
                        "endRowIndex": r,
                        "startColumnIndex": 5,  # Columna F
                        "endColumnIndex": 6,
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

    # Ancho de columnas
    # Columna A (labels)
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
    # Columna B (valores)
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
    # Columna C (estado)
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
    # Columna D (labels contextuales)
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 3,
                    "endIndex": 4,
                },
                "properties": {"pixelSize": 180},
                "fields": "pixelSize",
            }
        }
    )
    # Columna E (labels visualizaciones)
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 4,
                    "endIndex": 5,
                },
                "properties": {"pixelSize": 250},
                "fields": "pixelSize",
            }
        }
    )
    # Columna F (valores visualizaciones)
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 5,
                    "endIndex": 6,
                },
                "properties": {"pixelSize": 200},
                "fields": "pixelSize",
            }
        }
    )
    # Columna G (valores adicionales)
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 6,
                    "endIndex": 7,
                },
                "properties": {"pixelSize": 100},
                "fields": "pixelSize",
            }
        }
    )
    # Columna H (extra)
    reqs.append(
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 7,
                    "endIndex": 8,
                },
                "properties": {"pixelSize": 100},
                "fields": "pixelSize",
            }
        }
    )

    apply_formatting(ss, ws.id, reqs)
