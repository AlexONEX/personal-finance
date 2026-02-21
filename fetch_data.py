"""fetch_data.py

Script unificado para la obtención de datos del Ingresos Tracker.
Obtiene CER (BCRA), CCL (Ambito/dolarapi) y proyecciones REM (BCRA).
"""

import argparse
import io
import os
import warnings
from datetime import date, datetime

import openpyxl
import requests
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

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
    print(f"  CER: obteniendo {since} -> {until} desde BCRA...")
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
                verify=False,
                timeout=30,
            )
            resp.raise_for_status()
            body = resp.json()
            detalle = []
            for variable in body.get("results", []):
                detalle.extend(variable.get("detalle", []))
            for record in detalle:
                d = datetime.strptime(record["fecha"], "%Y-%m-%d").date()
                results[d] = record["valor"]
            total = body.get("metadata", {}).get("resultset", {}).get("count", 0)
            offset += len(detalle)
            if offset >= total or not detalle:
                break
        except Exception as e:
            print(f"  ERROR CER: {e}")
            break
    print(f"  CER: {len(results)} registros.")
    return results


def fetch_ccl_ambito(since: date, until: date) -> dict[date, float]:
    url = AMBITO_CCL_URL.format(desde=since.isoformat(), hasta=until.isoformat())
    print(f"  CCL: obteniendo {since} -> {until} desde Ambito...")
    out = {}
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
        for row in data[1:]:
            d = datetime.strptime(str(row[0]).strip(), "%d/%m/%Y").date()
            out[d] = float(row[1])
    except Exception as e:
        print(f"  WARNING CCL Ambito: {e}")
    print(f"  CCL: {len(out)} registros.")
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
        if venta and fecha:
            d = datetime.fromisoformat(fecha.replace("Z", "+00:00")).date()
            return d, float(venta)
    except Exception:
        pass
    return None


def get_rem_publication_links(since_date: tuple[int, int]) -> list[dict]:
    print(f"  REM: buscando reportes en {BCRA_TODOS_REM_URL}...")
    r = requests.get(BCRA_TODOS_REM_URL, verify=False, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
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
        except Exception:
            continue
    return sorted(links, key=lambda x: x["date"])


def get_xlsx_from_publication(pub_url: str) -> str | None:
    try:
        r = requests.get(pub_url, verify=False, timeout=30)
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
    except Exception:
        pass
    return None


def download_and_parse_rem(url: str) -> list[float]:
    try:
        r = requests.get(url, verify=False, timeout=30)
        wb = openpyxl.load_workbook(io.BytesIO(r.content), data_only=True)
        sheet = wb.worksheets[0]
        projections = []
        for row in range(7, 14):  # M a M+6
            val = sheet.cell(row=row, column=4).value
            projections.append(float(val) / 100.0 if val is not None else 0.0)
        val_12m = sheet.cell(row=14, column=4).value
        projections.append(float(val_12m) / 100.0 if val_12m is not None else 0.0)
        return projections
    except Exception:
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
            return max(dates)
    except Exception:
        pass

    return BACKFILL_FROM


def update_sheets(cer_data, ccl_data, rem_reports):
    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)

    if cer_data or ccl_data:
        print(f"  Actualizando {HISTORIC_SHEET}...")
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
            print(f"  Actualizando {REM_SHEET}...")
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

    if args.since:
        since_dt = datetime.strptime(args.since, "%Y-%m-%d").date()
    else:
        print("  Buscando última fecha actualizada en el sheet...")
        since_dt = get_last_date_from_sheet()

    until_dt = date.today()

    print(f"--- Actualizando dataset desde {since_dt} hasta {until_dt} ---")

    cer = fetch_cer(since_dt, until_dt)
    ccl = fetch_ccl_ambito(since_dt, until_dt)
    today = fetch_ccl_today()
    if today and today[0] >= since_dt:
        ccl[today[0]] = today[1]

    rem_links = get_rem_publication_links((since_dt.year, since_dt.month))
    rem_reports = {}
    for pub in rem_links:
        print(f"  REM: procesando {pub['period']}...")
        xlsx = get_xlsx_from_publication(pub["url"])
        if xlsx:
            projs = download_and_parse_rem(xlsx)
            if projs:
                rem_reports[f"{pub['date'][0]}-{pub['date'][1]:02d}-01"] = projs

    update_sheets(cer, ccl, rem_reports)
    print("\nDatos actualizados correctamente.")


if __name__ == "__main__":
    main()
