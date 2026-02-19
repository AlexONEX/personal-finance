# Ingresos Tracker - Argentina

Sistema automatizado para tracking de ingresos en Argentina con ajuste por inflacion (CER) y dolarizacion (CCL).

---

## Setup Rapido (3 minutos)

```bash
# 1. Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar repo
git clone <repo-url>
cd ingresos

# 3. Bootstrap (abre browser para autorizar)
uv run bootstrap.py
```

**Que hace:** Crea tu spreadsheet automaticamente con datos historicos desde 2022.

**Importante:** Se va a abrir el browser para que autorices "Ingresos Tracker" con tu cuenta Google. El `credentials.json` incluido en el repo es seguro (ver seccion Seguridad abajo).

---

## Que trackea

### Datos automaticos (se actualizan solos)
- **CER** - BCRA API (inflacion oficial)
- **CCL** - Ambito Financiero (dolar contado con liqui)

### Tu input manual (en la tab "test")
- Sueldo bruto mensual
- Aguinaldo (SAC) - Jun/Dic
- Bonos/beneficios empresa

### Analisis que calcula automaticamente
- Impuestos (jubilacion 11%, PAMI 3%, obra social 3%)
- Neto en ARS y USD
- **Le ganaste a la inflacion?** (sueldo real ajustado por CER)
- Poder adquisitivo mes a mes
- Indices y variaciones MoM

---

## Estructura del Spreadsheet

**4 sheets creadas automaticamente:**

1. **impuestos** - Tasas configurables (edita aca para cambiarlas)
2. **historic_data** - Datos diarios CER + CCL (auto-poblado)
3. **market_data** - Agregados mensuales (auto-calculado)
4. **test** - **TU INPUT ACA** - todo lo demas se calcula solo

**En la tab "test" ingresas:**
- Col A: Fecha (01/06/2024)
- Col B: Sueldo Bruto
- Col G: SAC Bruto (solo Jun/Dic)
- Col I-K: Bonos, comida, viajes (opcional)

**Formulas calculan automaticamente:**
- Impuestos, neto, conversion USD, analisis vs inflacion, etc.

---

## Actualizar Datos

### Manual
```bash
./update_daily.sh
```

### Automatico (recomendado)
```bash
./automation/install.sh  # Configura update diario a las 9 AM
```

---

## Comandos Utiles

```bash
# Actualizar datos desde fecha especifica
uv run fetch_historic.py --since 2022-01-01

# Recomputar agregados mensuales
uv run compute_market.py

# Recrear estructura del sheet (ADVERTENCIA: borra data)
uv run setup_sheet.py

# Testear toda la funcionalidad
uv run test_flow.py
```

---

## Seguridad y Privacidad

### Por que el repo incluye `credentials.json`?

Es un **OAuth Desktop App client**. Este archivo:
- **NO da acceso a tus datos** - solo identifica la app "Ingresos Tracker"
- **Requiere TU autorizacion** - se abre browser y vos decidis
- **Tu token es privado** - el `token.json` que se genera esta en .gitignore
- **Es seguro commitearlo** - disenado para apps publicas

De la [doc oficial de Google](https://developers.google.com/identity/protocols/oauth2/native-app):
> "The client secret is not treated as a secret for native apps."

### Que permisos tiene?

**Solo Google Sheets.** No puede leer emails, Drive, ni nada mas.

### Como revoco acceso?

https://myaccount.google.com/permissions - Remover "Ingresos Tracker"

### Que se commitea?

| Archivo | Repo | Privado | Descripcion |
|---------|------|---------|-------------|
| `credentials.json` | Si | No | OAuth client (publico) |
| `token.json` | No | Si | Tu access token |
| `.env` | No | Si | Tu SPREADSHEET_ID |
| `service_account.json` | No | Si | Si lo tenes |

---

## Troubleshooting

**Error: "Client secrets must be for a web or installed app"**
- El `credentials.json` esta corrupto. Re-clona el repo.

**Error: "SPREADSHEET_ID not set"**
- Corriste scripts sin hacer `bootstrap.py` primero.

**Los datos no se actualizan**
- Corri `./update_daily.sh` manualmente y verifica errores.

**Quiero cambiar tasas de impuestos**
- Edita directamente la sheet **impuestos**, todo se recalcula solo.

---

## Arquitectura

```
src/
├── connectors/      # APIs externas (BCRA, Ambito, Google Sheets)
├── core/            # Logica de negocio (agregaciones)
└── sheets/          # Definiciones y setup de sheets

Entry points (raiz):
- bootstrap.py       # Setup one-command
- fetch_historic.py  # Actualizar CER + CCL
- compute_market.py  # Agregacion mensual
- update_daily.sh    # Wrapper para updates
- test_flow.py       # Test suite
```

**Flujo de datos:**
```
BCRA API + Ambito.com
       |
fetch_historic.py -> historic_data (daily)
       |
compute_market.py -> market_data (monthly end-of-month)
       |
test sheet (VLOOKUP) -> tus inputs + analisis automatico
```

---

## Contributing

PRs bienvenidos para:
- Mas fuentes de datos (blue, MEP, oficial)
- Mas analisis
- Soporte multi-pais
- Bug fixes

---

## License

MIT

---

**Made with heart para sobrevivir a la inflacion argentina**
