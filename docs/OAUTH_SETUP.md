# OAuth Setup - Guía para Tus Propias Credenciales

Este instructivo es para usuarios que quieran usar `ingresos-tracker` con sus propias credenciales OAuth de Google Cloud.

**Tiempo estimado:** 5 minutos.
**Frecuencia:** Una sola vez.

## ¿Por qué crear tus propias credenciales?

Para que la aplicación pueda acceder a tus Google Sheets, necesitas un archivo `credentials.json`. Aunque el repo trae uno genérico para que pruebes rápido, crear el tuyo tiene ventajas:
1. **Independencia total:** Si doy de baja las credenciales compartidas por seguridad, las tuyas siguen funcionando.
2. **Sin límites de uso:** No compartes el límite de peticiones de Google (Rate Limits) con otros usuarios.
3. **Mayor privacidad:** Tú eres el "Dueño" de la aplicación en Google Cloud.

## Paso a Paso

### 1. Crear Proyecto en Google Cloud

1. Ve a: [https://console.cloud.google.com](https://console.cloud.google.com)
2. Haz clic en el selector de proyectos (arriba a la izquierda) > **"NEW PROJECT"**.
3. Nombre: `ingresos-tracker-personal`.
4. Haz clic en **"CREATE"** y selecciónalo.

### 2. Habilitar Google Sheets API

1. En el buscador de arriba: Escribe `Google Sheets API`.
2. Selecciónala y haz clic en **"ENABLE"**.

### 3. Configurar Pantalla de Consentimiento (OAuth Consent Screen)

1. Menú lateral: **"APIs & Services"** > **"OAuth consent screen"**.
2. Selecciona **"External"** > **"CREATE"**.
3. **App name:** `ingresos-tracker`.
4. **User support email:** Tu email.
5. **Developer contact info:** Tu email.
6. Haz clic en **"SAVE AND CONTINUE"**.
7. **Scopes:** Haz clic en **"ADD OR REMOVE SCOPES"**. Busca `https://www.googleapis.com/auth/spreadsheets`, márcalo y haz clic en **"UPDATE"**.
8. **Test users:** Haz clic en **"+ ADD USERS"** y agrega el mismo email con el que usarás Google Sheets. **(CRÍTICO: Si no haces esto, Google bloqueará el acceso)**.
9. Finaliza haciendo clic en **"BACK TO DASHBOARD"**.

### 4. Crear y Descargar Credenciales

1. Menú lateral: **"APIs & Services"** > **"Credentials"**.
2. Haz clic en **"+ CREATE CREDENTIALS"** > **"OAuth client ID"**.
3. **Application type:** Selecciona **"Desktop app"**.
4. Haz clic en **"CREATE"**.
5. Aparecerá un popup: Haz clic en **"DOWNLOAD JSON"**.

### 5. Configurar el Proyecto

1. Renombra el archivo descargado a `credentials.json`.
2. Muévelo a la carpeta raíz del proyecto `ingresos/`, reemplazando el que ya existe.

## Primer Uso y Verificación

Al ejecutar `uv run python bootstrap.py` (o cualquier script), se abrirá el navegador para autorizar:

1. Selecciona tu cuenta de Google.
2. Verás el aviso: **"Google hasn't verified this app"**.
3. Haz clic en **"Advanced"** > **"Go to ingresos-tracker (unsafe)"**.
4. Haz clic en **"Allow"** para otorgar permisos.

Este aviso es normal porque tú mismo eres el creador de la app y no has pasado por el proceso de auditoría oficial de Google (que solo tiene sentido para apps comerciales).

## Solución de Problemas Comunes

- **"Access blocked: has not completed verification":** Revisa el Paso 3, sub-paso 8. Olvidaste agregarte como "Test user".
- **"The user did not grant required scopes":** Al autorizar, asegúrate de marcar el permiso para ver/editar hojas de cálculo.

## Revocación de Acceso

Si alguna vez quieres quitar los permisos, ve a [Google Account - Third-party apps](https://myaccount.google.com/permissions) y elimina "ingresos-tracker".
