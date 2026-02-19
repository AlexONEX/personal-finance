"""compute_market.py

Aggregates daily data from historic_data into monthly end-of-month values
in market_data.

Logic:
  1. Read all rows from historic_data (Fecha, CER, CCL)
  2. Group by (year, month)
  3. Take the last available date of each month
  4. Write to market_data:
     - Fecha: first day of the month (for VLOOKUP matching in test sheet)
     - CER: end-of-month value
     - CCL: end-of-month value
     - Δ columns auto-calculate via formulas (already set by setup_sheet.py)

Usage:
    uv run compute_market.py
"""

import os
import sys
from collections import defaultdict
from datetime import date, datetime

import gspread
from dotenv import load_dotenv

from auth import get_gspread_client

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
HISTORIC_SHEET = "historic_data"
MARKET_SHEET = "market_data"
FIRST_DATA_ROW = 3


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
    # Group by (year, month) → {date: (cer, ccl)}
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


def main() -> None:
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID not set in .env", file=sys.stderr)
        sys.exit(1)

    print("Connecting to Google Sheets...")
    client = get_gspread_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # Read historic_data
    print(f"Reading {HISTORIC_SHEET!r}...")
    ws_historic = spreadsheet.worksheet(HISTORIC_SHEET)
    all_values = ws_historic.get_all_values()

    if len(all_values) < FIRST_DATA_ROW:
        print(f"  No data in {HISTORIC_SHEET}", file=sys.stderr)
        sys.exit(1)

    # Skip metadata (row 1) and headers (row 2), get data rows
    data_rows = all_values[FIRST_DATA_ROW - 1 :]
    print(f"  Found {len(data_rows)} daily records")

    # Aggregate to monthly
    print("Aggregating to monthly end-of-month values...")
    monthly_data = aggregate_to_monthly(data_rows)
    print(f"  Aggregated to {len(monthly_data)} months")

    if not monthly_data:
        print("  No monthly data to write.")
        return

    # Write to market_data
    print(f"Writing to {MARKET_SHEET!r}...")
    ws_market = spreadsheet.worksheet(MARKET_SHEET)

    # Clear existing data (keep row 1 = groups, row 2 = headers)
    existing = len([v for v in ws_market.col_values(1)[FIRST_DATA_ROW - 1 :] if v])
    if existing > 0:
        end_row = FIRST_DATA_ROW + existing - 1
        ws_market.batch_clear([f"A{FIRST_DATA_ROW}:B{end_row}", f"F{FIRST_DATA_ROW}:F{end_row}"])
        print(f"  Cleared {existing} existing rows")

    # Prepare payload: only write Fecha (A), CER (B), CCL (F)
    # Columns C/D/E (Δ CER) and G (Δ CCL) have formulas, don't overwrite
    payload_a_b = []
    payload_f = []
    for first_of_month, cer, ccl in monthly_data:
        payload_a_b.append([
            first_of_month.strftime("%d/%m/%Y"),
            cer if cer is not None else "",
        ])
        payload_f.append([ccl if ccl is not None else ""])

    start = FIRST_DATA_ROW
    end = start + len(monthly_data) - 1

    # Write A:B (Fecha, CER)
    ws_market.update(
        f"A{start}:B{end}",
        payload_a_b,
        value_input_option="USER_ENTERED",
    )
    # Write F (CCL)
    ws_market.update(
        f"F{start}:F{end}",
        payload_f,
        value_input_option="USER_ENTERED",
    )

    print(f"  Written {len(monthly_data)} months → rows {start}–{end}")
    print("\n✓ Done. Δ columns will auto-calculate from formulas.")


if __name__ == "__main__":
    main()
