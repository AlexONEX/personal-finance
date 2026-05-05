from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class REMProjection(Base):
    """Proyecciones de inflación del REM (BCRA).

    Cada fila corresponde a una publicación mensual.
    Los campos m0..m6 son proyecciones para el mes actual y los 6 siguientes.
    m12 es la proyección a 12 meses. Valores en formato decimal (0.03 = 3%).
    """

    __tablename__ = "rem_projections"

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    m0: Mapped[float | None] = mapped_column(Float, nullable=True)
    m1: Mapped[float | None] = mapped_column(Float, nullable=True)
    m2: Mapped[float | None] = mapped_column(Float, nullable=True)
    m3: Mapped[float | None] = mapped_column(Float, nullable=True)
    m4: Mapped[float | None] = mapped_column(Float, nullable=True)
    m5: Mapped[float | None] = mapped_column(Float, nullable=True)
    m6: Mapped[float | None] = mapped_column(Float, nullable=True)
    m12: Mapped[float | None] = mapped_column(Float, nullable=True)
