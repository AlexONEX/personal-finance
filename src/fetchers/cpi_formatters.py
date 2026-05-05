"""Formatters for CPI data."""

from typing import Any


def parse_numeric_value(value: Any) -> float | None:
    """Parse a value into a float or None."""
    if value is None:
        return None

    if isinstance(value, int | float):
        if str(value).strip() in ("", "-", "N/A", "nan"):
            return None
        return float(value)

    if isinstance(value, str):
        value = value.strip()
        # Handle common empty or invalid values
        if value in ("", "-", "N/A", "///", ".", ".."):
            return None

        # Remove percentage symbol if it exists
        value = value.replace("%", "").strip()

        # Check if valid before attempting conversion
        if not value or value in (".", ".."):
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    # For pandas NaN, etc.
    try:
        import pandas as pd

        if pd.isna(value):
            return None
    except ImportError:
        pass

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def format_for_sheets(value: float | None, is_percentage: bool = False) -> float | str:
    """Format a value for Google Sheets.

    Args:
        value: The numeric value to format
        is_percentage: If True, value is already a percentage (e.g., 5.2 for 5.2%)

    Returns:
        The formatted value or "N/A" if None
    """
    if value is None:
        return "N/A"
    return value
