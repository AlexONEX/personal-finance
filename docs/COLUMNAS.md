# Diccionario de Columnas - Sheet Ingresos

**Generado automáticamente desde `src/sheets/structure.py`**

## Grupos de Columnas

### PERIODO (A - A)

#### Columna A: Periodo Abonado

**Descripción:** Periodo al que corresponde el sueldo (auto-generado)

**Fórmula:**
```excel
=TEXT(BROW, "mmmm yyyy")
```

**Formato:** TEXT - `mmmm yyyy`

**Tipo:** Auto-calculado

---

### SUELDO (B - G)

#### Columna B: Fecha

**Descripción:** Fecha real de cobro

**Formato:** DATE - `dd/mm/yyyy`

**Tipo:** Input manual

---

#### Columna C: Bruto

**Descripción:** Sueldo bruto mensual (input manual)

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Input manual

---

#### Columna D: Jubilacion

**Descripción:** Descuento jubilación (11% del bruto)

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", ROUND(CROW*impuestos!$B$2,0))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna E: PAMI

**Descripción:** Descuento PAMI (3% del bruto)

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", ROUND(CROW*impuestos!$B$3,0))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna F: Obra Social

**Descripción:** Descuento obra social (3% del bruto)

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", ROUND(CROW*impuestos!$B$4,0))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna G: Neto

**Descripción:** Sueldo neto (bruto - descuentos)

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", CROW-DROW-EROW-FROW)
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

### AGUINALDO (H - I)

#### Columna H: SAC Bruto

**Descripción:** Aguinaldo bruto (input manual)

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Input manual

---

#### Columna I: SAC Neto

**Descripción:** Aguinaldo neto (SAC - descuentos)

**Fórmula:**
```excel
=IF(OR(ISBLANK(HROW), HROW=0), "-", HROW-ROUND(HROW*impuestos!$B$2,0)-ROUND(HROW*impuestos!$B$3,0)-ROUND(HROW*impuestos!$B$4,0))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

### BONOS (J - J)

#### Columna J: Bono Neto

**Descripción:** Bonos extraordinarios netos (input manual)

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Input manual

---

### BENEFICIOS (K - L)

#### Columna K: Tarjeta Corporativa

**Descripción:** Tarjeta corporativa mensual (input manual)

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Input manual

---

#### Columna L: Otros Beneficios

**Descripción:** Otros beneficios (input manual)

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Input manual

---

### TOTAL (M - M)

#### Columna M: Total Neto

**Descripción:** Total neto mensual (suma de todo)

**Fórmula:**
```excel
=IF(OR(ISBLANK(GROW), GROW="-"), "-", IFERROR(IF(SUM(GROW:LROW)=0, "-", SUM(GROW:LROW)), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

### COMPARACION CON ULTIMO AUMENTO ARS (N - S)

#### Columna N: Bruto Base

**Descripción:** Bruto al momento del último aumento

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IF(OR(ROW(CROW)=3, CROW<>CROW-1), CROW, NROW-1))
```

**Formato:** NUMBER - `#,##0`

**Tipo:** Auto-calculado

---

#### Columna O: Neto Base

**Descripción:** Neto al momento del último aumento

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IF(OR(ROW(CROW)=3, CROW<>CROW-1), GROW, OROW-1))
```

**Formato:** NUMBER - `#,##0`

**Tipo:** Auto-calculado

---

#### Columna P: CER Base

**Descripción:** Valor CER al momento del último aumento

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IF(OR(ROW(CROW)=3, CROW<>CROW-1), VLOOKUP(EOMONTH(BROW, 0), historic_data!$A$4:$B, 2, TRUE), PROW-1))
```

**Formato:** NUMBER - `0.0000`

**Tipo:** Auto-calculado

---

#### Columna Q: Paridad CER (Bruto)

**Descripción:** Sueldo bruto para mantener paridad CER

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0, PROW="-"), "-", IFERROR(NROW * (VLOOKUP(EOMONTH(BROW, 0), historic_data!$A$4:$B, 2, TRUE)/PROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna R: Paridad CER (Neto)

**Descripción:** Sueldo neto para mantener paridad CER

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0, PROW="-"), "-", IFERROR(OROW * (VLOOKUP(EOMONTH(BROW, 0), historic_data!$A$4:$B, 2, TRUE)/PROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna S: Poder Adq (Neto). vs Aumento

**Descripción:** Poder adquisitivo acumulado vs último aumento

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0, PROW="-"), "-", IFERROR((GROW/OROW) / (VLOOKUP(EOMONTH(BROW, 0), historic_data!$A$4:$B, 2, TRUE)/PROW) - 1, "-"))
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

### INFLACIÓN (CER) (T - V)

#### Columna T: Δ% CER MoM

**Descripción:** Variación CER mensual (30 días)

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IFERROR((VLOOKUP(BROW, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(BROW-30, historic_data!$A$4:$B, 2, TRUE)) - 1, "-"))
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

#### Columna U: Δ% Salario vs Cer

**Descripción:** Poder adquisitivo MoM (salario vs CER mes a mes)

**Fórmula:**
```excel
=IF(OR(TROW="-", ISBLANK(GROW), ISBLANK(GROW-1), GROW=0, GROW-1=0), "-", IFERROR((GROW/GROW-1)/(1+TROW)-1,"-"))
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

