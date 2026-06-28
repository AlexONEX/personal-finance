# Análisis ARS — Estructura de Columnas

Tab: `Análisis ARS` · Fila 1 = grupos · Fila 2 = headers · Datos desde fila 3
Columnas ocultas: D, E

**Heurística:** una sola ARRAYFORMULA en fila 3 cubre todo el rango.
Excepción: D y E usan carry-forward (se referencian a la fila anterior) — per-row o SCAN.

---

## Columnas

### A — Periodo
```excel
=ARRAYFORMULA(IF(Ingresos!B3:B="","",Ingresos!A3:A))
```

### B — Fecha
```excel
=ARRAYFORMULA(IF(Ingresos!B3:B="","",Ingresos!B3:B))
```

### C — Neto/Hora
Sueldo neto del mes dividido horas trabajadas (8h/día × días hábiles del mes).
```excel
=ARRAYFORMULA(IF(Ingresos!G3:G="","",IFERROR(
  Ingresos!G3:G / (NETWORKDAYS(DATE(YEAR(Ingresos!B3:B),MONTH(Ingresos!B3:B),1),EOMONTH(Ingresos!B3:B,0)) * Ingresos!$N$2),
"")))
```

### D — Neto/Hora Base *(oculta, per-row)*
Neto/Hora al momento del último aumento. Se congela cuando cambia el bruto.
Se referencia a la fila anterior (D2) → no puede ser ARRAYFORMULA simple.
```excel
=IF(OR(Ingresos!C3="",Ingresos!C3=0),"",IF(OR(ROW()=3,Ingresos!C3<>Ingresos!C2),C3,D2))
```
*Copiar hacia abajo en cada fila.*

### E — CER Base *(oculta, per-row)*
Valor CER al momento del último aumento. Se congela junto con D.
```excel
=IF(OR(Ingresos!C3="",Ingresos!C3=0),"",IF(OR(ROW()=3,Ingresos!C3<>Ingresos!C2),VLOOKUP(EOMONTH(Ingresos!B3,0),historic_data!$A$4:$B,2,TRUE),E2))
```
*Copiar hacia abajo en cada fila.*

### F — Paridad CER (Neto/Hora)
> **Q2: ¿Cuánto debería ganar hoy ajustado por CER?**

```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  D3:D * (VLOOKUP(EOMONTH(B3:B,0),historic_data!$A$4:$B,2,TRUE) / E3:E),
"-")))
```

### G — Poder Adq vs Aumento (CER)
> **Q1: ¿Cuánto gané/perdí vs CER desde el último aumento?**

```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  (C3:C/D3:D) / (VLOOKUP(EOMONTH(B3:B,0),historic_data!$A$4:$B,2,TRUE)/E3:E) - 1,
"-")))
```

### H — Objetivo 1m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 1 mes?**

Usa REM M+1 (col 3).
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C * (1+VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,3,FALSE)),
"-")))
```

### I — Objetivo 3m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 3 meses?**

Compuesto REM M+1 × M+2 × M+3.
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,3,FALSE),0))
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,4,FALSE),0))
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,5,FALSE),0)),
"-")))
```

### J — Objetivo 6m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 6 meses?**

Compuesto REM M+1 × … × M+6.
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,3,FALSE),0))
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,4,FALSE),0))
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,5,FALSE),0))
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,6,FALSE),0))
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,7,FALSE),0))
  * (1+IFERROR(VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,8,FALSE),0)),
"-")))
```

### K — Objetivo 12m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 12 meses?**

Usa REM Próx. 12m (col 9).
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C * (1+VLOOKUP(EOMONTH(B3:B,0),REM!$A$4:$I,9,FALSE)),
"-")))
```

---

## Grupos fila 1

| Columnas | Grupo |
|----------|-------|
| A–B | PERIODO |
| C | SUELDO |
| D–G | VS ÚLTIMO AUMENTO (CER) |
| H–K | PROYECCIÓN REM |

---

## Migración desde estructura anterior (21 → 11 columnas)

### Mover (ajustar referencias de columna)

| Col anterior | Col nueva | Nombre |
|-------------|-----------|--------|
| A | A | Periodo |
| B | B | Fecha |
| E | C | Neto/Hora |
| G | D | Neto/Hora Base |
| H | E | CER Base |
| J | F | Paridad CER (Neto/Hora) |
| K | G | Poder Adq vs Aumento (CER) |
| — | H | Objetivo 1m Neto/Hora *(nueva)* |
| R | I | Objetivo 3m Neto/Hora |
| U | J | Objetivo 6m Neto/Hora |
| — | K | Objetivo 12m Neto/Hora *(nueva)* |

### Eliminar

| Col | Nombre | Motivo |
|-----|--------|--------|
| C | Bruto total | duplicado de Ingresos |
| D | Bruto/Hora | versión bruto |
| F | Bruto/Hora Base | versión bruto |
| I | Paridad CER (Bruto/Hora) | versión bruto |
| L | Poder Adq. | redundante con G |
| M | Poder Adq vs INDEC (%) | fuera de scope |
| N | Δ% Sueldo MoM | no responde las 3 preguntas |
| O | Δ% Inflación MoM | no responde las 3 preguntas |
| P | REM 3m (%) | embebido en I |
| Q | Objetivo 3m Bruto/Hora | versión bruto |
| S | REM 6m (%) | embebido en J |
| T | Objetivo 6m Bruto/Hora | versión bruto |
