"""upload_to_inversiones.py

Lee el CSV de portfolio evolution y lo sube a la sheet Inversiones.
Solo sube datos RAW (columnas A-J), el resto son FÓRMULAS que buscan en historic_data.
"""

import csv
import os
from datetime import datetime, date
from calendar import monthrange
from dotenv import load_dotenv

from src.connectors.sheets import get_sheets_client

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
INVERSIONES_SHEET = "Inversiones"
HISTORIC_DATA_SHEET = "historic_data"


def load_portfolio_data(csv_file: str) -> list[dict]:
    """Carga datos del CSV de portfolio evolution."""
    data = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


def prepare_raw_data(portfolio_data: list[dict]) -> list[list]:
    """
    Prepara solo los datos RAW para subir (columnas A-J).

    A: Mes (formato dd/mm/yyyy - primer día del mes)
    B: Ingreso ARS
    C: Egreso ARS
    D: Valor Inicio ARS
    E: Valor Fin ARS
    F: Ganancia/Pérdida ARS
    G: Ingreso USD
    H: Egreso USD
    I: Valor Fin USD
    J: Ganancia/Pérdida USD
    """
    rows = []

    for data in portfolio_data:
        # Convert mes YYYY-MM to dd/mm/yyyy (first day of month)
        mes = data["Mes"]
        year, month = map(int, mes.split("-"))
        fecha = date(year, month, 1)
        fecha_str = fecha.strftime("%d/%m/%Y")

        rows.append([
            fecha_str,                          # A
            float(data["Ingresos ARS"]),        # B
            float(data["Egresos ARS"]),         # C
            float(data["Inicio ARS"]),          # D
            float(data["Fin ARS"]),             # E
            float(data["Ganancia ARS"]),        # F
            float(data["Ingresos USD"]),        # G
            float(data["Egresos USD"]),         # H
            float(data["Fin USD"]),             # I
            float(data["Ganancia USD"]),        # J
        ])

    return rows


def create_formulas(row_num: int) -> list:
    """
    Crea fórmulas para columnas K-X de una fila.

    K: CCL Fin Mes (último CCL del mes)
    L: Valor Fin USD*CCL
    M: Rendimiento % MoM
    N: Rendimiento % Acumulado
    O: CER Inicio Mes
    P: CER Fin Mes
    Q: Δ% CER MoM
    R: Rendimiento MoM vs CER
    S: Rendimiento Acumulado vs CER
    T: CCL Inicio Mes
    U: CCL Fin Mes
    V: Δ% CCL MoM
    W: Rendimiento MoM vs CCL
    X: Rendimiento Acumulado vs CCL
    """
    r = row_num
    prev_r = row_num - 1

    # Helper: último día del mes
    ultimo_dia_formula = f'DATE(YEAR(A{r}), MONTH(A{r}), DAY(EOMONTH(A{r}, 0)))'

    formulas = [
        # K: CCL Fin Mes
        f'=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH({ultimo_dia_formula}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-")',

        # L: Valor Fin USD * CCL
        f'=IF(K{r}="-", "-", I{r}*K{r})',

        # M: Rendimiento % MoM = (Fin - Inicio - Ingresos + Egresos) / (Inicio + Ingresos - Egresos)
        f'=IF(D{r}=0, "-", (E{r}-D{r}-B{r}+C{r})/(D{r}+B{r}-C{r}))',

        # N: Rendimiento % Acumulado
        f'=IF(M{r}="-", "-", IF(ROW(A{r})=2, M{r}, (1+N{prev_r})*(1+M{r})-1))',

        # O: CER Inicio Mes (primer día del mes)
        f'=IFERROR(VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE), "-")',

        # P: CER Fin Mes (último día del mes)
        f'=IFERROR(VLOOKUP({ultimo_dia_formula}, historic_data!$A$4:$B, 2, TRUE), "-")',

        # Q: Δ% CER MoM
        f'=IF(OR(O{r}="-", P{r}="-"), "-", (P{r}/O{r})-1)',

        # R: Rendimiento MoM vs CER
        f'=IF(OR(M{r}="-", Q{r}="-"), "-", M{r}-Q{r})',

        # S: Rendimiento Acumulado vs CER
        f'=IF(OR(N{r}="-", Q{r}="-"), "-", IF(ROW(A{r})=2, R{r}, (1+S{prev_r})*(1+R{r})-1))',

        # T: CCL Inicio Mes
        f'=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(A{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-")',

        # U: CCL Fin Mes
        f'=K{r}',

        # V: Δ% CCL MoM
        f'=IF(OR(T{r}="-", U{r}="-"), "-", (U{r}/T{r})-1)',

        # W: Rendimiento MoM vs CCL
        f'=IF(OR(M{r}="-", V{r}="-"), "-", M{r}-V{r})',

        # X: Rendimiento Acumulado vs CCL
        f'=IF(OR(N{r}="-", V{r}="-"), "-", IF(ROW(A{r})=2, W{r}, (1+X{prev_r})*(1+W{r})-1))',
    ]

    return formulas


