# Ingresos Tracker

Sistema automatizado para seguimiento de ingresos personales en Argentina. Compara tu sueldo contra inflación (CER), proyecciones de mercado (REM) y paridad dólar (CCL) para entender tu poder adquisitivo real.

## 🎯 ¿Qué hace?

Toma tu sueldo bruto mensual y calcula automáticamente:
- ✅ Descuentos legales (Jubilación 11%, PAMI 3%, Obra Social 3%)
- ✅ Sueldo neto en ARS y USD (CCL)
- ✅ Comparación vs inflación real (CER)
- ✅ Target salariales según proyecciones BCRA (REM)
- ✅ Tracking de poder adquisitivo en dólares
- ✅ Performance mensual de inversiones (integración con finance-tracking)

**Resultado:** Una Google Sheet completa con 38 columnas de análisis automático.

---

## 🚀 Quick Start

### Setup Inicial (5 minutos)

```bash
# 1. Instalar dependencias
uv sync

# 2. Crear spreadsheet con estructura completa
uv run bootstrap.py
```

El script `bootstrap.py` hace TODO automáticamente:
- ✅ Crea Google Sheet nueva
- ✅ Configura tabs (Ingresos, historic_data, REM, impuestos, Inversiones)
- ✅ Genera `.env` con SPREADSHEET_ID
- ✅ Aplica colores, formato y fórmulas

### Uso Mensual (1 minuto)

**Cuando cobras tu sueldo:**

1. **Actualizar datos de mercado:**
   ```bash
   ./update_dataset.sh
   ```
   Esto descarga automáticamente:
   - CER (inflación oficial BCRA)
   - CCL (dólar paralelo)
   - REM (proyecciones de mercado BCRA)
   - SPY (S&P 500 para benchmark)

2. **Cargar tu sueldo:**
   - Abrir Google Sheet → Tab "Ingresos"
   - Completar **solo estas columnas:**
     - Fecha (A)
     - Bruto (B)
     - SAC/Aguinaldo (H) - si corresponde
     - Bonos (J) - si corresponde
     - Beneficios (K) - si corresponde

   **TODO lo demás se calcula automáticamente** (descuentos, neto, comparativas, USD, inflación, proyecciones).

3. **Leer análisis automático:**
   - ¿Tu sueldo perdió contra inflación? → Ver columna "Variación respecto último aumento"
   - ¿Cuánto necesitás ganar para empatar CER? → Ver "Sueldo necesario para mantener poder adquisitivo"
   - ¿Qué proyecta el mercado? → Ver "REM 3 meses" y "REM 6 meses"

---

## 📊 Estructura del Spreadsheet

### Tabs

| Tab | Contenido | Quién escribe |
|-----|-----------|---------------|
| **Ingresos** | 37 columnas de análisis salarial | Vos (solo bruto) + Fórmulas |
| **historic_data** | CER, CCL, SPY históricos | Python (update_dataset.sh) |
| **REM** | Proyecciones BCRA 3m/6m | Python (update_dataset.sh) |
| **impuestos** | Tasas de descuentos legales | Manual (11%, 3%, 3%) |
| **Inversiones** | Portfolio evolution mensual | Python (desde finance-tracking) |
| **Panel** | Dashboard visual | Fórmulas (opcional) |

### Las 38 Columnas (Grupos Funcionales)

Ver `docs/COLUMNAS.md` para detalle completo. Resumen:

1. **PERIODO** (Col A) - Mes de pago (auto-generado)
2. **SUELDO** (Cols B-G) - Bruto → Descuentos → Neto ARS
3. **AGUINALDO** (Cols H-I) - 13° sueldo/SAC
4. **BONOS** (Col J) - Bonos extraordinarios
5. **BENEFICIOS** (Cols K-L) - Tarjeta corporativa, otros
6. **TOTAL** (Col M) - Total neto mensual
7. **COMPARACION CON ULTIMO AUMENTO ARS** (Cols N-S) - Paridad inflacionaria
8. **INFLACIÓN (CER)** (Cols T-V) - Variación CER mensual y acumulada
9. **PROYECCION REM** (Cols W-AB) - Targets según BCRA
10. **DÓLAR** (Cols AC-AF) - CCL y sueldo en USD
11. **VS ÚLTIMO AUMENTO USD** (Cols AG-AL) - Paridad USD

