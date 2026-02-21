"""Estructura REORGANIZADA de la sheet Ingresos - Feb 2026."""

# Row 1: Group headers (con merged ranges)
INCOME_GROUPS = [
    ("A", "A", ""),  # Fecha
    ("B", "F", "SUELDO"),
    ("G", "H", "AGUINALDO"),
    ("I", "I", "BONOS"),
    ("J", "K", "BENEFICIOS"),
    ("L", "L", "TOTAL"),
    ("M", "P", "INFLACIÓN (CER)"),
    ("Q", "T", "VS ÚLTIMO AUMENTO"),
    ("U", "V", "ANÁLISIS TOTAL"),
    ("W", "AB", "PROYECCIONES REM"),
    ("AC", "AG", "DÓLARES (CCL)"),
    ("AH", "AJ", "VS ÚLTIMO AUMENTO USD"),
]

# Row 2: Column headers con fórmulas
# {r} = número de fila actual, {r-1} = fila anterior
INCOME_COLUMNS = [
    # GRUPO 1: DATOS BASE & INGRESOS (A-L)
    ("A", "Fecha", None),
    ("B", "Bruto", None),
    (
        "C",
        "Jubilacion",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", ROUND(B{r}*impuestos!$B$2,0))',
    ),
    ("D", "PAMI", '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", ROUND(B{r}*impuestos!$B$3,0))'),
    (
        "E",
        "Obra Social",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", ROUND(B{r}*impuestos!$B$4,0))',
    ),
    ("F", "Neto", '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", B{r}-C{r}-D{r}-E{r})'),
    ("G", "SAC Bruto", None),
    (
        "H",
        "SAC Neto",
        '=IF(OR(ISBLANK(G{r}), G{r}=0), "-", G{r}-ROUND(G{r}*impuestos!$B$2,0)-ROUND(G{r}*impuestos!$B$3,0)-ROUND(G{r}*impuestos!$B$4,0))',
    ),
    ("I", "Bono Neto", None),
    ("J", "Comida", None),
    ("K", "Otros Beneficios", None),
    (
        "L",
        "Total Neto",
        '=IF(OR(ISBLANK(F{r}), F{r}="-"), "-", IFERROR(IF(SUM(F{r}:K{r})=0, "-", SUM(F{r}:K{r})), "-"))',
    ),
    # GRUPO 2: INFLACIÓN / CER (M-P)
    (
        "M",
        "Δ% CER MoM",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", IFERROR((VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(A{r-1}, historic_data!$A$4:$B, 2, TRUE)) - 1, "-"))',
    ),
    (
        "N",
        "Δ Sueldo MoM",
        '=IF(OR(ISBLANK(B{r}), B{r}=0, ISBLANK(B{r-1})), "-", IFERROR(F{r}/F{r-1}-1,"-"))',
    ),
    (
        "O",
        "Poder Adq. MoM",
        '=IF(OR(M{r}="-", N{r}="-"), "-", IFERROR((1+N{r})/(1+M{r})-1,"-"))',
    ),
    (
        "P",
        "Poder Adq. Acum.",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", IFERROR((F{r}/$F$3) / (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP($A$3, historic_data!$A$4:$B, 2, TRUE)) - 1, "-"))',
    ),
    # GRUPO 3: VS ÚLTIMO AUMENTO (Q-T)
    (
        "Q",
        "Bruto Base",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", IF(OR(ROW(B{r})=3, B{r}<>B{r-1}), B{r}, Q{r-1}))',
    ),
    (
        "R",
        "CER Base",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", IF(OR(ROW(B{r})=3, B{r}<>B{r-1}), VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE), R{r-1}))',
    ),
    (
        "S",
        "Atraso Real ARS",
        '=IF(OR(ISBLANK(B{r}), B{r}=0, R{r}="-"), "-", IFERROR((B{r}/Q{r}) / (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE)/R{r}) - 1, "-"))',
    ),
    (
        "T",
        "Paridad CER",
        '=IF(OR(ISBLANK(B{r}), B{r}=0, R{r}="-"), "-", IFERROR(Q{r} * (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE)/R{r}), "-"))',
    ),
    # GRUPO 4: ANÁLISIS TOTAL (U-V)
    (
        "U",
        "Ingreso a Valor Hoy",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", IFERROR(F{r} * (INDEX(historic_data!$B$4:$B, MATCH(9.9E+307, historic_data!$B$4:$B)) / VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE)), "-"))',
    ),
    (
        "V",
        "Δ Real vs Año Ant.",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", IFERROR((F{r} / VLOOKUP(EDATE(A{r},-12), $A:$F, 6, FALSE)) / (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(EDATE(A{r},-12), historic_data!$A$4:$B, 2, TRUE)) - 1, "-"))',
    ),
    # GRUPO 5: PROYECCIONES REM (W-AB)
    (
        "W",
        "REM 3m (%)",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", (1+IFERROR(VLOOKUP($A{r}, REM!$A$4:$I, 3, FALSE), 0))*(1+IFERROR(VLOOKUP($A{r}, REM!$A$4:$I, 4, FALSE), 0))*(1+IFERROR(VLOOKUP($A{r}, REM!$A$4:$I, 5, FALSE), 0))-1)',
    ),
    ("X", "Objetivo 3m", '=IF(W{r}="-", "-", IFERROR(B{r} * (1+W{r}), "-"))'),
    ("Y", "Δ 3m (%)", "=W{r}"),
    (
        "Z",
        "REM 6m (%)",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", (1+W{r})*(1+IFERROR(VLOOKUP($A{r}, REM!$A$4:$I, 6, FALSE), 0))*(1+IFERROR(VLOOKUP($A{r}, REM!$A$4:$I, 7, FALSE), 0))*(1+IFERROR(VLOOKUP($A{r}, REM!$A$4:$I, 8, FALSE), 0))-1)',
    ),
    ("AA", "Objetivo 6m", '=IF(Z{r}="-", "-", IFERROR(B{r} * (1+Z{r}), "-"))'),
    ("AB", "Δ 6m (%)", "=Z{r}"),
    # GRUPO 6: DÓLARES / USD (AC-AG)
    (
        "AC",
        "CCL",
        '=IF(OR(ISBLANK(B{r}), B{r}=0), "-", IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(A{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-"))',
    ),
    (
        "AD",
        "Δ % CCL MoM",
        '=IF(OR(AC{r}="-", AC{r-1}="-"), "-", IFERROR((AC{r}-AC{r-1})/AC{r-1}, "-"))',
    ),
    ("AE", "Sueldo USD", '=IF(OR(F{r}="-", AC{r}="-"), "-", IFERROR(F{r}/AC{r},"-"))'),
    (
        "AF",
        "Poder Adq. MoM (USD)",
        '=IF(OR(AE{r}="-", AE{r-1}="-"), "-", IFERROR((AE{r}/AE{r-1})-1, "-"))',
    ),
    (
        "AG",
        "Poder Adq. Acum. (USD)",
        '=IF(AE{r}="-", "-", IFERROR((AE{r}/$AE$3)-1, "-"))',
    ),
    # GRUPO 7: VS ÚLTIMO AUMENTO USD (AH-AJ)
    (
        "AH",
        "Atraso USD",
        '=IF(OR(AE{r}="-", ISBLANK(B{r})), "-", IFERROR((AE{r} / INDEX($AE:$AE, MAX(IF($B$3:B{r}<>$B$2:B{r-1}, ROW($B$3:B{r}))))) - 1, "-"))',
    ),
    (
        "AI",
        "Paridad USD",
        '=IF(OR(Q{r}="-", AC{r}="-"), "-", IFERROR(Q{r} * (AC{r} / INDEX($AC:$AC, MAX(IF($B$3:B{r}<>$B$2:B{r-1}, ROW($B$3:B{r}))))), "-"))',
    ),
    (
        "AJ",
        "Gap USD ($)",
        '=IF(OR(AI{r}="-", B{r}=0), "-", IFERROR(AI{r} - B{r}, "-"))',
    ),
]

