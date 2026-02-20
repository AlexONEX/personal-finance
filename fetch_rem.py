import os
import requests
import openpyxl
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import urllib3

from src.connectors.sheets import get_sheets_client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

REM_URL = "https://www.bcra.gob.ar/relevamiento-expectativas-mercado-rem/"
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
REM_SHEET_NAME = "REM"

def get_rem_xlsx_link():
    r = requests.get(REM_URL, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        if 'tablas-relevamiento-expectativas-mercado' in link['href'] and link['href'].endswith('.xlsx'):
            return "https://www.bcra.gob.ar" + link['href']
    return None

def download_and_parse_rem(url):
    r = requests.get(url, verify=False)
    with open("temp_rem.xlsx", "wb") as f:
        f.write(r.content)
    
    wb = openpyxl.load_workbook("temp_rem.xlsx", data_only=True)
    sheet = wb.worksheets[0] 
    
    data_table = []
    # Según debug: Rows 7 a 13 tienen los próximos meses
    for row in range(7, 14):
        date_val = sheet.cell(row=row, column=2).value # Periodo (datetime)
        val = sheet.cell(row=row, column=4).value # Mediana
        if val is not None and hasattr(date_val, 'year'):
            # Guardamos como YYYY-MM-01 para que Sheets lo tome como fecha
            data_table.append([
                f"{date_val.year}-{date_val.month}-01",
                float(val)/100.0
            ])
    return data_table

def update_rem_sheet(data_table):
    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)
    
    try:
        ws = ss.worksheet(REM_SHEET_NAME)
    except:
        ws = ss.add_worksheet(title=REM_SHEET_NAME, rows=50, cols=5)
    
    ws.clear()
    
    # Header de metadata
    metadata = [
        ["Última Actualización REM", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["", ""],
        ["Mes Proyectado", "Inflación Esperada (%)"]
    ]
    
    ws.update("A1", metadata, value_input_option="USER_ENTERED")
    ws.update("A4", data_table, value_input_option="USER_ENTERED")
    
    # Formateo
    ws.format("B4:B20", {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}})
    ws.format("A4:A20", {"numberFormat": {"type": "DATE", "pattern": "mmm-yy"}})
    ws.format("A3:B3", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.2, "green": 0.3, "blue": 0.4}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}}})

if __name__ == "__main__":
    link = get_rem_xlsx_link()
    if link:
        print(f"Descargando REM desde: {link}")
        data = download_and_parse_rem(link)
        update_rem_sheet(data)
        print("✓ Sheet 'REM' actualizado con tabla de búsqueda dinámica.")
    else:
        print("No se encontró el link del REM.")
