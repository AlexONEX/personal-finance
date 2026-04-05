# Resumen de Estructura - Análisis ARS y USD

**Fecha:** 2026-04-05
**Status:** FINAL - Listo para implementar

Este documento contiene la estructura final de columnas con fórmulas simplificadas (sin ARRAYFORMULA) listas para implementar.

---

## ANÁLISIS ARS - 24 columnas

### Configuración de Grupos (Row 1)
```python
ANALISIS_ARS_GROUPS = [
    ("A", "A", "PERIODO"),
    ("B", "D", "SUELDO"),
    ("E", "J", "VS ÚLTIMO AUMENTO (CER)"),
    ("K", "M", "VS ÚLTIMO AUMENTO (INDEC)"),  # K_BASE estará oculta entre K y L
    ("N", "Q", "VARIACIÓN MENSUAL"),
    ("R", "W", "PROYECCIÓN REM"),
]
```

### Columnas con Fórmulas (Row 3 para fila inicial, Row 4+ para siguientes)

```python
ANALISIS_ARS_COLUMNS = [
    # PERIODO
    ("A", "Periodo", '=IF(Ingresos!B3<>"", Ingresos!A3, "")'),

    # SUELDO
    ("B", "Fecha", '=IF(Ingresos!B3<>"", Ingresos!B3, "")'),
    ("C", "Bruto/Hora", '=IF(Ingresos!B3<>"", Ingresos!O3, "")'),
    ("D", "Neto/Hora", '=IF(Ingresos!B3<>"", Ingresos!P3, "")'),

    # VS ÚLTIMO AUMENTO (CER)
    ("E", "Bruto/Hora Base", {
        "row_3": '=IF(C3="", "", C3)',
        "row_4_plus": '=IF(C4="", "", IF(Ingresos!Q4=TRUE, C4, E3))'
    }),
    ("F", "Neto/Hora Base", {
        "row_3": '=IF(D3="", "", D3)',
        "row_4_plus": '=IF(D4="", "", IF(Ingresos!Q4=TRUE, D4, F3))'
    }),
    ("G", "CER Base", {
        "row_3": '=IF(B3="", "", IFERROR(VLOOKUP(EOMONTH(B3,1)+15, historic_data!$A$4:$B, 2, TRUE), 0))',
        "row_4_plus": '=IF(B4="", "", IF(Ingresos!Q4=TRUE, IFERROR(VLOOKUP(EOMONTH(B4,1)+15, historic_data!$A$4:$B, 2, TRUE), 0), G3))'
    }),
    ("H", "Paridad CER (Bruto/Hora)",
        '=IF(OR(B3="", C3="", E3="", G3=0), "", LET(d, EOMONTH(B3,1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", E3 * (cer/G3))))'
    ),
    ("I", "Paridad CER (Neto/Hora)",
        '=IF(OR(B3="", D3="", F3="", G3=0), "", LET(d, EOMONTH(B3,1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", F3 * (cer/G3))))'
    ),
    ("J", "Poder Adq vs Aumento (CER)",
        '=IF(OR(B3="", D3="", F3="", G3=0), "", LET(d, EOMONTH(B3,1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", (D3/F3) / (cer/G3) - 1)))'
    ),

    # VS ÚLTIMO AUMENTO (INDEC)
    ("K", "Índice INDEC Actual", {
        "row_3": '=IF(B3="", "", LET(mes, DATE(YEAR(B3), MONTH(B3), 1), infl, IFERROR(VLOOKUP(VALUE(mes), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$C$4:$C}), 2, FALSE), 0), 100 * (1 + infl/100)))',
        "row_4_plus": '=IF(B4="", "", LET(mes, DATE(YEAR(B4), MONTH(B4), 1), infl, IFERROR(VLOOKUP(VALUE(mes), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$C$4:$C}), 2, FALSE), 0), K3 * (1 + infl/100)))'
    }),

    # COLUMNA AUXILIAR - OCULTAR VISUALMENTE
    ("K_BASE", "INDEC Base (AUX)", {
        "row_3": '=IF(K3="", "", K3)',
        "row_4_plus": '=IF(K4="", "", IF(Ingresos!Q4=TRUE, K4, K_BASE3))',
        "hidden": True
    }),

    ("L", "Poder Adq vs REM (%)", '=IF(D3="", "", 0)'),  # TODO
    ("M", "Poder Adq vs INDEC (%)", {
        "row_3": '=IF(OR(D3="", F3="", K3="", K_BASE3=""), "", 0)',
        "row_4_plus": '=IF(OR(D4="", F4="", K4="", K_BASE4=""), "", (D4/F4) / (K4/K_BASE4) - 1)'
    }),

    # VARIACIÓN MENSUAL
    ("N", "Δ% CER MoM", {
        "row_3": '=IF(B3="", "", "")',
        "row_4_plus": '=IF(B4="", "", LET(d_act, EOMONTH(B4,1)+15, d_ant, EOMONTH(B3,1)+15, cer_act, IFERROR(VLOOKUP(d_act, historic_data!$A$4:$B, 2, TRUE), 0), cer_ant, IFERROR(VLOOKUP(d_ant, historic_data!$A$4:$B, 2, TRUE), 0), IF(OR(cer_act=0, cer_ant=0), "", (cer_act/cer_ant)-1)))'
    }),
    ("O", "Δ% $/Hora vs CER Acum",
        '=IF(OR(B3="", C3="", E3="", G3=0), "", LET(d, EOMONTH(B3,1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", (C3/E3) / (cer/G3) - 1)))'
    ),
    ("P", "CER Actual",
        '=IF(B3="", "", LET(d, EOMONTH(B3,1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", cer)))'
    ),
    ("Q", "CER Base", '=IF(B3="", "", G3)'),

    # PROYECCIÓN REM
    ("R", "REM 3m (%)",
        '=IF(OR(B3="", C3=""), "", LET(f, EOMONTH(B3,-1)+1, i1, IFERROR(VLOOKUP(f, REM!$A$4:$I, 3, TRUE), 0), i2, IFERROR(VLOOKUP(f, REM!$A$4:$I, 4, TRUE), 0), i3, IFERROR(VLOOKUP(f, REM!$A$4:$I, 5, TRUE), 0), (1+i1)*(1+i2)*(1+i3)-1))'
    ),
    ("S", "Objetivo 3m Bruto/Hora", '=IF(OR(B3="", C3="", R3=""), "", C3 * (1+R3))'),
    ("T", "Objetivo 3m Neto/Hora", '=IF(OR(B3="", D3="", R3=""), "", D3 * (1+R3))'),
    ("U", "REM 6m (%)",
        '=IF(OR(B3="", C3="", R3=""), "", LET(f, EOMONTH(B3,-1)+1, i4, IFERROR(VLOOKUP(f, REM!$A$4:$I, 6, TRUE), 0), i5, IFERROR(VLOOKUP(f, REM!$A$4:$I, 7, TRUE), 0), i6, IFERROR(VLOOKUP(f, REM!$A$4:$I, 8, TRUE), 0), (1+R3)*(1+i4)*(1+i5)*(1+i6)-1))'
    ),
    ("V", "Objetivo 6m Bruto/Hora", '=IF(OR(B3="", C3="", U3=""), "", C3 * (1+U3))'),
    ("W", "Objetivo 6m Neto/Hora", '=IF(OR(B3="", D3="", U3=""), "", D3 * (1+U3))'),
]
```

