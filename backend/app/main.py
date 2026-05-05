from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — registers all models with SQLAlchemy metadata
from app.database import Base, engine
from app.routers import historic, rem, salary

Base.metadata.create_all(bind=engine)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="Personal Finance API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(historic.router, prefix="/api/historic", tags=["historic"])
app.include_router(salary.router, prefix="/api/salary", tags=["salary"])
app.include_router(rem.router, prefix="/api/rem", tags=["rem"])


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
