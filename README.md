# Ingresos Tracker 🇦🇷

Sistema automatizado para tracking de ingresos en Argentina con ajuste por inflación (CER) y dolarización (CCL).

---

## 🚀 Setup Rápido (3 minutos)

```bash
# 1. Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar repo
git clone <repo-url>
cd ingresos

# 3. Bootstrap (abre browser para autorizar)
uv run bootstrap.py
```

**¿Qué hace?** Crea tu spreadsheet automáticamente con datos históricos desde 2022.

**Importante:** Se va a abrir el browser para que autorices "Ingresos Tracker" con tu cuenta Google. El `credentials.json` incluido en el repo es seguro (ver sección Seguridad abajo).

---

## 📊 ¿Qué trackea?

### Datos automáticos (se actualizan solos)
- **CER** - BCRA API (inflación oficial)
- **CCL** - Ambito Financiero (dólar contado con liqui)

### Tu input manual (en la tab "test")
- Sueldo bruto mensual
- Aguinaldo (SAC) - Jun/Dic
- Bonos/beneficios empresa

### Análisis que calcula automáticamente
- ✅ Impuestos (jubilación 11%, PAMI 3%, obra social 3%)
- ✅ Neto en ARS y USD
- ✅ **¿Le ganaste a la inflación?** (sueldo real ajustado por CER)
- ✅ Poder adquisitivo mes a mes
- ✅ Índices y variaciones MoM

---

## 📁 Estructura del Spreadsheet

**4 sheets creadas automáticamente:**

1. **impuestos** - Tasas configurables (editá acá para cambiarlas)
2. **historic_data** - Datos diarios CER + CCL (auto-poblado)
3. **market_data** - Agregados mensuales (auto-calculado)
4. **test** - **TU INPUT ACÁ** → todo lo demás se calcula solo

**En la tab "test" ingresás:**
- Col A: Fecha (01/06/2024)
- Col B: Sueldo Bruto
- Col G: SAC Bruto (solo Jun/Dic)
- Col I-K: Bonos, comida, viajes (opcional)

**Fórmulas calculan automáticamente:**
- Impuestos, neto, conversión USD, análisis vs inflación, etc.

---

## 🔄 Actualizar Datos

### Manual
```bash
./update_daily.sh
```

### Automático (recomendado)
```bash
./automation/install.sh  # Configura update diario a las 9 AM
```

---

## 🔧 Comandos Útiles

```bash
# Actualizar datos desde fecha específica
uv run fetch_historic.py --since 2022-01-01

# Recomputar agregados mensuales
uv run compute_market.py

# Recrear estructura del sheet (⚠️ borra data)
uv run setup_sheet.py

# Crear sheet de prueba para validar cambios
uv run setup_ingresos_replica.py
```

---

## 🔐 Seguridad y Privacidad

### ¿Por qué el repo incluye `credentials.json`?

Es un **OAuth Desktop App client**. Este archivo:
- ✅ **NO da acceso a tus datos** - solo identifica la app "Ingresos Tracker"
- ✅ **Requiere TU autorización** - se abre browser y vos decidís
- ✅ **Tu token es privado** - el `token.json` que se genera está en .gitignore
- ✅ **Es seguro commitearlo** - diseñado para apps públicas

De la [doc oficial de Google](https://developers.google.com/identity/protocols/oauth2/native-app):
> *"The client secret is not treated as a secret for native apps."*

### ¿Qué permisos tiene?

**Solo Google Sheets.** No puede leer emails, Drive, ni nada más.

### ¿Cómo revoco acceso?

https://myaccount.google.com/permissions → Remover "Ingresos Tracker"

### ¿Qué se commitea?

| Archivo | Repo | Privado | Descripción |
|---------|------|---------|-------------|
| `credentials.json` | ✅ Sí | No | OAuth client (público) |
| `token.json` | ❌ No | Sí | Tu access token |
| `.env` | ❌ No | Sí | Tu SPREADSHEET_ID |
| `service_account.json` | ❌ No | Sí | Si lo tenés |

---

## 🛠️ Troubleshooting

**Error: "Client secrets must be for a web or installed app"**
→ El `credentials.json` está corrupto. Re-clona el repo.

**Error: "SPREADSHEET_ID not set"**
→ Corriste scripts sin hacer `bootstrap.py` primero.

**Los datos no se actualizan**
→ Corrí `./update_daily.sh` manualmente y verificá errores.

**Quiero cambiar tasas de impuestos**
→ Editá directamente la sheet **impuestos**, todo se recalcula solo.

---

## 🏗️ Arquitectura (para developers)

```
BCRA API + Ambito.com
       ↓
fetch_historic.py → historic_data (daily)
       ↓
compute_market.py → market_data (monthly end-of-month)
       ↓
test sheet (VLOOKUP) → tus inputs + análisis automático
```

**Archivos principales:**
- `bootstrap.py` - Setup one-command
- `auth.py` - OAuth authentication
- `fetch_historic.py` - Fetch CER + CCL
- `compute_market.py` - Agregación mensual
- `setup_sheet.py` - Crea sheets con formulas
- `update_daily.sh` - Wrapper para updates

---

## 🤝 Contributing

PRs bienvenidos para:
- Más fuentes de datos (blue, MEP, oficial)
- Más análisis
- Soporte multi-país
- Bug fixes

Ver archivos del proyecto para entender estructura.

---

## 📝 License

MIT

---

## ⚡ Para usuarios avanzados

### Usar service account en vez de OAuth

Si preferís service account:

1. Creá service account en Google Cloud Console
2. Descargá JSON como `service_account.json`
3. Compartí el spreadsheet con el email del service account
4. Los scripts detectan automáticamente cuál usar (OAuth o service account)

### Cambiar fecha inicio histórico

Editá `.env`:
```
HISTORIC_START_DATE=2020-01-01
```

### Fork con tu propio OAuth client

1. Google Cloud Console → OAuth Desktop App
2. Reemplazá `credentials.json`
3. Listo

---

**Made with ❤️ para sobrevivir a la inflación argentina 🇦🇷**
