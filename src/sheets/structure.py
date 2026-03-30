"""Estructura de sheets del Ingresos Tracker - Mar 2026."""

from src.config import TAX_RATES

# =============================================================================
# INGRESOS - Tab principal simplificada (solo inputs + totales)
# =============================================================================

INCOME_GROUPS = [
    ("A", "A", "PERIODO"),
    ("B", "G", "SUELDO"),
    ("H", "I", "AGUINALDO"),
    ("J", "J", "BONOS"),
    ("K", "L", "BENEFICIOS"),
    ("M", "M", "TOTAL"),
    ("N", "P", "VALOR/HORA"),
    ("Q", "Q", "ASCENSO"),
]

INCOME_COLUMNS = [
    ("A", "Periodo Abonado", '=TEXT(B{r}, "mmmm yyyy")'),
    ("B", "Fecha", None),
    ("C", "Bruto", None),
    (
        "D",
        "Jubilacion",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", ROUND(C{r}*impuestos!$B$2,0))',
    ),
    ("E", "PAMI", '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", ROUND(C{r}*impuestos!$B$3,0))'),
    (
        "F",
        "Obra Social",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", ROUND(C{r}*impuestos!$B$4,0))',
    ),
    ("G", "Neto", '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", C{r}-D{r}-E{r}-F{r})'),
    ("H", "SAC Bruto", None),
    (
        "I",
        "SAC Neto",
        '=IF(OR(ISBLANK(H{r}), H{r}=0), "-", H{r}-ROUND(H{r}*impuestos!$B$2,0)-ROUND(H{r}*impuestos!$B$3,0)-ROUND(H{r}*impuestos!$B$4,0))',
    ),
    ("J", "Bono Neto", None),
    ("K", "Tarjeta Corporativa", None),
    ("L", "Otros Beneficios", None),
    (
        "M",
        "Total Neto",
        '=IF(OR(ISBLANK(G{r}), G{r}="-"), "-", IFERROR(IF(SUM(G{r}:L{r})=0, "-", SUM(G{r}:L{r})), "-"))',
    ),
    ("N", "Horas Diarias", None),
    (
        "O",
        "Bruto/Hora",
        '=IF(OR(ISBLANK(C{r}), C{r}=0, ISBLANK(N{r}), N{r}=0), "-", ROUND(C{r}/(N{r}*20), 2))',
    ),
    (
        "P",
        "Neto/Hora",
        '=IF(OR(ISBLANK(G{r}), G{r}="-", ISBLANK(N{r}), N{r}=0), "-", ROUND(G{r}/(N{r}*20), 2))',
    ),
    ("Q", "¿Ascenso?", None),
]

COLUMN_FORMATS = {
    "A": {"type": "TEXT", "pattern": "mmmm yyyy"},
    "B": {"type": "DATE", "pattern": "dd/mm/yyyy"},
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
    "M": {"type": "CURRENCY", "pattern": "$#,##0"},
    "N": {"type": "NUMBER", "pattern": "0"},
    "O": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "P": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "Q": {"type": "TEXT", "pattern": "@"},
}

COLUMN_DESCRIPTIONS = {
    "A": "Periodo al que corresponde el sueldo (auto-generado)",
    "B": "Fecha real de cobro",
    "C": "Sueldo bruto mensual (input manual)",
    "D": "Descuento jubilación (11% del bruto)",
    "E": "Descuento PAMI (3% del bruto)",
    "F": "Descuento obra social (3% del bruto)",
    "G": "Sueldo neto (bruto - descuentos)",
    "H": "Aguinaldo bruto (input manual)",
    "I": "Aguinaldo neto (SAC - descuentos)",
    "J": "Bonos extraordinarios netos (input manual)",
    "K": "Tarjeta corporativa mensual (input manual)",
    "L": "Otros beneficios (input manual)",
    "M": "Total neto mensual (suma de todo)",
    "N": "Horas diarias trabajadas (input manual: 7, 8, 9, etc.)",
    "O": "Bruto por hora = Bruto / (Horas * 20 días)",
    "P": "Neto por hora = Neto / (Horas * 20 días)",
}

# =============================================================================
# ANÁLISIS ARS - Sueldo vs Inflación en pesos
# =============================================================================

ANALISIS_ARS_GROUPS = [
    ("A", "A", "PERIODO"),
    ("B", "D", "SUELDO"),
    ("E", "J", "VS ÚLTIMO AUMENTO (CER)"),
    ("K", "L", "VS ÚLTIMO AUMENTO (REM)"),
    ("M", "N", "VARIACIÓN MENSUAL"),
    ("O", "T", "PROYECCIÓN REM"),
]

