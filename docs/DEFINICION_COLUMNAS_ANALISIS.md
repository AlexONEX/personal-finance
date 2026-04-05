# Definición de Columnas de Análisis ARS y USD

**Objetivo:** Definir correctamente cada columna antes de optimizar con ARRAYFORMULA.
**Fecha:** 2026-04-05
**Status:** DEFINICIÓN COMPLETA - Listo para implementar

---

## RESUMEN EJECUTIVO

### Análisis ARS - 24 columnas (23 visibles + 1 oculta)
| Grupo | Columnas | Descripción |
|-------|----------|-------------|
| **PERIODO** | A | Período abonado |
| **SUELDO** | B-D | Fecha, Bruto/Hora, Neto/Hora |
| **VS ÚLTIMO AUMENTO (CER)** | E-J | Base CER, Paridad CER, Poder Adq vs CER |
| **VS ÚLTIMO AUMENTO (INDEC)** | K-M | Índice INDEC, K_BASE (oculta), Poder Adq vs INDEC |
| **VARIACIÓN MENSUAL** | N-Q | CER MoM, Variación acumulada, CER Actual/Base |
| **PROYECCIÓN REM** | R-W | Objetivos a 3m y 6m según REM |

### Análisis USD - 16 columnas
| Grupo | Columnas | Descripción |
|-------|----------|-------------|
| **PERIODO** | A | Período abonado |
| **SUELDO ARS** | B-D | Fecha, Bruto, Neto |
| **SUELDO USD NOMINAL** | E-H | CCL, CCL MoM, Bruto USD, Neto USD |
| **SUELDO USD REAL** | I-L | CER, CCL Real, Bruto/Neto USD Real |
| **VS ÚLTIMO AUMENTO** | M-P | CCL Base, Bruto/Neto USD Base, Variación USD |

### Cambios vs Versión Anterior
- ✅ **Agregada:** Columna auxiliar K_BASE (INDEC Base) en Análisis ARS - se ocultará
- ✅ **Eliminadas:** Columnas P-Q (Paridad USD) en Análisis USD - no tenían sentido
- ✅ **Simplificadas:** Todas las fórmulas sin ARRAYFORMULA para facilitar debug
- ✅ **Documentado:** Matching correcto de CER e IPC con rezagos

---

## ANÁLISIS ARS - Sueldo vs Inflación en Pesos

### Grupo: PERIODO (A)

#### Columna A: Periodo Abonado
**Propósito:** Mostrar el período en formato "octubre 2023"
**Fuente:** Referencia a Ingresos!A
**Fórmula (Fila 3):**
```excel
=IF(Ingresos!B3<>"", Ingresos!A3, "")
```
**Lógica:** Si hay fecha en Ingresos, copiar el período

---

### Grupo: SUELDO (B-D)

#### Columna B: Fecha
**Propósito:** Fecha de cobro del sueldo
**Fuente:** Referencia a Ingresos!B (fecha de pago)
**Fórmula (Fila 3):**
```excel
=IF(Ingresos!B3<>"", Ingresos!B3, "")
```

#### Columna C: Bruto/Hora
**Propósito:** Sueldo bruto por hora trabajada
**Fuente:** Referencia a Ingresos!O
**Fórmula (Fila 3):**
```excel
=IF(Ingresos!B3<>"", Ingresos!O3, "")
```
**Cálculo en Ingresos:** `Bruto / (Horas_diarias × 20 días)`

#### Columna D: Neto/Hora
**Propósito:** Sueldo neto por hora trabajada
**Fuente:** Referencia a Ingresos!P
**Fórmula (Fila 3):**
```excel
=IF(Ingresos!B3<>"", Ingresos!P3, "")
```
**Cálculo en Ingresos:** `Neto / (Horas_diarias × 20 días)`

---

### Grupo: VS ÚLTIMO AUMENTO (CER) (E-J)

**Objetivo:** Comparar poder adquisitivo desde el último ascenso usando CER como métrica oficial.

#### Columna E: Bruto/Hora Base
**Propósito:** Sueldo bruto/hora del último ascenso (o inicio)
**Lógica:**
- Cuando hay ascenso (Ingresos!Q = TRUE), actualizar base
- Sino, mantener base anterior
- Primer valor = primer sueldo

**Fórmula (Fila 3):**
```excel
=IF(C3="", "", IF(OR(Ingresos!Q3=TRUE, ROW()=3), C3, E2))
```

