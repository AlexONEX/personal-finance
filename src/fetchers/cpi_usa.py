"""Fetcher for USA CPI from FRED (Federal Reserve Economic Data)."""

import logging
from datetime import datetime

import requests

from src.fetchers.cpi_formatters import format_for_sheets

logger = logging.getLogger(__name__)


class USACPIFetcher:
    """Fetches USA CPI data from FRED API."""

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    DEFAULT_SERIES_ID = "CPIAUCSL"  # Consumer Price Index for All Urban Consumers

    def __init__(self, api_key: str, series_id: str = DEFAULT_SERIES_ID) -> None:
        """Initialize the USA CPI fetcher.

        Args:
            api_key: FRED API key
            series_id: FRED series ID (default: CPIAUCSL)
        """
        self.api_key = api_key
        self.series_id = series_id

    def fetch(
        self, start_date: str
    ) -> tuple[list[list[str]], list[list[float]], list[list[float | str]]]:
        """Fetch USA CPI data.

        Args:
            start_date: Start date in YYYY-MM-DD format

        Returns:
            Tuple containing:
            - dates
            - indices (CPI values)
            - variations (month-over-month percentage changes)
        """
        monthly_records = self._fetch_monthly_records_from_api(start_date)
        return self._process_all_monthly_records(monthly_records)

    def _fetch_monthly_records_from_api(self, start_date: str) -> list[dict]:
        """Fetch monthly CPI records from FRED API."""
        url = self._build_api_url(start_date)
        response = self._make_api_request(url)
        return response.json()["observations"]

    def _build_api_url(self, start_date: str) -> str:
        """Build the FRED API URL."""
        return (
            f"{self.BASE_URL}"
            f"?series_id={self.series_id}"
            f"&api_key={self.api_key}"
            f"&file_type=json"
            f"&observation_start={start_date}"
        )

    def _make_api_request(self, url: str) -> requests.Response:
        """Make API request to FRED."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logger.info("USA CPI: Successfully fetched data from FRED API")
        return response

    def _process_all_monthly_records(
        self, monthly_records: list[dict]
    ) -> tuple[list[list[str]], list[list[float]], list[list[float | str]]]:
        """Process all monthly records and calculate variations."""
        dates: list[list[str]] = []
        indices: list[list[float]] = []
        variations: list[list[float | str]] = []

        for i in range(1, len(monthly_records)):
            current_record = monthly_records[i]
            previous_record = monthly_records[i - 1]

            # Skip records with invalid values
            if current_record.get("value") in (".", "", None):
                logger.debug(
                    f"USA CPI: Skipping record with invalid value at date: {current_record.get('date')}"
                )
                continue

            try:
                date_str = self._format_record_date(current_record)
                dates.append([date_str])

                cpi_value = self._extract_cpi_value(current_record)
                indices.append([cpi_value])

                variation = self._calculate_monthly_variation(
                    current_record, previous_record
                )
                variations.append([variation])
            except Exception as e:
                logger.warning(
                    f"USA CPI: Error processing record at date {current_record.get('date')}: {e}"
                )
                continue

        logger.info(f"USA CPI: Processed {len(dates)} records")
        return dates, indices, variations

    def _format_record_date(self, record: dict) -> str:
        """Format date from FRED record to dd/mm/yyyy."""
        date_str = record["date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")

    def _extract_cpi_value(self, record: dict) -> float:
        """Extract CPI value from record."""
        try:
            value = record["value"]
            if value == "." or value == "":
                raise ValueError(f"Invalid CPI value: '{value}'")
            return float(value)
        except (ValueError, KeyError) as e:
            logger.warning(f"USA CPI: Could not parse CPI value from record: {record}")
            raise ValueError(f"Failed to extract CPI value: {e}") from e

    def _calculate_monthly_variation(
        self, current_record: dict, previous_record: dict
    ) -> float | str:
        """Calculate month-over-month percentage variation."""
        try:
            current_value_raw = current_record["value"]
            previous_value_raw = previous_record["value"]

            # Validate values are not "." or empty strings
            if current_value_raw in (".", "", None) or previous_value_raw in (
                ".",
                "",
                None,
            ):
                return "N/A"

            current_value = float(current_value_raw)
            previous_value = float(previous_value_raw)

            if previous_value <= 0:
                return 0.0

            variation_pct = ((current_value / previous_value) - 1) * 100
            rounded_variation = round(variation_pct, 2)
            return format_for_sheets(rounded_variation, is_percentage=True)
        except (ValueError, TypeError, KeyError):
            logger.warning(
                f"USA CPI: Could not calculate variation. Current: {current_record.get('date')}, "
                f"Previous: {previous_record.get('date')}"
            )
            return "N/A"
