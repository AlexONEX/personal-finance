# Testing Rápido - Después del Refactoring

## 1. Verificar que todo compile ✅

```bash
# Imports OK
uv run python -c "from src.config import COLORS; print('✓ Config')"
uv run python -c "from src.fetchers import CERFetcher; print('✓ Fetchers')"
uv run python -c "from src.setup import setup_ingresos; print('✓ Setup')"

# Compilación OK
uv run python -m py_compile setup_sheet.py
uv run python -m py_compile fetch_data.py
```

## 2. Actualizar Datos (Testing)

```bash
# Actualizar desde última fecha registrada
./update_daily.sh

# Ver qué está pasando
tail -f logs/cron.log  # (si creaste el directorio logs)
```

## 3. Verificar en Google Sheets

Abrí: https://docs.google.com/spreadsheets/d/112sfaAbWxUFHitfZ74ba7I3JvkaEStpaCmo6w4BwaNg

Verificá:
- **historic_data** (pestaña): Nuevas filas con fechas recientes
- **REM** (pestaña): Timestamp actualizado en B1
- **Ingresos** (pestaña): Fórmulas funcionando con nuevos datos

## 4. Automatización Diaria (Local - macOS)

```bash
# Crear directorio de logs
mkdir -p logs

# Editar crontab
crontab -e

# Pegar esta línea (ejecuta todos los días a las 8 AM):
0 8 * * * cd /Users/alex/Github/me/ingresos && ./update_daily.sh >> logs/cron.log 2>&1

# Guardar y salir (:wq en vim)
```

## 5. Ver Logs

```bash
# Ver logs en tiempo real
tail -f logs/cron.log

# Ver últimas 50 líneas
tail -50 logs/cron.log

# Ver solo errores
grep ERROR logs/cron.log
```

## Comandos Útiles

```bash
# Actualizar desde fecha específica
./update_daily.sh --since 2024-01-01

# Ver ayuda
uv run python fetch_data.py --help

# Testear solo CER (sin actualizar sheet)
uv run python -c "
from src.fetchers import CERFetcher
from datetime import date
fetcher = CERFetcher()
data = fetcher.fetch(date(2024, 1, 1), date.today())
print(f'Fetched {len(data)} CER records')
"

# Testear solo CCL
uv run python -c "
from src.fetchers import CCLFetcher
from datetime import date
fetcher = CCLFetcher()
data = fetcher.fetch(date(2024, 1, 1), date.today())
print(f'Fetched {len(data)} CCL records')
"
```

## Troubleshooting

### "command not found: uv"

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### "SPREADSHEET_ID not defined"

```bash
cat .env
# Debería mostrar: SPREADSHEET_ID=112sfaAbWxUFHitfZ74ba7I3JvkaEStpaCmo6w4BwaNg
```

### "No credentials found"

```bash
ls -la token.json service_account.json
# Al menos uno debería existir
```

### Cron no ejecuta (macOS)

En macOS Catalina+ necesitás dar permisos a cron:
1. System Preferences → Security & Privacy → Privacy
2. Full Disk Access
3. Agregar `/usr/sbin/cron`

## Siguiente Paso: VPS

Ver `docs/DEPLOYMENT.md` para instrucciones completas de deployment a VPS.
