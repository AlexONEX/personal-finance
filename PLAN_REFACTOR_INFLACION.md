# Plan: Refactor de CER → Inflación Directa

## Problema Actual

**Fórmulas actuales usan CER:**
- CER es acumulativo (ej: CER 01/02 = 222, CER 29/02 = 269)
- Se actualiza diariamente prorrateando inflación
- Timing complejo (inflación de mes M se refleja desde ~día 13 de mes M+1)
- **No se puede matchear directamente sueldo → CER**

## Solución Propuesta

**Usar inflación INDEC directamente:**

1. **Matching directo:** Sueldo mes M → Inflación mes M
2. **Fallback REM:** Si no hay inflación → REM proyección M
3. **Índice acumulado:** Calcular índice base 100 desde inflación mensual

## Cambios Necesarios

### 1. Agregar columna de Índice Inflación en historic_data

**Nueva estructura:**
```
A: Fecha (último día del mes)
B: CER (mantener para referencia)
C: CCL
D: SPY
E: CER Estimado
F: Inflación Mensual % (decimal, ej: 0.132)
G: Índice Inflación (base 100, acumulativo) ← NUEVO
```

**Fórmula columna G:**
```
G4 = 100  (base)
G5 = G4 * (1 + F5)  (acumula inflación)
G6 = G5 * (1 + F6)
...
```

### 2. Modificar fórmulas Análisis ARS

**Columna G - "Índice Inflación Base":**
```excel
=LET(s, SCAN(0, SEQUENCE(ROWS(B3:B1000)), LAMBDA(a, i, LET(
    f, INDEX(B3:B1000, i),
    asc, INDEX(Ingresos!Q3:Q1000, i),
    mes, EOMONTH(f, 0),  # Último día del mes del sueldo
    idx_inflacion, VLOOKUP(mes, historic_data!$A$4:$G, 7, TRUE),  # Columna G = Índice
    rem_idx, IFERROR(VLOOKUP(EOMONTH(f,-1)+1, REM!$A$4:$J, 10, TRUE), 0),  # REM fallback
    v, IF(idx_inflacion>0, idx_inflacion, rem_idx),  # Precedencia: Inflación > REM
    IF(f="", a, IF(OR(a=0, a="", asc=TRUE), v, a))
))), ARRAYFORMULA(IF(C3:C1000="", "", s)))
```

**Columna H - "Paridad Inflación (Bruto/Hora)":**
```excel
=ARRAYFORMULA(IF((B3:B1000="")+(C3:C1000="")+(E3:E1000="")+(G3:G1000=0), "", LET(
    mes, EOMONTH(B3:B1000, 0),
    idx_actual, VLOOKUP(mes, historic_data!$A$4:$G, 7, TRUE),
    rem_actual, IFERROR(VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$J, 10, TRUE), 0),
    idx, IF(idx_actual>0, idx_actual, rem_actual),
    IF(idx=0, "", IFERROR(E3:E1000 * (idx/G3:G1000), ""))
)))
```

**Similar para columnas I, J, O (usar índice inflación en lugar de CER)**

### 3. Script para popular columna G (Índice Inflación)

**Crear: `populate_indice_inflacion.py`**
```python
# Leer inflación mensual de columna F
# Calcular índice acumulado base 100
# Escribir en columna G
```

### 4. Validador Sueldo → Inflación/REM

**Crear: `validar_matching_sueldo_inflacion.py`**
```python
# Para cada sueldo:
#   - Mes del sueldo → Buscar inflación de ese mes
#   - Si no hay inflación → Verificar que usa REM proyección M
#   - Validar que el matching es correcto
```

### 5. Actualizar documentación

**docs/CER_INFLATION_MATCHING.md →  docs/INFLACION_MATCHING.md:**
- Explicar por qué usamos inflación directa (no CER)
- Matching: Sueldo mes M → Inflación mes M → REM M si no hay dato
- Índice acumulado: cómo se calcula

## Ventajas

✅ Matching directo y simple: Sueldo marzo → Inflación marzo
✅ Sin ambigüedad de fechas (no más EOMONTH+13)
✅ REM fallback natural: si no hay inflación, usa REM M
✅ Datos ya disponibles: tenemos inflación en columna F
✅ Cálculos más transparentes y fáciles de validar

## Desventajas

⚠️ Requiere refactorizar fórmulas de Análisis ARS/USD
⚠️ Cambio arquitectónico (pero vale la pena)
⚠️ Necesita re-aplicar setup_sheet.py después de cambios

## Orden de Implementación

1. ✅ Crear columna G en historic_data (Índice Inflación)
2. ✅ Script populate_indice_inflacion.py
3. ✅ Modificar src/sheets/structure.py (fórmulas Análisis ARS)
4. ✅ Ejecutar setup_sheet.py para aplicar nuevas fórmulas
5. ✅ Validar con validar_matching_sueldo_inflacion.py
6. ✅ Actualizar documentación

## ¿Proceder?

Este refactor es **correcto y necesario**. El CER acumulativo no sirve para matching directo. La inflación mensual + REM fallback es la solución correcta.

¿Quieres que proceda con este refactor?