ANALISIS_ARS_COLUMNS = [
    # Referencia a Ingresos
    ("A", "Periodo", '=Ingresos!A{r}'),
    ("B", "Fecha", '=Ingresos!B{r}'),
    ("C", "Bruto/Hora", '=Ingresos!O{r}'),
    ("D", "Neto/Hora", '=Ingresos!P{r}'),
    # Comparación vs último aumento (CER) - basado en $/hora
    # Resetea baseline cuando Ingresos!Q{r}=TRUE (ascenso real marcado en Ingresos)
    (
        "E",
        "Bruto/Hora Base",
        '=IF(OR(C{r}="-", C{r}=0), "-", IF(ROW()=3, C{r}, IF(Ingresos!Q{r}=TRUE, C{r}, E{r-1})))',
    ),
    (
        "F",
        "Neto/Hora Base",
        '=IF(OR(C{r}="-", C{r}=0), "-", IF(ROW()=3, D{r}, IF(Ingresos!Q{r}=TRUE, D{r}, F{r-1})))',
    ),
    (
        "G",
        "CER Base",
        '=IF(OR(C{r}="-", C{r}=0), "-", IF(ROW()=3, VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE), IF(Ingresos!Q{r}=TRUE, VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE), G{r-1})))',
    ),
    (
        "H",
        "Paridad CER (Bruto/Hora)",
        '=IF(OR(C{r}="-", C{r}=0, G{r}="-"), "-", IFERROR(E{r} * (VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE)/G{r}), "-"))',
    ),
    (
        "I",
        "Paridad CER (Neto/Hora)",
        '=IF(OR(C{r}="-", C{r}=0, G{r}="-"), "-", IFERROR(F{r} * (VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE)/G{r}), "-"))',
    ),
    (
        "J",
        "Poder Adq vs Aumento (CER)",
        '=IF(OR(C{r}="-", C{r}=0, G{r}="-"), "-", IFERROR((D{r}/F{r}) / (VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE)/G{r}) - 1, "-"))',
    ),
    # Comparación vs último aumento (REM) - basado en $/hora
    (
        "K",
        "REM Base",
        '=IF(OR(C{r}="-", C{r}=0), "-", IF(ROW()=3, VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$J, 10, TRUE), IF(Ingresos!Q{r}=TRUE, VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$J, 10, TRUE), K{r-1})))',
    ),
    (
        "L",
        "Poder Adq vs Aumento (REM)",
        '=IF(OR(C{r}="-", C{r}=0, K{r}="-"), "-", IFERROR((D{r}/F{r}) / (VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$J, 10, TRUE)/K{r}) - 1, "-"))',
    ),
    # Variación mensual - basado en $/hora
    (
        "M",
        "Δ% CER MoM",
        '=IF(OR(C{r}="-", C{r}=0), "-", IFERROR((VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(B{r}-30, historic_data!$A$4:$B, 2, TRUE)) - 1, "-"))',
    ),
    (
        "N",
        "Δ% $/Hora vs CER Acum (desde ascenso)",
        '=IF(OR(C{r}="-", C{r}=0, E{r}="-", G{r}="-"), "-", IFERROR((C{r}/E{r}) / (VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE)/G{r}) - 1, "-"))',
    ),
    # Proyección REM - objetivos en $/hora
    (
        "O",
        "REM 3m (%)",
        '=IF(OR(C{r}="-", C{r}=0), "-", (1+IFERROR(VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$I, 3, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$I, 4, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$I, 5, TRUE), 0))-1)',
    ),
    ("P", "Objetivo 3m Bruto/Hora", '=IF(OR(O{r}="-", C{r}="-"), "-", IFERROR(C{r} * (1+O{r}), "-"))'),
    ("Q", "Objetivo 3m Neto/Hora", '=IF(OR(O{r}="-", D{r}="-"), "-", IFERROR(D{r} * (1+O{r}), "-"))'),
    (
        "R",
        "REM 6m (%)",
        '=IF(OR(C{r}="-", C{r}=0), "-", (1+O{r})*(1+IFERROR(VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$I, 6, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$I, 7, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B{r},-1)+1, REM!$A$4:$I, 8, TRUE), 0))-1)',
    ),
    ("S", "Objetivo 6m Bruto/Hora", '=IF(OR(R{r}="-", C{r}="-"), "-", IFERROR(C{r} * (1+R{r}), "-"))'),
    ("T", "Objetivo 6m Neto/Hora", '=IF(OR(R{r}="-", D{r}="-"), "-", IFERROR(D{r} * (1+R{r}), "-"))'),
]

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
    "K": {"type": "NUMBER", "pattern": "0.0000"},
    "L": {"type": "PERCENT", "pattern": "0.00%"},
    "M": {"type": "PERCENT", "pattern": "0.00%"},
    "N": {"type": "PERCENT", "pattern": "0.00%"},
    "O": {"type": "PERCENT", "pattern": "0.00%"},
    "P": {"type": "CURRENCY", "pattern": "$#,##0"},
    "Q": {"type": "CURRENCY", "pattern": "$#,##0"},
    "R": {"type": "PERCENT", "pattern": "0.00%"},
    "S": {"type": "CURRENCY", "pattern": "$#,##0"},
    "T": {"type": "CURRENCY", "pattern": "$#,##0"},
}

