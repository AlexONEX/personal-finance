from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class HistoricDataBase(BaseModel):
    date: date
    cer: float | None = None
    ccl: float | None = None
    spy: float | None = None
    cer_estimado: float | None = None
    inflacion_mensual: float | None = None


class HistoricDataCreate(HistoricDataBase):
    pass


class HistoricDataRead(HistoricDataBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
