# Automatización Diaria

Este directorio contiene los archivos para automatizar la actualización diaria de datos CER y CCL usando **launchd** (macOS).

## ¿Qué hace?

El job ejecuta `update_daily.sh` todos los días a las 9:00 AM, que:
1. Obtiene datos actualizados de CER, CCL y REM (`fetch_data.py`)

Los datos se actualizan automáticamente en tu spreadsheet sin intervención manual.

---

## Instalación

Desde la raíz del proyecto:

```bash
./automation/install.sh
```

Esto:
- Crea el plist en `~/Library/LaunchAgents/`
- Carga el job en launchd
- Configura ejecución diaria a las 9:00 AM

---

## Verificar que funciona

### Ver status del job

```bash
launchctl list | grep ingresos
```

Deberías ver una línea con `com.ingresos.daily-update`.

### Ejecutar manualmente (para testing)

```bash
launchctl start com.ingresos.daily-update
```

### Ver logs

```bash
# Logs del script
tail -f logs/update_*.log

# Logs de launchd
tail -f logs/launchd-stdout.log
tail -f logs/launchd-stderr.log
```

---

## Cambiar el horario

Editar `~/Library/LaunchAgents/com.ingresos.daily-update.plist`:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>21</integer>  <!-- 9 PM -->
    <key>Minute</key>
    <integer>30</integer>  <!-- :30 -->
</dict>
```

Luego recargar:

```bash
launchctl unload ~/Library/LaunchAgents/com.ingresos.daily-update.plist
launchctl load ~/Library/LaunchAgents/com.ingresos.daily-update.plist
```

---

## Desinstalación

```bash
./automation/uninstall.sh
```

Esto:
- Descarga el job de launchd
- Elimina el plist

---

## Troubleshooting

### El job no corre

1. Verificar que está cargado:
   ```bash
   launchctl list | grep ingresos
   ```

2. Ver errores:
   ```bash
   cat logs/launchd-stderr.log
   ```

3. Probar el script manualmente:
   ```bash
   ./update_daily.sh
   ```

### Permisos

Si ves errores de permisos, asegurate que:
- `update_daily.sh` es ejecutable (`chmod +x update_daily.sh`)
- Tenés acceso al spreadsheet con las credenciales OAuth

---

## Alternativa: cron (Linux/macOS)

Si preferís cron en lugar de launchd:

```bash
# Editar crontab
crontab -e

# Agregar esta línea (corre a las 9:00 AM todos los días)
0 9 * * * cd /Users/alex/Github/me/ingresos && ./update_daily.sh >> logs/cron.log 2>&1
```

**Nota:** cron tiene limitaciones en macOS moderno (requiere permisos de Full Disk Access). launchd es la solución recomendada para macOS.
