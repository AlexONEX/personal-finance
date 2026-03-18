"""Fetcher para CCL (Contado Con Liquidación) usando Ambito y dolarapi como fallback."""

import logging
from datetime import date, datetime

import requests

from src.config import API_URLS, FETCH_CONFIG
from src.fetchers.base import DataSource

logger = logging.getLogger(__name__)


class CCLFetcher(DataSource):
    """Obtiene cotización de dólar CCL desde múltiples fuentes."""

    def fetch(self, since: date, until: date) -> dict[date, float]:
        """Obtiene valores históricos de CCL.

        Primero intenta Ambito (histórico), luego complementa con dolarapi (hoy).

        Args:
            since: Fecha de inicio
            until: Fecha de fin

        Returns:
            Diccionario de fecha -> valor CCL
        """
        historical_data = self._fetch_ambito(since, until)
        today_data = self._fetch_today()
        if today_data and since <= today_data[0] <= until:
            historical_data[today_data[0]] = today_data[1]

        logger.info(
            f"CCL: fetched {len(historical_data)} records from {since} to {until}"
        )
        return historical_data

    def _fetch_ambito(self, since: date, until: date) -> dict[date, float]:
        """Obtiene datos históricos de CCL desde Ambito.com."""
        url = API_URLS["ambito_ccl"].format(
            desde=since.isoformat(), hasta=until.isoformat()
        )
        out = {}

        try:
            # User-Agent needed to bypass Ambito's bot detection
            resp = requests.get(
                url,
                timeout=FETCH_CONFIG["timeout_seconds"],
                headers={"User-Agent": "Mozilla/5.0"},
            )
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list):
                logger.error("CCL Ambito: unexpected response format (not a list)")
                return out

            for row in data[1:]:
                if not isinstance(row, list) or len(row) < 2:
                    logger.warning(f"CCL Ambito: skipping malformed row: {row}")
                    continue
                try:
                    d = datetime.strptime(str(row[0]).strip(), "%d/%m/%Y").date()
                    out[d] = float(row[1])
                except (ValueError, TypeError, IndexError) as e:
                    logger.warning(f"CCL Ambito: invalid row {row}: {e}")
                    continue

        except requests.exceptions.RequestException as e:
            logger.warning(f"CCL Ambito: request failed: {e}")
        except (ValueError, KeyError) as e:
            logger.error(f"CCL Ambito: invalid response format: {e}")

        return out

    def _fetch_today(self) -> tuple[date, float] | None:
        """Obtiene cotización de CCL del día desde dolarapi.com."""
        try:
            resp = requests.get(API_URLS["dolarapi_ccl"], timeout=10)
            resp.raise_for_status()
            body = resp.json()

            venta = body.get("venta")
            fecha = body.get("fechaActualizacion", "")

            if not venta or not fecha:
                logger.warning("CCL today: missing venta or fecha in response")
                return None

            try:
                d = datetime.fromisoformat(fecha.replace("Z", "+00:00")).date()
                return d, float(venta)
            except (ValueError, TypeError) as e:
                logger.warning(f"CCL today: invalid date or venta format: {e}")
                return None

        except requests.exceptions.RequestException as e:
            logger.warning(f"CCL today: request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.warning(f"CCL today: invalid response format: {e}")
            return None
