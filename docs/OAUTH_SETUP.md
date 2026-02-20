# OAuth Setup - Configuración para Usuarios

Este instructivo es para usuarios que quieran usar `ingresos-tracker` con sus propias credenciales OAuth.

**Tiempo estimado:** 5 minutos
**Es necesario hacerlo:** Una sola vez

## ¿Por qué necesito esto?

Para que la aplicación pueda acceder a tus Google Sheets, necesitás darle permiso mediante OAuth 2.0. Como la app aún no está verificada por Google, cada usuario debe crear sus propias credenciales.

## Paso a Paso

### 1. Crear Proyecto en Google Cloud

1. Andá a: https://console.cloud.google.com
2. Click en el selector de proyectos (arriba a la izquierda)
3. Click **"NEW PROJECT"**
4. Nombre: `ingresos-tracker` (o el que quieras)
5. Click **"CREATE"**
6. Esperá unos segundos y seleccioná el nuevo proyecto

### 2. Habilitar Google Sheets API

1. En el menú lateral: **"APIs & Services"** > **"Library"**
2. Buscá: `Google Sheets API`
3. Click en **"Google Sheets API"**
4. Click **"ENABLE"**

### 3. Configurar OAuth Consent Screen

1. Menú lateral: **"APIs & Services"** > **"OAuth consent screen"**
2. Seleccioná **"External"** (o Internal si tenés Google Workspace)
3. Click **"CREATE"**

**Completar el formulario:**
- **App name:** `ingresos-tracker` (o el que quieras)
- **User support email:** tu email
- **Developer contact information:** tu email
- Dejá el resto en blanco por ahora
- Click **"SAVE AND CONTINUE"**

**Scopes:**
- Click **"ADD OR REMOVE SCOPES"**
- Buscá: `https://www.googleapis.com/auth/spreadsheets`
- Marcá el checkbox
- Click **"UPDATE"**
- Click **"SAVE AND CONTINUE"**

**Test users:**
- Click **"+ ADD USERS"**
- Agregá tu email (el que usarás para Google Sheets)
- Click **"ADD"**
- Click **"SAVE AND CONTINUE"**
- Click **"BACK TO DASHBOARD"**

### 4. Crear Credenciales OAuth

1. Menú lateral: **"APIs & Services"** > **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Seleccioná **"OAuth client ID"**
4. Application type: **"Desktop app"**
5. Name: `ingresos-tracker-desktop` (o el que quieras)
6. Click **"CREATE"**
7. Aparecerá un popup con tus credenciales
8. Click **"DOWNLOAD JSON"**

### 5. Configurar el Proyecto

1. Renombrá el archivo descargado a `credentials.json`
2. Movelo a la carpeta raíz del proyecto `ingresos/`

```bash
mv ~/Downloads/client_secret_*.json /path/to/ingresos/credentials.json
```

### 6. Primer Uso - Autorización

La primera vez que ejecutes la app:

```bash
uv run python inspect_ingresos.py
```

1. Se abrirá tu navegador automáticamente
2. Seleccioná tu cuenta de Google
3. Verás un warning: **"Google hasn't verified this app"**
   - Esto es normal porque creaste la app vos mismo
   - Click **"Advanced"**
   - Click **"Go to ingresos-tracker (unsafe)"**
4. Click **"Allow"** para dar permisos
5. La ventana se cerrará automáticamente
6. Se creará un archivo `token.json` (no lo borres!)

**El archivo `token.json`:**
- Contiene tu token de acceso
- Se renueva automáticamente
- No lo subas a GitHub (ya está en `.gitignore`)
- Si lo borrás, tendrás que autorizar de nuevo

## Troubleshooting

### Error: "Access blocked: ingresos-tracker has not completed the Google verification process"

**Solución:** Asegurate de haber agregado tu email como "test user" en el paso 3.

### Error: "The user did not grant the required scopes"

**Solución:** En el paso de autorización (paso 6), asegurate de clickear "Allow" y no "Deny".

### Error: "invalid_grant" o "Token has been expired or revoked"

**Solución:** Borrá `token.json` y volvé a autorizar:

```bash
rm token.json
uv run python inspect_ingresos.py
```

### No se abre el navegador automáticamente

1. Fijate si hay una URL en la terminal
2. Copiá y pegá esa URL en tu navegador manualmente
3. Completá el flujo de autorización

## Seguridad

### ¿Es seguro?

Sí, porque:
- **Vos creás las credenciales** en tu propia cuenta de Google Cloud
- **Vos controlás qué permisos das** (solo acceso a Sheets)
- **Los tokens se guardan localmente** en tu máquina (no se comparten)
- **Podés revocar el acceso** en cualquier momento desde: https://myaccount.google.com/permissions

### Revocar Acceso

Si querés quitar los permisos:
1. Andá a: https://myaccount.google.com/permissions
2. Buscá "ingresos-tracker"
3. Click **"Remove access"**

## Archivos Importantes

- `credentials.json` - **NO subir a GitHub** - Credenciales de tu app OAuth
- `token.json` - **NO subir a GitHub** - Token de acceso generado
- Ambos ya están en `.gitignore`

## ¿Necesito hacer esto cada vez?

**No.** Solo necesitás:
- Crear el proyecto y credenciales: **1 vez**
- Autorizar (paso 6): **1 vez** (o si borrás `token.json`)

Después de eso, la app funciona automáticamente.

---

## Próximos Pasos

Una vez completado el setup:
- Ejecutá `uv run python inspect_ingresos.py` para ver las fórmulas
- Ejecutá otros scripts del proyecto normalmente
- Disfrutá tracking tus ingresos ajustados por inflación
