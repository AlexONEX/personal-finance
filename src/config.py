"""Configuración centralizada del Ingresos Tracker.

Este archivo contiene todas las constantes, configuraciones y valores hardcodeados
que antes estaban dispersos en setup_sheet.py, fetch_data.py y structure.py.
"""

from datetime import date

# =============================================================================
# GOOGLE SHEETS - Configuración de hojas
# =============================================================================

SHEETS = {
    "INGRESOS": "Ingresos",
    "HISTORIC": "historic_data",
    "REM": "REM",
    "IMPUESTOS": "impuestos",
    "PANEL": "Panel",
    "INVERSIONES": "Inversiones",
    "ANALISIS_ARS": "Análisis ARS",
    "ANALISIS_USD": "Análisis USD",
    "SIMULADOR_INFLACION": "Simulador_Inflacion",
    "CPI": "CPI",
}

# =============================================================================
# GOOGLE SHEETS - Configuración de filas y límites
# =============================================================================

SHEET_LIMITS = {
    "first_data_row_ingresos": 3,
    "first_data_row_historic": 4,
    "first_data_row_rem": 4,
    "max_rows": 1000,
}

# =============================================================================
# IMPUESTOS - Tasas y configuración fiscal
# =============================================================================

TAX_RATES = {
    "jubilacion": {"rate": 0.11, "law": "Ley 24241"},
    "pami": {"rate": 0.03, "law": "Ley 19032"},
    "obra_social": {"rate": 0.03, "law": "Ley 23660"},
    "otro": {"rate": 0.00, "law": "—"},
}

# =============================================================================
# COLORES - Esquema de colores para headers y grupos
# =============================================================================

COLORS = {
    # Grupos de columnas en Ingresos
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
    # Grupos de Análisis ARS
    "PERIODO": {"red": 0.85, "green": 0.85, "blue": 0.85},
    "VS ÚLTIMO AUMENTO (CER)": {"red": 1.0, "green": 0.8, "blue": 0.8},
    "VS ÚLTIMO AUMENTO (REM)": {"red": 0.8, "green": 1.0, "blue": 1.0},
    "VARIACIÓN MENSUAL": {"red": 1.0, "green": 1.0, "blue": 0.8},
    "PROYECCIÓN REM": {"red": 0.8, "green": 1.0, "blue": 1.0},
    # Grupos de Análisis USD
    "SUELDO ARS": {"red": 0.8, "green": 0.898, "blue": 1.0},
    "SUELDO USD NOMINAL": {"red": 0.898, "green": 1.0, "blue": 0.898},
    "SUELDO USD REAL": {"red": 1.0, "green": 0.898, "blue": 0.8},
    "VS ÚLTIMO AUMENTO": {"red": 0.988, "green": 0.898, "blue": 0.804},
    # Grupo Valor/Hora en Ingresos
    "VALOR/HORA": {"red": 0.8, "green": 0.9, "blue": 0.8},
    # Colores base para headers
    "header_bg": {"red": 0.2, "green": 0.3, "blue": 0.4},
    "header_fg": {"red": 1.0, "green": 1.0, "blue": 1.0},
}

# Grupos de columnas para Inversiones
INVERSIONES_COLORS = {
    "INPUTS": {"red": 0.8, "green": 0.898, "blue": 1.0},
    "GANANCIAS": {"red": 1.0, "green": 1.0, "blue": 0.8},
    "RENDIMIENTO ARS": {"red": 1.0, "green": 0.8, "blue": 0.8},
    "RENDIMIENTO USD": {"red": 0.898, "green": 1.0, "blue": 0.898},
    "CCL": {"red": 0.988, "green": 0.898, "blue": 0.804},
}

INVERSIONES_GROUPS = [
    ("A", "I", "INPUTS"),
    ("J", "K", "GANANCIAS"),
    ("L", "R", "RENDIMIENTO ARS"),
    ("S", "Y", "RENDIMIENTO USD"),
    ("Z", "AC", "CCL"),
]

INVERSIONES_COLUMN_FORMATS = {
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

# =============================================================================
# DATA FETCHING - APIs y URLs
# =============================================================================

API_URLS = {
    "bcra_cer": "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30",
    "ambito_ccl": "https://mercados.ambito.com//dolarrava/cl/grafico/{desde}/{hasta}",
    "dolarapi_ccl": "https://dolarapi.com/v1/dolares/contadoconliqui",
    "bcra_rem_base": "https://www.bcra.gob.ar",
    "bcra_rem_publications": "https://www.bcra.gob.ar/todos-relevamiento-de-expectativas-de-mercado-rem/",
}

# Configuración de fetching
FETCH_CONFIG = {
    "bcra_pagination_limit": 3000,
    "timeout_seconds": 30,
    "backfill_from": date(2022, 1, 1),
    "max_workers_parallel": 5,
    "max_workers_rem": 3,
}

# Mapeo de meses (español -> número)
MONTHS_MAP = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

MONTHS_MAP_SHORT = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}

# =============================================================================
# FORMATOS - Configuración de visualización
# =============================================================================

NUMBER_FORMATS = {
    "date": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "text": {"type": "TEXT", "pattern": "mmmm yyyy"},
    "currency": {"type": "CURRENCY", "pattern": "$#,##0"},
    "currency_decimals": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "number": {"type": "NUMBER", "pattern": "#,##0"},
    "number_decimals": {"type": "NUMBER", "pattern": "#,##0.00"},
    "number_four_decimals": {"type": "NUMBER", "pattern": "0.0000"},
    "percent": {"type": "PERCENT", "pattern": "0.00%"},
}

# =============================================================================
# UTILIDADES
# =============================================================================


def get_tax_rate(tax_name: str) -> float:
    """Obtiene la tasa de un impuesto por nombre."""
    return TAX_RATES.get(tax_name.lower(), {}).get("rate", 0.0)


def get_color(group_name: str, default_to_header: bool = True) -> dict:
    """Obtiene el color de un grupo. Si no existe, devuelve header_bg por defecto."""
    if group_name in COLORS:
        return COLORS[group_name]
    if default_to_header:
        return COLORS["header_bg"]
    return {"red": 1.0, "green": 1.0, "blue": 1.0}


def lighten_color(color: dict, factor: float = 0.85) -> dict:
    """Crea una versión más clara de un color para fondos de datos."""
    return {
        "red": min(1.0, color["red"] + (1 - color["red"]) * factor),
        "green": min(1.0, color["green"] + (1 - color["green"]) * factor),
        "blue": min(1.0, color["blue"] + (1 - color["blue"]) * factor),
    }
