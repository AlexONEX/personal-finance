"""fetch_data.py

Script unificado para la obtención de datos del Ingresos Tracker.
Obtiene CER (BCRA), CCL (Ambito/dolarapi), SPY (yfinance) y proyecciones REM (BCRA).
"""

import argparse
import logging
import os
import urllib3
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

from dotenv import load_dotenv

from src.config import FETCH_CONFIG, MONTHS_MAP_SHORT, SHEET_LIMITS, SHEETS
from src.connectors.sheets import get_sheets_client
from src.fetchers import (
    CCLFetcher,
    CERFetcher,
    InflacionMensualFetcher,
    REMFetcher,
    SPYFetcher,
)

# Suppress only InsecureRequestWarning for BCRA (they have cert issues)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
HISTORIC_SHEET = SHEETS["HISTORIC"]
REM_SHEET = SHEETS["REM"]
FIRST_DATA_ROW = SHEET_LIMITS["first_data_row_historic"]
BACKFILL_FROM = FETCH_CONFIG["backfill_from"]


def get_last_date_from_sheet() -> date:
    """Obtiene la última fecha registrada en historic_data para actualizar desde ahí.

    Retrocede 7 días desde la última fecha válida para reescribir/actualizar datos recientes.
    Si la última fecha es futura (datos proyectados), usa hoy menos 7 días.
    """
    try:
        client = get_sheets_client()
        ss = client.open_by_key(SPREADSHEET_ID)
        ws_h = ss.worksheet(HISTORIC_SHEET)
        existing_rows = ws_h.get_all_values()[FIRST_DATA_ROW - 1 :]

        dates = []
        today = date.today()

        for row in existing_rows:
            if len(row) >= 1 and row[0]:
                try:
                    d = datetime.strptime(row[0], "%d/%m/%Y").date()
                    # Only consider dates up to today (ignore future/projected dates)
                    if d <= today:
                        dates.append(d)
                except ValueError:
                    continue

        if dates:
            last_valid_date = max(dates)
            # Rewind 7 days to rewrite/update recent data
            rewind_date = last_valid_date - timedelta(days=7)
            logger.info(f"Last valid date in sheet: {last_valid_date}, rewinding to {rewind_date} to rewrite recent data")
            return rewind_date

    except Exception as e:
        logger.error(f"Failed to get last date from sheet: {e}")

    return BACKFILL_FROM


def get_last_rem_date_from_sheet() -> tuple[int, int]:
    """
    Obtiene la última fecha (año, mes) de REM para actualizar solo datos posteriores.
    Returns: (year, month) tuple, defaults to (2022, 1) if sheet is empty.
    """
    try:
        client = get_sheets_client()
        ss = client.open_by_key(SPREADSHEET_ID)
        ws_r = ss.worksheet(REM_SHEET)
        existing_rows = ws_r.get_all_values()[3:]

        dates = []
        for row in existing_rows:
            if len(row) >= 1 and row[0]:
                date_str = row[0].strip()
                try:
                    # Try YYYY-MM-DD format first
                    if "-" in date_str and len(date_str.split("-")[0]) == 4:
                        parts = date_str.split("-")
                        year = int(parts[0])
                        month = int(parts[1])
                        dates.append((year, month))
                    # Try mmm-YY format (e.g., "ene-20")
                    elif "-" in date_str and len(date_str.split("-")[0]) <= 3:
                        parts = date_str.split("-")
                        month_str = parts[0].lower()
                        year_short = parts[1]

                        if month_str in MONTHS_MAP_SHORT:
                            month = MONTHS_MAP_SHORT[month_str]
                            year = 2000 + int(year_short)
                            dates.append((year, month))
                except (ValueError, IndexError, KeyError) as e:
                    logger.warning(f"Failed to parse REM date '{date_str}': {e}")
                    continue

        if dates:
            return max(dates)

    except Exception as e:
        logger.error(f"Failed to get last REM date from sheet: {e}")

    return (BACKFILL_FROM.year, BACKFILL_FROM.month)


