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
    Prepara solo los datos RAW para subir (columnas A-I).

    A: Mes (formato dd/mm/yyyy - primer día del mes)
    B: Ingreso ARS
    C: Egreso ARS
    D: Valor Inicio ARS
    E: Valor Fin ARS
    F: Ingreso USD
    G: Egreso USD
    H: Valor Inicio USD
    I: Valor Fin USD
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
            float(data["Ingresos USD"]),        # F
            float(data["Egresos USD"]),         # G
            float(data["Inicio USD"]),          # H
            float(data["Fin USD"]),             # I
        ])

    return rows


def create_formulas(row_num: int) -> list:
    """
    Crea fórmulas para columnas J-Y de una fila.

    J: Ganancia/Pérdida ARS
    K: Ganancia/Pérdida USD
    L: CCL Fin Mes (último CCL del mes)
    M: Valor Fin USD*CCL
    N: Rendimiento % MoM
    O: Rendimiento % Acumulado
    P: CER Inicio Mes
    Q: CER Fin Mes
    R: Δ% CER MoM
    S: Rendimiento MoM vs CER
    T: Rendimiento Acumulado vs CER
    U: CCL Inicio Mes
    V: CCL Fin Mes
    W: Δ% CCL MoM
    X: Rendimiento MoM vs CCL
    Y: Rendimiento Acumulado vs CCL
    """
    r = row_num
    prev_r = row_num - 1

    # Helper: último día del mes
    ultimo_dia_formula = f'DATE(YEAR(A{r}), MONTH(A{r}), DAY(EOMONTH(A{r}, 0)))'

    formulas = [
        # J: Ganancia ARS = Fin - Inicio - Ingresos + Egresos
        f'=E{r}-D{r}-B{r}+C{r}',

        # K: Ganancia USD = Fin - Inicio - Ingresos + Egresos
        f'=I{r}-H{r}-F{r}+G{r}',

        # L: CCL Fin Mes
        f'=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH({ultimo_dia_formula}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-")',

        # M: Valor Fin USD * CCL
        f'=IF(L{r}="-", "-", I{r}*L{r})',

        # N: Rendimiento % MoM = (Fin - Inicio - Ingresos + Egresos) / (Inicio + Ingresos - Egresos)
        f'=IF(D{r}=0, "-", (E{r}-D{r}-B{r}+C{r})/(D{r}+B{r}-C{r}))',

        # O: Rendimiento % Acumulado
        f'=IF(N{r}="-", "-", IF(ROW(A{r})=2, N{r}, (1+O{prev_r})*(1+N{r})-1))',

        # P: CER Inicio Mes (primer día del mes)
        f'=IFERROR(VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE), "-")',

        # Q: CER Fin Mes (último día del mes)
        f'=IFERROR(VLOOKUP({ultimo_dia_formula}, historic_data!$A$4:$B, 2, TRUE), "-")',

        # R: Δ% CER MoM
        f'=IF(OR(P{r}="-", Q{r}="-"), "-", (Q{r}/P{r})-1)',

        # S: Rendimiento MoM vs CER
        f'=IF(OR(N{r}="-", R{r}="-"), "-", N{r}-R{r})',

        # T: Rendimiento Acumulado vs CER
        f'=IF(OR(O{r}="-", R{r}="-"), "-", IF(ROW(A{r})=2, S{r}, (1+T{prev_r})*(1+S{r})-1))',

        # U: CCL Inicio Mes
        f'=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(A{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-")',

        # V: CCL Fin Mes
        f'=L{r}',

        # W: Δ% CCL MoM
        f'=IF(OR(U{r}="-", V{r}="-"), "-", (V{r}/U{r})-1)',

        # X: Rendimiento MoM vs CCL
        f'=IF(OR(N{r}="-", W{r}="-"), "-", N{r}-W{r})',

        # Y: Rendimiento Acumulado vs CCL
        f'=IF(OR(O{r}="-", W{r}="-"), "-", IF(ROW(A{r})=2, X{r}, (1+Y{prev_r})*(1+X{r})-1))',
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
        "Ingreso USD",
        "Egreso USD",
        "Valor Inicio USD",
        "Valor Fin USD",
        "Ganancia/Pérdida ARS",
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
    ws.batch_clear([f"A1:Y{last_row}"])

    # Upload headers
    print(f"Uploading headers...")
    ws.update(range_name="A1:Y1", values=[headers])

    # Upload RAW data (A-I)
    print(f"Uploading {len(data_rows)} rows of raw data (columns A-I)...")
    ws.update(
        range_name=f"A2:I{len(data_rows) + 1}",
        values=data_rows,
        value_input_option="USER_ENTERED",
    )

    # Upload formulas (J-Y)
    print(f"Uploading formulas (columns J-Y)...")
    formula_updates = []

    for i in range(2, len(data_rows) + 2):  # Start at row 2
        formulas = create_formulas(i)
        # Batch update for this row
        formula_updates.append({
            "range": f"J{i}:Y{i}",
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
    print(f"\n2. Preparing raw data (columns A-I)...")
    data_rows = prepare_raw_data(portfolio_data)
    print(f"   Prepared {len(data_rows)} rows")

    # Upload
    print(f"\n3. Uploading to sheet {INVERSIONES_SHEET}...")
    client = get_sheets_client()
    upload_to_sheet(client, data_rows)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    print("\nColumnas A-I: Datos raw de IEB (mes, ingresos, egresos, valores)")
    print("Columnas J-Y: Fórmulas calculadas (ganancias, CCL, CER, rendimientos)")


if __name__ == "__main__":
    main()
