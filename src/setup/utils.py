"""Funciones compartidas para el setup de Google Sheets."""

import gspread


def col_idx(letter: str) -> int:
    """Convierte letra de columna (A, B, ..., Z, AA, AB, ...) a índice (0, 1, ..., 25, 26, 27, ...).

    Args:
        letter: Letra de columna en formato Excel (A-ZZ)

    Returns:
        Índice de columna (0-indexed)
    """
    res = 0
    for char in letter.upper():
        res = res * 26 + (ord(char) - ord("A") + 1)
    return res - 1


def get_or_create_worksheet(
    ss: gspread.Spreadsheet, title: str, rows: int = 1000, cols: int = 60
) -> gspread.Worksheet:
    """Obtiene una worksheet existente o la crea si no existe.

    Args:
        ss: Spreadsheet de gspread
        title: Nombre de la worksheet
        rows: Número de filas (por defecto 1000)
        cols: Número de columnas (por defecto 60)

    Returns:
        Worksheet de gspread
    """
    try:
        return ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return ss.add_worksheet(title=title, rows=rows, cols=cols)


def apply_formatting(ss: gspread.Spreadsheet, sheet_id: int, requests: list) -> None:
    """Aplica formateo batch a una sheet.

    Args:
        ss: Spreadsheet de gspread
        sheet_id: ID de la sheet
        requests: Lista de requests de la API de Google Sheets
    """
    if requests:
        ss.batch_update({"requests": requests})
