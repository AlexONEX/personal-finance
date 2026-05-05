from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SalaryEntry(Base):
    __tablename__ = "salary_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, unique=True, index=True)
    bruto: Mapped[float] = mapped_column(Float, nullable=False)
    sac_bruto: Mapped[float | None] = mapped_column(Float, nullable=True)
    bono_neto: Mapped[float | None] = mapped_column(Float, nullable=True)
    tarjeta_corporativa: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_beneficios: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_diarias: Mapped[float | None] = mapped_column(Float, nullable=True)
    ascenso: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
