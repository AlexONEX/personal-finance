"""Fetcher para SPY (S&P 500 ETF) usando yfinance."""

import logging
from datetime import date

import yfinance as yf

from src.fetchers.base import DataSource

logger = logging.getLogger(__name__)


class SPYFetcher(DataSource):
    """Obtiene precios de cierre de SPY usando yfinance."""

    def fetch(self, since: date, until: date) -> dict[date, float]:
        """Obtiene precios históricos de cierre de SPY.

        Args:
            since: Fecha de inicio
            until: Fecha de fin

        Returns:
            Diccionario de fecha -> precio de cierre
        """
        out = {}

        try:
            ticker = yf.Ticker("SPY")
            df = ticker.history(start=since, end=until, interval="1d")

            if df.empty:
                logger.warning(f"SPY: no data returned for {since} to {until}")
                return out

            for idx, row in df.iterrows():
                d = idx.date() if hasattr(idx, "date") else idx
                out[d] = float(row["Close"])

            logger.info(f"SPY: fetched {len(out)} days from {since} to {until}")

        except Exception as e:
            logger.error(f"SPY: failed to fetch data: {e}")

        return out
