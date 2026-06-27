# Análisis ARS — Estructura de Columnas

Tab: `Análisis ARS` · Fila 1 = grupos · Fila 2 = headers · Datos desde fila 3
Columnas ocultas: D, E

## Columnas

### A — Periodo
Referencia directa a Ingresos.
```excel
=Ingresos!A3
```

### B — Fecha
Referencia directa a Ingresos.
```excel
=Ingresos!B3
```

### C — Neto/Hora
Sueldo neto del mes dividido horas trabajadas (8h/día × días hábiles del mes).
*Fórmula existente — no cambiar.*

### D — Neto/Hora Base *(oculta)*
Neto/Hora al momento del último aumento. Se congela cuando cambia el bruto.
*Fórmula existente — no cambiar.*

### E — CER Base *(oculta)*
Valor CER al momento del último aumento. Se congela junto con D.
*Fórmula existente — no cambiar.*

### F — Paridad CER (Neto/Hora)
> **Q2: ¿Cuánto debería ganar hoy ajustado por CER?**

*Fórmula existente — no cambiar.*

### G — Poder Adq vs Aumento (CER)
> **Q1: ¿Cuánto gané/perdí vs CER desde el último aumento?**

*Fórmula existente — no cambiar.*

### H — Objetivo 1m Neto/Hora *(nueva)*
> **Q3: ¿Cuánto debería ganar en 1 mes para mantener poder adquisitivo?**

Usa REM M+1 (col 3).
```excel
=IF(C3="","-",IFERROR(C3*(1+VLOOKUP(EOMONTH(B3,0),REM!$A$4:$I,3,FALSE)),"-"))
```

### I — Objetivo 3m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 3 meses?**

*Fórmula existente (era col R) — no cambiar.*

### J — Objetivo 6m Neto/Hora
> **Q3: ¿Cuánto debería ganar en 6 meses?**

*Fórmula existente (era col U) — no cambiar.*

### K — Objetivo 12m Neto/Hora *(nueva)*
> **Q3: ¿Cuánto debería ganar en 12 meses?**

Usa REM Próx. 12m (col 9).
```excel
=IF(C3="","-",IFERROR(C3*(1+VLOOKUP(EOMONTH(B3,0),REM!$A$4:$I,9,FALSE)),"-"))
```

## Grupos fila 1

| Columnas | Grupo |
|----------|-------|
| A–B | PERIODO |
| C | SUELDO |
| D–G | VS ÚLTIMO AUMENTO (CER) |
| H–K | PROYECCIÓN REM |

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
| D | Bruto/Hora | versión bruto, no responde las 3 preguntas |
| F | Bruto/Hora Base | versión bruto |
| I | Paridad CER (Bruto/Hora) | versión bruto |
| L | Poder Adq. | redundante con G |
| M | Poder Adq vs INDEC (%) | fuera de scope |
| N | Δ% Sueldo MoM | helper, no responde las 3 preguntas |
| O | Δ% Inflación MoM | helper |
| P | REM 3m (%) | helper embebido en fórmula de I |
| Q | Objetivo 3m Bruto/Hora | versión bruto |
| S | REM 6m (%) | helper embebido en fórmula de J |
| T | Objetivo 6m Bruto/Hora | versión bruto |
