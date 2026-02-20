"""Estructura REORGANIZADA de la sheet Ingresos - Feb 2026."""

# Row 1: Group headers (con merged ranges)
INCOME_GROUPS = [
    ("A", "A", ""),  # Fecha
    ("B", "F", "SUELDO"),
    ("G", "H", "AGUINALDO"),
    ("I", "I", "BONOS"),
    ("J", "K", "BENEFICIOS"),
    ("L", "L", "TOTAL"),
    ("M", "O", "INFLACIÓN (CER)"),
    ("P", "S", "VS ÚLTIMO AUMENTO"),
    ("T", "U", "ANÁLISIS TOTAL"),
    ("V", "AA", "PROYECCIONES REM"),
    ("AB", "AD", "DÓLARES (CCL)"),
    ("AE", "AG", "VS ÚLTIMO AUMENTO USD"),
]

# Row 2: Column headers con fórmulas
# Formato: (columna, header, formula_template)
# {r} = número de fila actual, {r-1} = fila anterior
INCOME_COLUMNS = [
    # GRUPO 1: DATOS BASE & INGRESOS (A-L)
    ("A", "Fecha", None),
    ("B", "Bruto", None),
    ("C", "Jubilacion", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$2,0))'),
    ("D", "PAMI", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$3,0))'),
    ("E", "Obra Social", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$4,0))'),
    ("F", "Neto", '=IF(ISBLANK(B{r}),"",B{r}-C{r}-D{r}-E{r})'),
    ("G", "SAC Bruto", None),
    ("H", "SAC Neto", '=IF(ISBLANK(G{r}),"",G{r}-ROUND(G{r}*impuestos!$B$2,0)-ROUND(G{r}*impuestos!$B$3,0)-ROUND(G{r}*impuestos!$B$4,0))'),
    ("I", "Bono Neto", None),
    ("J", "Comida", None),
    ("K", "Otros Beneficios", None),
    ("L", "Total Neto", '=IFERROR(IF(SUM(F{r}:K{r})=0, "", SUM(F{r}:K{r})), "")'),

    # GRUPO 2: INFLACIÓN / CER (M-AA)
    # Deltas mensuales
    ("M", "Δ% CER MoM", '=IFERROR((VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(A{r-1}, historic_data!$A$4:$B, 2, TRUE)) - 1, "-")'),
    ("N", "Δ Sueldo MoM", '=IFERROR(F{r}/F{r-1}-1,"-")'),
    ("O", "Poder Adq. MoM", '=IFERROR((1+N{r})/(1+M{r})-1,"-")'),

    # VS Último Aumento
    ("P", "Bruto Base", '=IF(OR(ROW(B{r})=3, B{r}<>B{r-1}), B{r}, P{r-1})'),
    ("Q", "CER Base", '=IF(OR(ROW(B{r})=3, B{r}<>B{r-1}), VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE), Q{r-1})'),
    ("R", "Atraso Real ARS", '=IFERROR((B{r}/P{r}) / (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE)/Q{r}) - 1, "")'),
    ("S", "Paridad CER", '=IFERROR(P{r} * (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE)/Q{r}), "")'),

    # Análisis Total
    ("T", "Sueldo Ajustado CER", '=IFERROR(L{r} * (VLOOKUP($A$3, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE)), "")'),
    ("U", "Aum. Real Total", '=IFERROR((B{r}/$B$3) / (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE)/VLOOKUP($A$3, historic_data!$A$4:$B, 2, TRUE)) - 1, "")'),

    # Proyecciones REM
    ("V", "REM 3m (%)", '=(1+IFERROR(VLOOKUP(EDATE($A{r}, 1), REM!$A$4:$B, 2, FALSE), 0))*(1+IFERROR(VLOOKUP(EDATE($A{r}, 2), REM!$A$4:$B, 2, FALSE), 0))*(1+IFERROR(VLOOKUP(EDATE($A{r}, 3), REM!$A$4:$B, 2, FALSE), 0))-1'),
    ("W", "Objetivo 3m", '=IFERROR(B{r} * (1+V{r}), "")'),
    ("X", "Δ 3m ($)", '=IFERROR(W{r} - B{r}, "")'),
    ("Y", "REM 6m (%)", '=(1+V{r})*(1+IFERROR(VLOOKUP(EDATE($A{r}, 4), REM!$A$4:$B, 2, FALSE), 0))*(1+IFERROR(VLOOKUP(EDATE($A{r}, 5), REM!$A$4:$B, 2, FALSE), 0))*(1+IFERROR(VLOOKUP(EDATE($A{r}, 6), REM!$A$4:$B, 2, FALSE), 0))-1'),
    ("Z", "Objetivo 6m", '=IFERROR(B{r} * (1+Y{r}), "")'),
    ("AA", "Δ 6m ($)", '=IFERROR(Z{r} - B{r}, "")'),

    # GRUPO 3: DÓLARES / USD (AB-AG)
    ("AB", "CCL", '=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(A{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "")'),
    ("AC", "Delta % CCL MoM", '=IFERROR((AB{r}-AB{r-1})/AB{r-1}, "-")'),
    ("AD", "Sueldo USD", '=IFERROR(L{r}/AB{r},"")'),
    ("AE", "Delta Sueldo USD MoM", '=IFERROR((AD{r}/AD{r-1})-1, "-")'),
    ("AF", "Atraso USD", '=IFERROR((AD{r} / INDEX($AD:$AD, MAX(IF($B$3:B{r}<>$B$2:B{r-1}, ROW($B$3:B{r}))))) - 1, "")'),
    ("AG", "Paridad USD", '=IFERROR(P{r} * (AB{r} / INDEX($AB:$AB, MAX(IF($B$3:B{r}<>$B$2:B{r-1}, ROW($B$3:B{r}))))), "")'),
]

