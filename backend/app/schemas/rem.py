from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class REMProjectionBase(BaseModel):
    publication_date: date
    m0: float | None = None
    m1: float | None = None
    m2: float | None = None
    m3: float | None = None
    m4: float | None = None
    m5: float | None = None
    m6: float | None = None
    m12: float | None = None


class REMProjectionCreate(REMProjectionBase):
    pass


class REMProjectionRead(REMProjectionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
