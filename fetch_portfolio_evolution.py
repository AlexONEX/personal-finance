"""fetch_portfolio_evolution.py

Obtiene la evolución mensual del portfolio de IEB usando el endpoint /portfolio/performance.
Para cada mes calcula:
- Valor inicio mes
- Ingresos (deposits)
- Egresos (withdrawals)
- Valor fin mes
- Total invertido acumulado
- Ganancia/pérdida
"""

import os
from datetime import date
from calendar import monthrange

import requests
from dotenv import load_dotenv

load_dotenv()

IEB_ACCOUNT_ID = os.environ.get("IEB_ACCOUNT_ID", "26935110")
IEB_USER_AGENT = os.environ.get("IEB_USER_AGENT")
IEB_X_DEVICE_ID = os.environ.get("IEB_X_DEVICE_ID")
IEB_X_CLIENT_NAME = os.environ.get("IEB_X_CLIENT_NAME")
IEB_BASE_URL = "https://core.iebmas.grupoieb.com.ar/api"

# Fecha de inicio del portfolio (primer deposit)
PORTFOLIO_START_DATE = date(2025, 1, 20)


def get_headers(bearer_token: str) -> dict:
    """Construye headers para requests a IEB API."""
    return {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": IEB_USER_AGENT,
        "X-device-id": IEB_X_DEVICE_ID,
        "X-Client-Name": IEB_X_CLIENT_NAME,
        "X-Use-Wrapped-Single-Values": "true",
        "Origin": "https://hb.iebmas.com.ar",
        "Referer": "https://hb.iebmas.com.ar/",
    }


def fetch_monthly_performance(
    bearer_token: str, from_date: date, to_date: date, currency: str = "ARS"
) -> dict:
    """
    Obtiene performance del portfolio para un rango de fechas.

    Endpoint: GET /api/portfolio/customer-account/{account_id}/performance
    """
    url = f"{IEB_BASE_URL}/portfolio/customer-account/{IEB_ACCOUNT_ID}/performance"
    params = {
        "fromDate": f"{from_date.isoformat()}T03:00:00.000Z",
        "toDate": f"{to_date.isoformat()}T23:59:59.000Z",
        "currency": currency,
    }

    response = requests.get(
        url, headers=get_headers(bearer_token), params=params, timeout=30
    )
    response.raise_for_status()
    return response.json()


def calculate_cash_flows(performance_detail: list[dict]) -> tuple[float, float]:
    """
    Calcula ingresos y egresos desde performanceDetail.

    Returns:
        (ingresos, egresos)
    """
    ingresos = 0
    egresos = 0

    deposit_codes = {"COBW", "COUW"}  # Códigos de deposits
    withdrawal_codes = {"PAGW"}  # Códigos de withdrawals

    for detail in performance_detail:
        doc_key = detail.get("documentKey", "")
        total = abs(detail.get("total", 0))

        if doc_key in deposit_codes:
            ingresos += total
        elif doc_key in withdrawal_codes:
            egresos += total

    return ingresos, egresos


def get_month_range(year: int, month: int, start_date: date) -> tuple[date, date]:
    """
    Devuelve (from_date, to_date) para un mes dado.
    Si es el primer mes, usa PORTFOLIO_START_DATE como from_date.
    """
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Si es el primer mes, usar la fecha de inicio del portfolio
    if first_day <= start_date <= last_day:
        from_date = start_date
    else:
        from_date = first_day

    return from_date, last_day