**Fórmula (Fila 4+):**
```excel
=IF(C4="", "", IF(Ingresos!Q4=TRUE, C4, E3))
```

**Ejemplo:**
```
Fila 3  | Oct 2023  | Bruto/Hora: 2000 | Ascenso: FALSE | Base: 2000
Fila 4  | Nov 2023  | Bruto/Hora: 2167 | Ascenso: FALSE | Base: 2000
...
Fila 15 | Dic 2024  | Bruto/Hora: 12737| Ascenso: TRUE  | Base: 12737 ← RESET
Fila 16 | Ene 2025  | Bruto/Hora: 12737| Ascenso: FALSE | Base: 12737
```

#### Columna F: Neto/Hora Base
**Propósito:** Sueldo neto/hora del último ascenso (o inicio)
**Lógica:** Igual que columna E pero con Neto

**Fórmula (Fila 3):**
```excel
=IF(D3="", "", IF(OR(Ingresos!Q3=TRUE, ROW()=3), D3, F2))
```

**Fórmula (Fila 4+):**
```excel
=IF(D4="", "", IF(Ingresos!Q4=TRUE, D4, F3))
```

#### Columna G: CER Base
**Propósito:** Valor de CER del último ascenso
**Lógica de Matching CER:**
- Sueldo cobrado en mes M → usar CER del día 15 del mes M+1
- Ejemplo: Sueldo 30/10/2023 → CER 15/11/2023
- Esto refleja que el CER incorpora la inflación de octubre a mediados de noviembre

**Fórmula (Fila 3):**
```excel
=IF(B3="", "",
   IF(OR(Ingresos!Q3=TRUE, ROW()=3),
      IFERROR(VLOOKUP(EOMONTH(B3,1)+15, historic_data!$A$4:$B, 2, TRUE), 0),
      G2))
```

**Fórmula (Fila 4+):**
```excel
=IF(B4="", "",
   IF(Ingresos!Q4=TRUE,
      IFERROR(VLOOKUP(EOMONTH(B4,1)+15, historic_data!$A$4:$B, 2, TRUE), 0),
      G3))
```

**Ejemplo:**
```
Fecha: 30/10/2023 → EOMONTH(30/10/23, 1) = 30/11/2023 → +15 = 15/12/2023
Buscar CER en historic_data con fecha 15/12/2023
```

**IMPORTANTE:** Usamos VLOOKUP con `range_lookup=TRUE` para encontrar el CER más cercano si no hay dato exacto del día 15.

#### Columna H: Paridad CER (Bruto/Hora)
**Propósito:** Lo que DEBERÍA ser tu sueldo bruto/hora hoy si solo hubiera seguido la inflación
**Fórmula:**
```excel
=IF(OR(B3="", C3="", E3="", G3=0), "",
   LET(
      fecha_cer, EOMONTH(B3,1)+15,
      cer_actual, IFERROR(VLOOKUP(fecha_cer, historic_data!$A$4:$B, 2, TRUE), 0),
      IF(cer_actual=0, "", E3 * (cer_actual/G3))
   ))
```

**Lógica:**
```
Paridad = Bruto_Base × (CER_Actual / CER_Base)
```

**Ejemplo:**
```
Bruto/Hora Base (E3): $2,000
CER Base (G3): 173.7867 (del 15/12/2023)
CER Actual (15/01/2024): 200.5
Paridad = $2,000 × (200.5/173.7867) = $2,307.80
```

Si tu Bruto/Hora actual es $2,400, le ganaste a la inflación.

#### Columna I: Paridad CER (Neto/Hora)
**Propósito:** Lo mismo que H pero con Neto/Hora
**Fórmula:**
```excel
=IF(OR(B3="", D3="", F3="", G3=0), "",
   LET(
      fecha_cer, EOMONTH(B3,1)+15,
      cer_actual, IFERROR(VLOOKUP(fecha_cer, historic_data!$A$4:$B, 2, TRUE), 0),
      IF(cer_actual=0, "", F3 * (cer_actual/G3))
   ))
```

