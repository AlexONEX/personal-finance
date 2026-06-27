# Personal Finance Tracker

Track income, investments, and macro data (CER/CCL/REM/CPI) via Google Sheets + SQLite.

## What runs in production

Daily systemd timer (`personal-finance-fetch.timer`, 08:00) runs `fetch_data.py`:
- Fetches CER, CCL, SPY, REM (full M0-M6 + 12m via BCRA scraper), CPI (INDEC, CABA, USA/FRED)
- Writes to Google Sheets (`historic_data`, `REM`, `CPI` tabs) and SQLite as backup

Manual scripts (not automated):
- `fetch_investments.py` — pulls IEB portfolio evolution → `Inversiones` tab
- `upload_investments.py` — CSV fallback for the same

Force a backfill: `uv run fetch_data.py --since YYYY-MM-DD`

## Roadmap

### 1. Lean up Análisis ARS
The tab has too many columns. The three questions it needs to answer:
1. How much have I gained/lost vs CER since my last raise? (Poder Adq vs Aumento CER)
2. What should my salary be today adjusted for CER? (Paridad CER Neto/Hora)
3. Given REM projections, what should I earn in 1m / 3m / 6m / 12m to keep purchasing power?

Everything else is a helper column or duplicate — remove it.

### 2. Build Análisis USD
Same three questions as Análisis ARS, denominated in USD (CCL):
1. How much have I gained/lost vs CCL since my last raise?
2. What should my salary be today in USD?
3. Given REM USD projections, what should I earn in 1m / 3m / 6m / 12m?

## Out of scope

- **Expenses**: tracked in hledger separately
- **Web app**: lives in `personal-finance-html`, not active here