def main():
    print("=" * 60)
    print("   PORTFOLIO EVOLUTION - IEB   ")
    print("=" * 60)

    # Pedir token
    bearer_token = input("\nPaste your IEB access_token: ").strip()

    if not bearer_token:
        print("Error: Token is required")
        return

    # Generar lista de meses a procesar
    current_date = date.today()
    start_year, start_month = PORTFOLIO_START_DATE.year, PORTFOLIO_START_DATE.month
    end_year, end_month = current_date.year, current_date.month

    months_to_process = []

    for year in range(start_year, end_year + 1):
        start_m = start_month if year == start_year else 1
        end_m = end_month if year == end_year else 12

        for month in range(start_m, end_m + 1):
            months_to_process.append(date(year, month, 1))

    print(f"\nProcessing {len(months_to_process)} months...")
    print(f"From: {months_to_process[0].strftime('%Y-%m')}")
    print(f"To: {months_to_process[-1].strftime('%Y-%m')}\n")

    # Procesar cada mes
    results = []

    for month_date in months_to_process:
        year, month = month_date.year, month_date.month
        month_key = f"{year}-{month:02d}"

        from_date, to_date = get_month_range(year, month, PORTFOLIO_START_DATE)

        try:
            # Fetch ARS y USD
            perf_ars = fetch_monthly_performance(
                bearer_token, from_date, to_date, "ARS"
            )
            perf_usd = fetch_monthly_performance(
                bearer_token, from_date, to_date, "USD"
            )

            # Calcular cash flows
            ingresos_ars, egresos_ars = calculate_cash_flows(
                perf_ars.get("performanceDetail", [])
            )
            ingresos_usd, egresos_usd = calculate_cash_flows(
                perf_usd.get("performanceDetail", [])
            )

            results.append(
                {
                    "mes": month_key,
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat(),
                    "ars": {
                        "valor_inicio": perf_ars.get("oldTotalPosition", 0),
                        "valor_fin": perf_ars.get("currentTotalPosition", 0),
                        "ingresos": ingresos_ars,
                        "egresos": egresos_ars,
                        "total_invertido": perf_ars.get("investedTotal", 0),
                        "ganancia": perf_ars.get("earnings", 0),
                    },
                    "usd": {
                        "valor_inicio": perf_usd.get("oldTotalPosition", 0),
                        "valor_fin": perf_usd.get("currentTotalPosition", 0),
                        "ingresos": ingresos_usd,
                        "egresos": egresos_usd,
                        "total_invertido": perf_usd.get("investedTotal", 0),
                        "ganancia": perf_usd.get("earnings", 0),
                    },
                }
            )

            print(f"✓ {month_key}")

        except requests.exceptions.RequestException as e:
            print(f"✗ {month_key}: {e}")
            continue

    # Imprimir resumen
    print("\n" + "=" * 100)
    print("MONTHLY PORTFOLIO EVOLUTION")
    print("=" * 100)
    print(
        f"{'Mes':<10} {'Inicio ARS':>15} {'Ingr':>12} {'Egr':>12} {'Fin ARS':>15} {'G/L ARS':>12} | {'Fin USD':>12} {'G/L USD':>10}"
    )
    print("-" * 100)

    for r in results:
        ars = r["ars"]
        usd = r["usd"]
        print(
            f"{r['mes']:<10} "
            f"${ars['valor_inicio']:>14,.0f} "
            f"${ars['ingresos']:>11,.0f} "
            f"${ars['egresos']:>11,.0f} "
            f"${ars['valor_fin']:>14,.0f} "
            f"${ars['ganancia']:>11,.0f} | "
            f"${usd['valor_fin']:>11,.2f} "
            f"${usd['ganancia']:>9,.2f}"
        )

    print("=" * 100)

    # Guardar en CSV
    import csv

    csv_file = "portfolio_evolution.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Mes",
                "Inicio ARS",
                "Ingresos ARS",
                "Egresos ARS",
                "Fin ARS",
                "Total Invertido ARS",
                "Ganancia ARS",
                "Inicio USD",
                "Ingresos USD",
                "Egresos USD",
                "Fin USD",
                "Total Invertido USD",
                "Ganancia USD",
            ]
        )

        for r in results:
            writer.writerow(
                [
                    r["mes"],
                    r["ars"]["valor_inicio"],
                    r["ars"]["ingresos"],
                    r["ars"]["egresos"],
                    r["ars"]["valor_fin"],
                    r["ars"]["total_invertido"],
                    r["ars"]["ganancia"],
                    r["usd"]["valor_inicio"],
                    r["usd"]["ingresos"],
                    r["usd"]["egresos"],
                    r["usd"]["valor_fin"],
                    r["usd"]["total_invertido"],
                    r["usd"]["ganancia"],
                ]
            )

    print(f"\n✅ Saved to {csv_file}")


if __name__ == "__main__":
    main()
