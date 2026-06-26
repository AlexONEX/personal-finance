# Plan — Google Sheets / Excel (source of truth)

Este repo es el pipeline de fetchers → Google Sheets (+ backup en SQLite local).
El web app (FastAPI + frontend vanilla JS) se movió a `personal-finance-html`
para retomarlo más adelante sin mezclar concerns.

## Fetchers → Sheets + DB (dual-write) ✅ COMPLETA

- `fetch_data.py` escribe en Google Sheets (fuente de verdad actual) y en
  SQLite (`src/db/writer.py`) como backup/export
- REM vía API de BCRA (variable 29) en lugar de scraping
- Systemd timer (`systemd/personal-finance-fetch.service` + `.timer`) reemplaza
  `update_dataset.sh`

## Próximos pasos

- Dejar el flujo de Sheets/Excel estable y sin pendientes antes de retomar el frontend
- El frontend/backend vive en `personal-finance-html`, ver ese repo cuando se reanude la Fase 2 del web app

## Fuera del scope

- **Gastos**: se usa hledger con su webui
- **Inversiones**: integración con finance-tracking
