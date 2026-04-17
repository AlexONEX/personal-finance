#!/usr/bin/env python3
"""Marca los ascensos reales en la columna ¿Ascenso? de la tab Ingresos."""

import os
from datetime import datetime

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# Load environment
load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "service_account.json")

# Google Sheets setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
ss = gc.open_by_key(SPREADSHEET_ID)

# Fechas de ascensos reales
ASCENSOS = [
    datetime(2024, 12, 2),  # Trainee → Junior+
    datetime(2025, 8, 1),  # Junior+ → Semi-Senior
]

print("Leyendo datos de Ingresos...")
ws = ss.worksheet("Ingresos")

# Leer columna B (Fecha) desde row 3
fechas = ws.col_values(2)[2:]  # Skip headers (rows 1-2)

print(f"Total filas de datos: {len(fechas)}")
print()

# Encontrar las filas que corresponden a los ascensos
updates = []
for i, fecha_str in enumerate(fechas):
    if not fecha_str or fecha_str == "-":
        continue

    try:
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
    except ValueError:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            continue

    # Check if this date is an ascenso
    if fecha in ASCENSOS:
        row_num = i + 3  # +3 because: +2 for headers, +1 for 1-indexed
        updates.append(
            {
                "range": f"Q{row_num}",  # Column Q = ¿Ascenso?
                "values": [[True]],
            }
        )
        print(f"✓ Marcando ascenso en fila {row_num}: {fecha_str}")

if updates:
    print()
    print(f"Actualizando {len(updates)} celdas en Ingresos columna Q...")
    ws.batch_update(updates, value_input_option="USER_ENTERED")
    print("✅ Ascensos marcados correctamente")
else:
    print("⚠️  No se encontraron fechas de ascensos en los datos")

print()
print("=" * 60)
print("FECHAS DE ASCENSOS BUSCADAS:")
for fecha in ASCENSOS:
    print(f"  - {fecha.strftime('%d/%m/%Y')}")
print("=" * 60)