**Input manual:** Solo columnas B, C, H, J, K, L (6 de 38).
**Auto-calculadas:** Las otras 32 columnas.

---

## 📁 Estructura del Proyecto

```
ingresos/
├── src/
│   ├── connectors/
│   │   └── sheets.py           # Google Sheets OAuth/Service Account
│   └── sheets/
│       └── structure.py        # Schema de columnas y formato
├── docs/
│   ├── COLUMNAS.md             # Diccionario completo de 37 columnas
│   └── OAUTH_SETUP.md          # Setup de credenciales propias
├── bootstrap.py                # 🌟 Setup completo one-command
├── setup_sheet.py              # Crea estructura de sheet (usado por bootstrap)
├── fetch_data.py               # Descarga CER, CCL, REM, SPY
├── fetch_portfolio_evolution.py # IEB portfolio data (opcional)
├── upload_to_inversiones.py    # Sube portfolio a sheet
├── update_dataset.sh           # 🌟 Script mensual (ejecutar esto)
├── test_ieb_endpoint.py        # Tests de IEB API
├── pyproject.toml              # Dependencias (Python 3.11+)
├── .env                        # Config auto-generada por bootstrap
├── credentials.json            # OAuth genérico (incluido en repo)
└── token.json                  # Tu token personal (gitignored)
```

**Total:** ~1,600 líneas de Python

---

## ⚙️ Configuración

### Variables de entorno (.env)

Generado automáticamente por `bootstrap.py`:

```bash
SPREADSHEET_ID=<auto-generado>
HISTORIC_START_DATE=2022-01-01

# Opcional - Solo si usás integración con portfolio de inversiones
IEB_ACCOUNT_ID=26935110
IEB_USER_AGENT=...
IEB_X_DEVICE_ID=...
IEB_X_CLIENT_NAME=...
```

### Autenticación Google

**Opción A (Rápida - Recomendada):**
- Usa el `credentials.json` incluido en el repo
- Es seguro compartirlo (ver sección de Seguridad)
- `bootstrap.py` lo detecta automáticamente

**Opción B (Custom):**
- Crear tus propias credenciales en Google Cloud
- Seguir `docs/OAUTH_SETUP.md`
- Útil si vas a usar intensivamente (evita límites compartidos)

---

## 🔍 Fuentes de Datos

| Dato | Fuente | Frecuencia | Confiabilidad |
|------|--------|------------|---------------|
| **CER** | BCRA API (`api.bcra.gob.ar`) | Diaria | ⭐⭐⭐⭐⭐ |
| **CCL** | Ambito.com + dolarapi.com | Tiempo real | ⭐⭐⭐⭐ |
| **REM** | BCRA Excel (web scraping) | Mensual | ⭐⭐⭐⭐ (oficial) |
| **SPY** | yfinance | Diaria | ⭐⭐⭐⭐⭐ |
| **Portfolio** | IEB API (opcional) | Manual | ⭐⭐⭐⭐ |

### CER (Inflación Oficial)
- Coeficiente de Estabilización de Referencia
- Más confiable que CPI mensual para comparaciones intra-año
- Fuente: BCRA (Banco Central de la República Argentina)

### CCL (Contado con Liquidación)
- Dólar implícito usado por inversores para girar dinero al exterior
- Más representativo que dólar oficial para poder adquisitivo real
- Fuente primaria: Ambito.com (JSON endpoint)
- Fallback: dolarapi.com

### REM (Relevamiento de Expectativas de Mercado)
- Proyecciones de inflación 3 y 6 meses adelante
- Encuesta mensual BCRA a economistas, consultoras y bancos
- **Utilidad:** Negociar aumentos ("el mercado proyecta X% para los próximos 6 meses")

---

## 🔄 Pipeline de Datos

```
update_dataset.sh ejecuta:
  ├── fetch_cer()            → BCRA API
  ├── fetch_ccl_ambito()     → Ambito.com JSON
  ├── fetch_ccl_today()      → dolarapi.com (real-time)
  ├── fetch_spy()            → yfinance (S&P 500)
  └── get_rem_publication()  → BCRA website
       ├── HTML parsing
       ├── Excel download
       ├── openpyxl parse
       └── Upload to REM sheet

Paralelo (ThreadPoolExecutor):
  ├── CER + CCL + SPY en paralelo
  └── REM secuencial (depende de Excel parse)
```