# Formatos por columna
COLUMN_FORMATS = {
    "A": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "B": {"type": "CURRENCY", "pattern": "$#,##0"},
    "C": {"type": "CURRENCY", "pattern": "$#,##0"},
    "D": {"type": "CURRENCY", "pattern": "$#,##0"},
    "E": {"type": "CURRENCY", "pattern": "$#,##0"},
    "F": {"type": "CURRENCY", "pattern": "$#,##0"},
    "G": {"type": "CURRENCY", "pattern": "$#,##0"},
    "H": {"type": "CURRENCY", "pattern": "$#,##0"},
    "I": {"type": "CURRENCY", "pattern": "$#,##0"},
    "J": {"type": "CURRENCY", "pattern": "$#,##0"},
    "K": {"type": "CURRENCY", "pattern": "$#,##0"},
    "L": {"type": "CURRENCY", "pattern": "$#,##0"},
    "M": {"type": "PERCENT", "pattern": "0.00%"},
    "N": {"type": "PERCENT", "pattern": "0.00%"},
    "O": {"type": "PERCENT", "pattern": "0.00%"},
    "P": {"type": "PERCENT", "pattern": "0.00%"},
    "Q": {"type": "NUMBER", "pattern": "#,##0"},
    "R": {"type": "NUMBER", "pattern": "0.0000"},
    "S": {"type": "PERCENT", "pattern": "0.00%"},
    "T": {"type": "CURRENCY", "pattern": "$#,##0"},
    "U": {"type": "CURRENCY", "pattern": "$#,##0"},
    "V": {"type": "PERCENT", "pattern": "0.00%"},
    "W": {"type": "PERCENT", "pattern": "0.00%"},
    "X": {"type": "CURRENCY", "pattern": "$#,##0"},
    "Y": {"type": "PERCENT", "pattern": "0.00%"},
    "Z": {"type": "PERCENT", "pattern": "0.00%"},
    "AA": {"type": "CURRENCY", "pattern": "$#,##0"},
    "AB": {"type": "PERCENT", "pattern": "0.00%"},
    "AC": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "AD": {"type": "PERCENT", "pattern": "0.00%"},
    "AE": {"type": "NUMBER", "pattern": "#,##0.00"},
    "AF": {"type": "PERCENT", "pattern": "0.00%"},
    "AG": {"type": "PERCENT", "pattern": "0.00%"},
    "AH": {"type": "PERCENT", "pattern": "0.00%"},
    "AI": {"type": "CURRENCY", "pattern": "$#,##0"},
    "AJ": {"type": "CURRENCY", "pattern": "$#,##0"},
}