def upload_to_sheet(client, data_rows: list[list]):
    """Sube datos RAW y fórmulas a la sheet Inversiones."""
    ss = client.open_by_key(SPREADSHEET_ID)
    ws = ss.worksheet(INVERSIONES_SHEET)

    # Headers
    headers = [
        "Mes",
        "Ingreso ARS",
        "Egreso ARS",
        "Valor Inicio ARS",
        "Valor Fin ARS",
        "Ganancia/Pérdida ARS",
        "Ingreso USD",
        "Egreso USD",
        "Valor Fin USD",
        "Ganancia/Pérdida USD",
        "CCL Fin Mes",
        "Valor Fin USD*CCL",
        "Rendimiento % MoM",
        "Rendimiento % Acum",
        "CER Inicio",
        "CER Fin",
        "Δ% CER MoM",
        "Rend MoM vs CER",
        "Rend Acum vs CER",
        "CCL Inicio",
        "CCL Fin",
        "Δ% CCL MoM",
        "Rend MoM vs CCL",
        "Rend Acum vs CCL",
    ]

    # Clear existing data
    print(f"Clearing existing data in {INVERSIONES_SHEET}...")
    last_row = len(data_rows) + 10
    ws.batch_clear([f"A1:X{last_row}"])

    # Upload headers
    print(f"Uploading headers...")
    ws.update(range_name="A1:X1", values=[headers])

    # Upload RAW data (A-J)
    print(f"Uploading {len(data_rows)} rows of raw data (columns A-J)...")
    ws.update(
        range_name=f"A2:J{len(data_rows) + 1}",
        values=data_rows,
        value_input_option="USER_ENTERED",
    )

    # Upload formulas (K-X)
    print(f"Uploading formulas (columns K-X)...")
    formula_updates = []

    for i, row in enumerate(data_rows, start=2):  # Start at row 2
        formulas = create_formulas(i)
        formula_row = [[f] for f in formulas]  # Convert to column format

        # Batch update for this row
        formula_updates.append({
            "range": f"K{i}:X{i}",
            "values": [formulas]
        })

    # Batch update all formulas
    if formula_updates:
        ws.batch_update(formula_updates, value_input_option="USER_ENTERED")

    print("✅ Upload complete!")


def main():
    print("=" * 60)
    print("   UPLOAD TO INVERSIONES   ")
    print("=" * 60)

    csv_file = "portfolio_evolution.csv"

    # Load data
    print(f"\n1. Loading portfolio data from {csv_file}...")
    portfolio_data = load_portfolio_data(csv_file)
    print(f"   Loaded {len(portfolio_data)} months")

    # Prepare raw data
    print(f"\n2. Preparing raw data (columns A-J)...")
    data_rows = prepare_raw_data(portfolio_data)
    print(f"   Prepared {len(data_rows)} rows")

    # Upload
    print(f"\n3. Uploading to sheet {INVERSIONES_SHEET}...")
    client = get_sheets_client()
    upload_to_sheet(client, data_rows)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    print("\nColumnas A-J: Datos de IEB")
    print("Columnas K-X: Fórmulas que buscan en historic_data")


if __name__ == "__main__":
    main()