def update_sheets(cer_data, ccl_data, spy_data, inflacion_data, rem_reports):
    """Actualiza las hojas de Google Sheets con los datos obtenidos."""
    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    if cer_data or ccl_data or spy_data or inflacion_data:
        ws_h = ss.worksheet(HISTORIC_SHEET)

        existing_rows = ws_h.get_all_values()[FIRST_DATA_ROW - 1 :]
        data_map = {}
        for row in existing_rows:
            if len(row) >= 1 and row[0]:
                data_map[row[0]] = [
                    row[1] if len(row) > 1 else "",
                    row[2] if len(row) > 2 else "",
                    row[3] if len(row) > 3 else "",
                    row[4] if len(row) > 4 else "",  # CER Estimado (col E)
                    row[5] if len(row) > 5 else "",  # Inflación Mensual (col F)
                ]

        for d, val in cer_data.items():
            fmt_d = d.strftime("%d/%m/%Y")
            if fmt_d not in data_map:
                data_map[fmt_d] = ["", "", "", "", ""]
            data_map[fmt_d][0] = val

        for d, val in ccl_data.items():
            fmt_d = d.strftime("%d/%m/%Y")
            if fmt_d not in data_map:
                data_map[fmt_d] = ["", "", "", "", ""]
            data_map[fmt_d][1] = val

        for d, val in spy_data.items():
            fmt_d = d.strftime("%d/%m/%Y")
            if fmt_d not in data_map:
                data_map[fmt_d] = ["", "", "", "", ""]
            data_map[fmt_d][2] = val

        # Inflación mensual se asocia al último día del mes
        for d, val in inflacion_data.items():
            fmt_d = d.strftime("%d/%m/%Y")
            if fmt_d not in data_map:
                data_map[fmt_d] = ["", "", "", "", ""]
            data_map[fmt_d][4] = val  # Columna F (índice 4 en data_map)

        sorted_dates = sorted(
            data_map.keys(), key=lambda x: datetime.strptime(x, "%d/%m/%Y")
        )
        payload = [
            [
                d,
                data_map[d][0],
                data_map[d][1],
                data_map[d][2],
                data_map[d][3],
                data_map[d][4],
            ]
            for d in sorted_dates
        ]

        ws_h.update(
            range_name=f"A{FIRST_DATA_ROW}:F{FIRST_DATA_ROW + len(payload) - 1}",
            values=payload,
            value_input_option="USER_ENTERED",
        )

    if rem_reports:
        ws_r = ss.worksheet(REM_SHEET)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws_r.update(
            range_name="B1", values=[[timestamp]], value_input_option="USER_ENTERED"
        )

        # Get raw values (dates as serial numbers) to compare correctly
        existing_rem_raw = ws_r.get("A4:I", value_render_option="UNFORMATTED_VALUE")
        existing_rem_raw = existing_rem_raw if existing_rem_raw else []

        # Convert serial dates to "YYYY-MM-DD" for comparison
        # Google Sheets epoch is 1899-12-30
        existing_months = set()
        for row in existing_rem_raw:
            if len(row) >= 1 and row[0]:
                val = row[0]
                if isinstance(val, (int, float)):
                    # Convert serial to date
                    d = date(1899, 12, 30) + timedelta(days=int(val))
                    existing_months.add(d.strftime("%Y-%m-%d"))
                elif isinstance(val, str):
                    existing_months.add(val)

        new_reports = {
            month: projs
            for month, projs in rem_reports.items()
            if month not in existing_months
        }

        if new_reports:
            # Count only rows with actual data (non-empty column A)
            rows_with_data = sum(
                1 for row in existing_rem_raw if len(row) >= 1 and row[0]
            )
            next_row = 4 + rows_with_data
            sorted_new_months = sorted(new_reports.keys())
            payload = [[m] + new_reports[m] for m in sorted_new_months]

            ws_r.update(
                range_name=f"A{next_row}:I{next_row + len(payload) - 1}",
                values=payload,
                value_input_option="USER_ENTERED",
            )
            logger.info(f"Added {len(payload)} new REM reports")
        else:
            logger.info("No new REM reports to add")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch all data for Ingresos Tracker. "
        "Por defecto, actualiza desde la última fecha registrada en el sheet."
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Fecha inicio YYYY-MM-DD (opcional, por defecto usa última fecha del sheet)",
    )
    args = parser.parse_args()

    # Validación de input
    if args.since:
        try:
            since_dt = datetime.strptime(args.since, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {args.since}. Use YYYY-MM-DD")
            return

        if since_dt > date.today():
            logger.error("Start date cannot be in the future")
            return
        if since_dt < date(2000, 1, 1):
            logger.error("Start date seems unreasonably old (before 2000)")
            return
    else:
        since_dt = get_last_date_from_sheet()

    today = date.today()
    until_dt_future = today + timedelta(days=45)

    print(
        f"Updating dataset from {since_dt} to {today} (CER until {until_dt_future})..."
    )

    # Crear instancias de fetchers
    cer_fetcher = CERFetcher()
    ccl_fetcher = CCLFetcher()
    spy_fetcher = SPYFetcher()
    inflacion_fetcher = InflacionMensualFetcher()
    rem_fetcher = REMFetcher()

    with ThreadPoolExecutor(
        max_workers=FETCH_CONFIG["max_workers_parallel"]
    ) as executor:
        future_cer = executor.submit(cer_fetcher.fetch, since_dt, until_dt_future)
        future_ccl = executor.submit(ccl_fetcher.fetch, since_dt, today)
        future_spy = executor.submit(spy_fetcher.fetch, since_dt, today)
        future_inflacion = executor.submit(inflacion_fetcher.fetch, since_dt, today)

        cer = future_cer.result()
        ccl = future_ccl.result()
        spy = future_spy.result()
        inflacion = future_inflacion.result()

    last_rem_date = get_last_rem_date_from_sheet()
    logger.info(f"Last REM date in sheet: {last_rem_date[0]}-{last_rem_date[1]:02d}")
    rem_reports = rem_fetcher.fetch(last_rem_date)
    logger.info(f"Rem report, first row data: {next(iter(rem_reports.items()), ('N/A', 'N/A'))}")

    update_sheets(cer, ccl, spy, inflacion, rem_reports)
    print("Dataset updated successfully")


if __name__ == "__main__":
    main()
