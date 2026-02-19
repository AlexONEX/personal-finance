"""BCRA API connector para obtener CER (Coeficiente de Estabilizacion de Referencia)."""

import warnings
from datetime import date, datetime

import requests

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

BCRA_URL = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30"


def fetch_cer(since: date, until: date) -> dict[date, float]:
    """Fetch CER daily values from BCRA API.

    Args:
        since: Start date
        until: End date

    Returns:
        Dictionary mapping date to CER value
    """
    results: dict[date, float] = {}
    offset, limit = 0, 3000

    print(f"  CER: fetching {since} -> {until} from BCRA...")

    while True:
        resp = requests.get(
            BCRA_URL,
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

        # v4 structure: results[0]["detalle"] holds the date/value pairs
        detalle: list[dict] = []
        for variable in body.get("results", []):
            detalle.extend(variable.get("detalle", []))

        for record in detalle:
            d = datetime.strptime(record["fecha"], "%Y-%m-%d").date()
            results[d] = record["valor"]

        total = body.get("metadata", {}).get("resultset", {}).get("count", 0)
        offset += len(detalle)
        if offset >= total or not detalle:
            break

    print(f"  CER: {len(results)} records")
    return results