#### Columna J: Poder Adquisitivo vs Aumento (CER)
**Propósito:** **MÉTRICA CLAVE** - ¿Ganaste o perdiste poder adquisitivo?
**Fórmula:**
```excel
=IF(OR(B3="", D3="", F3="", G3=0), "",
   LET(
      fecha_cer, EOMONTH(B3,1)+15,
      cer_actual, IFERROR(VLOOKUP(fecha_cer, historic_data!$A$4:$B, 2, TRUE), 0),
      IF(cer_actual=0, "",
         (D3/F3) / (cer_actual/G3) - 1
      )
   ))
```

**Lógica:**
```
Variación_Real = (Neto_Actual/Neto_Base) / (CER_Actual/CER_Base) - 1
```

**Interpretación:**
- `+10%` = Ganaste 10% de poder adquisitivo (le ganaste al CER)
- `0%` = Mantuviste poder adquisitivo (empate con CER)
- `-10%` = Perdiste 10% de poder adquisitivo (te licuaron)

**Ejemplo (Período 3 actual):**
```
Neto/Hora Actual (D30): $18,325
Neto/Hora Base Ago 2025 (F30): $18,333
CER Actual (Abr 2026): 774.14
CER Base (Ago 2025): 639.7752

Variación = (18325/18333) / (774.14/639.7752) - 1
          = 0.9996 / 1.210 - 1
          = -17.4%  ← LICUACIÓN
```

---

### Grupo: VS ÚLTIMO AUMENTO (INDEC) (K-M)

**Objetivo:** Comparar con IPC Nacional (dato puro, sin rezago).

#### Columna K: Índice INDEC Actual
**Propósito:** Índice acumulado de inflación nacional desde el inicio
**Base:** 100 en octubre 2023
**Lógica de Matching:**
- Sueldo cobrado en mes M → usar inflación publicada de mes M
- Ejemplo: Sueldo 30/10/2023 → inflación octubre 2023 (8.3%)
- Los datos en CPI!A están como 01/10/2023 (primer día del mes)

**Fórmula (Fila 3 - Primera fila):**
```excel
=IF(B3="", "",
   LET(
      mes_fecha, DATE(YEAR(B3), MONTH(B3), 1),
      inflacion, IFERROR(VLOOKUP(VALUE(mes_fecha), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$C$4:$C}), 2, FALSE), 0),
      100 * (1 + inflacion/100)
   ))
```

**Fórmula (Fila 4+):**
```excel
=IF(B4="", "",
   LET(
      mes_fecha, DATE(YEAR(B4), MONTH(B4), 1),
      inflacion, IFERROR(VLOOKUP(VALUE(mes_fecha), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$C$4:$C}), 2, FALSE), 0),
      K3 * (1 + inflacion/100)
   ))
```

**Ejemplo:**
```
Fila 3  | Oct 2023 | Inflación: 8.3%  | Índice: 100 × 1.083 = 108.3
Fila 4  | Nov 2023 | Inflación: 12.8% | Índice: 108.3 × 1.128 = 122.2
Fila 5  | Dic 2023 | Inflación: 25.5% | Índice: 122.2 × 1.255 = 153.3
...
Fila 30 | Abr 2026 | Inflación: 2.5%  | Índice: 430.8 × 1.025 = 441.6
```

**NOTA CRÍTICA:** El matching es:
```
CPI!$A (fecha)    | CPI!$C (inflación nacional)
01/10/2023        | 8.3
01/11/2023        | 12.8
```

Usamos `VALUE()` para convertir fechas a números y hacer VLOOKUP correcto.

#### Columna L: Poder Adq vs REM (%)
**Propósito:** Placeholder para comparar con expectativas REM
**Status:** TODO - Por ahora en 0
**Fórmula:**
```excel
=IF(D3="", "", 0)
```

**NOTA:** Se implementará en el futuro cuando definamos la metodología de comparación con REM.

---

#### COLUMNA AUXILIAR: K_BASE (Índice INDEC Base) - OCULTA
**Propósito:** Trackear el índice INDEC del último ascenso
**Ubicación:** Insertar después de columna K, luego ocultar
**Práctica Excel:** Las columnas auxiliares se crean y se ocultan visualmente, pero permanecen en el sheet

**Fórmula (Fila 3):**
```excel
=IF(K3="", "", K3)
```

**Fórmula (Fila 4+):**
```excel
=IF(K4="", "", IF(Ingresos!Q4=TRUE, K4, K_BASE3))
```

**Lógica:**
- Primera fila: copiar K3 (índice inicial = 108.3)
- Filas siguientes:
  - Si hay ascenso (Ingresos!Q = TRUE): resetear base al índice actual
  - Sino: mantener base anterior