### Formatos de Número

```python
ANALISIS_ARS_FORMATS = {
    "A": {"type": "TEXT", "pattern": "mmmm yyyy"},
    "B": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "C": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "D": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "E": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "F": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "G": {"type": "NUMBER", "pattern": "0.0000"},
    "H": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "I": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "J": {"type": "PERCENT", "pattern": "0.00%"},
    "K": {"type": "NUMBER", "pattern": "0.00"},
    "K_BASE": {"type": "NUMBER", "pattern": "0.00"},  # OCULTA
    "L": {"type": "PERCENT", "pattern": "0.00%"},
    "M": {"type": "PERCENT", "pattern": "0.00%"},
    "N": {"type": "PERCENT", "pattern": "0.00%"},
    "O": {"type": "PERCENT", "pattern": "0.00%"},
    "P": {"type": "NUMBER", "pattern": "0.0000"},
    "Q": {"type": "NUMBER", "pattern": "0.0000"},
    "R": {"type": "PERCENT", "pattern": "0.00%"},
    "S": {"type": "CURRENCY", "pattern": "$#,##0"},
    "T": {"type": "CURRENCY", "pattern": "$#,##0"},
    "U": {"type": "PERCENT", "pattern": "0.00%"},
    "V": {"type": "CURRENCY", "pattern": "$#,##0"},
    "W": {"type": "CURRENCY", "pattern": "$#,##0"},
}
```

