from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.salary import SalaryEntry
from app.schemas.salary import SalaryEntryCreate, SalaryEntryRead, SalaryEntryUpdate

router = APIRouter()


@router.get("/", response_model=list[SalaryEntryRead])
def list_salary(db: Session = Depends(get_db)) -> list[SalaryEntry]:
    return list(db.scalars(select(SalaryEntry).order_by(SalaryEntry.fecha)).all())


@router.post("/", response_model=SalaryEntryRead, status_code=201)
def create_salary(entry: SalaryEntryCreate, db: Session = Depends(get_db)) -> SalaryEntry:
    record = SalaryEntry(**entry.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{entry_id}", response_model=SalaryEntryRead)
def update_salary(
    entry_id: int, entry: SalaryEntryUpdate, db: Session = Depends(get_db)
) -> SalaryEntry:
    record = db.get(SalaryEntry, entry_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    for field, value in entry.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{entry_id}", status_code=204)
def delete_salary(entry_id: int, db: Session = Depends(get_db)) -> None:
    record = db.get(SalaryEntry, entry_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(record)
    db.commit()