**Ejemplo:**
```
Fila 3  | Oct 2023 | K: 108.3  | K_BASE: 108.3  | Ascenso: FALSE
Fila 4  | Nov 2023 | K: 122.2  | K_BASE: 108.3  | Ascenso: FALSE
...
Fila 15 | Dic 2024 | K: 312.3  | K_BASE: 312.3  | Ascenso: TRUE  ← RESET
Fila 16 | Ene 2025 | K: 318.2  | K_BASE: 312.3  | Ascenso: FALSE
```

---

#### Columna M: Poder Adquisitivo vs INDEC (%)
**Propósito:** **MÉTRICA CLAVE** - Variación real usando IPC Nacional
**Depende de:** Columna auxiliar K_BASE

**Fórmula (Fila 3):**
```excel
=IF(OR(D3="", F3="", K3="", K_BASE3=""), "", 0)
```
(Primera fila: 0% porque es la base)

**Fórmula (Fila 4+):**
```excel
=IF(OR(D4="", F4="", K4="", K_BASE4=""), "",
   (D4/F4) / (K4/K_BASE4) - 1
)
```

**Lógica:**
```
Variación_Real = (Neto_Actual/Neto_Base) / (INDEC_Actual/INDEC_Base) - 1
```

**Interpretación:**
- `+10%` = Ganaste 10% vs inflación INDEC
- `0%` = Empate con inflación INDEC
- `-10%` = Perdiste 10% vs inflación INDEC

**Ejemplo (Período actual desde Ago 2025):**
```
Neto/Hora Actual (D30): $18,325
Neto/Hora Base (F30): $18,333
INDEC Actual (K30): 441.6
INDEC Base (K_BASE30): 373.8

Variación = (18325/18333) / (441.6/373.8) - 1
          = 0.9996 / 1.181 - 1
          = -15.3%  ← LICUACIÓN vs IPC Nacional
```

---

### Grupo: VARIACIÓN MENSUAL (N-Q)

**Objetivo:** Métricas mes a mes, no acumuladas.

#### Columna N: Δ% CER MoM
**Propósito:** Variación del CER del mes actual vs mes anterior
**Fórmula (Fila 3):**
```excel
=IF(B3="", "", "")
```
(Primera fila no tiene comparación)

**Fórmula (Fila 4+):**
```excel
=IF(B4="", "",
   LET(
      fecha_cer_actual, EOMONTH(B4,1)+15,
      fecha_cer_anterior, EOMONTH(B3,1)+15,
      cer_actual, IFERROR(VLOOKUP(fecha_cer_actual, historic_data!$A$4:$B, 2, TRUE), 0),
      cer_anterior, IFERROR(VLOOKUP(fecha_cer_anterior, historic_data!$A$4:$B, 2, TRUE), 0),
      IF(OR(cer_actual=0, cer_anterior=0), "", (cer_actual/cer_anterior)-1)
   ))
```

**Ejemplo:**
```
Fila 3: Oct 2023 → CER 15/12/2023 = 173.79
Fila 4: Nov 2023 → CER 15/01/2024 = 196.27
Δ% = (196.27/173.79) - 1 = 12.95%
```

#### Columna O: Δ% $/Hora vs CER Acumulado
**Propósito:** Variación real acumulada desde último ascenso
**Fórmula:**
```excel
=IF(OR(B3="", C3="", E3="", G3=0), "",
   LET(
      fecha_cer, EOMONTH(B3,1)+15,
      cer_actual, IFERROR(VLOOKUP(fecha_cer, historic_data!$A$4:$B, 2, TRUE), 0),
      IF(cer_actual=0, "",
         (C3/E3) / (cer_actual/G3) - 1
      )
   ))
```

**Lógica:** Igual que columna J pero con Bruto en vez de Neto.

#### Columna P: CER Actual
**Propósito:** Valor del CER para este sueldo
**Fórmula:**
```excel
=IF(B3="", "",
   LET(
      fecha_cer, EOMONTH(B3,1)+15,
      cer, IFERROR(VLOOKUP(fecha_cer, historic_data!$A$4:$B, 2, TRUE), 0),
      IF(cer=0, "", cer)
   ))
```

#### Columna Q: CER Base
**Propósito:** Referencia al CER del último ascenso
**Fórmula:**
```excel
=IF(B3="", "", G3)
```

