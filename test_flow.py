#!/usr/bin/env python3

import os
import sys
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

from fetch_historic import fetch_cer, fetch_ccl_ambito, fetch_ccl_today

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SERVICE_ACCOUNT = "service_account.json"


def test_connection():
    """Test 1: Conexión a Google Sheets"""
    print("\n" + "=" * 60)
    print("TEST 1: Conexión a Google Sheets")
    print("=" * 60)

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
        client = gspread.authorize(creds)
        ss = client.open_by_key(SPREADSHEET_ID)

        print(f"✓ Conectado: {ss.title}")
        print(f"  URL: {ss.url}")

        sheets = [ws.title for ws in ss.worksheets()]
        print(f"  Sheets disponibles: {', '.join(sheets)}")

        return ss
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_fetch_apis():
    """Test 2: APIs de datos (sin escribir)"""
    print("\n" + "=" * 60)
    print("TEST 2: Fetch de APIs (CER + CCL)")
    print("=" * 60)

    since = date(2026, 2, 10)
    until = date(2026, 2, 19)

    # Test CER (últimos 5 días)
    print("\n[CER - BCRA API]")
    try:
        cer_data = fetch_cer(since, until)

        print(f"✓ CER: {len(cer_data)} registros")
        if cer_data:
            last_3 = sorted(cer_data.items())[-3:]
            for d, val in last_3:
                print(f"  {d}: {val:.4f}")
    except Exception as e:
        print(f"✗ CER Error: {e}")

    # Test CCL Ambito (últimos 5 días)
    print("\n[CCL - Ambito grafico]")
    try:
        ccl_data = fetch_ccl_ambito(since, until)

        print(f"✓ CCL: {len(ccl_data)} registros")
        if ccl_data:
            last_3 = sorted(ccl_data.items())[-3:]
            for d, val in last_3:
                print(f"  {d}: ${val:.2f}")
    except Exception as e:
        print(f"✗ CCL Error: {e}")

    # Test CCL today
    print("\n[CCL - dolarapi hoy]")
    try:
        today_data = fetch_ccl_today()
        if today_data:
            d, val = today_data
            print(f"✓ CCL hoy: {d} = ${val:.2f}")
        else:
            print("⚠ No data from dolarapi")
    except Exception as e:
        print(f"✗ dolarapi Error: {e}")


def test_historic_data(ss):
    """Test 3: Verificar historic_data sheet"""
    print("\n" + "=" * 60)
    print("TEST 3: Verificar historic_data")
    print("=" * 60)

    try:
        ws = ss.worksheet("historic_data")

        # Check metadata row
        row1 = ws.row_values(1)
        print(f"✓ Metadata row: {row1[:3]}")

        # Check headers
        row2 = ws.row_values(2)
        print(f"✓ Headers: {row2[:3]}")

        # Check data count
        col_a = ws.col_values(1)
        data_count = len([v for v in col_a[2:] if v])  # Skip metadata + header
        print(f"✓ Registros de datos: {data_count}")

        # Check last 3 rows
        all_data = ws.get("A3:C")
        if all_data:
            last_3 = all_data[-3:]
            print("\nÚltimos 3 registros:")
            for row in last_3:
                fecha = row[0] if len(row) > 0 else ""
                cer = row[1] if len(row) > 1 else ""
                ccl = row[2] if len(row) > 2 else ""
                print(f"  {fecha:12} | CER: {cer:9} | CCL: {ccl}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_ingresos_sheet(ss):
    """Test 4: Verificar sheet Ingresos"""
    print("\n" + "=" * 60)
    print("TEST 4: Verificar sheet 'Ingresos'")
    print("=" * 60)

    try:
        ws = ss.worksheet("Ingresos")

        # Check headers
        row1 = ws.row_values(1)
        row2 = ws.row_values(2)

        print("✓ Group headers (row 1):")
        for i, val in enumerate(row1[:15], 1):
            if val:
                col = chr(64 + i)
                print(f"  {col}: {val}")

        print("\n✓ Column headers (row 2):")
        for i, val in enumerate(row2[:15], 1):
            if val:
                col = chr(64 + i)
                print(f"  {col}: {val}")

        # Check if there's data
        col_a = ws.col_values(1)
        data_count = len([v for v in col_a[2:] if v])  # Skip 2 header rows
        print(f"\n✓ Filas de datos ingresadas: {data_count}")

        # Sample first data row
        if data_count > 0:
            row3 = ws.get("A3:F3")[0]
            print("\nPrimera fila de datos (sample):")
            labels = ["Fecha", "Bruto", "Jubilación", "PAMI", "Obra Social", "Neto"]
            for i, (label, val) in enumerate(zip(labels, row3)):
                print(f"  {label}: {val}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_formulas(ss):
    """Test 5: Verificar que fórmulas funcionan"""
    print("\n" + "=" * 60)
    print("TEST 5: Verificar fórmulas")
    print("=" * 60)

    try:
        ws = ss.worksheet("Ingresos")

        # Get row 3 formulas
        formulas = ws.get("A3:X3", value_render_option="FORMULA")[0]

        print("Fórmulas detectadas en row 3:")
        formula_cols = []
        for i, val in enumerate(formulas[:24], 1):
            col = chr(64 + i)
            if isinstance(val, str) and val.startswith("="):
                formula_cols.append(col)
                display = val if len(val) < 60 else val[:57] + "..."
                print(f"  {col}: {display}")

        print(f"\n✓ Total fórmulas activas: {len(formula_cols)}")

        # Check if formulas are calculating
        values = ws.get("A3:X3", value_render_option="FORMATTED_VALUE")[0]
        calculated = []
        for i, val in enumerate(values[:24], 1):
            col = chr(64 + i)
            if col in formula_cols and val and val != "#ERROR!":
                calculated.append((col, val))

        print(
            f"✓ Fórmulas calculando correctamente: {len(calculated)}/{len(formula_cols)}"
        )

        if calculated:
            print("\nSample de valores calculados:")
            for col, val in calculated[:5]:
                print(f"  {col}: {val}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID not set in .env")
        sys.exit(1)

    print("=" * 60)
    print("TEST SUITE - Ingresos Tracker")
    print("=" * 60)
    print(f"Spreadsheet ID: {SPREADSHEET_ID}")

    # Run tests
    ss = test_connection()
    if not ss:
        print("\n✗ Conexión falló. Abortando tests.")
        sys.exit(1)

    test_fetch_apis()
    test_historic_data(ss)
    test_ingresos_sheet(ss)
    test_formulas(ss)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETO")
    print("=" * 60)
    print("""
Próximos pasos:
1. Para actualizar datos: ./update_daily.sh
2. Para automatizar: ./automation/install.sh
3. Para ingresar datos: Abrí la tab 'Ingresos' y completá cols A, B, G
""")


if __name__ == "__main__":
    main()