---

## 🔗 Integración con finance-tracking

Si tenés el proyecto `finance-tracking` (para tracking de inversiones):

### 1. Compartir credenciales
Ambos proyectos usan el mismo `service_account.json` para escribir en Google Sheets.

### 2. Fetch portfolio evolution
```bash
uv run fetch_portfolio_evolution.py
```
Descarga datos mensuales de IEB (requiere credenciales IEB en `.env`).

### 3. Upload a sheet "Inversiones"
```bash
uv run upload_to_inversiones.py
```
Escribe a la tab "Inversiones" de tu sheet de ingresos.

**Workflow integrado:**
1. Semanal: Ejecutar `finance-tracking/main.py` (actualizar portfolio detallado)
2. Mensual: Ejecutar `ingresos/update_dataset.sh` (traer datos macro)
3. Mensual: Ejecutar `ingresos/fetch_portfolio_evolution.py` (sync con sheet Inversiones)

---

## 🛠️ Scripts Disponibles

### bootstrap.py (Solo una vez)
```bash
uv run bootstrap.py
```
Setup completo:
- Crea Google Sheet nueva
- Configura estructura completa (tabs, headers, formato, colores)
- Genera `.env` con SPREADSHEET_ID
- Autentica con Google OAuth

### update_dataset.sh (Mensual)
```bash
./update_dataset.sh
```
Actualiza datos económicos:
- Descarga CER, CCL, REM, SPY
- Escribe a sheet
- Loguea resultado a `update_dataset.log`

**Tip:** Ejecutar el 1° de cada mes o cuando recibís recibo de sueldo.

### fetch_portfolio_evolution.py (Opcional)
```bash
uv run fetch_portfolio_evolution.py
```
Descarga performance mensual de inversiones desde IEB.

Requiere en `.env`:
```
IEB_ACCOUNT_ID=...
IEB_USER_AGENT=...
IEB_X_DEVICE_ID=...
IEB_X_CLIENT_NAME=...
```

### fetch_data.py (Standalone)
```bash
uv run fetch_data.py
```
Solo descarga datos económicos (sin logs). `update_dataset.sh` usa este script internamente.

---

## 🐛 Troubleshooting

### Error: "Could not read Spreadsheet ID"
**Causa:** `.env` no existe o está corrupto.

**Solución:**
```bash
# Regenerar con bootstrap
uv run bootstrap.py
```

### Error: "BCRA API SSL verification failed"
**Causa:** Infraestructura BCRA tiene problemas de certificados SSL históricos (común en Argentina).

**Solución:** Ya manejado en el código con `verify=False` solo para BCRA. No es un problema de seguridad (es conocido).

### Error: "REM publication not found"
**Causa:** BCRA cambió formato de su website o no publicó datos este mes.

**Solución:** Esperar a que BCRA publique o parsear manualmente desde:
https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_Expectativas_de_Mercado.asp

### Error: "Permission denied on Google Sheets"
**Causa:** OAuth token expiró o scope insuficiente.

**Solución:**
```bash
# Eliminar token y re-autenticar
rm token.json
uv run bootstrap.py  # Re-autorizar
```

### Aviso: "Google hasn't verified this app"
**Esperado y normal** - ver sección de Seguridad abajo.

---

## 🔒 Seguridad y Privacidad

### ¿Es seguro el credentials.json incluido?

**Sí.** Para apps de escritorio, el `client_secret` en `credentials.json` NO se considera confidencial:

