"""Módulo de setup para configurar hojas de Google Sheets.

Estructura:
- utils.py: Funciones compartidas (col_idx, get_or_create_worksheet, etc.)
- impuestos.py: Setup de hoja de impuestos
- historic.py: Setup de hoja de datos históricos
- rem.py: Setup de hoja de proyecciones REM
- ingresos.py: Setup de hoja principal de ingresos
- inversiones.py: Setup de hoja de inversiones
- analisis_ars.py: Setup de hoja Análisis ARS
- analisis_usd.py: Setup de hoja Análisis USD
- dashboard.py: Setup de hoja Dashboard
"""

from src.setup.analisis_ars import setup_analisis_ars
from src.setup.analisis_usd import setup_analisis_usd
from src.setup.dashboard import setup_dashboard
from src.setup.historic import setup_historic
from src.setup.impuestos import setup_impuestos
from src.setup.ingresos import setup_ingresos
from src.setup.inversiones import setup_inversiones
from src.setup.rem import setup_rem
from src.setup.simulador import setup_simulador
from src.setup.utils import apply_formatting, col_idx, get_or_create_worksheet

__all__ = [
    "col_idx",
    "get_or_create_worksheet",
    "apply_formatting",
    "setup_impuestos",
    "setup_historic",
    "setup_rem",
    "setup_ingresos",
    "setup_inversiones",
    "setup_analisis_ars",
    "setup_analisis_usd",
    "setup_dashboard",
    "setup_simulador",
]
