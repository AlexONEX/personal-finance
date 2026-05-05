from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CPIData(Base):
    __tablename__ = "cpi_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    # INDEC - Total Nacional
    indec_tn_nivel_general: Mapped[float | None] = mapped_column(Float, nullable=True)
    indec_tn_nucleo: Mapped[float | None] = mapped_column(Float, nullable=True)
    indec_tn_estacionales: Mapped[float | None] = mapped_column(Float, nullable=True)
    indec_tn_regulados: Mapped[float | None] = mapped_column(Float, nullable=True)
    # INDEC - GBA
    indec_gba_nivel_general: Mapped[float | None] = mapped_column(Float, nullable=True)
    indec_gba_nucleo: Mapped[float | None] = mapped_column(Float, nullable=True)
    indec_gba_estacionales: Mapped[float | None] = mapped_column(Float, nullable=True)
    indec_gba_regulados: Mapped[float | None] = mapped_column(Float, nullable=True)
    # CABA
    caba_nivel_general: Mapped[float | None] = mapped_column(Float, nullable=True)
    # USA
    usa_cpi: Mapped[float | None] = mapped_column(Float, nullable=True)
