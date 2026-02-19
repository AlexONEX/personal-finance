"""DolarApi.com connector para obtener CCL actual."""

import sys
from datetime import date, datetime

import requests


def fetch_ccl_today() -> tuple[date, float] | None:
    """Fetch today's CCL value from dolarapi.com.

    Returns:
        Tuple of (date, ccl_value) or None if failed
    """
    try:
        resp = requests.get(
            "https://dolarapi.com/v1/dolares/contadoconliqui", timeout=10
        )
        resp.raise_for_status()
        body = resp.json()
        venta = body.get("venta")
        fecha = body.get("fechaActualizacion", "")
        if venta and fecha:
            d = datetime.fromisoformat(fecha.replace("Z", "+00:00")).date()
            return d, float(venta)
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"  WARNING: dolarapi error: {e}", file=sys.stderr)
    return None
