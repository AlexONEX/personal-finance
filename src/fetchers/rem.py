"""Fetcher para REM (Relevamiento de Expectativas de Mercado) del BCRA.

Usa la API REST del BCRA (variable 29: mediana IPC interanual próximos 12 meses).
"""

import logging
from datetime import date

import requests
import urllib3

from src.config import API_URLS, FETCH_CONFIG

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

_REM_12M_VAR_ID = 29


class REMFetcher:
    """Obtiene la proyección REM de inflación interanual 12m desde la API del BCRA."""

    def fetch(self, since_date: tuple[int, int]) -> dict[str, float]:
        """Obtiene proyecciones REM de inflación interanual a 12 meses.

        Args:
            since_date: Tupla (año, mes) desde donde obtener datos

        Returns:
            Diccionario de "YYYY-MM-01" -> proyección en decimal (ej: 0.238 para 23.8%)
        """
        year, month = since_date
        desde = date(year, month, 1).strftime("%Y-%m-%d")
        hasta = date.today().strftime("%Y-%m-%d")
        url = f"{API_URLS['bcra_monetarias']}/{_REM_12M_VAR_ID}"

        try:
            r = requests.get(
                url,
                params={"desde": desde, "hasta": hasta, "limit": 100},
                timeout=FETCH_CONFIG["timeout_seconds"],
                verify=False,
            )
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"REM: failed to fetch from BCRA API: {e}")
            return {}

        results: dict[str, float] = {}
        for item in r.json().get("results", []):
            for entry in item.get("detalle", []):
                fecha_str: str = entry["fecha"]  # "YYYY-MM-DD" (último día del mes)
                year_m, month_m = int(fecha_str[:4]), int(fecha_str[5:7])
                month_key = f"{year_m}-{month_m:02d}-01"
                results[month_key] = float(entry["valor"]) / 100.0

        logger.info(f"REM: fetched {len(results)} records since {since_date}")
        return results
