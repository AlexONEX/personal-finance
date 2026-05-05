from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.historic import HistoricData
from app.schemas.historic import HistoricDataRead

router = APIRouter()


@router.get("/", response_model=list[HistoricDataRead])
def list_historic(
    since: date | None = Query(default=None),
    until: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[HistoricData]:
    stmt = select(HistoricData).order_by(HistoricData.date)
    if since is not None:
        stmt = stmt.where(HistoricData.date >= since)
    if until is not None:
        stmt = stmt.where(HistoricData.date <= until)
    return list(db.scalars(stmt).all())