# =============================================================================
# ANÁLISIS USD - Sueldo en dólares nominal y real
# =============================================================================

ANALISIS_USD_GROUPS = [
    ("A", "A", "PERIODO"),
    ("B", "D", "SUELDO ARS"),
    ("E", "H", "SUELDO USD NOMINAL"),
    ("I", "L", "SUELDO USD REAL"),
    ("M", "R", "VS ÚLTIMO AUMENTO"),
]

ANALISIS_USD_COLUMNS = [
    # Referencia a Ingresos
    ("A", "Periodo", '=Ingresos!A{r}'),
    ("B", "Fecha", '=Ingresos!B{r}'),
    ("C", "Bruto ARS", '=Ingresos!C{r}'),
    ("D", "Neto ARS", '=Ingresos!G{r}'),
    # Sueldo USD Nominal
    (
        "E",
        "CCL",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(B{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-"))',
    ),
    (
        "F",
        "Δ% CCL MoM",
        '=IF(E{r}="-", "-", IFERROR((E{r} - INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(EOMONTH(B{r}, -1), FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1))) / INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(EOMONTH(B{r}, -1), FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "-"))',
    ),
    (
        "G",
        "Bruto USD",
        '=IF(OR(C{r}=0, E{r}="-"), "-", IFERROR(C{r}/E{r},"-"))',
    ),
    (
        "H",
        "Neto USD",
        '=IF(OR(D{r}="-", E{r}="-"), "-", IFERROR(D{r}/E{r},"-"))',
    ),
    # Sueldo USD Real (ajustado por inflación)
    (
        "I",
        "CER",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", VLOOKUP(B{r}, historic_data!$A$4:$B, 2, TRUE))',
    ),
    (
        "J",
        "CCL Real",
        '=IF(OR(E{r}="-", I{r}="-", I$3="-"), "-", IFERROR(E{r} * (I$3 / I{r}), "-"))',
    ),
    (
        "K",
        "Bruto USD Real",
        '=IF(OR(C{r}=0, J{r}="-"), "-", IFERROR(C{r}/J{r},"-"))',
    ),
    (
        "L",
        "Neto USD Real",
        '=IF(OR(D{r}="-", J{r}="-"), "-", IFERROR(D{r}/J{r},"-"))',
    ),
    # VS Último Aumento - resetea cuando Ingresos!Q{r}=TRUE
    (
        "M",
        "CCL Base",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", IF(ROW()=3, E{r}, IF(Ingresos!Q{r}=TRUE, E{r}, M{r-1})))',
    ),
    (
        "N",
        "Bruto USD Base",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", IF(ROW()=3, G{r}, IF(Ingresos!Q{r}=TRUE, G{r}, N{r-1})))',
    ),
    (
        "O",
        "Neto USD Base",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "-", IF(ROW()=3, H{r}, IF(Ingresos!Q{r}=TRUE, H{r}, O{r-1})))',
    ),
    (
        "P",
        "Paridad USD (Bruto)",
        "=IF(OR(ISBLANK(C{r}), E{r}=\"-\", M{r}=\"-\"), \"-\", IFERROR('Análisis ARS'!E{r} * (E{r}/M{r}), \"-\"))",
    ),
    (
        "Q",
        "Paridad USD (Neto)",
        "=IF(OR(ISBLANK(C{r}), E{r}=\"-\", M{r}=\"-\"), \"-\", IFERROR('Análisis ARS'!F{r} * (E{r}/M{r}), \"-\"))",
    ),
    (
        "R",
        "Atraso USD",
        '=IF(OR(H{r}="-", O{r}="-"), "-", IFERROR((H{r}/O{r})-1, "-"))',
    ),
]

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
    "P": {"type": "CURRENCY", "pattern": "$#,##0"},
    "Q": {"type": "CURRENCY", "pattern": "$#,##0"},
    "R": {"type": "PERCENT", "pattern": "0.00%"},
}

# =============================================================================
# Otras estructuras existentes
# =============================================================================

IMPUESTOS_ROWS = [
    ("Jubilacion", TAX_RATES["jubilacion"]["rate"], TAX_RATES["jubilacion"]["law"]),
    ("PAMI", TAX_RATES["pami"]["rate"], TAX_RATES["pami"]["law"]),
    ("Obra Social", TAX_RATES["obra_social"]["rate"], TAX_RATES["obra_social"]["law"]),
    ("Otro", TAX_RATES["otro"]["rate"], TAX_RATES["otro"]["law"]),
]