1. **Google lo permite explícitamente:** [Documentación oficial](https://developers.google.com/identity/protocols/oauth2#installed)
2. **RFC 8252 (OAuth 2.0 for Native Apps):** Confirma que apps nativas no pueden mantener secretos seguros
3. **Tu token es privado:** El archivo `token.json` (que SÍ es secreto) se genera localmente y está en `.gitignore`

### Datos que NUNCA salen de tu Google Drive

- Montos de sueldos
- Datos personales
- Movimientos de inversión

**Todo vive en tu Google Sheet, con permisos que controlás vos.**

### SSL y conexiones seguras

- **BCRA:** `verify=False` solo para BCRA (infraestructura argentina conocida por problemas de certs)
- **Google APIs:** HTTPS con verificación completa
- **Dolarapi/Ambito:** HTTPS con verificación completa

---

## 📖 Documentación Adicional

- **docs/COLUMNAS.md:** Explicación detallada de las 37 columnas
- **docs/OAUTH_SETUP.md:** Crear tus propias credenciales Google Cloud

---

## 🎯 Casos de Uso Reales

### 1. Negociar aumento
```
"El REM proyecta 45% de inflación para los próximos 6 meses.
Mi sueldo actual de $500K debería ser $725K para mantener poder adquisitivo."
```
→ Ver columna "Sueldo necesario REM 6 meses"

### 2. Evaluar oferta laboral
```
"Me ofrecen $600K. ¿Es mejor que mi sueldo actual ajustado por inflación?"
```
→ Comparar con columna "Sueldo ajustado inflación (CER)"

### 3. Trackear depreciación del peso
```
"Hace 6 meses ganaba USD 1,200 al CCL. Hoy gano USD 980 con el mismo sueldo ARS."
```
→ Ver columna "Sueldo en USD (CCL)"

### 4. Evaluar portfolio de inversiones
```
"Mis inversiones subieron 50% en ARS pero perdieron 10% contra el dólar."
```
→ Ver tab "Inversiones" + columna "Return vs CCL"

---

## 👥 Para Conocidos (Setup en 5 min)

1. **Clonar repo:**
   ```bash
   git clone https://github.com/tu-usuario/ingresos.git
   cd ingresos
   ```

2. **Instalar uv** (si no lo tenés):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Setup completo:**
   ```bash
   uv sync
   uv run bootstrap.py
   ```

   Esto:
   - Te abre navegador para autorizar Google
   - Crea Google Sheet nueva
   - Te muestra URL de tu sheet
   - Genera `.env` automáticamente

4. **Primer uso:**
   ```bash
   ./update_dataset.sh  # Descargar datos macro
   ```

   Después abrir Google Sheet y cargar tu primer sueldo (solo columnas A, B, H, J, K).

5. **Uso mensual:**
   - Ejecutar `./update_dataset.sh` el 1° de cada mes
   - Cargar sueldo nuevo en sheet

**Eso es todo.** No necesitás tocar código.

---

## 🔮 Roadmap Futuro

### Corto Plazo
- [ ] Panel visual con gráficos (tab "Panel")
- [ ] Export a PDF mensual automático
- [ ] Alertas por email cuando inflación > X%

### Largo Plazo - Merge con finance-tracking
**Visión:** App TypeScript unificada para tracking patrimonial completo.

**Features:**
- Frontend web único (React)
- Backend TypeScript + PostgreSQL
- Módulo ingresos + Módulo inversiones
- Dashboard consolidado (patrimonio neto, cash flow, ROI)
- Docker local → Deploy cloud

**No comenzar hasta:**
- ✅ Ambos proyectos estables y funcionando bien
- ✅ Todas las fuentes de datos confiables

Ver `finance-tracking/README.md` para más detalles de la visión.

---

## 🛠️ Desarrollo

### Comandos útiles

```bash
# Ejecutar tests de IEB API
uv run test_ieb_endpoint.py

# Ejecutar tests de performance
uv run test_performance.py

# Ver logs de última ejecución
tail -f update_dataset.log
```

### Stack Técnico

- **Runtime:** Python 3.11+ con `uv` package manager
- **Google Sheets:** `gspread` (OAuth 2.0)
- **Scraping:** `BeautifulSoup4` (BCRA, Ambito)
- **Excel:** `openpyxl` (REM parsing)
- **Finance:** `yfinance` (SPY data)
- **Concurrency:** `ThreadPoolExecutor` (fetch paralelo)

---

## 📝 License

MIT

---

## 🤝 Contribuciones

Acepto PRs para:
- Nuevas fuentes de datos económicos
- Mejoras en parsing de REM
- Dashboards visuales (gráficos)
- Documentación

---

**Última actualización:** 2024-02-24
**Mantenedor:** Alex (@AlexONEX)
**Relacionado:** [finance-tracking](https://github.com/AlexONEX/finance-tracking) - Portfolio tracking system
