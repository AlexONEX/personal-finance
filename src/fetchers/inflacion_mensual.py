"""Fetcher para Inflación Mensual (IPC) del BCRA - ID 27."""

import logging
from datetime import date, datetime

import requests

from src.config import FETCH_CONFIG
from src.fetchers.base import DataSource

logger = logging.getLogger(__name__)


class InflacionMensualFetcher(DataSource):
    """Obtiene datos de inflación mensual desde la API del BCRA."""

    def fetch(self, since: date, until: date) -> dict[date, float]:
        """Obtiene valores de inflación mensual con paginación automática.

        Args:
            since: Fecha de inicio
            until: Fecha de fin

        Returns:
            Diccionario de fecha (último día del mes) -> inflación mensual %
        """
        results = {}
        offset = 0
        limit = FETCH_CONFIG["bcra_pagination_limit"]

        while True:
            try:
                # ID 27 = Inflación mensual (IPC)
                resp = requests.get(
                    "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/27",
                    params={
                        "desde": since.isoformat(),
                        "hasta": until.isoformat(),
                        "limit": limit,
                        "offset": offset,
                    },
                    timeout=FETCH_CONFIG["timeout_seconds"],
                    verify=False,  # BCRA cert issues
                )
                resp.raise_for_status()
                body = resp.json()

                detalle = []
                for variable in body.get("results", []):
                    detalle.extend(variable.get("detalle", []))

                for record in detalle:
                    if "fecha" not in record or "valor" not in record:
                        logger.warning(f"Inflación mensual: skipping malformed record: {record}")
                        continue
                    try:
                        # La fecha viene como último día del mes (ej: 2024-12-31)
                        d = datetime.strptime(record["fecha"], "%Y-%m-%d").date()
                        # El valor viene como porcentaje (ej: 2.7 = 2.7%)
                        # Lo guardamos como decimal (2.7 / 100 = 0.027)
                        results[d] = float(record["valor"]) / 100
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Inflación mensual: invalid date or value in record {record}: {e}"
                        )
                        continue

                total = body.get("metadata", {}).get("resultset", {}).get("count", 0)
                offset += len(detalle)
                if offset >= total or not detalle:
                    break

            except requests.exceptions.SSLError as e:
                logger.error(f"Inflación mensual: SSL verification failed: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Inflación mensual: request failed: {e}")
                break
            except (KeyError, ValueError) as e:
                logger.error(f"Inflación mensual: invalid response format: {e}")
                break

        logger.info(f"Inflación mensual: fetched {len(results)} records from {since} to {until}")
        return results
