"""Fetcher for CABA Argentina CPI (Índice de Precios al Consumidor CABA)."""

import io
import logging
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.fetchers.cpi_formatters import format_for_sheets, parse_numeric_value

logger = logging.getLogger(__name__)


class CABACPIFetcher:
    """Fetches CABA CPI data from official Excel files."""

    DEFAULT_PAGE_URL = "https://www.estadisticaciudad.gob.ar/eyc/banco-datos/ipcba-base-2021-100-evolucion-del-nivel-general-estacionales-regulados-y-resto-ipcba-indices-y-variaciones-porcentuales-respecto-del-mes-anterior-ciudad-de-buenos-aires-febrero-de-2022-ago/"

    DATA_START_ROW = 4
    INDICES_COLUMNS: dict[str, int] = {
        "nivel_general": 1,
        "estacionales": 2,
        "regulados": 3,
        "resto": 4,
    }
    VARIATIONS_COLUMNS: dict[str, int] = {
        "nivel_general": 5,
        "estacionales": 6,
        "regulados": 7,
        "resto": 8,
    }

    def __init__(self, page_url: str | None = None) -> None:
        """Initialize the CABA CPI fetcher.

        Args:
            page_url: Optional custom page URL to scrape Excel from
        """
        self.page_url = page_url or self.DEFAULT_PAGE_URL

    def fetch(
        self, start_date: str = "2022-02-01"
    ) -> tuple[
        list[list[str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[str]],
        list[list[str]],
        list[list[str]],
        list[list[str]],
    ]:
        """Fetch CABA CPI data.

        Args:
            start_date: Start date in YYYY-MM-DD format

        Returns:
            Tuple containing:
            - dates
            - indices_nivel_general
            - indices_estacionales
            - indices_regulados
            - indices_resto
            - variations_nivel_general
            - variations_estacionales
            - variations_regulados
            - variations_resto
        """
        excel_url = self._scrape_latest_excel_url()
        response = self._download_excel_from_url(excel_url)
        df = self._parse_excel_to_dataframe(response.content)
        return self._extract_all_cpi_data(df, start_date)

    def _scrape_latest_excel_url(self) -> str:
        """Scrape the latest Excel URL from the CABA statistics page."""
        html_content = self._fetch_page_content()
        return self._find_excel_url_in_html(html_content)

    def _fetch_page_content(self) -> bytes:
        """Fetch the HTML content from the page."""
        response = requests.get(self.page_url)
        response.raise_for_status()
        logger.info(f"CABA CPI: Fetched page content from {self.page_url}")
        return response.content

    def _find_excel_url_in_html(self, html_content: bytes) -> str:
        """Find the Excel URL in the HTML content."""
        soup = BeautifulSoup(html_content, "html.parser")

        for link in soup.find_all("a", href=True):
            if self._is_ipcba_excel_link(link["href"]):
                logger.info(f"CABA CPI: Found Excel URL: {link['href']}")
                return link["href"]

        raise ValueError("No Excel file found on CABA statistics page")

    def _is_ipcba_excel_link(self, href: str) -> bool:
        """Check if link is an IPCBA Excel file."""
        return ".xlsx" in href and "IPCBA" in href

    def _download_excel_from_url(self, url: str) -> requests.Response:
        """Download Excel file from URL."""
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"CABA CPI: Downloaded Excel file from {url}")
        return response

    def _parse_excel_to_dataframe(self, content: bytes) -> pd.DataFrame:
        """Parse Excel content to DataFrame."""
        return pd.read_excel(io.BytesIO(content), sheet_name=0, header=None)

    def _extract_all_cpi_data(
        self, df: pd.DataFrame, start_date: str
    ) -> tuple[
        list[list[str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[float | str]],
        list[list[str]],
        list[list[str]],
        list[list[str]],
        list[list[str]],
    ]:
        """Extract all CPI data from DataFrame."""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        dates: list[list[str]] = []
        indices = {key: [] for key in self.INDICES_COLUMNS}
        variations = {key: [] for key in self.VARIATIONS_COLUMNS}

        for row_idx in range(self.DATA_START_ROW, len(df)):
            date_str = self._extract_formatted_date_from_row(df, row_idx, start_dt)
            if date_str is None:
                break
            if date_str == "":
                continue

            dates.append([date_str])
            self._append_index_values_from_row(df, row_idx, indices)
            self._append_variation_values_from_row(df, row_idx, variations)

        return (
            dates,
            indices["nivel_general"],
            indices["estacionales"],
            indices["regulados"],
            indices["resto"],
            variations["nivel_general"],
            variations["estacionales"],
            variations["regulados"],
            variations["resto"],
        )

    def _extract_formatted_date_from_row(
        self, df: pd.DataFrame, row_idx: int, start_date: datetime
    ) -> str | None:
        """Extract and format date from row."""
        row_date = df.iloc[row_idx, 0]

        if pd.isna(row_date):
            return None

        if self._is_invalid_date_marker(row_date):
            return None

        date_obj = self._parse_date_from_cell(row_date)
        if not date_obj:
            return ""

        if date_obj < start_date:
            return ""

        return date_obj.strftime("%d/%m/%Y")

    def _is_invalid_date_marker(self, value: Any) -> bool:
        """Check if value is an invalid date marker."""
        if not isinstance(value, str):
            return False
        return value.startswith("///") or "no corresponde" in value.lower()

    def _parse_date_from_cell(self, date_val: Any) -> datetime | None:
        """Parse a date value from the Excel file."""
        try:
            if isinstance(date_val, str):
                return datetime.strptime(date_val, "%Y-%m-%d")
            return pd.to_datetime(date_val)
        except (ValueError, TypeError):
            return None

    def _append_index_values_from_row(
        self, df: pd.DataFrame, row_idx: int, indices: dict
    ) -> None:
        """Append index values from row."""
        for key, col_idx in self.INDICES_COLUMNS.items():
            value = self._extract_numeric_value_from_cell(df, row_idx, col_idx)
            indices[key].append([value])

    def _append_variation_values_from_row(
        self, df: pd.DataFrame, row_idx: int, variations: dict
    ) -> None:
        """Append variation values from row."""
        for key, col_idx in self.VARIATIONS_COLUMNS.items():
            value = self._extract_percentage_from_cell(df, row_idx, col_idx)
            variations[key].append([value])

    def _extract_numeric_value_from_cell(
        self, df: pd.DataFrame, row: int, col: int
    ) -> float | str:
        """Extract numeric value from cell."""
        value = df.iloc[row, col]
        return self._format_as_numeric(value)

    def _extract_percentage_from_cell(
        self, df: pd.DataFrame, row: int, col: int
    ) -> float | str:
        """Extract percentage value from cell."""
        value = df.iloc[row, col]
        return self._format_as_percentage(value)

    def _format_as_numeric(self, value: Any) -> float | str:
        """Format value as numeric for sheets."""
        if self._is_empty_value(value):
            return "N/A"

        try:
            return float(value)
        except (ValueError, TypeError):
            return "N/A"

    def _format_as_percentage(self, value: Any) -> float | str:
        """Format value as percentage for sheets."""
        if self._is_empty_value(value):
            return "N/A"

        parsed = parse_numeric_value(value)
        return format_for_sheets(parsed, is_percentage=True)

    def _is_empty_value(self, value: Any) -> bool:
        """Check if value is empty."""
        return pd.isna(value) or value == "///" or value == ""
