"""upload_to_inversiones.py

Lee el CSV de portfolio evolution y lo sube a la sheet Inversiones.
Solo sube datos RAW (columnas A-J), el resto son FÓRMULAS que buscan en historic_data.
"""

import csv
import os
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
    Prepara solo los datos RAW para subir (columnas B-I).
    Columna A será una fórmula de fecha automática (mes +1).

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
        rows.append(
            [
                float(data["Ingresos ARS"]),  # B
                float(data["Egresos ARS"]),  # C
                float(data["Inicio ARS"]),  # D
                float(data["Fin ARS"]),  # E
                float(data["Ingresos USD"]),  # F
                float(data["Egresos USD"]),  # G
                float(data["Inicio USD"]),  # H
                float(data["Fin USD"]),  # I
            ]
        )

    return rows


def create_formulas(row_num: int) -> list:
    """
    Crea fórmulas para columnas J-AC de una fila.

    J: Ganancia ARS
    K: Ganancia USD
    L: Rend % MoM ARS
    M: Rend % Acum ARS
    N: CER Inicio
    O: CER Fin
    P: Δ% CER MoM
    Q: Rend vs CER MoM
    R: Rend vs CER Acum
    S: Rend % MoM USD
    T: Rend % Acum USD
    U: SPY Inicio
    V: SPY Fin
    W: Δ% SPY MoM
    X: Rend vs SPY MoM
    Y: Rend vs SPY Acum
    Z: CCL Inicio
    AA: CCL Fin
    AB: Δ% CCL MoM
    AC: Valor USD*CCL
    """
    r = row_num
    prev_r = row_num - 1

    # Helper: último día del mes
    ultimo_dia_formula = f"DATE(YEAR(A{r}), MONTH(A{r}), DAY(EOMONTH(A{r}, 0)))"

    # Primera fila de datos es row 3
    is_first_row = f"ROW(A{r})=3"

    formulas = [
        # J: Ganancia ARS = Fin - Inicio - Ingresos + Egresos
        f"=E{r}-D{r}-B{r}+C{r}",
        # K: Ganancia USD = Fin - Inicio - Ingresos + Egresos
        f"=I{r}-H{r}-F{r}+G{r}",
        # L: Rendimiento % MoM ARS = (Fin - Inicio - Ingresos + Egresos) / (Inicio + Ingresos - Egresos)
        f'=IF(D{r}=0, "-", (E{r}-D{r}-B{r}+C{r})/(D{r}+B{r}-C{r}))',
        # M: Rendimiento % Acumulado ARS
        f'=IF(L{r}="-", "-", IF({is_first_row}, L{r}, (1+M{prev_r})*(1+L{r})-1))',
        # N: CER Inicio Mes (primer día del mes)
        f'=IFERROR(VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE), "-")',
        # O: CER Fin Mes (último día del mes)
        f'=IFERROR(VLOOKUP({ultimo_dia_formula}, historic_data!$A$4:$B, 2, TRUE), "-")',
        # P: Δ% CER MoM
        f'=IF(OR(N{r}="-", O{r}="-"), "-", (O{r}/N{r})-1)',
        # Q: Rendimiento MoM vs CER
        f'=IF(OR(L{r}="-", P{r}="-"), "-", L{r}-P{r})',
        # R: Rendimiento Acumulado vs CER
        f'=IF(OR(M{r}="-", P{r}="-"), "-", IF({is_first_row}, Q{r}, (1+R{prev_r})*(1+Q{r})-1))',
        # S: Rendimiento % MoM USD = (Fin - Inicio - Ingresos + Egresos) / (Inicio + Ingresos - Egresos)
        f'=IF(H{r}=0, "-", (I{r}-H{r}-F{r}+G{r})/(H{r}+F{r}-G{r}))',
        # T: Rendimiento % Acumulado USD
        f'=IF(S{r}="-", "-", IF({is_first_row}, S{r}, (1+T{prev_r})*(1+S{r})-1))',
        # U: SPY Inicio Mes (primer día del mes o último valor disponible antes)
        # Usa FILTER para obtener valores <= fecha, luego toma el último
        f'=IFERROR(INDEX(FILTER(historic_data!$D$4:$D, historic_data!$A$4:$A <= A{r}, historic_data!$D$4:$D <> ""), COUNTA(FILTER(historic_data!$D$4:$D, historic_data!$A$4:$A <= A{r}, historic_data!$D$4:$D <> ""))), "-")',
        # V: SPY Fin Mes (último día del mes o último valor disponible antes)
        f'=IFERROR(INDEX(FILTER(historic_data!$D$4:$D, historic_data!$A$4:$A <= {ultimo_dia_formula}, historic_data!$D$4:$D <> ""), COUNTA(FILTER(historic_data!$D$4:$D, historic_data!$A$4:$A <= {ultimo_dia_formula}, historic_data!$D$4:$D <> ""))), "-")',
        # W: Δ% SPY MoM
        f'=IF(OR(U{r}="-", V{r}="-"), "-", (V{r}/U{r})-1)',
        # X: Rendimiento MoM vs SPY
        f'=IF(OR(S{r}="-", W{r}="-"), "-", S{r}-W{r})',
        # Y: Rendimiento Acumulado vs SPY
        f'=IF(OR(T{r}="-", W{r}="-"), "-", IF({is_first_row}, X{r}, (1+Y{prev_r})*(1+X{r})-1))',
        # Z: CCL Inicio Mes
        f'=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(A{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-")',
        # AA: CCL Fin Mes
        f'=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH({ultimo_dia_formula}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-")',
        # AB: Δ% CCL MoM
        f'=IF(OR(Z{r}="-", AA{r}="-"), "-", (AA{r}/Z{r})-1)',
        # AC: Valor Fin USD * CCL Fin
        f'=IF(AA{r}="-", "-", I{r}*AA{r})',
    ]

    return formulas


