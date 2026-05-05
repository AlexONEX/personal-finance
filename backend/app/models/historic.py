from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HistoricData(Base):
    __tablename__ = "historic_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    cer: Mapped[float | None] = mapped_column(Float, nullable=True)
    ccl: Mapped[float | None] = mapped_column(Float, nullable=True)
    spy: Mapped[float | None] = mapped_column(Float, nullable=True)
    cer_estimado: Mapped[float | None] = mapped_column(Float, nullable=True)
    inflacion_mensual: Mapped[float | None] = mapped_column(Float, nullable=True)
