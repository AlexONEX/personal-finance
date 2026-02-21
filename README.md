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

La primera vez que ejecutes cualquier script, se abrirá un navegador para autorizar el acceso a Google Sheets. El token se guardará automáticamente.

## Uso Diario

### Actualizar datos de mercado (CER, CCL, REM)

```bash
./update_daily.sh
```

### Cargar tus ingresos

Abrí la hoja `Ingresos` en tu spreadsheet y completá solo estas columnas:
- **A (Fecha)**: Primer día del mes (ej: 01/06/2024)
- **B (Bruto)**: Sueldo bruto del mes
- **G (SAC Bruto)**: Aguinaldo (solo Jun/Dic)
- **I (Bono Neto)**: Bonos extraordinarios (opcional)
- **J (Comida)**: Beneficio de comida (opcional)
- **K (Otros Beneficios)**: Otros beneficios (opcional)

Todo lo demás se calcula automáticamente.

### Automatización (opcional)

Para actualizar los datos automáticamente todos los días:

```bash
./automation/install.sh
```

Esto configura un job que corre a las 9:00 AM todos los días.

## Estructura del Spreadsheet

El spreadsheet tiene 5 hojas:

- **Ingresos**: Tu registro mensual de ingresos y todos los cálculos
- **historic_data**: Datos históricos de CER y CCL (actualizado por `fetch_data.py`)
- **REM**: Proyecciones de inflación del BCRA (actualizado por `fetch_data.py`)
- **impuestos**: Tasas de descuentos (Jubilación 11%, PAMI 3%, Obra Social 3%)
- **Panel**: Instrucciones para sincronización interna

## Documentación

- [Diccionario de Columnas](docs/COLUMNAS.md) - Explicación detallada de cada columna
- [OAuth Setup](docs/OAUTH_SETUP.md) - Cómo configurar tus propias credenciales OAuth (opcional)
- [Automatización](automation/README.md) - Detalles sobre la actualización automática diaria

## Configuración

Si cambian los aportes de ley, editalos en la hoja `impuestos` del spreadsheet.
