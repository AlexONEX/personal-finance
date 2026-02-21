"""fetch_historic.py

Fetches CER and CCL historical data and writes to historic_data.

Sources:
  CER  — BCRA API var 30, daily
  CCL  — IOL DatosHistoricos HTML table (POST) for full history
         + dolarapi.com for today's value

Modes:
  No flags        → append only rows newer than the last date in the sheet
  --since DATE    → clear existing data and rewrite from DATE (backfill)

Usage:
    uv run fetch_historic.py                      # incremental update
    uv run fetch_historic.py --since 2022-01-01   # full backfill
"""

import argparse
import os
import sys
import warnings
from datetime import date, datetime, timedelta

import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SERVICE_ACCOUNT = "service_account.json"

HISTORIC_SHEET = "historic_data"
FIRST_DATA_ROW = 4  # row 1 = metadata, row 2 = col headers, row 3 = spacer
BACKFILL_FROM = date(2022, 1, 1)

BCRA_URL = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30"
AMBITO_GRAFICO_URL = "https://mercados.ambito.com//dolarrava/cl/grafico/{desde}/{hasta}"

# ---------------------------------------------------------------------------
# Google Sheets helpers
# ---------------------------------------------------------------------------


def _get_worksheet() -> gspread.Worksheet:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(HISTORIC_SHEET)


def _last_date_in_sheet(ws: gspread.Worksheet) -> date | None:
    col_a = ws.col_values(1)
    data = [v for v in col_a[FIRST_DATA_ROW - 1 :] if v]
    if not data:
        return None
    return datetime.strptime(data[-1], "%d/%m/%Y").date()


def _clear_data_rows(ws: gspread.Worksheet) -> None:
    """Wipe all data rows (keeps metadata row 1 and header row 2)."""
    end_row = ws.row_count
    if end_row < FIRST_DATA_ROW:
        return
    ws.batch_clear([f"A{FIRST_DATA_ROW}:Z{end_row}"])
    print(f"  Cleared rows {FIRST_DATA_ROW}–{end_row}")


def _write_rows(
    ws: gspread.Worksheet,
    rows: list[tuple[date, float | None, float | None]],
) -> None:
    if not rows:
        print("  No rows to write.")
        return
    payload = [
        [
            r[0].strftime("%d/%m/%Y"),
            r[1] if r[1] is not None else "",
            r[2] if r[2] is not None else "",
        ]
        for r in rows
    ]
    start = FIRST_DATA_ROW
    end = start + len(payload) - 1
    ws.update(f"A{start}:C{end}", payload, value_input_option="USER_ENTERED")
    print(f"  Written {len(payload)} rows → rows {start}–{end}")


def _append_rows(
    ws: gspread.Worksheet,
    rows: list[tuple[date, float | None, float | None]],
    after: date,
) -> None:
    new = [r for r in rows if r[0] > after]
    if not new:
        print("  Nothing new to append — sheet is up to date.")
        return
    existing = len([v for v in ws.col_values(1)[FIRST_DATA_ROW - 1 :] if v])
    start = FIRST_DATA_ROW + existing
    end = start + len(new) - 1
    payload = [
        [
            r[0].strftime("%d/%m/%Y"),
            r[1] if r[1] is not None else "",
            r[2] if r[2] is not None else "",
        ]
        for r in new
    ]
    ws.update(f"A{start}:C{end}", payload, value_input_option="USER_ENTERED")
    print(f"  Appended {len(new)} rows → rows {start}–{end}")


# ---------------------------------------------------------------------------
# CER — BCRA API (var 30)
# ---------------------------------------------------------------------------


def fetch_cer(since: date, until: date) -> dict[date, float]:
    results: dict[date, float] = {}
    offset, limit = 0, 3000

    print(f"  CER: fetching {since} → {until} from BCRA…")
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


# ---------------------------------------------------------------------------
# CCL — Ambito Financiero
#
# Endpoint: mercados.ambito.com//dolarrava/cl/grafico/{desde}/{hasta}
# Dates in URL: YYYY-MM-DD
# Response: JSON array → [["fecha","DOLAR CCL"], ["19/01/2022",216.39], ...]
# ---------------------------------------------------------------------------


def fetch_ccl_ambito(since: date, until: date) -> dict[date, float]:
    url = AMBITO_GRAFICO_URL.format(
        desde=since.isoformat(),
        hasta=until.isoformat(),
    )
    print(f"  CCL: fetching {since} → {until} from Ambito grafico…")
    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"  WARNING: Ambito request failed: {e}", file=sys.stderr)
        return {}

    if not isinstance(data, list) or len(data) < 2:
        print(f"  WARNING: Ambito — unexpected response shape: {type(data)}")
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


def fetch_ccl_today() -> tuple[date, float] | None:
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch CER + CCL into historic_data")
    parser.add_argument(
        "--since",
        type=date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="Start date. When provided, clears existing data and rewrites from scratch.",
    )
    args = parser.parse_args()

    if not SPREADSHEET_ID:
        print("ERROR: SPREADSHEET_ID not set in .env", file=sys.stderr)
        sys.exit(1)

    print("Connecting to Google Sheets…")
    ws = _get_worksheet()

    last = _last_date_in_sheet(ws)
    force_rewrite = args.since is not None
    since = args.since or (last + timedelta(days=1) if last else BACKFILL_FROM)
    until = date.today()

    print(f"Last date in sheet : {last or '(empty)'}")
    print(
        f"Mode               : {'full rewrite from ' + str(since) if force_rewrite else 'incremental append'}"
    )
    print(f"Fetching           : {since} → {until}\n")

    if not force_rewrite and since > until:
        print("Sheet is already up to date.")
        return

    # ── Fetch ────────────────────────────────────────────────────────────────
    cer_data = fetch_cer(since, until)

    ccl_data = fetch_ccl_ambito(since, until)

    today_ccl = fetch_ccl_today()
    if today_ccl:
        d, v = today_ccl
        if d >= since:
            ccl_data[d] = v
            print(f"  CCL (dolarapi top-up): {d} = {v}")

    # ── Merge (outer join on date) ───────────────────────────────────────────
    all_dates = sorted(cer_data.keys() | ccl_data.keys())
    rows: list[tuple[date, float | None, float | None]] = [
        (d, cer_data.get(d), ccl_data.get(d)) for d in all_dates
    ]
    print(f"\nMerged: {len(rows)} date rows")

    # ── Write ────────────────────────────────────────────────────────────────
    if force_rewrite:
        print("Clearing existing data…")
        _clear_data_rows(ws)
        _write_rows(ws, rows)
    else:
        _append_rows(ws, rows, after=last)  # type: ignore[arg-type]

    print("\nDone.")


if __name__ == "__main__":
    main()
