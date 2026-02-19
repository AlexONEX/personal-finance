"""Aggregation logic for converting daily data to monthly end-of-month values."""

from collections import defaultdict
from datetime import date, datetime


def _parse_date(s: str) -> date | None:
    """Parse DD/MM/YYYY date string."""
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None


def _parse_float(s: str) -> float | None:
    """Parse float, return None if invalid."""
    try:
        return float(s) if s else None
    except (ValueError, TypeError):
        return None


def aggregate_to_monthly(
    rows: list[list[str]],
) -> list[tuple[date, float | None, float | None]]:
    """Group daily data by month, take end-of-month values.

    Args:
        rows: List of [fecha_str, cer_str, ccl_str] from historic_data

    Returns:
        List of (first_of_month_date, cer_eom, ccl_eom) sorted by date
    """
    # Group by (year, month) -> {date: (cer, ccl)}
    monthly: dict[tuple[int, int], dict[date, tuple[float | None, float | None]]] = (
        defaultdict(dict)
    )

    for row in rows:
        if len(row) < 3:
            continue
        d = _parse_date(row[0])
        if not d:
            continue
        cer = _parse_float(row[1])
        ccl = _parse_float(row[2])
        monthly[(d.year, d.month)][d] = (cer, ccl)

    # For each month, take the latest date
    result: list[tuple[date, float | None, float | None]] = []
    for (year, month), dates_data in sorted(monthly.items()):
        last_date = max(dates_data.keys())
        cer_eom, ccl_eom = dates_data[last_date]
        # Store as first-of-month for VLOOKUP matching
        first_of_month = date(year, month, 1)
        result.append((first_of_month, cer_eom, ccl_eom))

    return result
