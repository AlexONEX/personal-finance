from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rem import REMProjection
from app.schemas.rem import REMProjectionRead

router = APIRouter()


@router.get("/", response_model=list[REMProjectionRead])
def list_rem(
    since: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[REMProjection]:
    stmt = select(REMProjection).order_by(REMProjection.publication_date)
    if since is not None:
        stmt = stmt.where(REMProjection.publication_date >= since)
    return list(db.scalars(stmt).all())
