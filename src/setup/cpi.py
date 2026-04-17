"""Setup para la hoja CPI (Consumer Price Index)."""

import logging

from src.config import COLORS, SHEETS
from src.setup.utils import apply_column_formats, apply_group_colors, create_header_row

logger = logging.getLogger(__name__)


CPI_GROUPS = [
    ("A", "A", "FECHA"),
    ("B", "E", "INDEC - TOTAL NACIONAL"),
    ("F", "I", "INDEC - GBA"),
    ("J", "M", "CABA - ÍNDICES"),
    ("N", "Q", "CABA - VARIACIONES"),
]

CPI_COLUMNS = [
    ("A", "Fecha"),
    # INDEC - TOTAL NACIONAL
    ("B", "Nivel General"),
    ("C", "Estacionales"),
    ("D", "Regulados"),
    ("E", "Núcleo"),
    # INDEC - GBA
    ("F", "Nivel General"),
    ("G", "Estacionales"),
    ("H", "Regulados"),
    ("I", "Núcleo"),
    # CABA - ÍNDICES
    ("J", "Nivel General"),
    ("K", "Estacionales"),
    ("L", "Regulados"),
    ("M", "Resto"),
    # CABA - VARIACIONES
    ("N", "Nivel General %"),
    ("O", "Estacionales %"),
    ("P", "Regulados %"),
    ("Q", "Resto %"),
]

CPI_FORMATS = {
    "A": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    # INDEC variations are percentages
    "B": {"type": "PERCENT", "pattern": "0.00%"},
    "C": {"type": "PERCENT", "pattern": "0.00%"},
    "D": {"type": "PERCENT", "pattern": "0.00%"},
    "E": {"type": "PERCENT", "pattern": "0.00%"},
    "F": {"type": "PERCENT", "pattern": "0.00%"},
    "G": {"type": "PERCENT", "pattern": "0.00%"},
    "H": {"type": "PERCENT", "pattern": "0.00%"},
    "I": {"type": "PERCENT", "pattern": "0.00%"},
    # CABA indices are numbers
    "J": {"type": "NUMBER", "pattern": "#,##0.00"},
    "K": {"type": "NUMBER", "pattern": "#,##0.00"},
    "L": {"type": "NUMBER", "pattern": "#,##0.00"},
    "M": {"type": "NUMBER", "pattern": "#,##0.00"},
    # CABA variations are percentages
    "N": {"type": "PERCENT", "pattern": "0.00%"},
    "O": {"type": "PERCENT", "pattern": "0.00%"},
    "P": {"type": "PERCENT", "pattern": "0.00%"},
    "Q": {"type": "PERCENT", "pattern": "0.00%"},
}


def setup_cpi(ss):
    """Configura la estructura de la hoja CPI."""
    logger.info("Setting up CPI sheet structure...")

    try:
        ws = ss.worksheet(SHEETS["CPI"])
    except Exception:
        logger.info("CPI sheet not found, creating it...")
        ws = ss.add_worksheet(title=SHEETS["CPI"], rows=1000, cols=20)

    # Header superior (fila 1): Título principal
    ws.update(range_name="A1", values=[["CPI Data (INDEC & CABA)"]])
    ws.format(
        "A1",
        {
            "textFormat": {"bold": True, "fontSize": 14},
            "horizontalAlignment": "LEFT",
        },
    )

    # Última actualización (fila 2)
    ws.update(range_name="A2", values=[["Última actualización:"]])
    ws.update(range_name="B2", values=[["—"]])

    # Fila 3: Headers de columnas
    header_titles = [col[1] for col in CPI_COLUMNS]
    create_header_row(ws, 3, header_titles)

    # Aplicar colores a grupos
    apply_group_colors(ws, 3, CPI_GROUPS, COLORS)

    # Aplicar formatos de columna
    apply_column_formats(ws, CPI_FORMATS, start_row=4, end_row=1000)

    logger.info("CPI sheet structure configured successfully")
