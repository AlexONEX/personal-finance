# Análisis ARS — Estructura de Columnas

Tab: `Análisis ARS` · Fila 1 = grupos · Fila 2 = headers · Datos desde fila 3
Columnas ocultas: D, E

**Heurística:** una sola ARRAYFORMULA en fila 3 cubre todo el rango. Sin excepciones.

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
Referencia directa a Ingresos!P (calculado allí como `Neto / (HorasDiarias × 20)`).
```excel
=ARRAYFORMULA(IF(Ingresos!B3:B<>"", Ingresos!P3:P, ""))
```

### D — Neto/Hora Base *(oculta)*
Neto/Hora al momento del último ascenso. SCAN con carry-forward; se resetea cuando `Ingresos!Q` es TRUE.
```excel
=LET(
  s, SCAN(0, SEQUENCE(ROWS(C3:C1000)), LAMBDA(acc, i,
    LET(
      val, INDEX(C3:C1000, i),
      asc, INDEX(Ingresos!Q3:Q1000, i),
      IF(val="", acc,
        IF(OR(acc=0, acc="", asc=TRUE), val, acc)
      )
    )
  )),
  ARRAYFORMULA(IF(C3:C1000="", "", s))
)
```

### E — CER Base *(oculta)*
CER al momento del último ascenso. Mismo SCAN pero acumula el CER de cada fila en vez del Neto/Hora.
```excel
=LET(
  s, SCAN(0, SEQUENCE(ROWS(C3:C1000)), LAMBDA(acc, i,
    LET(
      val, INDEX(C3:C1000, i),
      asc, INDEX(Ingresos!Q3:Q1000, i),
      cer, IFERROR(VLOOKUP(EOMONTH(INDEX(Ingresos!B3:B1000, i), 0), historic_data!$A$4:$B, 2, TRUE), 0),
      IF(val="", acc,
        IF(OR(acc=0, acc="", asc=TRUE), cer, acc)
      )
    )
  )),
  ARRAYFORMULA(IF(C3:C1000="", "", s))
)

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

Usa REM M+1 (col 3). REM guarda primer día del mes → `DATE(YEAR,MONTH,1)` para match exacto.
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C * (1+VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,3,FALSE)),
"-")))
```

### I — Objetivo 3m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 3 meses?**

Compuesto REM M+1 × M+2 × M+3.
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,3,FALSE),0))
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,4,FALSE),0))
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,5,FALSE),0)),
"-")))
```

### J — Objetivo 6m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 6 meses?**

Compuesto REM M+1 × … × M+6.
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,3,FALSE),0))
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,4,FALSE),0))
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,5,FALSE),0))
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,6,FALSE),0))
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,7,FALSE),0))
  * (1+IFERROR(VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,8,FALSE),0)),
"-")))
```

### K — Objetivo 12m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 12 meses?**

Usa REM Próx. 12m (col 9).
```excel
=ARRAYFORMULA(IF(C3:C="","-",IFERROR(
  C3:C * (1+VLOOKUP(DATE(YEAR(B3:B),MONTH(B3:B),1),REM!$A$4:$I,9,FALSE)),
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