COLUMN_DESCRIPTIONS = {
    "A": "Fecha del registro mensual",
    "B": "Sueldo bruto mensual (input manual)",
    "C": "Descuento jubilación (11% del bruto)",
    "D": "Descuento PAMI (3% del bruto)",
    "E": "Descuento obra social (3% del bruto)",
    "F": "Sueldo neto (bruto - descuentos)",
    "G": "Aguinaldo bruto (input manual)",
    "H": "Aguinaldo neto (SAC - descuentos)",
    "I": "Bonos extraordinarios netos (input manual)",
    "J": "Beneficio de comida mensual (input manual)",
    "K": "Otros beneficios (input manual)",
    "L": "Total neto mensual (suma de todo)",
    "M": "Inflación del mes (CER)",
    "N": "Variación nominal de sueldo neto",
    "O": "Poder adquisitivo ganado/perdido en el mes",
    "P": "Poder adquisitivo acumulado desde el inicio (Neto vs CER)",
    "Q": "Bruto al momento del último aumento",
    "R": "Valor CER al momento del último aumento",
    "S": "% de atraso real vs inflación desde último aumento",
    "T": "Sueldo para mantener paridad CER",
    "U": "Sueldo Neto llevado a valor de hoy por inflación",
    "V": "Crecimiento real interanual móvil (Neto vs CER)",
    "W": "Inflación proyectada REM 3m",
    "X": "Sueldo bruto objetivo para dentro de 3 meses",
    "Y": "% de aumento sugerido hoy para cubrir los próximos 3 meses",
    "Z": "Inflación proyectada REM 6m",
    "AA": "Sueldo bruto objetivo para dentro de 6 meses",
    "AB": "% de aumento sugerido hoy para cubrir los próximos 6 meses",
    "AC": "Dólar CCL cierre de mes",
    "AD": "Variación % CCL MoM",
    "AE": "Sueldo Neto en USD CCL",
    "AF": "Poder adquisitivo ganado/perdido en dólares (MoM)",
    "AG": "Poder adquisitivo acumulado en dólares desde inicio",
    "AH": "% de caída/subida en USD desde último aumento",
    "AI": "Sueldo en pesos necesario hoy para recuperar los mismos dólares que el día del aumento",
    "AJ": "Diferencia en pesos (AI - B) que falta ganar para recuperar tu valor en dólares original",
}

IMPUESTOS_ROWS = [
    ("Jubilacion", 0.11, "Ley 24241"),
    ("PAMI", 0.03, "Ley 19032"),
    ("Obra Social", 0.03, "Ley 23660"),
    ("Otro", 0.00, "—"),
]

HISTORIC_VARIABLES = [
    (None, "Fecha", None),
    (30, "CER", "CER"),
    ("IOL/dolarapi", "CCL", "CCL"),
]
