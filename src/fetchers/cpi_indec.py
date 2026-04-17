"""Fetcher for INDEC Argentina CPI (Índice de Precios al Consumidor)."""

import io
import logging
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import requests

from src.fetchers.cpi_formatters import format_for_sheets, parse_numeric_value

logger = logging.getLogger(__name__)


class INDECCPIFetcher:
    """Fetches INDEC CPI data from official Excel files."""

    BASE_URL = "https://www.indec.gob.ar/ftp/cuadros/economia/"

    DATE_ROW = 5
    TOTAL_NACIONAL_ROWS: dict[str, int] = {
        "nivel_general": 9,
        "estacionales": 24,
        "nucleo": 25,
        "regulados": 26,
    }
    GBA_ROWS: dict[str, int] = {
        "nivel_general": 39,
        "estacionales": 54,
        "nucleo": 55,
        "regulados": 56,
    }

    def __init__(self) -> None:
        """Initialize the INDEC CPI fetcher."""
        self.base_url = self.BASE_URL

    def fetch(
        self, start_date: str = "2022-02-01"
    ) -> tuple[
        list[list[str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
    ]:
        """Fetch INDEC CPI data.

        Args:
            start_date: Start date in YYYY-MM-DD format

        Returns:
            Tuple containing:
            - dates
            - total_nacional_nivel_general
            - total_nacional_estacionales
            - total_nacional_regulados
            - total_nacional_nucleo
            - gba_nivel_general
            - gba_estacionales
            - gba_regulados
            - gba_nucleo
        """
        response = self._download_latest_available_excel()
        df = self._parse_excel_to_dataframe(response.content)
        return self._extract_all_cpi_data(df, start_date)

    def _download_latest_available_excel(self) -> requests.Response:
        """Download the latest available INDEC Excel file."""
        for month_offset in range(5):
            target_date = datetime.now() - timedelta(days=month_offset * 30)
            url = self._build_excel_url_for_date(target_date)

            response = self._try_download_from_url(url)
            if response:
                logger.info(f"INDEC CPI: Downloaded file from {url}")
                return response

        raise ValueError("No INDEC file found")

    def _build_excel_url_for_date(self, date: datetime) -> str:
        """Build the Excel file URL for a given date."""
        month = date.strftime("%m")
        year = date.strftime("%y")
        filename = f"sh_ipc_{month}_{year}.xls"
        return f"{self.base_url}{filename}"

    def _try_download_from_url(self, url: str) -> requests.Response | None:
        """Try to download file from URL."""
        try:
            response = requests.get(url, timeout=10)
            if self._is_valid_excel_response(response):
                return response
        except requests.RequestException as e:
            logger.debug(f"INDEC CPI: Failed to download from {url}: {e}")
        return None

    def _is_valid_excel_response(self, response: requests.Response) -> bool:
        """Check if response is a valid Excel file."""
        if response.status_code != 200:
            return False
        content_type = response.headers.get("Content-Type", "")
        return "excel" in content_type.lower()

    def _parse_excel_to_dataframe(self, content: bytes) -> pd.DataFrame:
        """Parse Excel content to DataFrame."""
        return pd.read_excel(
            io.BytesIO(content), sheet_name=0, header=None, engine="xlrd"
        )

    def _extract_all_cpi_data(
        self, df: pd.DataFrame, start_date: str
    ) -> tuple[
        list[list[str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
    ]:
        """Extract all CPI data from DataFrame."""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        dates: list[list[str]] = []
        total_nacional = {key: [] for key in self.TOTAL_NACIONAL_ROWS}
        gba = {key: [] for key in self.GBA_ROWS}

        for col_idx in range(1, len(df.columns)):
            date_str = self._extract_formatted_date_from_column(df, col_idx, start_dt)
            if not date_str:
                continue

            dates.append([date_str])
            self._append_values_for_region(
                df, col_idx, total_nacional, self.TOTAL_NACIONAL_ROWS
            )
            self._append_values_for_region(df, col_idx, gba, self.GBA_ROWS)

        return (
            dates,
            total_nacional["nivel_general"],
            total_nacional["estacionales"],
            total_nacional["regulados"],
            total_nacional["nucleo"],
            gba["nivel_general"],
            gba["estacionales"],
            gba["regulados"],
            gba["nucleo"],
        )

    def _extract_formatted_date_from_column(
        self, df: pd.DataFrame, col_idx: int, start_date: datetime
    ) -> str | None:
        """Extract and format date from column."""
        date_val = df.iloc[self.DATE_ROW, col_idx]

        if pd.isna(date_val):
            return None

        date_obj = self._parse_date_value(date_val)
        if not date_obj or date_obj < start_date:
            return None

        return date_obj.strftime("%d/%m/%Y")

    def _parse_date_value(self, date_val: Any) -> datetime | None:
        """Parse a date value from the Excel file."""
        try:
            if isinstance(date_val, str):
                return pd.to_datetime(date_val, errors="coerce")
            return pd.to_datetime(date_val)
        except (ValueError, TypeError):
            return None

    def _append_values_for_region(
        self, df: pd.DataFrame, col_idx: int, region_data: dict, row_mapping: dict
    ) -> None:
        """Append values for a specific region."""
        for key, row_idx in row_mapping.items():
            value = self._extract_percentage_from_cell(df, row_idx, col_idx)
            region_data[key].append([value])

    def _extract_percentage_from_cell(
        self, df: pd.DataFrame, row: int, col: int
    ) -> float | str:
        """Extract percentage value from cell."""
        value = df.iloc[row, col]
        return self._format_as_percentage(value)

    def _format_as_percentage(self, value: Any) -> float | str:
        """Format value as percentage for sheets."""
        parsed = parse_numeric_value(value)
        return format_for_sheets(parsed, is_percentage=True)
