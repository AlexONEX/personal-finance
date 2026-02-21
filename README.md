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

3. **Configurar Credenciales de Google**
   Para que la app funcione, necesitas un archivo `credentials.json` en la raíz.
   
   - **Opción A (Rápida):** Usa el archivo `credentials.json` que viene en el repo (credenciales compartidas).
   - **Opción B (Recomendada):** Crea tus propias credenciales en Google Cloud siguiendo [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md). Esto evita límites de uso compartidos.

4. **Crear spreadsheet y cargar estructura**
   ```bash
   uv run bootstrap.py
   ```
   Esto creará un nuevo Google Spreadsheet con todas las hojas y fórmulas configuradas.

## Uso Mensual

**Cada vez que cobras el sueldo:**

1. **Actualizar datos de mercado (CER, CCL, REM)**
   ```bash
   ./update_dataset.sh
   ```

2. **Cargar tu sueldo del mes**
   Abre la hoja `Ingresos` y completa solo las columnas de input manual (Fecha, Bruto, SAC, Bonos, Beneficios). Todo lo demás se calcula automáticamente.

## Estructura del Spreadsheet

- **Ingresos**: Registro mensual y cálculos de poder adquisitivo.
- **historic_data**: Datos históricos de CER y CCL.
- **REM**: Proyecciones de inflación del BCRA.
- **impuestos**: Tasas de descuentos (Jubilación, PAMI, etc.).

## Seguridad y Credenciales

### ¿Es seguro usar este `credentials.json`?
Sí. Este proyecto incluye un `credentials.json` genérico para facilitar el inicio. Para aplicaciones de escritorio, Google y los estándares de la industria confirman que esto es seguro:

1. **Google lo permite explícitamente**: Según la [documentación oficial de Google](https://developers.google.com/identity/protocols/oauth2#installed), el `client_secret` en apps instaladas no se considera confidencial.
2. **Estándar RFC 8252**: El [estándar OAuth 2.0 para Native Apps](https://datatracker.ietf.org/doc/html/rfc8252) confirma que estas apps no pueden mantener secretos de forma segura y que la seguridad real reside en el flujo a través del navegador.
3. **Tu cuenta es privada**: Cada usuario autoriza **su propia cuenta**. El archivo `token.json` (que SÍ es secreto) se genera localmente, está en `.gitignore` y nunca se comparte.

### Aviso de "Google hasn't verified this app"
Al autorizar la app por primera vez, verás este aviso. Es **normal y esperado** porque:
- El proceso de [verificación oficial](https://support.google.com/cloud/answer/7454865?hl=en) es un trámite burocrático pensado para productos comerciales masivos.
- Para herramientas personales o de código abierto ejecutadas localmente, Google permite este flujo bajo la responsabilidad del usuario ("Advanced" > "Go to...").

### SSL y Privacidad
- **SSL**: Se usa `verify=False` **únicamente** para el BCRA debido a fallas técnicas históricas en sus servidores. El resto de las conexiones (Google, APIs de dólar) son seguras.
- **Privacidad**: Ningún dato de tu sueldo sale de tu Google Drive.

## Documentación

- [Diccionario de Columnas](docs/COLUMNAS.md) - Explicación de cada cálculo.
- [OAuth Setup](docs/OAUTH_SETUP.md) - Guía para crear tus propias credenciales.

## Soporte

Si tienes dudas o problemas, abre un Issue en el repositorio o contacta a [ingresos-tracker@proton.me](mailto:ingresos-tracker@proton.me).
