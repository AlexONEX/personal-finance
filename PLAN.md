# Plan de Migración: Google Sheets → Web App

## Fase 1 — Backend Foundation ✅ COMPLETA

- FastAPI + SQLAlchemy 2.0 + SQLite en `/srv/data/personal-finance/personal-finance.db`
- Modelos tipados: `salary_entries`, `historic_data`, `rem_projections`, `cpi_data`
- Endpoints: `GET/POST/PATCH/DELETE /api/salary/`, `GET /api/historic/`, `GET /api/rem/`
- Ruff (linter + formatter) con ANN obligatorio en código nuevo, mypy strict
- Systemd: `personal-finance-api.service` → uvicorn en `127.0.0.1:8087`
- Nginx: SSL en puerto 8453 → `https://mars.tail56f9e.ts.net:8453`

## Fase 2 — Frontend Vanilla JS ← EN CURSO

- Sin framework, sin build step — HTML/CSS/JS estáticos servidos por nginx desde `frontend/`
- 3 tabs: **Ingresos** (input + tabla calculada), **Análisis ARS**, **Dashboard**
- Chart.js vía CDN para gráficos
- Cálculos en cliente: descuentos, totales, variaciones MoM
- No se muestran datos de CPI, REM, ni BCRA

## Fase 3 — Fetchers → DB (mantener Sheets como backup)

- Modificar `fetch_data.py` para escribir en SQLite además de Sheets (dual-write)
- `get_last_date_from_sheet()` → `get_last_date_from_db()`
- Systemd timer que reemplaza `update_dataset.sh`
- La Sheet pasa a ser export/backup opcional

## Fase 4 — Ingresos CRUD completo (source of truth → DB)

- El frontend reemplaza la edición manual de la Sheet
- Import script para migrar entradas históricas de Sheets → DB
- Deprecar dependencia de gspread para escritura de ingresos

## Fase 5 — Análisis ARS/USD como endpoints calculados

- `GET /api/analysis/ars` — re-implementa fórmulas de la tab Analisis ARS
- `GET /api/analysis/usd` — re-implementa fórmulas de la tab Analisis USD
- Usa CCL y CER de la DB (disponibles después de Fase 3)
- Frontend consume los endpoints en lugar de calcular en cliente

## Fuera del scope

- **Gastos**: se usa hledger con su webui
- **REM, CPI, datos BCRA**: no se muestran en el frontend
- **Inversiones**: integración con finance-tracking (post Fase 5)