---

## ANÁLISIS USD - 16 columnas

### Configuración de Grupos (Row 1)
```python
ANALISIS_USD_GROUPS = [
    ("A", "A", "PERIODO"),
    ("B", "D", "SUELDO ARS"),
    ("E", "H", "SUELDO USD NOMINAL"),
    ("I", "L", "SUELDO USD REAL"),
    ("M", "P", "VS ÚLTIMO AUMENTO"),
]
```

### Columnas con Fórmulas

```python
ANALISIS_USD_COLUMNS = [
    # PERIODO
    ("A", "Periodo", '=IF(Ingresos!B3<>"", Ingresos!A3, "")'),

    # SUELDO ARS
    ("B", "Fecha", '=IF(Ingresos!B3<>"", Ingresos!B3, "")'),
    ("C", "Bruto ARS", '=IF(Ingresos!B3<>"", Ingresos!C3, "")'),
    ("D", "Neto ARS", '=IF(Ingresos!B3<>"", Ingresos!G3, "")'),

    # SUELDO USD NOMINAL
    ("E", "CCL", '=IF(B3="", "", IFERROR(LOOKUP(B3, historic_data!$A$4:$A, historic_data!$C$4:$C), ""))'),
    ("F", "Δ% CCL MoM", {
        "row_3": '=""',
        "row_4_plus": '=IF(E4="", "", IFERROR((E4 - LOOKUP(EOMONTH(B4,-1), historic_data!$A$4:$A, historic_data!$C$4:$C)) / LOOKUP(EOMONTH(B4,-1), historic_data!$A$4:$A, historic_data!$C$4:$C), ""))'
    }),
    ("G", "Bruto USD", '=IF(OR(B3="", C3="", E3=""), "", C3/E3)'),
    ("H", "Neto USD", '=IF(OR(B3="", D3="", E3=""), "", D3/E3)'),

    # SUELDO USD REAL
    ("I", "CER", '=IF(B3="", "", LET(d, EOMONTH(B3,1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", cer)))'),
    ("J", "CCL Real", '=IF(OR(B3="", E3="", I3="", I$3=""), "", E3 * (I$3 / I3))'),
    ("K", "Bruto USD Real", '=IF(OR(B3="", C3="", J3=""), "", C3/J3)'),
    ("L", "Neto USD Real", '=IF(OR(B3="", D3="", J3=""), "", D3/J3)'),

    # VS ÚLTIMO AUMENTO
    ("M", "CCL Base", {
        "row_3": '=IF(E3="", "", E3)',
        "row_4_plus": '=IF(E4="", "", IF(Ingresos!Q4=TRUE, E4, M3))'
    }),
    ("N", "Bruto USD Base", {
        "row_3": '=IF(G3="", "", G3)',
        "row_4_plus": '=IF(G4="", "", IF(Ingresos!Q4=TRUE, G4, N3))'
    }),
    ("O", "Neto USD Base", {
        "row_3": '=IF(H3="", "", H3)',
        "row_4_plus": '=IF(H4="", "", IF(Ingresos!Q4=TRUE, H4, O3))'
    }),
    ("P", "Variación USD (%)", '=IF(OR(B3="", H3="", O3=""), "", (H3/O3)-1)'),
]
```

### Formatos de Número

