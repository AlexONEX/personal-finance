"""fetch_data.py

Script unificado para la obtención de datos del Ingresos Tracker.
Obtiene CER (BCRA), CCL (Ambito/dolarapi) y proyecciones REM (BCRA).
"""

import argparse
import io
import logging
import os
from datetime import date, datetime

import openpyxl
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SERVICE_ACCOUNT = "service_account.json"

HISTORIC_SHEET = "historic_data"
REM_SHEET = "REM"
FIRST_DATA_ROW = 4
BACKFILL_FROM = date(2022, 1, 1)

BCRA_API_URL = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30"
AMBITO_CCL_URL = "https://mercados.ambito.com//dolarrava/cl/grafico/{desde}/{hasta}"
BCRA_TODOS_REM_URL = (
    "https://www.bcra.gob.ar/todos-relevamiento-de-expectativas-de-mercado-rem/"
)
BCRA_BASE_URL = "https://www.bcra.gob.ar"

MONTHS_MAP = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def fetch_cer(since: date, until: date) -> dict[date, float]:
    results = {}
    offset, limit = 0, 3000
    logger.info(f"CER: fetching {since} -> {until} from BCRA...")

    while True:
        try:
            resp = requests.get(
                BCRA_API_URL,
                params={
                    "desde": since.isoformat(),
                    "hasta": until.isoformat(),
                    "limit": limit,
                    "offset": offset,
                },
                timeout=30,
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
                    logger.warning(f"CER: invalid date or value in record {record}: {e}")
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

    logger.info(f"CER: fetched {len(results)} records")
    return results


def fetch_ccl_ambito(since: date, until: date) -> dict[date, float]:
    url = AMBITO_CCL_URL.format(desde=since.isoformat(), hasta=until.isoformat())
    logger.info(f"CCL: fetching {since} -> {until} from Ambito...")
    out = {}

    try:
        # User-Agent needed to bypass Ambito's bot detection
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, list):
            logger.error(f"CCL Ambito: unexpected response format (not a list)")
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

    logger.info(f"CCL: fetched {len(out)} records from Ambito")
    return out


def fetch_ccl_today() -> tuple[date, float] | None:
    try:
        resp = requests.get(
            "https://dolarapi.com/v1/dolares/contadoconliqui", timeout=10
        )
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


def get_rem_publication_links(since_date: tuple[int, int]) -> list[dict]:
    logger.info(f"REM: searching for reports at {BCRA_TODOS_REM_URL}...")

    try:
        r = requests.get(BCRA_TODOS_REM_URL, timeout=30)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"REM: failed to fetch publication list: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        logger.warning("REM: no table found in publication page")
        return []

    links = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        link_tag = cols[0].find("a", href=True)
        if not link_tag:
            continue

        period_text = cols[2].get_text(strip=True)
        try:
            m_text, y_text = period_text.split()
            period_date = (int(y_text), MONTHS_MAP[m_text.lower()])

            if period_date < since_date:
                continue

            pub_url = link_tag["href"]
            if not pub_url.startswith("http"):
                pub_url = BCRA_BASE_URL + pub_url

            links.append({"url": pub_url, "date": period_date, "period": period_text})

        except (ValueError, KeyError) as e:
            logger.warning(f"REM: failed to parse row {period_text}: {e}")
            continue

    logger.info(f"REM: found {len(links)} publication links")
    return sorted(links, key=lambda x: x["date"])


