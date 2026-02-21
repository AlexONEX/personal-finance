"""fetch_data.py

Script unificado para la obtención de datos del Ingresos Tracker.
Obtiene CER (BCRA), CCL (Ambito/dolarapi) y proyecciones REM (BCRA).

Uso:
    uv run fetch_data.py                      # Actualización incremental
    uv run fetch_data.py --since 2022-01-01   # Backfill total
"""

import argparse
import io
import os
import sys
import warnings
from datetime import date, datetime, timedelta

import gspread
import openpyxl
import requests
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client

# Configuración de advertencias y logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

load_dotenv()

# ---------------------------------------------------------------------------
# Configuración Global
# ---------------------------------------------------------------------------
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SERVICE_ACCOUNT = "service_account.json"

HISTORIC_SHEET = "historic_data"
REM_SHEET = "REM"
FIRST_DATA_ROW = 4  # Metadata(1) + Headers(2) + Spacer(3)
BACKFILL_FROM = date(2022, 1, 1)

BCRA_API_URL = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30"
AMBITO_CCL_URL = "https://mercados.ambito.com//dolarrava/cl/grafico/{desde}/{hasta}"
BCRA_TODOS_REM_URL = "https://www.bcra.gob.ar/todos-relevamiento-de-expectativas-de-mercado-rem/"
BCRA_BASE_URL = "https://www.bcra.gob.ar"

MONTHS_MAP = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

# ---------------------------------------------------------------------------
# Lógica de CER y CCL (Histórico)
# ---------------------------------------------------------------------------

def fetch_cer(since: date, until: date) -> dict[date, float]:
    results = {}
    offset, limit = 0, 3000
    print(f"  CER: obteniendo {since} → {until} desde BCRA...")
    while True:
        try:
            resp = requests.get(BCRA_API_URL, params={
                "desde": since.isoformat(), "hasta": until.isoformat(),
                "limit": limit, "offset": offset
            }, verify=False, timeout=30)
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
            if offset >= total or not detalle: break
        except Exception as e:
            print(f"  ERROR CER: {e}")
            break
    print(f"  CER: {len(results)} registros.")
    return results

def fetch_ccl_ambito(since: date, until: date) -> dict[date, float]:
    url = AMBITO_CCL_URL.format(desde=since.isoformat(), hasta=until.isoformat())
    print(f"  CCL: obteniendo {since} → {until} desde Ambito...")
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
        resp = requests.get("https://dolarapi.com/v1/dolares/contadoconliqui", timeout=10)
        resp.raise_for_status()
        body = resp.json()
        venta = body.get("venta")
        fecha = body.get("fechaActualizacion", "")
        if venta and fecha:
            d = datetime.fromisoformat(fecha.replace("Z", "+00:00")).date()
            return d, float(venta)
    except: pass
    return None

# ---------------------------------------------------------------------------
# Lógica de REM (Proyecciones)
# ---------------------------------------------------------------------------

def get_rem_publication_links(since_date: tuple[int, int]) -> list[dict]:
    print(f"  REM: buscando reportes en {BCRA_TODOS_REM_URL}...")
    r = requests.get(BCRA_TODOS_REM_URL, verify=False, timeout=30)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    if not table: return []
    links = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) < 3: continue
        link_tag = cols[0].find('a', href=True)
        if not link_tag: continue
        period_text = cols[2].get_text(strip=True)
        try:
            m_text, y_text = period_text.split()
            period_date = (int(y_text), MONTHS_MAP[m_text.lower()])
            if period_date < since_date: continue
            pub_url = link_tag['href']
            if not pub_url.startswith('http'): pub_url = BCRA_BASE_URL + pub_url
            links.append({'url': pub_url, 'date': period_date, 'period': period_text})
        except: continue
    return sorted(links, key=lambda x: x['date'])

def get_xlsx_from_publication(pub_url: str) -> str | None:
    try:
        r = requests.get(pub_url, verify=False, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            text, href = link.get_text().lower(), link['href'].lower()
            if ('tablas' in text or 'tablas' in href) and href.endswith('.xlsx'):
                return link['href'] if link['href'].startswith('http') else BCRA_BASE_URL + link['href']
    except: pass
    return None

def download_and_parse_rem(url: str) -> list[float]:
    try:
        r = requests.get(url, verify=False, timeout=30)
        wb = openpyxl.load_workbook(io.BytesIO(r.content), data_only=True)
        sheet = wb.worksheets[0]
        projections = []
        for row in range(7, 14): # M a M+6
            val = sheet.cell(row=row, column=4).value
            projections.append(float(val)/100.0 if val is not None else 0.0)
        val_12m = sheet.cell(row=14, column=4).value
        projections.append(float(val_12m)/100.0 if val_12m is not None else 0.0)
        return projections
    except: return []

# ---------------------------------------------------------------------------
# Escritura en Google Sheets
# ---------------------------------------------------------------------------

def update_sheets(cer_data, ccl_data, rem_reports):
    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)
    
    # 1. Update historic_data
    if cer_data or ccl_data:
        print(f"  Actualizando {HISTORIC_SHEET}...")
        ws_h = ss.worksheet(HISTORIC_SHEET)
        all_dates = sorted(cer_data.keys() | ccl_data.keys())
        payload = [[d.strftime("%d/%m/%Y"), cer_data.get(d, ""), ccl_data.get(d, "")] for d in all_dates]
        # Clear and write
        ws_h.batch_clear([f"A{FIRST_DATA_ROW}:C2000"])
        ws_h.update(range_name=f"A{FIRST_DATA_ROW}:C{FIRST_DATA_ROW + len(payload) - 1}", values=payload, value_input_option="USER_ENTERED")

    # 2. Update REM matrix
    if rem_reports:
        print(f"  Actualizando {REM_SHEET}...")
        ws_r = ss.worksheet(REM_SHEET)
        headers = ["Mes Reporte", "Mes M", "Mes M+1", "Mes M+2", "Mes M+3", "Mes M+4", "Mes M+5", "Mes M+6", "Próx. 12m"]
        sorted_reports = sorted(rem_reports.keys())
        payload = [[m] + rem_reports[m] for m in sorted_reports]
        ws_r.batch_clear(["A4:I100"])
        ws_r.update(range_name=f"A4:I{4 + len(payload) - 1}", values=payload, value_input_option="USER_ENTERED")

def main():
    parser = argparse.ArgumentParser(description="Fetch all data for Ingresos Tracker")
    parser.add_argument("--since", type=str, default=BACKFILL_FROM.isoformat(), help="Fecha inicio YYYY-MM-DD")
    args = parser.parse_args()
    
    since_dt = datetime.strptime(args.since, "%Y-%m-%d").date()
    until_dt = date.today()
    
    print(f"--- Iniciando actualización desde {since_dt} ---")
    
    # CER + CCL
    cer = fetch_cer(since_dt, until_dt)
    ccl = fetch_ccl_ambito(since_dt, until_dt)
    today = fetch_ccl_today()
    if today and today[0] >= since_dt: ccl[today[0]] = today[1]
    
    # REM
    rem_links = get_rem_publication_links((since_dt.year, since_dt.month))
    rem_reports = {}
    for pub in rem_links:
        print(f"  REM: procesando {pub['period']}...")
        xlsx = get_xlsx_from_publication(pub['url'])
        if xlsx:
            projs = download_and_parse_rem(xlsx)
            if projs: rem_reports[f"{pub['date'][0]}-{pub['date'][1]:02d}-01"] = projs
            
    update_sheets(cer, ccl, rem_reports)
    print("
✓ Datos actualizados correctamente.")

if __name__ == "__main__":
    main()