HISTORIC_VARIABLES = [
    (None, "Fecha", None),
    (30, "CER", "CER"),
    ("IOL/dolarapi", "CCL", "CCL"),
    ("yfinance", "SPY", "SPY"),
]

# =============================================================================
# DASHBOARD - Métricas para negociación salarial
# =============================================================================

DASHBOARD_SECTIONS = [
    ("RESUMEN EJECUTIVO", 2, 6),
    ("PODER ADQUISITIVO", 8, 12),
    ("COMPARATIVAS", 14, 18),
    ("ÚLTIMO MES", 20, 24),
    ("TARGETS/OBJETIVOS", 26, 30),
]

DASHBOARD_ROWS = [
    # RESUMEN EJECUTIVO (rows 2-6)
    (2, "A", "Métrica", None),
    (2, "B", "Valor", None),
    (2, "C", "Estado", None),
    (3, "A", "Pérdida vs CER desde último ascenso", None),
    (3, "B", '=IFERROR(INDEX(\'Análisis ARS\'!J:J, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (3, "C", '=IF(B3="-", "-", IF(B3<-0.1, "🔴", IF(B3<-0.05, "🟡", "🟢")))', None),
    (4, "A", "Meses desde último ascenso", None),
    (4, "B", '=IFERROR(DATEDIF(INDEX(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE), COUNTA(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE))), TODAY(), "M"), "-")', None),
    (5, "A", "Aumento necesario para empatar CER (%)", None),
    (5, "B", '=IF(B3="-", "-", IFERROR(1/(1+B3)-1, "-"))', None),

    # PODER ADQUISITIVO (rows 8-12)
    (8, "A", "Métrica", None),
    (8, "B", "Valor", None),
    (9, "A", "Neto/Hora actual", None),
    (9, "B", '=IFERROR(INDEX(\'Análisis ARS\'!D:D, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (10, "A", "Neto/Hora ajustado por CER (debería ser)", None),
    (10, "B", '=IFERROR(INDEX(\'Análisis ARS\'!I:I, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (11, "A", "Brecha salarial ($/hora)", None),
    (11, "B", '=IF(OR(B9="-", B10="-"), "-", B9-B10)', None),
    (12, "A", "Brecha salarial (%)", None),
    (12, "B", '=IF(OR(B9="-", B10="-"), "-", (B9/B10)-1)', None),

    # COMPARATIVAS (rows 14-18)
    (14, "A", "Comparativa", None),
    (14, "B", "Pérdida %", None),
    (14, "C", "Debería ganar", None),
    (15, "A", "vs CER acumulado", None),
    (15, "B", '=B3', None),
    (15, "C", '=IF(B9="-", "-", B9/(1+B3))', None),
    (16, "A", "vs REM proyectado", None),
    (16, "B", '=IFERROR(INDEX(\'Análisis ARS\'!L:L, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (16, "C", '=IF(OR(B9="-", B16="-"), "-", B9/(1+B16))', None),
    (17, "A", "vs USD (CCL)", None),
    (17, "B", '=IFERROR(INDEX(\'Análisis USD\'!R:R, MATCH(2, 1/(\'Análisis USD\'!B:B<>""), -1)), "-")', None),
    (17, "C", '=IF(OR(B9="-", B17="-"), "-", B9/(1+B17))', None),

    # ÚLTIMO MES (rows 20-24)
    (20, "A", "Métrica", None),
    (20, "B", "Valor", None),
    (21, "A", "Inflación CER último mes", None),
    (21, "B", '=IFERROR(INDEX(\'Análisis ARS\'!M:M, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (22, "A", "Cambio $/Hora vs CER acumulado", None),
    (22, "B", '=IFERROR(INDEX(\'Análisis ARS\'!N:N, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (23, "A", "Tendencia últimos 3 meses", None),
    (23, "B", '=IF(B22="-", "-", IF(B22<-0.05, "📉 Perdiendo", IF(B22<0.05, "➡️ Estable", "📈 Ganando")))', None),

    # TARGETS/OBJETIVOS (rows 26-30)
    (26, "A", "Objetivo", None),
    (26, "B", "Valor", None),
    (27, "A", "Aumento mínimo para empatar CER", None),
    (27, "B", '=B5', None),
    (28, "A", "Objetivo REM 3 meses", None),
    (28, "B", '=IFERROR(INDEX(\'Análisis ARS\'!P:P, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (29, "A", "Objetivo REM 6 meses", None),
    (29, "B", '=IFERROR(INDEX(\'Análisis ARS\'!S:S, MATCH(2, 1/(\'Análisis ARS\'!B:B<>""), -1)), "-")', None),
    (30, "A", "Nuevo sueldo objetivo (Neto/Hora CER)", None),
    (30, "B", '=B10', None),
]