def get_xlsx_from_publication(pub_url: str) -> str | None:
    try:
        r = requests.get(pub_url, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for link in soup.find_all("a", href=True):
            text, href = link.get_text().lower(), link["href"].lower()
            if ("tablas" in text or "tablas" in href) and href.endswith(".xlsx"):
                xlsx_url = link["href"]
                if not xlsx_url.startswith("http"):
                    xlsx_url = BCRA_BASE_URL + xlsx_url

                # Fix for BCRA bug: redirect internal dev links to production
                if "desa.bcra.net" in xlsx_url:
                    xlsx_url = xlsx_url.replace(
                        "sitiopublico.desa.bcra.net", "www.bcra.gob.ar"
                    )
                return xlsx_url

    except requests.exceptions.RequestException as e:
        logger.warning(f"REM: failed to fetch publication page {pub_url}: {e}")
    except Exception as e:
        logger.warning(f"REM: failed to parse publication page {pub_url}: {e}")

    return None


def download_and_parse_rem(url: str) -> list[float]:
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        wb = openpyxl.load_workbook(io.BytesIO(r.content), data_only=True)
        sheet = wb.worksheets[0]

        projections = []
        for row in range(7, 14):  # M a M+6
            val = sheet.cell(row=row, column=4).value
            if val is not None:
                try:
                    projections.append(float(val) / 100.0)
                except (ValueError, TypeError) as e:
                    logger.warning(f"REM: invalid projection value at row {row}: {val} ({e})")
                    projections.append(0.0)
            else:
                projections.append(0.0)

        val_12m = sheet.cell(row=14, column=4).value
        if val_12m is not None:
            try:
                projections.append(float(val_12m) / 100.0)
            except (ValueError, TypeError) as e:
                logger.warning(f"REM: invalid 12m projection: {val_12m} ({e})")
                projections.append(0.0)
        else:
            projections.append(0.0)

        return projections

    except requests.exceptions.RequestException as e:
        logger.error(f"REM: failed to download XLSX from {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"REM: failed to parse XLSX from {url}: {e}")
        return []


def get_last_date_from_sheet() -> date:
    """Obtiene la última fecha registrada en historic_data para actualizar desde ahí."""
    try:
        client = get_sheets_client()
        ss = client.open_by_key(SPREADSHEET_ID)
        ws_h = ss.worksheet(HISTORIC_SHEET)
        existing_rows = ws_h.get_all_values()[FIRST_DATA_ROW - 1 :]

        dates = []
        for row in existing_rows:
            if len(row) >= 1 and row[0]:
                try:
                    d = datetime.strptime(row[0], "%d/%m/%Y").date()
                    dates.append(d)
                except ValueError:
                    continue

        if dates:
            last_date = max(dates)
            logger.info(f"Last date in sheet: {last_date}")
            return last_date

    except Exception as e:
        logger.warning(f"Failed to get last date from sheet: {e}, using default {BACKFILL_FROM}")

    return BACKFILL_FROM


def update_sheets(cer_data, ccl_data, rem_reports):
    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    if cer_data or ccl_data:
        logger.info(f"Updating {HISTORIC_SHEET}...")
        ws_h = ss.worksheet(HISTORIC_SHEET)

        existing_rows = ws_h.get_all_values()[FIRST_DATA_ROW - 1 :]
        data_map = {}
        for row in existing_rows:
            if len(row) >= 1 and row[0]:
                data_map[row[0]] = [
                    row[1] if len(row) > 1 else "",
                    row[2] if len(row) > 2 else "",
                ]

        for d, val in cer_data.items():
            fmt_d = d.strftime("%d/%m/%Y")
            if fmt_d not in data_map:
                data_map[fmt_d] = ["", ""]
            data_map[fmt_d][0] = val

        for d, val in ccl_data.items():
            fmt_d = d.strftime("%d/%m/%Y")
            if fmt_d not in data_map:
                data_map[fmt_d] = ["", ""]
            data_map[fmt_d][1] = val

        sorted_dates = sorted(
            data_map.keys(), key=lambda x: datetime.strptime(x, "%d/%m/%Y")
        )
        payload = [[d, data_map[d][0], data_map[d][1]] for d in sorted_dates]

        ws_h.update(
            range_name=f"A{FIRST_DATA_ROW}:C{FIRST_DATA_ROW + len(payload) - 1}",
            values=payload,
            value_input_option="USER_ENTERED",
        )

    if rem_reports:
        logger.info(f"Updating {REM_SHEET}...")
        ws_r = ss.worksheet(REM_SHEET)

        existing_rem = ws_r.get_all_values()[3:]
        rem_map = {}
        for row in existing_rem:
            if len(row) >= 1 and row[0]:
                rem_map[row[0]] = row[1:9]

        for m, projs in rem_reports.items():
            rem_map[m] = projs

        sorted_months = sorted(rem_map.keys())
        payload = [[m] + rem_map[m] for m in sorted_months]

        ws_r.batch_clear(["A4:I500"])
        ws_r.update(
            range_name=f"A4:I{4 + len(payload) - 1}",
            values=payload,
            value_input_option="USER_ENTERED",
        )


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

        # Validar rango de fechas razonable
        if since_dt > date.today():
            logger.error("Start date cannot be in the future")
            return
        if since_dt < date(2000, 1, 1):
            logger.error("Start date seems unreasonably old (before 2000)")
            return
    else:
        logger.info("Searching for last updated date in sheet...")
        since_dt = get_last_date_from_sheet()

    until_dt = date.today()

    logger.info(f"=== Updating dataset from {since_dt} to {until_dt} ===")

    cer = fetch_cer(since_dt, until_dt)
    ccl = fetch_ccl_ambito(since_dt, until_dt)
    today = fetch_ccl_today()
    if today and today[0] >= since_dt:
        ccl[today[0]] = today[1]

    rem_links = get_rem_publication_links((since_dt.year, since_dt.month))
    rem_reports = {}
    for pub in rem_links:
        logger.info(f"REM: processing {pub['period']}...")
        xlsx = get_xlsx_from_publication(pub["url"])
        if xlsx:
            projs = download_and_parse_rem(xlsx)
            if projs:
                rem_reports[f"{pub['date'][0]}-{pub['date'][1]:02d}-01"] = projs

    update_sheets(cer, ccl, rem_reports)
    logger.info("Dataset updated successfully")


if __name__ == "__main__":
    main()
