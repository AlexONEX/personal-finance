"""Fetcher para CER (Coeficiente de Estabilización de Referencia) del BCRA."""

import logging
from datetime import date, datetime

import requests

from src.config import API_URLS, FETCH_CONFIG
from src.fetchers.base import DataSource

logger = logging.getLogger(__name__)


class CERFetcher(DataSource):
    """Obtiene datos de CER desde la API del BCRA."""

    def fetch(self, since: date, until: date) -> dict[date, float]:
        """Obtiene valores de CER con paginación automática.

        Args:
            since: Fecha de inicio
            until: Fecha de fin

        Returns:
            Diccionario de fecha -> valor CER
        """
        results = {}
        offset = 0
        limit = FETCH_CONFIG["bcra_pagination_limit"]

        while True:
            try:
                # WARNING: BCRA API has certificate issues (known Argentina Central Bank infrastructure issue)
                # Using verify=False ONLY for BCRA endpoints as a necessary exception
                resp = requests.get(
                    API_URLS["bcra_cer"],
                    params={
                        "desde": since.isoformat(),
                        "hasta": until.isoformat(),
                        "limit": limit,
                        "offset": offset,
                    },
                    timeout=FETCH_CONFIG["timeout_seconds"],
                    verify=False,
                )
                resp.raise_for_status()
                body = resp.json()

                detalle = []
                for variable in body.get("results", []):
                    detalle.extend(variable.get("detalle", []))

                for record in detalle:
                    if "fecha" not in record or "valor" not in record:
                        logger.warning(f"CER: skipping malformed record: {record}")
                        continue
                    try:
                        d = datetime.strptime(record["fecha"], "%Y-%m-%d").date()
                        results[d] = float(record["valor"])
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"CER: invalid date or value in record {record}: {e}"
                        )
                        continue

                total = body.get("metadata", {}).get("resultset", {}).get("count", 0)
                offset += len(detalle)
                if offset >= total or not detalle:
                    break

            except requests.exceptions.SSLError as e:
                logger.error(f"CER: SSL verification failed: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"CER: request failed: {e}")
                break
            except (KeyError, ValueError) as e:
                logger.error(f"CER: invalid response format: {e}")
                break

        logger.info(f"CER: fetched {len(results)} records from {since} to {until}")
        return results
