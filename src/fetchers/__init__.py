"""Módulo de fetchers para obtener datos de fuentes externas.

Estructura:
- base.py: Clase abstracta DataSource
- cer.py: Fetcher para CER (BCRA API)
- ccl.py: Fetcher para CCL (Ambito + dolarapi)
- rem.py: Fetcher para REM (BCRA web scraping + Excel)
- spy.py: Fetcher para SPY (yfinance)
- inflacion_mensual.py: Fetcher para Inflación Mensual (BCRA API)
"""

from src.fetchers.base import DataSource
from src.fetchers.cer import CERFetcher
from src.fetchers.ccl import CCLFetcher
from src.fetchers.rem import REMFetcher
from src.fetchers.spy import SPYFetcher
from src.fetchers.inflacion_mensual import InflacionMensualFetcher

__all__ = [
    "DataSource",
    "CERFetcher",
    "CCLFetcher",
    "REMFetcher",
    "SPYFetcher",
    "InflacionMensualFetcher",
]
