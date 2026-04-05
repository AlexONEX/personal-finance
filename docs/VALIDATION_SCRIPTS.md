# Guía de Scripts de Validación CER

## Índice
1. [validate_cer_calcs.py - Validación CER vs Inflación](#1-validate_cer_calcspy---validación-cer-vs-inflación)
2. [validar_matching_inflacion.py - Validación Matching Temporal](#2-validar_matching_inflacionpy---validación-matching-temporal)
3. [test_cer_matching.py - Test Manual](#3-test_cer_matchingpy---test-manual)
4. [Troubleshooting](#troubleshooting)

---

## 1. validate_cer_calcs.py - Validación CER vs Inflación

### Descripción

Compara la variación mensual del CER con la inflación mensual publicada por INDEC. Detecta discrepancias que excedan la tolerancia configurada (default ±0.1%).

### Ejecución

#### Opción 1: Leer desde Google Sheets (Default)

```bash
python validate_cer_calcs.py
```

Lee datos históricos (CER, CER Estimado, Inflación) desde la hoja `historic_data`.

#### Opción 2: Fetch Datos Frescos de BCRA

```bash
python validate_cer_calcs.py --fetch
```

Descarga datos directamente de las APIs del BCRA (no lee sheets).

#### Opción 3: Exportar a JSON

```bash
python validate_cer_calcs.py --output json
```

Exporta el reporte en formato JSON para procesamiento programático.

#### Opción 4: Tolerancia Custom

```bash
python validate_cer_calcs.py --tolerance 0.2
```

Usa tolerancia de ±0.2% en lugar del default (±0.1%).

#### Opción 5: Fetch con Rango Custom

```bash
python validate_cer_calcs.py --fetch --since 2023-01-01 --until 2023-12-31
```

Fetcha datos solo para el año 2023.

### Interpretación del Output

#### Output de Texto (Default)

```
VALIDACIÓN CER vs INFLACIÓN INDEC
======================================
Fecha      | CER Δ%  | Inflación % | Δ     | Status          | Nota
-----------------------------------------------------------------------------------
31/01/2024 |  +2.65  |      +2.71  | -0.06 | ✓ OK            |
28/02/2024 |  +3.01  |      +2.96  | +0.05 | ✓ OK            |
31/03/2024 |  +8.21  |      +8.45  | -0.24 | ⚠ CER EST       | CER estimado usado
30/04/2024 |  +0.00  |      +2.50  |  0.00 | ✗ SIN CER       | Falta CER para 13/05/2024

RESUMEN
=======
Total meses analizados: 26
Dentro de tolerancia ±0.1%: 24 (92.3%)
Fuera de tolerancia: 2 (7.7%)
Sin CER disponible: 1
Usando CER Estimado: 1

PROBLEMÁTICOS / ALERTAS
-----------------------
  31/05/2024: CER estimado usado para 13/06/2024
  30/06/2024: Falta CER para 13/07/2024
```

#### Símbolos de Status

| Símbolo | Significado | Acción |
|---------|-------------|--------|
| ✓ OK | Dentro de tolerancia ±0.1% | Ninguna |
| ⚠ FUERA | Fuera de tolerancia | Investigar discrepancia |
| ⚠ CER EST | Usando CER Estimado | Validar cuando haya CER oficial |
| ✗ SIN CER | Sin dato CER disponible | Usar REM proyección M |

#### Output JSON

```json
{
  "total_meses": 26,
  "dentro_tolerancia": 24,
  "fuera_tolerancia": 2,
  "sin_cer": 1,
  "sin_inflacion": 0,
  "usando_cer_estimado": 1,
  "tolerancia_pct": 0.1,
  "discrepancias": [
    {
      "fecha": "2024-01-31",
      "cer_pct": 2.65,
      "inflacion_pct": 2.71,
      "delta": -0.06,
      "status": "OK",
      "nota": ""
    },
    ...
  ]
}
```

### ¿Cuándo Ejecutar?

- **Después de fetch_data.py** - Para validar datos recién descargados
- **Mensualmente** - Cuando INDEC publica inflación nueva (días 11-16 de cada mes)
- **Antes de análisis** - Para asegurar coherencia de datos históricos
- **Después de correcciones** - Para verificar que ajustes manuales son correctos

### ¿Qué Hacer con Discrepancias?

#### Discrepancia ✗ SIN CER

```
30/06/2024: Falta CER para 13/07/2024
```

**Acciones:**
1. Verificar en BCRA si CER ya fue publicado
2. Si sí: Ejecutar `fetch_data.py` para actualizar
3. Si no: Usar REM proyección M (automático en fórmulas con fallback)
4. Re-validar cuando CER esté disponible

#### Discrepancia ⚠ CER EST

```
31/05/2024: CER estimado usado para 13/06/2024
```

**Acciones:**
1. Verificar si CER oficial ya está disponible
2. Si sí: Actualizar columna B de historic_data
3. Si no: Documentar en columna "Nota" que se usó estimado
4. Re-validar cuando CER oficial esté disponible

#### Discrepancia ⚠ FUERA (delta > ±0.1%)

```
31/08/2024: Delta +0.18%
```

**Acciones:**
1. Verificar datos en fuente original (BCRA APIs):
   - CER: https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30
   - Inflación: https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/27
2. Revisar si hubo cambios metodológicos en BCRA
3. Validar cálculo manual:
   ```python
   cer_variacion = (cer_actual / cer_anterior - 1) * 100
   inflacion_pct = inflacion_decimal * 100
   delta = abs(cer_variacion - inflacion_pct)
   ```
4. Documentar la discrepancia si es legítima

---

## 2. validar_matching_inflacion.py - Validación Matching Temporal

### Descripción

Verifica que para cada sueldo se está usando el CER correcto según la heurística EOMONTH+13. Detecta edge cases como CER faltante, CER futuro, o gaps grandes.

### Ejecución

#### Opción 1: Análisis Completo (Default)

```bash
python validar_matching_inflacion.py
```

Valida todos los salarios del sheet Ingresos contra CER de historic_data.

#### Opción 2: Exportar a JSON

```bash
python validar_matching_inflacion.py --output json
```

Exporta el reporte en formato JSON.

#### Opción 3: Gap Máximo Custom

```bash
python validar_matching_inflacion.py --max-gap 45
```

Acepta gap de hasta 45 días entre CER objetivo y real (default 30).

### Interpretación del Output

#### Output de Texto (Default)

```
VALIDACIÓN: Salario → CER
===========================
Validados: 47 | OK: 46 (97.9%) | REM fallback: 1 (2.1%)
===========================

DETALLE
-------
Fecha Salario   | CER Objetivo    | CER Real        | Valor        | Gap    | Status
-------------------------------------------------------------------------------------
15/01/2024      | 13/02/2024      | 13/02/2024      | 6.8547       | 0d     | ✓ OK
15/02/2024      | 13/03/2024      | 13/03/2024      | 7.0125       | 0d     | ✓ OK
15/03/2024      | 13/04/2024      | 13/04/2024      | 7.6023       | 0d     | ✓ OK
15/05/2024      | 13/06/2024      | N/A             | N/A          | N/A    | ⚠ REM
15/12/2024      | 13/01/2025      | N/A             | N/A          | N/A    | ✗ FALTA CER

PROBLEMÁTICOS / ALERTAS
-----------------------
  15/05/2024 → Usando REM como fallback (valor: 1.042)
  15/12/2024 → Usar REM proyección M: 1.0385
```

#### Símbolos de Status

| Símbolo | Significado | Acción |
|---------|-------------|--------|
| ✓ OK | CER oficial encontrado | Ninguna |
| ⚠ REM | Usando REM como fallback | Normal para sueldos recientes |
| ⚠ GAP | Gap > 30 días entre objetivo y real | Verificar datos faltantes |
| ✗ FALTA CER | Sin CER ni REM disponible | Usar populate_inflacion_futura.py |
| ✗ FUTURO | CER de fecha futura (bug) | Revisar fórmulas |

### ¿Cuándo Ejecutar?

- **Después de agregar nuevos sueldos** - Para verificar matching correcto
- **Después de modificar fórmulas** - Para validar que cambios son correctos
- **Para diagnosticar cálculos** - Cuando poder adquisitivo parece incorrecto
- **Mensualmente** - Como parte de rutina de validación

### ¿Qué Hacer con Problemas?

#### Problema: ⚠ REM (Usando REM fallback)

```
15/05/2024 → Usando REM como fallback (valor: 1.042)
```

**Interpretación:** Sueldo reciente sin CER oficial aún, usando REM proyección.

**Acciones:**
1. **Si sueldo es de hace > 1 mes:** Ejecutar `fetch_data.py` para actualizar CER
2. **Si sueldo es reciente:** Normal, REM es la mejor estimación disponible
3. **Re-validar** cuando CER oficial esté disponible

#### Problema: ✗ FALTA CER (Sin datos)

```
15/12/2024 → Usar REM proyección M: 1.0385
```

**Interpretación:** No hay CER ni REM para esa fecha.

**Acciones:**
1. Ejecutar `python populate_inflacion_futura.py` para llenar CER Estimado
2. O esperar a que CER oficial se publique
3. O marcar como N/A en análisis

#### Problema: ⚠ GAP (Gap grande)

```
15/07/2023 → Gap de 35 días entre objetivo y CER disponible
```

**Interpretación:** CER objetivo es 13/08/2023 pero solo hay CER hasta 09/07/2023.

**Acciones:**
1. Fetch datos históricos adicionales: `python fetch_data.py --since 2023-07-01 --until 2023-08-31`
2. Verificar que no hay gap real en datos de BCRA
3. Usar CER Estimado para llenar gap si es necesario

#### Problema: ✗ FUTURO (CER futuro - bug)

```
15/03/2024 → CER de fecha futura: 20/06/2024
```

**Interpretación:** BUG en fórmulas o datos. CER objetivo no debería ser futuro.

**Acciones:**
1. Verificar fórmula en Análisis ARS columna G (CER Base)
2. Verificar fecha del sueldo en Ingresos columna B
3. Re-ejecutar setup_sheet.py si fórmulas están corruptas

---

## 3. test_cer_matching.py - Test Manual

### Descripción

Test interactivo que muestra visualmente cómo funciona el matching sueldo→CER. Útil para debugging y entender la heurística.

### Ejecución

```bash
python test_cer_matching.py
```

### Output Esperado

```
TEST DE MATCHING: Salario → CER
================================================================================
Fecha Salario   Fecha Objetivo  CER Fecha       CER Valor    Inflación    Mes Inflación
----------------------------------------------------------------------------------------
15/01/2024      13/02/2024      13/02/2024      6.8547       2.71%        Ene 2024
15/02/2024      13/03/2024      13/03/2024      7.0125       2.96%        Feb 2024
15/03/2024      13/04/2024      13/04/2024      7.6023       8.45%        Mar 2024
================================================================================

Verificación:
- ¿'Fecha Objetivo' = último día mes salario + 13 días?
- ¿'CER Fecha' = 'Fecha Objetivo' (o más cercano anterior)?
- ¿El CER refleja la inflación del mismo mes que el salario?
================================================================================

ANÁLISIS AUTOMÁTICO CON VALIDADOR
================================================================================
Total salarios validados: 47
Salarios OK: 46 (97.9%)
Salarios sin CER: 1
Salarios con gap grande: 0

⚠ ALERTAS:
  15/12/2024 → Usar REM proyección M
================================================================================
```

### Verificación Manual

Usa esta tabla para verificar manualmente que el matching es correcto:

1. **Fecha Objetivo** = último día del mes de "Fecha Salario" + 13 días
2. **CER Fecha** = "Fecha Objetivo" (o más cercano anterior si exacto no existe)
3. **Inflación** debería corresponder al mismo mes que "Fecha Salario"

### ¿Cuándo Usar?

- **Debugging:** Cuando un sueldo específico tiene cálculo incorrecto
- **Entender heurística:** Para visualizar cómo funciona EOMONTH+13
- **Validar cambios:** Después de modificar fórmulas o datos

---

## Troubleshooting

### Error: "SPREADSHEET_ID not defined in .env"

**Causa:** Falta variable de entorno.

**Solución:**
```bash
echo "SPREADSHEET_ID=tu_spreadsheet_id_aqui" >> .env
```

### Error: "SSL verification failed"

**Causa:** APIs del BCRA tienen certificados SSL vencidos frecuentemente.

**Solución:** El código ya maneja esto con `verify=False`. Si persiste:
```bash
python validate_cer_calcs.py --from-sheets  # Usar sheets en lugar de APIs
```

### Error: "No module named 'src.validators'"

**Causa:** Python no encuentra el módulo.

**Solución:**
```bash
export PYTHONPATH="${PYTHONPATH}:/Users/alex/Github/me/ingresos"
python validate_cer_calcs.py
```

O ejecutar desde el directorio root del proyecto:
```bash
cd /Users/alex/Github/me/ingresos
python validate_cer_calcs.py
```

### Warning: "Skipping malformed row"

**Causa:** Datos en sheets con formato incorrecto (fechas, números).

**Solución:**
1. Revisar Google Sheets en la fila mencionada
2. Verificar formato de columnas:
   - Columna A (Fecha): `dd/mm/yyyy`
   - Columna B (CER): Número decimal
   - Columna F (Inflación): Número decimal (ej: 0.027 no 2.7%)

### Discrepancias Inconsistentes

**Síntoma:** Resultados diferentes entre scripts.

**Causa:** Datos en sheets desactualizados.

**Solución:**
```bash
# 1. Fetch datos frescos
python fetch_data.py

# 2. Re-validar
python validate_cer_calcs.py --from-sheets
python validar_matching_inflacion.py
```

### Gap Inesperado

**Síntoma:** Gap de 15+ días cuando debería ser 0.

**Causa:** Datos faltantes en historic_data.

**Solución:**
```bash
# Fetch rango específico
python fetch_data.py --since 2024-05-01 --until 2024-06-30

# Re-validar
python validar_matching_inflacion.py
```

---

## Ejemplos de Flujos Completos

### Flujo 1: Validación Mensual (Rutina)

```bash
# Día 15 de cada mes (después de publicación de inflación)

# 1. Fetch datos nuevos
python fetch_data.py

# 2. Validar CER vs Inflación
python validate_cer_calcs.py --from-sheets

# 3. Validar matching de todos los sueldos
python validar_matching_inflacion.py

# 4. Si todo OK, continuar con análisis
# Si hay problemas, investigar con test_cer_matching.py
```

### Flujo 2: Debugging de Sueldo Específico

```bash
# Síntoma: Poder adquisitivo de sueldo 15/03/2024 parece incorrecto

# 1. Test manual para ver matching visual
python test_cer_matching.py

# 2. Validar matching de todos los sueldos
python validar_matching_inflacion.py

# 3. Buscar problemas en output
# Ej: "15/03/2024 → Gap de 10 días"

# 4. Revisar datos en Google Sheets
# Verificar que CER de 13/04/2024 existe y es correcto

# 5. Si falta CER, fetch datos
python fetch_data.py --since 2024-03-01 --until 2024-04-30

# 6. Re-validar
python validar_matching_inflacion.py
```

### Flujo 3: Validar Después de Cambios en Fórmulas

```bash
# Después de modificar src/sheets/structure.py

# 1. Re-aplicar fórmulas
python setup_sheet.py

# 2. Validar que matching sigue correcto
python validar_matching_inflacion.py

# 3. Validar que variaciones siguen correctas
python validate_cer_calcs.py --from-sheets

# 4. Si hay problemas, revisar fórmulas modificadas
```

---

**Última actualización:** 2026-04-04
**Autor:** Sistema de validación CER - ingresos
