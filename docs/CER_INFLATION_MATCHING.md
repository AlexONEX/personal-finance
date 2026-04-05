# CER - Inflación: Matching Temporal y Validación

## Índice
1. [Concepto: ¿Por qué EOMONTH+13?](#concepto-por-qué-eomonth13)
2. [Validación: Tolerancia ±0.1%](#validación-tolerancia-01)
3. [REM como Fallback](#rem-como-fallback)
4. [Edge Cases](#edge-cases)
5. [Scripts de Validación](#scripts-de-validación)
6. [Checklist de Verificación Manual](#checklist-de-verificación-manual)

---

## Concepto: ¿Por qué EOMONTH+13?

### Timeline de Publicación

El CER (Coeficiente de Estabilización de Referencia) refleja la inflación mensual publicada por el INDEC, pero con un **desfase temporal** de aproximadamente 13 días. Este desfase existe porque:

1. **Inflación del mes M** ocurre durante todo el mes (ej: marzo 2024)
2. **INDEC calcula y publica** la inflación entre el día 11-16 del mes M+1 (ej: 12 abril 2024)
3. **BCRA actualiza el CER** con la nueva inflación desde el día ~13 del mes M+1 (ej: 13 abril 2024)

### Ejemplo Concreto

```
MES: MARZO 2024
-----------------
01-31 marzo:    Inflación ocurre (supongamos 2.71%)
12 abril:       INDEC publica inflación de marzo = 2.71%
13 abril:       BCRA publica CER actualizado con inflación de marzo
15 abril:       Se cobra sueldo de marzo

¿QUÉ CER USAR PARA SUELDO DE MARZO?
→ CER del 13 de abril (refleja inflación de marzo)

FÓRMULA:
→ EOMONTH(15-abr, 0) + 13 = 30-mar + 13 = 13-abr ✓ CORRECTO
```

### Heurística Implementada

Para un sueldo de fecha X:
1. **Calcular último día del mes:** `EOMONTH(X, 0)`
2. **Sumar 13 días:** `EOMONTH(X, 0) + 13`
3. **Buscar CER de esa fecha** (o más cercano anterior)

**Resultado:** CER que refleja la inflación del mismo mes que el sueldo.

---

## Validación: Tolerancia ±0.1%

### ¿Qué Se Compara?

El script `validate_cer_calcs.py` compara:

```
Variación CER mensual:
  (CER_mes_actual / CER_mes_anterior - 1) * 100

vs

Inflación INDEC mensual:
  inflacion_mensual * 100  (viene como decimal en API)
```

### Tolerancia ±0.1%

**±0.1% es aceptable** por:
- **Redondeos:** BCRA y INDEC redondean de forma diferente
- **Actualizaciones parciales:** CER puede actualizarse intra-día
- **Períodos incompletos:** Meses con días hábiles variables

**Ejemplos aceptables:**
```
CER: +2.65%  vs  Inflación: +2.71%  →  Δ = 0.06%  ✓ OK
CER: +3.01%  vs  Inflación: +2.96%  →  Δ = 0.05%  ✓ OK
CER: +8.21%  vs  Inflación: +8.25%  →  Δ = 0.04%  ✓ OK
```

### Cuándo Investigar

**Fuera de ±0.1% requiere investigación:**
```
CER: +2.50%  vs  Inflación: +2.71%  →  Δ = 0.21%  ⚠ FUERA
```

**Posibles causas:**
1. **Datos faltantes:** CER oficial no disponible, se usó CER Estimado
2. **Cambios metodológicos:** BCRA modificó cálculo de CER
3. **Eventos especiales:** Feriados bancarios, cambios regulatorios
4. **Errores de datos:** API devolvió datos incorrectos o incompletos

---

## REM como Fallback

### Precedencia de Fuentes

El sistema usa esta jerarquía para obtener CER:

```
1. CER Oficial (historic_data columna B)
   ↓ si no existe
2. CER Estimado (historic_data columna E)
   ↓ si no existe
3. REM Índice (REM columna J)
   ↓ si no existe
4. ERROR (sin datos disponibles)
```

### ¿Cuándo Se Usa REM?

REM (Relevamiento de Expectativas de Mercado) se usa cuando:

**Caso 1: Sueldo futuro (mes actual sin inflación publicada)**
```
Hoy: 05 abril 2024
Sueldo: 30 marzo 2024
CER objetivo: 13 abril 2024 (aún no existe)

→ Usar REM proyección M de marzo 2024
```

**Caso 2: Gap histórico (datos faltantes)**
```
Sueldo: 15 mayo 2023
CER objetivo: 13 junio 2023
CER oficial: NO DISPONIBLE (falta histórico)

→ Usar REM de mayo 2023 si existe
```

### Cómo Se Calcula REM

REM usa el **índice acumulado** (columna J del sheet REM):
```
J4 = 1 (base)
J5 = J4 * (1 + C5)  # C5 = proyección mes M
J6 = J5 * (1 + C6)  # C6 = proyección mes M+1
...
```

Este índice refleja cómo evolucionaría el poder adquisitivo siguiendo las expectativas del mercado.

### Limitaciones de REM

**REM es proyección, NO dato real:**
- ✅ Útil para **estimar** inflación futura
- ✅ Oficial del BCRA (consulta a analistas económicos)
- ❌ **No reemplaza** datos reales de CER
- ❌ Puede diferir de inflación real (especialmente en Argentina)

**Recomendación:** Una vez que el CER oficial esté disponible, **re-validar** cálculos que usaron REM.

---

## Edge Cases

### 1. Sueldo en Período Sin Datos Históricos

**Problema:**
```
Sueldo: 15 enero 2021
Sistema tiene datos desde 2022-01-01
```

**Solución:**
- Fetch datos históricos adicionales: `python fetch_data.py --since 2021-01-01`
- O usar REM si existe para ese período
- O marcar como N/A en análisis

### 2. Cambios de Sistemas BCRA

**Problema:**
```
BCRA cambió metodología de cálculo de CER en fecha X
CER antes de X vs después de X no son comparables
```

**Solución:**
- Documentar cambio en columna "Nota" de historic_data
- Usar CER Estimado corregido por metodología vieja
- Ajustar análisis para considerar cambio de base

### 3. Transiciones de Moneda

**Problema:**
```
Pesificación, cambio de denominación (pesos → pesos nuevos)
Inflación histórica puede estar en moneda diferente
```

**Solución:**
- Convertir todos los valores a moneda actual
- Usar factor de conversión documentado
- Validar continuidad de serie temporal

### 4. Feriados Bancarios Prolongados

**Problema:**
```
Feriado bancario en día de publicación CER (ej: Semana Santa)
CER se publica 1-2 días después de lo esperado
```

**Solución:**
- VLOOKUP con `TRUE` (búsqueda aproximada) captura automáticamente el CER del día anterior más cercano
- Validar con script que gap no sea > 30 días

---

## Scripts de Validación

### 1. validate_cer_calcs.py

**Qué hace:** Compara variación mensual de CER con inflación INDEC

**Cuándo ejecutar:**
- Después de `fetch_data.py` (para validar datos nuevos)
- Mensualmente (cuando se publica inflación nueva)
- Antes de analizar poder adquisitivo

**Ejemplo:**
```bash
python validate_cer_calcs.py --from-sheets
```

Ver detalles en [VALIDATION_SCRIPTS.md](VALIDATION_SCRIPTS.md)

### 2. validar_matching_inflacion.py

**Qué hace:** Verifica que cada sueldo usa el CER correcto

**Cuándo ejecutar:**
- Después de agregar nuevos sueldos en Ingresos
- Después de modificar fórmulas de Análisis ARS
- Para diagnosticar problemas de cálculo

**Ejemplo:**
```bash
python validar_matching_inflacion.py
```

Ver detalles en [VALIDATION_SCRIPTS.md](VALIDATION_SCRIPTS.md)

### 3. test_cer_matching.py

**Qué hace:** Test manual + validación automática

**Cuándo ejecutar:**
- Para debugging de matching específico
- Para entender visualmente la heurística

**Ejemplo:**
```bash
python test_cer_matching.py
```

---

## Checklist de Verificación Manual

Antes de confiar en un cálculo de poder adquisitivo, verificar:

```
[ ] ¿Fecha CER objetivo (EOMONTH+13) tiene sentido?
    Ej: Sueldo 15-mar → CER objetivo debe ser ~13-abr

[ ] ¿CER objetivo existe en historic_data?
    Verificar en Google Sheets, columna B

[ ] ¿CER valor está en rango sensato?
    Ej: 2024 → CER entre 0.95 y 1.50 (aprox)

[ ] ¿Inflación del mes es similar a variación CER?
    Diferencia < ±0.1% → OK
    Diferencia > ±0.1% → INVESTIGAR

[ ] ¿No se está usando CER futuro?
    Gap días debe ser >= 0

[ ] ¿Si no hay CER, se usó REM como fallback?
    Status = "⚠ REM" en validación

[ ] ¿CER Base se resetea solo en ascensos reales?
    Columna Q de Ingresos = TRUE cuando hay ascenso
```

### Ejemplo de Validación Manual

```python
from datetime import date, timedelta
import calendar

# Sueldo
fecha_salario = date(2024, 3, 15)

# Cálculo manual de CER objetivo
ultimo_dia = date(2024, 3, calendar.monthrange(2024, 3)[1])  # 31-mar
cer_objetivo = ultimo_dia + timedelta(days=13)  # 13-abr

print(f"Fecha sueldo: {fecha_salario}")
print(f"CER objetivo: {cer_objetivo}")
print(f"Verificar que CER de {cer_objetivo} existe en historic_data")
```

---

## Recursos Adicionales

- **API BCRA CER:** https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/30
- **API BCRA Inflación:** https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/27
- **REM BCRA:** https://www.bcra.gob.ar/todos-relevamiento-de-expectativas-de-mercado-rem/
- **Metodología CER:** https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp

---

**Última actualización:** 2026-04-04
**Autor:** Sistema de validación CER - ingresos