# Formatos por columna
COLUMN_FORMATS = {
    # Fecha
    "A": {"type": "DATE", "pattern": "dd/mm/yyyy"},

    # Moneda - Ingresos
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

    # CER/Inflación
    "M": {"type": "PERCENT", "pattern": "0.00%"},   # Delta CER MoM
    "N": {"type": "PERCENT", "pattern": "0.00%"},   # Delta Sueldo MoM
    "O": {"type": "PERCENT", "pattern": "0.00%"},   # Poder Adq. MoM
    "P": {"type": "NUMBER", "pattern": "#,##0"},    # Bruto Base
    "Q": {"type": "NUMBER", "pattern": "0.0000"},   # CER Base
    "R": {"type": "PERCENT", "pattern": "0.00%"},   # Atraso Real ARS
    "S": {"type": "CURRENCY", "pattern": "$#,##0"}, # Paridad CER
    "T": {"type": "CURRENCY", "pattern": "$#,##0"}, # Sueldo Ajustado CER
    "U": {"type": "PERCENT", "pattern": "0.00%"},   # Aum. Real Total
    "V": {"type": "PERCENT", "pattern": "0.00%"},   # REM 3m
    "W": {"type": "CURRENCY", "pattern": "$#,##0"}, # Objetivo 3m
    "X": {"type": "CURRENCY", "pattern": "$#,##0"}, # Delta 3m
    "Y": {"type": "PERCENT", "pattern": "0.00%"},   # REM 6m
    "Z": {"type": "CURRENCY", "pattern": "$#,##0"}, # Objetivo 6m
    "AA": {"type": "CURRENCY", "pattern": "$#,##0"},# Delta 6m

    # Dólares
    "AB": {"type": "CURRENCY", "pattern": "$#,##0.00"}, # CCL
    "AC": {"type": "PERCENT", "pattern": "0.00%"},      # Delta CCL MoM
    "AD": {"type": "NUMBER", "pattern": "#,##0.00"},    # Sueldo USD
    "AE": {"type": "PERCENT", "pattern": "0.00%"},      # Delta Sueldo USD MoM
    "AF": {"type": "PERCENT", "pattern": "0.00%"},      # Atraso USD
    "AG": {"type": "CURRENCY", "pattern": "$#,##0"},    # Paridad USD
}

# Descripción de cada columna (para documentación)
COLUMN_DESCRIPTIONS = {
    # INGRESOS
    "A": "Fecha del registro mensual",
    "B": "Sueldo bruto mensual (input manual)",
    "C": "Descuento jubilación (11% del bruto)",
    "D": "Descuento PAMI (3% del bruto)",
    "E": "Descuento obra social (3% del bruto)",
    "F": "Sueldo neto (bruto - descuentos)",
    "G": "Aguinaldo bruto (input manual, 2 veces al año)",
    "H": "Aguinaldo neto (SAC - descuentos 17%)",
    "I": "Bonos extraordinarios netos (input manual)",
    "J": "Beneficio de comida mensual (input manual)",
    "K": "Otros beneficios (input manual)",
    "L": "Total neto mensual (suma de todo)",

    # CER/INFLACIÓN
    "M": "Inflación del mes (variación CER mes a mes)",
    "N": "Aumento de sueldo nominal del mes",
    "O": "Poder adquisitivo real (si ganaste/perdiste vs inflación)",
    "P": "Sueldo bruto del último aumento",
    "Q": "Valor CER del último aumento",
    "R": "% atrasado vs inflación desde último aumento",
    "S": "Sueldo que deberías tener para mantener paridad con CER",
    "T": "Sueldo base ajustado por inflación total",
    "U": "Aumento real total desde inicio (descontando inflación)",
    "V": "Inflación proyectada próximos 3 meses (REM)",
    "W": "Sueldo objetivo en 3 meses para mantener poder adquisitivo",
    "X": "Diferencia en pesos a negociar (3 meses)",
    "Y": "Inflación proyectada próximos 6 meses (REM)",
    "Z": "Sueldo objetivo en 6 meses",
    "AA": "Diferencia en pesos a negociar (6 meses)",

    # DÓLARES
    "AB": "Cotización dólar CCL del día",
    "AC": "Variación % CCL vs mes anterior",
    "AD": "Total neto convertido a dólares CCL",
    "AE": "Variación % sueldo USD vs mes anterior",
    "AF": "% atrasado en USD vs último aumento",
    "AG": "Sueldo en pesos para mantener paridad USD",
}

# Impuestos sheet (sin cambios)
IMPUESTOS_ROWS = [
    ("Jubilacion", 0.11, "Ley 24241"),
    ("PAMI", 0.03, "Ley 19032"),
    ("Obra Social", 0.03, "Ley 23660"),
    ("Otro", 0.00, "—"),
]

# Historic data (sin cambios)
HISTORIC_VARIABLES = [
    (None, "Fecha", None),
    (30, "CER", "CER"),  # BCRA var 30
    ("IOL/dolarapi", "CCL", "CCL"),
]
