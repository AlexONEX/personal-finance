from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class CPIDataBase(BaseModel):
    date: date
    indec_tn_nivel_general: float | None = None
    indec_tn_nucleo: float | None = None
    indec_tn_estacionales: float | None = None
    indec_tn_regulados: float | None = None
    indec_gba_nivel_general: float | None = None
    indec_gba_nucleo: float | None = None
    indec_gba_estacionales: float | None = None
    indec_gba_regulados: float | None = None
    caba_nivel_general: float | None = None
    usa_cpi: float | None = None


class CPIDataCreate(CPIDataBase):
    pass


class CPIDataRead(CPIDataBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
