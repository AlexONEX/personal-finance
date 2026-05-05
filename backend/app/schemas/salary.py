from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class SalaryEntryBase(BaseModel):
    fecha: date
    bruto: Annotated[float, Field(gt=0)]
    sac_bruto: Annotated[float, Field(gt=0)] | None = None
    bono_neto: Annotated[float, Field(gt=0)] | None = None
    tarjeta_corporativa: Annotated[float, Field(ge=0)] | None = None
    otros_beneficios: Annotated[float, Field(ge=0)] | None = None
    horas_diarias: Annotated[float, Field(gt=0, le=24)] | None = None
    notes: str | None = None


class SalaryEntryCreate(SalaryEntryBase):
    pass


class SalaryEntryUpdate(BaseModel):
    bruto: Annotated[float, Field(gt=0)] | None = None
    sac_bruto: Annotated[float, Field(gt=0)] | None = None
    bono_neto: Annotated[float, Field(gt=0)] | None = None
    tarjeta_corporativa: Annotated[float, Field(ge=0)] | None = None
    otros_beneficios: Annotated[float, Field(ge=0)] | None = None
    horas_diarias: Annotated[float, Field(gt=0, le=24)] | None = None
    notes: str | None = None


class SalaryEntryRead(SalaryEntryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
