# Comandos Disponibles

## Actualización de Datos

### Actualizar datos de CER, CCL, SPY y REM

```bash
# Actualizar desde última fecha registrada
./update_daily.sh

# Actualizar desde fecha específica
./update_daily.sh --since 2024-01-01

# Ver ayuda
uv run python fetch_data.py --help
```

## Visualización REM

### Curvas de Expectativas

```bash
# Últimos 6 meses (recomendado)
uv run python plot_rem_curves.py --months 6 --output rem_6m.png

# Últimos 3 meses
uv run python plot_rem_curves.py -m 3 -o rem_3m.png

# Últimos 12 meses
uv run python plot_rem_curves.py -m 12 -o rem_12m.png

# Todos los meses desde 2022
uv run python plot_rem_curves.py -o rem_all.png

# Con título customizado
uv run python plot_rem_curves.py -m 6 -o rem.png -t "Expectativas REM - Q1 2026"

# Mostrar sin guardar
uv run python plot_rem_curves.py -m 6
```

### Evolución por Horizonte

```bash
# Evolución temporal de cada horizonte (M, M+1, M+2...)
uv run python plot_rem_curves.py --evolution -o rem_evolution.png

# Con título customizado
uv run python plot_rem_curves.py -e -o rem_evo.png -t "Evolución REM por Horizonte"
```

### Ayuda

```bash
uv run python plot_rem_curves.py --help
```

## Setup Inicial (Primera Vez)

```bash
# Configurar sheets y autenticación
uv run python bootstrap.py

# Configurar estructura de sheets
uv run python setup_sheet.py
```

## Portfolio IEB (Opcional)

```bash
# Obtener evolución de portfolio
uv run python fetch_portfolio_evolution.py

# Upload a sheet Inversiones
uv run python upload_to_inversiones.py
```

## Automatización

### Cron Job Diario (Local)

```bash
# Editar crontab
crontab -e

# Agregar (ejecuta todos los días a las 8 AM)
0 8 * * * cd /Users/alex/Github/me/ingresos && ./update_daily.sh >> logs/cron.log 2>&1
```

### Ver Logs

```bash
# Logs en tiempo real
tail -f logs/cron.log

# Últimas 50 líneas
tail -50 logs/cron.log
```

## Estructura del Proyecto

```
ingresos/
├── src/
│   ├── config.py              # Configuración centralizada
│   ├── connectors/
│   │   └── sheets.py          # Autenticación Google Sheets
│   ├── fetchers/
│   │   ├── cer.py             # Fetcher CER (BCRA)
│   │   ├── ccl.py             # Fetcher CCL (Ambito/dolarapi)
│   │   ├── rem.py             # Fetcher REM (BCRA web scraping)
│   │   └── spy.py             # Fetcher SPY (yfinance)
│   ├── setup/
│   │   ├── ingresos.py        # Setup sheet Ingresos
│   │   ├── historic.py        # Setup sheet historic_data
│   │   ├── rem.py             # Setup sheet REM
│   │   ├── impuestos.py       # Setup sheet impuestos
│   │   └── inversiones.py     # Setup sheet Inversiones
│   └── sheets/
│       └── structure.py       # Definición de columnas y fórmulas
│
├── bootstrap.py               # Setup inicial (una sola vez)
├── setup_sheet.py             # Configurar estructura sheets
├── fetch_data.py              # Actualizar datos CER/CCL/REM/SPY
├── plot_rem_curves.py         # Plotear expectativas REM
├── update_daily.sh            # Script actualización diaria
│
├── fetch_portfolio_evolution.py   # Portfolio IEB (opcional)
└── upload_to_inversiones.py       # Upload portfolio (opcional)
```

## Archivos Importantes

- `.env` - Variables de entorno (SPREADSHEET_ID, etc.)
- `token.json` - Token OAuth Google (gitignored)
- `service_account.json` - Service account (gitignored)
- `credentials.json` - OAuth credentials (incluido en repo)

## Deployment

Ver `docs/DEPLOYMENT.md` para instrucciones completas de deployment a VPS.
