"""Módulo de fetchers para obtener datos de fuentes externas.

Estructura:
- base.py: Clase abstracta DataSource
- cer.py: Fetcher para CER (BCRA API)
- ccl.py: Fetcher para CCL (Ambito + dolarapi)
- rem.py: Fetcher para REM (BCRA web scraping + Excel)
- spy.py: Fetcher para SPY (yfinance)
- inflacion_mensual.py: Fetcher para Inflación Mensual (BCRA API)
- cpi_indec.py: Fetcher para CPI INDEC
- cpi_caba.py: Fetcher para CPI CABA
"""

from src.fetchers.base import DataSource
from src.fetchers.cer import CERFetcher
from src.fetchers.ccl import CCLFetcher
from src.fetchers.rem import REMFetcher
from src.fetchers.spy import SPYFetcher
from src.fetchers.inflacion_mensual import InflacionMensualFetcher
from src.fetchers.cpi_indec import INDECCPIFetcher
from src.fetchers.cpi_caba import CABACPIFetcher

__all__ = [
    "DataSource",
    "CERFetcher",
    "CCLFetcher",
    "REMFetcher",
    "SPYFetcher",
    "InflacionMensualFetcher",
    "INDECCPIFetcher",
    "CABACPIFetcher",
]
