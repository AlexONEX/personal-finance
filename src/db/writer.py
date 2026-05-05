"""Dual-write helpers: persist fetcher data to SQLite alongside Google Sheets.

Uses SQLAlchemy Core (no ORM) with a lazy engine so DATABASE_URL is read from
the environment after load_dotenv() has been called by the caller.
"""

import logging
import os
from datetime import date, datetime, timedelta

from sqlalchemy import Column, Date, Float, Integer, MetaData, Table, create_engine, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

_BACKFILL_FROM = date(2022, 1, 1)
_DEFAULT_DB = "sqlite:////srv/data/personal-finance/personal-finance.db"

_engine: Engine | None = None

_meta = MetaData()

_historic = Table(
    "historic_data",
    _meta,
    Column("id", Integer, primary_key=True),
    Column("date", Date, unique=True),
    Column("cer", Float),
    Column("ccl", Float),
    Column("spy", Float),
    Column("cer_estimado", Float),
    Column("inflacion_mensual", Float),
)

_cpi = Table(
    "cpi_data",
    _meta,
    Column("id", Integer, primary_key=True),
    Column("date", Date, unique=True),
    Column("indec_tn_nivel_general", Float),
    Column("indec_tn_nucleo", Float),
    Column("indec_tn_estacionales", Float),
    Column("indec_tn_regulados", Float),
    Column("indec_gba_nivel_general", Float),
    Column("indec_gba_nucleo", Float),
    Column("indec_gba_estacionales", Float),
    Column("indec_gba_regulados", Float),
    Column("caba_nivel_general", Float),
    Column("usa_cpi", Float),
)

_rem = Table(
    "rem_projections",
    _meta,
    Column("id", Integer, primary_key=True),
    Column("publication_date", Date, unique=True),
    Column("m0", Float),
    Column("m1", Float),
    Column("m2", Float),
    Column("m3", Float),
    Column("m4", Float),
    Column("m5", Float),
    Column("m6", Float),
    Column("m12", Float),
)


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL", _DEFAULT_DB)
        _engine = create_engine(db_url, connect_args={"check_same_thread": False})
    return _engine


def get_last_date_from_db() -> date:
    """Última fecha en historic_data, retrocedida 7 días para reescribir datos recientes."""
    with _get_engine().connect() as conn:
        result = conn.execute(select(func.max(_historic.c.date))).scalar()
    if result:
        return result - timedelta(days=7)
    return _BACKFILL_FROM


def get_last_rem_date_from_db() -> tuple[int, int]:
    """Último mes (año, mes) en rem_projections."""
    with _get_engine().connect() as conn:
        result = conn.execute(select(func.max(_rem.c.publication_date))).scalar()
    if result:
        return (result.year, result.month)
    return (_BACKFILL_FROM.year, _BACKFILL_FROM.month)


def write_historic_to_db(
    cer_data: dict[date, float],
    ccl_data: dict[date, float],
    spy_data: dict[date, float],
    inflacion_data: dict[date, float],
) -> None:
    """Upsert en historic_data. Preserva valores existentes cuando el nuevo es None."""
    all_dates = set(cer_data) | set(ccl_data) | set(spy_data) | set(inflacion_data)
    if not all_dates:
        return

    rows = [
        {
            "date": d,
            "cer": cer_data.get(d),
            "ccl": ccl_data.get(d),
            "spy": spy_data.get(d),
            "inflacion_mensual": inflacion_data.get(d),
        }
        for d in sorted(all_dates)
    ]

    stmt = sqlite_insert(_historic).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["date"],
        set_={
            "cer": func.coalesce(stmt.excluded.cer, _historic.c.cer),
            "ccl": func.coalesce(stmt.excluded.ccl, _historic.c.ccl),
            "spy": func.coalesce(stmt.excluded.spy, _historic.c.spy),
            "inflacion_mensual": func.coalesce(
                stmt.excluded.inflacion_mensual, _historic.c.inflacion_mensual
            ),
        },
    )

    with _get_engine().begin() as conn:
        conn.execute(stmt)

    logger.info(f"DB: upserted {len(rows)} historic_data rows")


def _cpi_float(cpi_data: dict, key: str, i: int) -> float | None:
    series = cpi_data.get(key, [])
    if i >= len(series):
        return None
    val = series[i][0] if series[i] else None
    if val == "N/A" or val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def write_cpi_to_db(cpi_data: dict) -> None:
    """Upsert en cpi_data desde el dict consolidado producido por fetch_data."""
    dates_rows = cpi_data.get("dates", [])
    if not dates_rows:
        return

    rows = []
    for i, date_row in enumerate(dates_rows):
        try:
            d = datetime.strptime(date_row[0], "%d/%m/%Y").date()
        except (ValueError, IndexError):
            continue
        rows.append(
            {
                "date": d,
                "indec_tn_nivel_general": _cpi_float(cpi_data, "indec_tn_nivel_general", i),
                "indec_tn_nucleo": _cpi_float(cpi_data, "indec_tn_nucleo", i),
                "indec_tn_estacionales": _cpi_float(cpi_data, "indec_tn_estacionales", i),
                "indec_tn_regulados": _cpi_float(cpi_data, "indec_tn_regulados", i),
                "indec_gba_nivel_general": _cpi_float(cpi_data, "indec_gba_nivel_general", i),
                "indec_gba_nucleo": _cpi_float(cpi_data, "indec_gba_nucleo", i),
                "indec_gba_estacionales": _cpi_float(cpi_data, "indec_gba_estacionales", i),
                "indec_gba_regulados": _cpi_float(cpi_data, "indec_gba_regulados", i),
                "caba_nivel_general": _cpi_float(cpi_data, "caba_idx_nivel_general", i),
                "usa_cpi": _cpi_float(cpi_data, "usa_cpi_index", i),
            }
        )

    if not rows:
        return

    cpi_cols = [col.name for col in _cpi.c if col.name not in ("id", "date")]
    stmt = sqlite_insert(_cpi).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["date"],
        set_={col: func.coalesce(getattr(stmt.excluded, col), _cpi.c[col]) for col in cpi_cols},
    )

    with _get_engine().begin() as conn:
        conn.execute(stmt)

    logger.info(f"DB: upserted {len(rows)} cpi_data rows")


def write_rem_to_db(rem_reports: dict[str, list[float]]) -> None:
    """Upsert en rem_projections desde el dict de REMFetcher."""
    if not rem_reports:
        return

    rows = []
    for month_key, projections in rem_reports.items():
        if len(projections) < 8:
            continue
        try:
            pub_date = date.fromisoformat(month_key)
        except ValueError:
            continue
        rows.append(
            {
                "publication_date": pub_date,
                "m0": projections[0],
                "m1": projections[1],
                "m2": projections[2],
                "m3": projections[3],
                "m4": projections[4],
                "m5": projections[5],
                "m6": projections[6],
                "m12": projections[7],
            }
        )

    if not rows:
        return

    rem_cols = [col.name for col in _rem.c if col.name not in ("id", "publication_date")]
    stmt = sqlite_insert(_rem).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["publication_date"],
        set_={col: getattr(stmt.excluded, col) for col in rem_cols},
    )

    with _get_engine().begin() as conn:
        conn.execute(stmt)

    logger.info(f"DB: upserted {len(rows)} rem_projection rows")