Simple copia de columna G para tenerla visible.

---

### Grupo: PROYECCIÓN REM (R-W)

**Objetivo:** Objetivos de sueldo basados en expectativas del mercado (REM).

#### Columna R: REM 3m (%)
**Propósito:** Inflación esperada acumulada en próximos 3 meses según REM
**Lógica:**
- Buscar en REM sheet las proyecciones de M+1, M+2, M+3
- Acumular: (1 + i1) × (1 + i2) × (1 + i3) - 1

**Fórmula:**
```excel
=IF(OR(B3="", C3=""), "",
   LET(
      fecha_busqueda, EOMONTH(B3,-1)+1,
      i1, IFERROR(VLOOKUP(fecha_busqueda, REM!$A$4:$I, 3, TRUE), 0),
      i2, IFERROR(VLOOKUP(fecha_busqueda, REM!$A$4:$I, 4, TRUE), 0),
      i3, IFERROR(VLOOKUP(fecha_busqueda, REM!$A$4:$I, 5, TRUE), 0),
      (1+i1)*(1+i2)*(1+i3)-1
   ))
```

**Columnas REM:**
```
Col 3 (C): M+1
Col 4 (D): M+2
Col 5 (E): M+3
Col 6 (F): M+4
Col 7 (G): M+5
Col 8 (H): M+6
```

#### Columna S: Objetivo 3m Bruto/Hora
**Propósito:** Lo que debería ser tu bruto/hora en 3 meses
**Fórmula:**
```excel
=IF(OR(B3="", C3="", R3=""), "", C3 * (1+R3))
```

#### Columna T: Objetivo 3m Neto/Hora
**Fórmula:**
```excel
=IF(OR(B3="", D3="", R3=""), "", D3 * (1+R3))
```

#### Columna U: REM 6m (%)
**Propósito:** Inflación esperada acumulada en próximos 6 meses
**Fórmula:**
```excel
=IF(OR(B3="", C3="", R3=""), "",
   LET(
      fecha_busqueda, EOMONTH(B3,-1)+1,
      i4, IFERROR(VLOOKUP(fecha_busqueda, REM!$A$4:$I, 6, TRUE), 0),
      i5, IFERROR(VLOOKUP(fecha_busqueda, REM!$A$4:$I, 7, TRUE), 0),
      i6, IFERROR(VLOOKUP(fecha_busqueda, REM!$A$4:$I, 8, TRUE), 0),
      (1+R3)*(1+i4)*(1+i5)*(1+i6)-1
   ))
```

**Nota:** Parte de REM 3m (R3) y le suma los próximos 3 meses.

#### Columna V: Objetivo 6m Bruto/Hora
```excel
=IF(OR(B3="", C3="", U3=""), "", C3 * (1+U3))
```

#### Columna W: Objetivo 6m Neto/Hora
```excel
=IF(OR(B3="", D3="", U3=""), "", D3 * (1+U3))
```

---

## ANÁLISIS USD - Sueldo en Dólares Nominal y Real

### Grupo: PERIODO (A)

#### Columna A: Periodo
```excel
=IF(Ingresos!B3<>"", Ingresos!A3, "")
```

---

### Grupo: SUELDO ARS (B-D)

#### Columna B: Fecha
```excel
=IF(Ingresos!B3<>"", Ingresos!B3, "")
```

#### Columna C: Bruto ARS
```excel
=IF(Ingresos!B3<>"", Ingresos!C3, "")
```

#### Columna D: Neto ARS
```excel
=IF(Ingresos!B3<>"", Ingresos!G3, "")
```

---

### Grupo: SUELDO USD NOMINAL (E-H)

**Objetivo:** Tu sueldo convertido a USD al tipo de cambio del día.

#### Columna E: CCL
**Propósito:** Cotización del dólar CCL (Contado con Liquidación) del día de cobro
**Fórmula:**
```excel
=IF(B3="", "",
   IFERROR(LOOKUP(B3, historic_data!$A$4:$A, historic_data!$C$4:$C), "")
)
```

**Nota:** LOOKUP busca el último valor menor o igual a B3, útil si no hay dato exacto.

#### Columna F: Δ% CCL MoM
**Propósito:** Variación del CCL vs mes anterior
**Fórmula (Fila 3):**
```excel
=""
```