#### Columna V: Δ% Salario vs Cer Acum

**Descripción:** Poder adquisitivo acumulado desde inicio (salario vs CER total)

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IFERROR((CROW/C$3) / (VLOOKUP(EOMONTH(BROW, 0), historic_data!$A$4:$B, 2, TRUE)/VLOOKUP(EOMONTH(B$3, 0), historic_data!$A$4:$B, 2, TRUE)) - 1, "-"))
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

### PROYECCION REM (W - AB)

#### Columna W: REM 3m (%)

**Descripción:** Inflación proyectada REM 3m

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", (1+IFERROR(VLOOKUP(EOMONTH(BROW, 0), REM!$A$4:$I, 3, FALSE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(BROW, 0), REM!$A$4:$I, 4, FALSE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(BROW, 0), REM!$A$4:$I, 5, FALSE), 0))-1)
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

#### Columna X: Objetivo 3m Bruto

**Descripción:** Sueldo bruto objetivo para dentro de 3 meses

**Fórmula:**
```excel
=IF(WROW="-", "-", IFERROR(CROW * (1+WROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna Y: Objetivo 3m Neto

**Descripción:** Sueldo neto objetivo para dentro de 3 meses

**Fórmula:**
```excel
=IF(WROW="-", "-", IFERROR(GROW * (1+WROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna Z: REM 6m (%)

**Descripción:** Inflación proyectada REM 6m

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", (1+WROW)*(1+IFERROR(VLOOKUP(EOMONTH(BROW, 0), REM!$A$4:$I, 6, FALSE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(BROW, 0), REM!$A$4:$I, 7, FALSE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(BROW, 0), REM!$A$4:$I, 8, FALSE), 0))-1)
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

#### Columna AA: Objetivo 6m Bruto

**Descripción:** Sueldo bruto objetivo para dentro de 6 meses

**Fórmula:**
```excel
=IF(ZROW="-", "-", IFERROR(CROW * (1+ZROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna AB: Objetivo 6m Neto

**Descripción:** Sueldo neto objetivo para dentro de 6 meses

**Fórmula:**
```excel
=IF(ZROW="-", "-", IFERROR(GROW * (1+ZROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

### DÓLAR (AC - AF)

#### Columna AC: CCL

**Descripción:** Dólar CCL cierre de mes

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(BROW, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-"))
```

**Formato:** CURRENCY - `$#,##0.00`

**Tipo:** Auto-calculado

---

#### Columna AD: Δ % CCL MoM

**Descripción:** Variación % CCL MoM

**Fórmula:**
```excel
=IF(ACROW="-", "-", IFERROR((ACROW - INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(EOMONTH(BROW, -1), FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1))) / INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(EOMONTH(BROW, -1), FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-"))
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

#### Columna AE: Sueldo USD Bruto

**Descripción:** Sueldo Bruto en USD CCL

**Fórmula:**
```excel
=IF(OR(CROW=0, ACROW="-"), "-", IFERROR(CROW/ACROW,"-"))
```

**Formato:** NUMBER - `#,##0.00`

**Tipo:** Auto-calculado

---

#### Columna AF: Sueldo USD Neto

**Descripción:** Sueldo Neto en USD CCL

**Fórmula:**
```excel
=IF(OR(GROW="-", ACROW="-"), "-", IFERROR(GROW/ACROW,"-"))
```

**Formato:** NUMBER - `#,##0.00`

**Tipo:** Auto-calculado

---

### VS ÚLTIMO AUMENTO USD (AG - AL)

#### Columna AG: CCL Base

**Descripción:** CCL al momento del último aumento

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IF(OR(ROW(CROW)=3, CROW<>CROW-1), ACROW, AGROW-1))
```

**Formato:** CURRENCY - `$#,##0.00`

**Tipo:** Auto-calculado

---

#### Columna AH: Sueldo USD Bruto Base

**Descripción:** Sueldo Bruto USD al momento del último aumento

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IF(OR(ROW(CROW)=3, CROW<>CROW-1), AEROW, AHROW-1))
```

**Formato:** NUMBER - `#,##0.00`

**Tipo:** Auto-calculado

---

#### Columna AI: Sueldo USD Neto Base

**Descripción:** Sueldo Neto USD al momento del último aumento

**Fórmula:**
```excel
=IF(OR(ISBLANK(CROW), CROW=0), "-", IF(OR(ROW(CROW)=3, CROW<>CROW-1), AFROW, AIROW-1))
```

**Formato:** NUMBER - `#,##0.00`

**Tipo:** Auto-calculado

---

#### Columna AJ: Paridad USD (Bruto)

**Descripción:** Sueldo en ARS para recuperar Bruto USD del aumento

**Fórmula:**
```excel
=IF(OR(NROW="-", ACROW="-", AGROW="-"), "-", IFERROR(NROW * (ACROW/AGROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna AK: Paridad USD (Neto)

**Descripción:** Sueldo en ARS para recuperar Neto USD del aumento

**Fórmula:**
```excel
=IF(OR(OROW="-", ACROW="-", AGROW="-"), "-", IFERROR(OROW * (ACROW/AGROW), "-"))
```

**Formato:** CURRENCY - `$#,##0`

**Tipo:** Auto-calculado

---

#### Columna AL: Atraso USD

**Descripción:** Atraso real en USD vs último aumento

**Fórmula:**
```excel
=IF(OR(AFROW="-", AIROW="-"), "-", IFERROR((AFROW/AIROW)-1, "-"))
```

**Formato:** PERCENT - `0.00%`

**Tipo:** Auto-calculado

---

## Tabla Resumen

| Col | Nombre | Tipo | Formato |
|-----|--------|------|---------|
| A | Periodo Abonado | Auto | TEXT |
| B | Fecha | Manual | DATE |
| C | Bruto | Manual | CURRENCY |
| D | Jubilacion | Auto | CURRENCY |
| E | PAMI | Auto | CURRENCY |
| F | Obra Social | Auto | CURRENCY |
| G | Neto | Auto | CURRENCY |
| H | SAC Bruto | Manual | CURRENCY |
| I | SAC Neto | Auto | CURRENCY |
| J | Bono Neto | Manual | CURRENCY |
| K | Tarjeta Corporativa | Manual | CURRENCY |
| L | Otros Beneficios | Manual | CURRENCY |
| M | Total Neto | Auto | CURRENCY |
| N | Bruto Base | Auto | NUMBER |
| O | Neto Base | Auto | NUMBER |
| P | CER Base | Auto | NUMBER |
| Q | Paridad CER (Bruto) | Auto | CURRENCY |
| R | Paridad CER (Neto) | Auto | CURRENCY |
| S | Poder Adq (Neto). vs Aumento | Auto | PERCENT |
| T | Δ% CER MoM | Auto | PERCENT |
| U | Δ% Salario vs Cer | Auto | PERCENT |
| V | Δ% Salario vs Cer Acum | Auto | PERCENT |
| W | REM 3m (%) | Auto | PERCENT |
| X | Objetivo 3m Bruto | Auto | CURRENCY |
| Y | Objetivo 3m Neto | Auto | CURRENCY |
| Z | REM 6m (%) | Auto | PERCENT |
| AA | Objetivo 6m Bruto | Auto | CURRENCY |
| AB | Objetivo 6m Neto | Auto | CURRENCY |
| AC | CCL | Auto | CURRENCY |
| AD | Δ % CCL MoM | Auto | PERCENT |
| AE | Sueldo USD Bruto | Auto | NUMBER |
| AF | Sueldo USD Neto | Auto | NUMBER |
| AG | CCL Base | Auto | CURRENCY |
| AH | Sueldo USD Bruto Base | Auto | NUMBER |
| AI | Sueldo USD Neto Base | Auto | NUMBER |
| AJ | Paridad USD (Bruto) | Auto | CURRENCY |
| AK | Paridad USD (Neto) | Auto | CURRENCY |
| AL | Atraso USD | Auto | PERCENT |

## Tasas de Impuestos

| Impuesto | Tasa | Ley |
|----------|------|-----|
| Jubilacion | 11% | Ley 24241 |
| PAMI | 3% | Ley 19032 |
| Obra Social | 3% | Ley 23660 |
| Otro | 0% | — |

## Inputs Manuales Requeridos

Para cada mes, debes ingresar manualmente:

- **B** (Fecha)
- **C** (Bruto)
- **H** (SAC Bruto)
- **J** (Bono Neto)
- **K** (Tarjeta Corporativa)
- **L** (Otros Beneficios)

---

*Última actualización: Auto-generado*

Para actualizar este archivo, ejecutá:
```bash
uv run python generate_columnas_doc.py
```