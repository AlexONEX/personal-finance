# Ingresos Tracker

Sistema automatizado para el seguimiento de ingresos personales en Argentina, con ajuste por inflación (CER), proyecciones de mercado (REM) y comparativa en dólares (CCL).

## Requisitos

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (package manager)
- Cuenta de Google (para acceder al spreadsheet)

## Setup Inicial

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/ingresos.git
   cd ingresos
   ```

2. **Instalar dependencias**
   ```bash
   uv sync
   ```

3. **Crear spreadsheet y cargar estructura**
   ```bash
   uv run bootstrap.py
   ```
   Esto creará un nuevo Google Spreadsheet con todas las hojas y fórmulas configuradas.

4. **Cargar datos históricos** (opcional, ya incluido en bootstrap)
   ```bash
   uv run fetch_data.py
   ```

### Autorización OAuth (primera vez)

La primera vez que ejecutes cualquier script, se abrirá un navegador para autorizar el acceso a Google Sheets:

1. Seleccioná tu cuenta de Google
2. Verás un warning: **"Google hasn't verified this app"**
   - Esto es normal - la app usa credenciales compartidas del repo
   - Click **"Advanced"**
   - Click **"Go to ingresos-tracker (unsafe)"**
3. Click **"Allow"** para dar permisos de acceso a Sheets
4. El token se guardará automáticamente en `token.json`

**¿Por qué aparece este warning?**
La app no está "verificada" por Google porque [el proceso de verificación](https://support.google.com/cloud/answer/7454865?hl=en) es extremadamente largo y complejo. Además, **no necesitamos verificación** según la propia documentación de Google, ya que este proyecto es:
- Código open source experimental/personal (no un producto comercial)
- Ejecutado localmente por cada usuario (no un servicio centralizado)
- No lanzado al público como servicio

Por eso usamos credenciales OAuth compartidas (`credentials.json`) incluidas en el repositorio. Esto permite que funcione sin que cada usuario tenga que crear su propio proyecto en Google Cloud. Es seguro porque solo pedimos permisos de lectura/escritura de Sheets y el código es open source.

Si preferís usar tus propias credenciales OAuth, seguí la guía en [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md).

## Uso Mensual

**Cada vez que cobrás el sueldo:**

1. **Actualizar datos de mercado (CER, CCL, REM)**
   ```bash
   ./update_dataset.sh
   ```

   Este script busca automáticamente la última fecha actualizada en el sheet y completa todos los datos faltantes hasta hoy.

2. **Cargar tu sueldo del mes**

   Abrí la hoja `Ingresos` en tu spreadsheet y completá solo estas columnas:
   - **A (Fecha)**: Primer día del mes (ej: 01/06/2024)
   - **B (Bruto)**: Sueldo bruto del mes
   - **G (SAC Bruto)**: Aguinaldo (solo Jun/Dic)
   - **I (Bono Neto)**: Bonos extraordinarios (opcional)
   - **J (Comida)**: Beneficio de comida (opcional)
   - **K (Otros Beneficios)**: Otros beneficios (opcional)

   Todo lo demás se calcula automáticamente.

## Estructura del Spreadsheet

El spreadsheet tiene 5 hojas:

- **Ingresos**: Tu registro mensual de ingresos y todos los cálculos
- **historic_data**: Datos históricos de CER y CCL (actualizado por `fetch_data.py`)
- **REM**: Proyecciones de inflación del BCRA (actualizado por `fetch_data.py`)
- **impuestos**: Tasas de descuentos (Jubilación 11%, PAMI 3%, Obra Social 3%)
- **Panel**: Instrucciones para sincronización interna

## Seguridad y Credenciales

### ¿Por qué `credentials.json` está en el repositorio?

Este proyecto incluye `credentials.json` (credenciales OAuth) en el repositorio para simplificar el setup. Esto es **seguro para aplicaciones desktop** porque:

1. **Google lo permite explícitamente**: Según la [documentación oficial de Google](https://developers.google.com/identity/protocols/oauth2#installed), para aplicaciones instaladas/desktop el `client_secret` **no se considera confidencial**:
   > "The client secret is not treated as a secret for installed applications and native applications, because there is no way to guarantee the client secret will remain confidential."

2. **RFC 8252 (OAuth 2.0 for Native Apps)**: El estándar oficial confirma que aplicaciones nativas **no pueden mantener secretos** de forma segura:
   > "This best current practice requires that only external user-agents like the browser are used for OAuth by native apps. It documents how native apps can implement authorization flows using the browser."

3. **La seguridad real viene de**:
   - Cada usuario autoriza **su propia cuenta** mediante el flujo OAuth en el navegador
   - El `token.json` (que SÍ es secreto y contiene acceso a tu cuenta) está en `.gitignore` y nunca se comparte
   - Los permisos se limitan solo a Google Sheets (scope específico)

4. **Riesgos reales** (bajos):
   - Alguien podría spamear requests y Google revoca las credenciales compartidas → solución: regenerar
   - **NO hay riesgo** de acceso a cuentas de usuarios (cada uno autoriza la suya)

### ¿Querés usar tus propias credenciales?

Si preferís crear tus propias credenciales OAuth (usuarios avanzados), seguí la guía en [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md).

### Archivos importantes

- `credentials.json` - Credenciales OAuth compartidas (incluidas en repo)
- `token.json` - Tu token de acceso personal (en `.gitignore`, NUNCA compartir)
- Ambos archivos deben estar en la raíz del proyecto

### Nota sobre SSL y BCRA

El código usa `verify=False` **únicamente** para requests al BCRA (Banco Central de Argentina) debido a problemas conocidos con sus certificados SSL. Todas las demás conexiones (Google Sheets, dolarapi, Ambito) usan verificación SSL completa. Esta es una excepción necesaria y documentada para acceder a datos oficiales de inflación.

## Documentación

- [Diccionario de Columnas](docs/COLUMNAS.md) - Explicación detallada de cada columna
- [OAuth Setup](docs/OAUTH_SETUP.md) - Cómo configurar tus propias credenciales OAuth (opcional)

## Configuración

Si cambian los aportes de ley, editalos en la hoja `impuestos` del spreadsheet.