**Fórmula (Fila 4+):**
```excel
=IF(E4="", "",
   IFERROR(
      (E4 - LOOKUP(EOMONTH(B4,-1), historic_data!$A$4:$A, historic_data!$C$4:$C)) /
      LOOKUP(EOMONTH(B4,-1), historic_data!$A$4:$A, historic_data!$C$4:$C),
      ""
   )
)
```

#### Columna G: Bruto USD
**Propósito:** Tu sueldo bruto en dólares nominales
**Fórmula:**
```excel
=IF(OR(B3="", C3="", E3=""), "", C3/E3)
```

**Ejemplo:**
```
Bruto ARS: $1,528,416
CCL: $1,100
Bruto USD = $1,528,416 / $1,100 = USD 1,389.47
```

#### Columna H: Neto USD
**Fórmula:**
```excel
=IF(OR(B3="", D3="", E3=""), "", D3/E3)
```

---

### Grupo: SUELDO USD REAL (I-L)

**Objetivo:** Tu sueldo en USD ajustado por inflación (dólares constantes).

#### Columna I: CER
**Propósito:** CER del período (para ajustar por inflación)
**Fórmula:**
```excel
=IF(B3="", "",
   LET(
      fecha_cer, EOMONTH(B3,1)+15,
      cer, IFERROR(VLOOKUP(fecha_cer, historic_data!$A$4:$B, 2, TRUE), 0),
      IF(cer=0, "", cer)
   ))
```

Misma lógica que Análisis ARS columna P.

#### Columna J: CCL Real
**Propósito:** CCL ajustado por inflación, base = primera fila
**Fórmula:**
```excel
=IF(OR(B3="", E3="", I3="", I$3=""), "",
   E3 * (I$3 / I3)
)
```

**Lógica:**
```
CCL_Real = CCL_Nominal × (CER_Base / CER_Actual)
```

**Ejemplo:**
```
Oct 2023: CCL=$300, CER=173.79
Abr 2026: CCL=$1,200, CER=774.14

CCL_Real_Abr26 = $1,200 × (173.79/774.14) = $269.45

Interpretación: El dólar de abril 2026 vale MENOS en términos reales
que el dólar de octubre 2023 (el peso se fortaleció en términos reales).
```

#### Columna K: Bruto USD Real
**Propósito:** Tu sueldo bruto en dólares constantes (ajustado por inflación)
**Fórmula:**
```excel
=IF(OR(B3="", C3="", J3=""), "", C3/J3)
```

**Ejemplo:**
```
Bruto ARS: $1,528,416
CCL Real: $683.67
Bruto USD Real = $1,528,416 / $683.67 = USD 2,235.79

vs Bruto USD Nominal: USD 1,389.47

El sueldo real en USD es mayor porque el peso se fortaleció.
```

#### Columna L: Neto USD Real
**Fórmula:**
```excel
=IF(OR(B3="", D3="", J3=""), "", D3/J3)
```

---

### Grupo: VS ÚLTIMO AUMENTO (M-P)

**Objetivo:** Comparar tu sueldo USD desde el último ascenso.

**NOTA:** Se eliminaron las columnas P y Q (Paridad USD Bruto/Neto) porque no tenían sentido conceptual.

#### Columna M: CCL Base
**Propósito:** CCL del último ascenso
**Fórmula (Fila 3):**
```excel
=IF(E3="", "", E3)
```

**Fórmula (Fila 4+):**
```excel
=IF(E4="", "", IF(Ingresos!Q4=TRUE, E4, M3))
```

#### Columna N: Bruto USD Base
**Fórmula (Fila 3):**
```excel
=IF(G3="", "", G3)
```

**Fórmula (Fila 4+):**
```excel
=IF(G4="", "", IF(Ingresos!Q4=TRUE, G4, N3))
```

#### Columna O: Neto USD Base
**Fórmula (Fila 3):**
```excel
=IF(H3="", "", H3)
```

**Fórmula (Fila 4+):**
```excel
=IF(H4="", "", IF(Ingresos!Q4=TRUE, H4, O3))
```

#### Columna P: Variación USD (%)
**Propósito:** **MÉTRICA CLAVE** - ¿Ganaste o perdiste en USD desde el último ascenso?
**Fórmula:**
```excel
=IF(OR(B3="", H3="", O3=""), "", (H3/O3)-1)
```

**Lógica:**
```
Variación_USD = (Neto_USD_Actual / Neto_USD_Base) - 1
```

