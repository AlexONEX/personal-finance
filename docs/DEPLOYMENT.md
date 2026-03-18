# Deployment y Automatización

## Testing Local (Primera vez)

### 1. Verificar que todo esté configurado

```bash
# Verificar .env
cat .env

# Verificar credentials
ls -la token.json service_account.json

# Verificar imports
uv run python -c "from src.config import COLORS; print('✓ Config OK')"
uv run python -c "from src.fetchers import CERFetcher; print('✓ Fetchers OK')"
uv run python -c "from src.setup import setup_ingresos; print('✓ Setup OK')"
```

### 2. Actualizar datos (primera ejecución)

```bash
# Actualización desde última fecha registrada en el sheet
./update_daily.sh

# O actualizar desde fecha específica
./update_daily.sh --since 2024-01-01
```

### 3. Verificar en Google Sheets

Abrí tu spreadsheet y verificá:
- **historic_data**: Nuevas filas con CER, CCL, SPY
- **REM**: Nuevas proyecciones de inflación
- **Última Actualización**: Timestamp actualizado

## Automatización Local (macOS/Linux)

### Cron Job Diario

```bash
# Editar crontab
crontab -e

# Agregar esta línea (ejecuta todos los días a las 8 AM)
0 8 * * * cd /Users/alex/Github/me/ingresos && ./update_daily.sh >> logs/cron.log 2>&1
```

### Crear directorio de logs

```bash
mkdir -p logs
touch logs/cron.log
```

### Ver logs

```bash
tail -f logs/cron.log
```

## Deployment a VPS

### 1. Preparar VPS (Ubuntu/Debian)

```bash
# Conectar al VPS
ssh user@your-vps-ip

# Instalar dependencias
sudo apt update
sudo apt install -y python3 python3-pip git curl

# Instalar uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Clonar repositorio
cd ~
git clone https://github.com/your-username/ingresos.git
cd ingresos
```

### 2. Configurar Credentials

**Opción A: Service Account (Recomendado para VPS)**

```bash
# Copiar service account desde local
scp service_account.json user@your-vps-ip:~/ingresos/

# En el VPS
cd ~/ingresos
chmod 600 service_account.json
```

**Opción B: OAuth Token**

```bash
# Copiar token desde local
scp token.json user@your-vps-ip:~/ingresos/

# En el VPS
cd ~/ingresos
chmod 600 token.json
```

### 3. Configurar .env

```bash
# En el VPS
cat > .env << EOF
SPREADSHEET_ID=112sfaAbWxUFHitfZ74ba7I3JvkaEStpaCmo6w4BwaNg
GOOGLE_CREDENTIALS_FILE=service_account.json
EOF
```

### 4. Testear manualmente

```bash
# Primera actualización
./update_daily.sh

# Verificar en Google Sheets que funcionó
```

### 5. Configurar Cron Job en VPS

```bash
# Editar crontab
crontab -e

# Ejecutar todos los días a las 6 AM UTC (3 AM Argentina)
0 6 * * * cd /home/user/ingresos && ./update_daily.sh >> logs/cron.log 2>&1

# Crear directorio de logs
mkdir -p ~/ingresos/logs
```

### 6. Monitoreo (Opcional)

```bash
# Ver logs en tiempo real
ssh user@your-vps-ip
tail -f ~/ingresos/logs/cron.log

# Ver últimas 50 líneas
tail -50 ~/ingresos/logs/cron.log
```

### 7. Rotación de Logs (Opcional)

```bash
# Crear logrotate config
sudo tee /etc/logrotate.d/ingresos << EOF
/home/user/ingresos/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

## Troubleshooting

### Error: "No credentials found"

```bash
# Verificar que existan
ls -la token.json service_account.json

# Verificar permisos
chmod 600 token.json service_account.json
```

### Error: "SPREADSHEET_ID not defined"

```bash
# Verificar .env
cat .env

# Debería mostrar:
# SPREADSHEET_ID=112sfaAbWxUFHitfZ74ba7I3JvkaEStpaCmo6w4BwaNg
```

### Error: "SSL verification failed (BCRA)"

Esto es normal, BCRA tiene problemas de certificados. El código usa `verify=False` solo para endpoints de BCRA (documentado).

### Error: "REM publication not found"

BCRA puede haber cambiado el formato de su sitio web. Verificá:
```bash
curl -k https://www.bcra.gob.ar/todos-relevamiento-de-expectativas-de-mercado-rem/
```

### Cron job no ejecuta

```bash
# Verificar que cron esté corriendo
sudo service cron status

# Ver logs de cron del sistema
sudo tail -f /var/log/syslog | grep CRON

# Verificar que el script sea ejecutable
chmod +x ~/ingresos/update_daily.sh
```

## Alternativas de Automatización

### systemd Timer (Linux moderno)

```bash
# Crear service
sudo tee /etc/systemd/system/ingresos-update.service << EOF
[Unit]
Description=Ingresos Data Update
After=network.target

[Service]
Type=oneshot
User=user
WorkingDirectory=/home/user/ingresos
ExecStart=/home/user/ingresos/update_daily.sh
StandardOutput=append:/home/user/ingresos/logs/systemd.log
StandardError=append:/home/user/ingresos/logs/systemd.log
EOF

# Crear timer
sudo tee /etc/systemd/system/ingresos-update.timer << EOF
[Unit]
Description=Ingresos Daily Update Timer

[Timer]
OnCalendar=daily
OnCalendar=06:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Activar
sudo systemctl daemon-reload
sudo systemctl enable ingresos-update.timer
sudo systemctl start ingresos-update.timer

# Verificar status
sudo systemctl status ingresos-update.timer
sudo systemctl list-timers
```

### GitHub Actions (Cloud)

Si querés ejecutarlo en la nube sin VPS, podés usar GitHub Actions gratis:

```yaml
# .github/workflows/update-data.yml
name: Daily Data Update

on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Setup credentials
        run: |
          echo "${{ secrets.SERVICE_ACCOUNT_JSON }}" > service_account.json
          echo "SPREADSHEET_ID=${{ secrets.SPREADSHEET_ID }}" > .env

      - name: Update data
        run: ./update_daily.sh
```

Necesitarías configurar secrets en GitHub:
- `SERVICE_ACCOUNT_JSON`: Contenido de service_account.json
- `SPREADSHEET_ID`: Tu spreadsheet ID

## Costos

- **Local/VPS con cron**: Gratis (si ya tenés el VPS)
- **VPS dedicado**: $5-10/mes (DigitalOcean, Hetzner, Linode)
- **GitHub Actions**: Gratis (2000 minutos/mes en plan free)
- **Google Cloud Run**: ~$0 (casi gratis para tareas diarias)

## Recomendación

Para tu caso:
1. **Testear local** primero con `./update_daily.sh`
2. **VPS con cron** es la solución más simple y confiable
3. **GitHub Actions** si no querés mantener un VPS
