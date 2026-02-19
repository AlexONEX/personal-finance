"""Ambito Financiero API connector para obtener CCL historico."""

import sys
from datetime import date, datetime

import requests

AMBITO_GRAFICO_URL = "https://mercados.ambito.com//dolarrava/cl/grafico/{desde}/{hasta}"


def fetch_ccl_ambito(since: date, until: date) -> dict[date, float]:
    """Fetch CCL historical data from Ambito Financiero.

    Args:
        since: Start date
        until: End date

    Returns:
        Dictionary mapping date to CCL value
    """
    url = AMBITO_GRAFICO_URL.format(
        desde=since.isoformat(),
        hasta=until.isoformat(),
    )
    print(f"  CCL: fetching {since} -> {until} from Ambito grafico...")

    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"  WARNING: Ambito request failed: {e}", file=sys.stderr)
        return {}

    if not isinstance(data, list) or len(data) < 2:
        print(f"  WARNING: Ambito - unexpected response shape: {type(data)}")
        return {}

    # First row is headers: ["fecha", "DOLAR CCL"]
    # Rest: ["DD/MM/YYYY", value]
    print(f"  Ambito headers: {data[0]}")
    print(f"  Ambito sample : {data[1:3]}")

    out: dict[date, float] = {}
    for row in data[1:]:
        try:
            raw_date = str(row[0]).strip()
            raw_price = row[1]  # Already a number
            # Date format: DD/MM/YYYY
            d = datetime.strptime(raw_date, "%d/%m/%Y").date()
            out[d] = float(raw_price)
        except (ValueError, IndexError, TypeError):
            continue

    print(f"  CCL (Ambito grafico): {len(out)} records")
    return out