def upload_to_sheet(client, data_rows: list[list]):
    """Sube datos RAW y fórmulas a la sheet Inversiones."""
    ss = client.open_by_key(SPREADSHEET_ID)
    ws = ss.worksheet(INVERSIONES_SHEET)

    # Row 1: Group titles
    group_titles = [
        "INPUTS",  # A
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",  # B-I (span)
        "GANANCIAS",  # J
        "",  # K (span)
        "RENDIMIENTO ARS",  # L
        "",
        "",
        "",
        "",
        "",
        "",  # M-R (span)
        "RENDIMIENTO USD",  # S
        "",
        "",
        "",
        "",
        "",
        "",  # T-Y (span)
        "CCL",  # Z
        "",
        "",
        "",  # AA-AC (span)
    ]

    # Row 2: Column headers
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
        "Ganancia ARS",
        "Ganancia USD",
        "Rend % MoM",
        "Rend % Acum",
        "CER Inicio",
        "CER Fin",
        "Δ% CER MoM",
        "Rend vs CER MoM",
        "Rend vs CER Acum",
        "Rend % MoM",
        "Rend % Acum",
        "SPY Inicio",
        "SPY Fin",
        "Δ% SPY MoM",
        "Rend vs SPY MoM",
        "Rend vs SPY Acum",
        "CCL Inicio",
        "CCL Fin",
        "Δ% CCL MoM",
        "Valor USD*CCL",
    ]

    # Clear existing data
    print(f"Clearing existing data in {INVERSIONES_SHEET}...")
    last_row = len(data_rows) + 10
    ws.batch_clear([f"A1:AC{last_row}"])

    # Upload group titles (row 1)
    print("Uploading group titles...")
    ws.update(range_name="A1:AC1", values=[group_titles])

    # Upload headers (row 2)
    print("Uploading headers...")
    ws.update(range_name="A2:AC2", values=[headers])

    # Upload columna A: Fecha inicial + fórmulas de mes +1
    print("Uploading fecha column...")
    # Row 3: primera fecha (01/01/2025 - primer mes de portfolio)
    ws.update(
        range_name="A3", values=[["01/01/2025"]], value_input_option="USER_ENTERED"
    )

    # Row 4+: fórmula EDATE(A3, 1) que suma 1 mes
    date_formulas = []
    for i in range(4, len(data_rows) + 3):  # Start at row 4
        date_formulas.append([f"=EDATE(A{i - 1}, 1)"])

    if date_formulas:
        ws.update(
            range_name=f"A4:A{len(data_rows) + 2}",
            values=date_formulas,
            value_input_option="USER_ENTERED",
        )

    # Upload RAW data (B-I) starting at row 3
    print(f"Uploading {len(data_rows)} rows of raw data (columns B-I)...")
    ws.update(
        range_name=f"B3:I{len(data_rows) + 2}",
        values=data_rows,
        value_input_option="USER_ENTERED",
    )

    # Upload formulas (J-AC) starting at row 3
    print("Uploading formulas (columns J-AC)...")
    formula_updates = []

    for i in range(3, len(data_rows) + 3):  # Start at row 3
        formulas = create_formulas(i)
        # Batch update for this row
        formula_updates.append({"range": f"J{i}:AC{i}", "values": [formulas]})

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
    print("\n2. Preparing raw data (columns A-I)...")
    data_rows = prepare_raw_data(portfolio_data)
    print(f"   Prepared {len(data_rows)} rows")

    # Upload
    print(f"\n3. Uploading to sheet {INVERSIONES_SHEET}...")
    client = get_sheets_client()
    upload_to_sheet(client, data_rows)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    print("\nEstructura:")
    print(
        "- Row 1: Títulos de grupos (INPUTS, GANANCIAS, RENDIMIENTO ARS, RENDIMIENTO USD, CCL)"
    )
    print("- Row 2: Headers de columnas")
    print("- Row 3+: Datos")
    print("\nColumna A: Fórmula de fecha (mes +1)")
    print("  - A3: 01/01/2025 (manual - podés cambiar)")
    print("  - A4+: =EDATE(A3, 1) (automático)")
    print("Columnas B-I: Datos raw de IEB (ingresos, egresos, valores ARS/USD)")
    print(
        "Columnas J-AC: Fórmulas calculadas (ganancias, rendimientos ARS/USD vs CER/SPY, CCL)"
    )


if __name__ == "__main__":
    main()