**Interpretación:**
- `+15%` = Ganaste 15% en USD nominal (mejora cambiaria)
- `0%` = Mantuviste sueldo en USD
- `-15%` = Perdiste 15% en USD (licuación cambiaria)

**Ejemplo (Período 3):**
```
Neto USD Actual (Abr 2026): USD 2,000
Neto USD Base (Ago 2025): USD 2,200

Variación = (2000/2200) - 1 = -9.1% ← LICUACIÓN CAMBIARIA
```

**NOTA:** Esta métrica es complementaria a las métricas ARS. Muestra si tu sueldo creció en dólares, independientemente de la inflación.

---

## PROBLEMAS IDENTIFICADOS Y SOLUCIONES

### 1. ARRAYFORMULA con SCAN
**Problema:** SCAN no se puede usar en fórmulas individuales
**Solución:** Usar referencias a fila anterior (E3, F3, etc.)

### 2. Matching CER con Sueldo
**Problema:** Rezago del CER (refleja inflación de mes M-1)
**Solución:**
- Sueldo mes M → CER día 15 mes M+1
- Fórmula: `EOMONTH(fecha_sueldo, 1) + 15`

### 3. Matching IPC INDEC con Sueldo
**Problema:** IPC se publica ~día 15 mes M+1 con inflación de mes M
**Solución:**
- Sueldo mes M → IPC mes M
- Dato en CPI!A como `01/M/YYYY`
- Convertir con `DATE(YEAR(fecha), MONTH(fecha), 1)`

### 4. Índice INDEC Base en Ascensos
**Problema:** Necesitamos resetear base en cada ascenso sin SCAN
**Solución:** ✅ Agregada columna auxiliar `K_BASE` (oculta) que trackea el índice del último ascenso

### 5. Columnas P y Q en Análisis USD
**Problema:** "Paridad USD" no tiene sentido conceptual
**Solución:** ✅ ELIMINADAS - Análisis USD ahora tiene 16 columnas (A-P)

---

## PLAN DE IMPLEMENTACIÓN

### Fase 1: Validar Fórmulas (ACTUAL)
1. ✅ Documentar cada columna
2. ✅ Definir fórmulas sin ARRAYFORMULA
3. ⏳ Validar con datos reales
4. ⏳ Corregir bugs

### Fase 2: Implementar Fórmulas Simples
1. Actualizar `src/sheets/structure.py`
2. Cambiar todas las fórmulas ARRAYFORMULA por fórmulas de fila 3
3. Probar con `python setup_sheet.py`
4. Validar resultados manualmente

### Fase 3: Optimizar con ARRAYFORMULA
1. Una vez validadas las fórmulas simples
2. Convertir a ARRAYFORMULA columna por columna
3. Validar que den los mismos resultados
4. Commit

---

## DECISIONES TOMADAS ✅

1. **Columna M (Poder Adq vs INDEC):**
   - ✅ Agregada columna auxiliar K_BASE (Índice INDEC Base)
   - ✅ Se insertará después de columna K y se ocultará visualmente
   - ✅ Práctica estándar Excel: columnas auxiliares se ocultan pero permanecen en el sheet

2. **Columnas P y Q (Paridad USD):**
   - ✅ ELIMINADAS - No tenían sentido conceptual
   - ✅ Análisis USD ahora tiene 16 columnas (A-P) en vez de 18

3. **Columna L (Poder Adq vs REM):**
   - ✅ Se deja en 0 por ahora
   - ✅ TODO para implementar en el futuro

## PENDIENTES DE VALIDACIÓN

1. **Validación de Fórmulas:**
   - Comparar resultados con cálculos manuales en CALCULO_MANUAL_METRICAS.md
   - Verificar matching CER (sueldo mes M → CER día 15 mes M+1)
   - Verificar matching IPC INDEC (sueldo mes M → IPC mes M)

2. **Testing:**
   - Implementar en Google Sheets de prueba
   - Validar con datos reales de ingresos.txt
   - Verificar que columnas resetean correctamente en ascensos

---

## PRÓXIMOS PASOS

1. **AHORA:** Revisar este documento con el usuario
2. Tomar decisiones sobre pendientes
3. Implementar fórmulas simples en structure.py
4. Testear con datos reales
5. Validar contra cálculos manuales
6. Optimizar con ARRAYFORMULA