```python
ANALISIS_USD_FORMATS = {
    "A": {"type": "TEXT", "pattern": "mmmm yyyy"},
    "B": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "C": {"type": "CURRENCY", "pattern": "$#,##0"},
    "D": {"type": "CURRENCY", "pattern": "$#,##0"},
    "E": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "F": {"type": "PERCENT", "pattern": "0.00%"},
    "G": {"type": "NUMBER", "pattern": "#,##0.00"},
    "H": {"type": "NUMBER", "pattern": "#,##0.00"},
    "I": {"type": "NUMBER", "pattern": "0.0000"},
    "J": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "K": {"type": "NUMBER", "pattern": "#,##0.00"},
    "L": {"type": "NUMBER", "pattern": "#,##0.00"},
    "M": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "N": {"type": "NUMBER", "pattern": "#,##0.00"},
    "O": {"type": "NUMBER", "pattern": "#,##0.00"},
    "P": {"type": "PERCENT", "pattern": "0.00%"},
}
```

---

## NOTAS DE IMPLEMENTACIÓN

### 1. Columnas con Fórmulas Variables
Algunas columnas tienen fórmulas diferentes para fila 3 vs fila 4+. En el código Python:

```python
if isinstance(formula, dict):
    if "row_3" in formula:
        # Primera fila de datos (row 3)
        formula_3 = formula["row_3"]
    if "row_4_plus" in formula:
        # Copiar formula_4_plus a celdas 4 en adelante
        formula_4_plus = formula["row_4_plus"]
```

### 2. Columna Auxiliar K_BASE
- Se inserta después de columna K
- Debe marcarse como oculta: `{"hidden": True}`
- En la implementación, agregar request para ocultar esta columna

### 3. Orden de Operaciones
1. Crear headers (rows 1-2)
2. Limpiar datos viejos (row 3+)
3. Insertar fórmulas row 3
4. Copiar fórmulas row 4+ (para columnas con variantes)
5. Aplicar formatos de número
6. Aplicar colores de grupos
7. Ocultar columna K_BASE

### 4. Referencias entre Sheets
- `Ingresos!` - Sheet principal de sueldos
- `historic_data!` - CER, CCL, SPY históricos
- `CPI!` - Inflación mensual (IPC Nacional y CABA)
- `REM!` - Relevamiento de Expectativas de Mercado
- `'Análisis ARS'!` - Solo en Análisis USD columna P

### 5. Funciones Críticas
- `EOMONTH(fecha, meses)` - Último día del mes ± meses
- `VLOOKUP(valor, rango, columna, TRUE/FALSE)` - Búsqueda exacta o aproximada
- `LOOKUP(valor, rango_busqueda, rango_resultado)` - Último valor ≤ buscado
- `LET(var1, val1, ..., expresión)` - Variables temporales
- `VALUE(fecha)` - Convertir fecha a número para VLOOKUP
- `ARRAYFORMULA({...})` - Solo en casos específicos (CPI matching)

---

## CHECKLIST DE VALIDACIÓN

### Pre-implementación
- [ ] Backup del spreadsheet actual
- [ ] Documentar estructura actual
- [ ] Crear sheet de testing

### Durante implementación
- [ ] Crear columnas A-W en Análisis ARS
- [ ] Crear columnas A-P en Análisis USD
- [ ] Insertar fórmulas row 3
- [ ] Copiar fórmulas row 4+ donde corresponda
- [ ] Ocultar columna K_BASE
- [ ] Aplicar formatos de número
- [ ] Aplicar colores de grupos

### Post-implementación
- [ ] Validar fila 3 (Oct 2023) contra cálculo manual
- [ ] Validar fila 15 (Dic 2024 - primer ascenso)
- [ ] Validar fila 23 (Ago 2025 - segundo ascenso)
- [ ] Validar fila 30 (Abr 2026 - actual)
- [ ] Verificar que columnas resetean en ascensos
- [ ] Verificar matching CER (día 15 mes M+1)
- [ ] Verificar matching IPC (mes M)
- [ ] Comparar con CALCULO_MANUAL_METRICAS.md

### Optimización futura
- [ ] Convertir a ARRAYFORMULA una vez validadas las fórmulas simples
- [ ] Documentar patrones de ARRAYFORMULA usados
- [ ] Re-validar que ARRAYFORMULA da mismos resultados
