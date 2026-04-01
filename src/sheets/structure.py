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
    ("A", "Periodo Abonado", '=ARRAYFORMULA(IF(B3:B<>"", TEXT(B3:B, "mmmm yyyy"), ""))'),
    ("B", "Fecha", None),
    ("C", "Bruto", None),
    (
        "D",
        "Jubilacion",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "", ROUND(C{r}*impuestos!$B$2,0))',
    ),
    ("E", "PAMI", '=IF(OR(ISBLANK(C{r}), C{r}=0), "", ROUND(C{r}*impuestos!$B$3,0))'),
    (
        "F",
        "Obra Social",
        '=IF(OR(ISBLANK(C{r}), C{r}=0), "", ROUND(C{r}*impuestos!$B$4,0))',
    ),
    ("G", "Neto", '=IF(OR(ISBLANK(C{r}), C{r}=0), "", C{r}-D{r}-E{r}-F{r})'),
    ("H", "SAC Bruto", None),
    (
        "I",
        "SAC Neto",
        '=IF(OR(ISBLANK(H{r}), H{r}=0), "", H{r}-ROUND(H{r}*impuestos!$B$2,0)-ROUND(H{r}*impuestos!$B$3,0)-ROUND(H{r}*impuestos!$B$4,0))',
    ),
    ("J", "Bono Neto", None),
    ("K", "Tarjeta Corporativa", None),
    ("L", "Otros Beneficios", None),
    (
        "M",
        "Total Neto",
        '=IF(OR(ISBLANK(G{r}), G{r}=""), "", IFERROR(IF(SUM(G{r}:L{r})=0, "", SUM(G{r}:L{r})), ""))',
    ),
    ("N", "Horas Diarias", None),
    (
        "O",
        "Bruto/Hora",
        '=IF(OR(ISBLANK(C{r}), C{r}=0, ISBLANK(N{r}), N{r}=0), "", ROUND(C{r}/(N{r}*20), 2))',
    ),
    (
        "P",
        "Neto/Hora",
        '=IF(OR(ISBLANK(G{r}), G{r}="", ISBLANK(N{r}), N{r}=0), "", ROUND(G{r}/(N{r}*20), 2))',
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
    ("M", "P", "VARIACIÓN MENSUAL"),
    ("Q", "V", "PROYECCIÓN REM"),
]

ANALISIS_ARS_COLUMNS = [
    # Referencia a Ingresos
    ("A", "Periodo", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!A3:A1000, ""))'),
    ("B", "Fecha", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!B3:B1000, ""))'),
    ("C", "Bruto/Hora", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!O3:O1000, ""))'),
    ("D", "Neto/Hora", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!P3:P1000, ""))'),
    # Comparación vs último aumento (CER) - basado en $/hora
    (
        "E",
        "Bruto/Hora Base",
        '=SCAN(0, SEQUENCE(ROWS(C3:C1000)), LAMBDA(acc, i, LET(val, INDEX(C3:C1000, i), asc, INDEX(Ingresos!Q3:Q1000, i), IF(val="", "", IF(OR(acc=0, asc=TRUE), val, acc)))))',
    ),
    (
        "F",
        "Neto/Hora Base",
        '=SCAN(0, SEQUENCE(ROWS(D3:D1000)), LAMBDA(acc, i, LET(val, INDEX(D3:D1000, i), asc, INDEX(Ingresos!Q3:Q1000, i), IF(val="", "", IF(OR(acc=0, asc=TRUE), val, acc)))))',
    ),
    (
        "G",
        "CER Base",
        '=LET(s, SCAN(0, SEQUENCE(ROWS(B3:B1000)), LAMBDA(a, i, LET(f, INDEX(B3:B1000, i), asc, INDEX(Ingresos!Q3:Q1000, i), v, IFERROR(VLOOKUP(EOMONTH(f, 0) + 15, historic_data!$A$4:$B, 2, TRUE), 0), IF(f="", 0, IF(OR(a=0, asc=TRUE), v, a))))), ARRAYFORMULA(IF(B3:B1000="", "", s)))',
    ),
    (
        "H",
        "Paridad CER (Bruto/Hora)",
        '=ARRAYFORMULA(IF((B3:B1000="")+(E3:E1000="")+(G3:G1000=0), "", IFERROR(E3:E1000 * (VLOOKUP(EOMONTH(B3:B1000, 0) + 15, historic_data!$A$4:$B, 2, TRUE)/G3:G1000), "")))',
    ),
    (
        "I",
        "Paridad CER (Neto/Hora)",
        '=ARRAYFORMULA(IF((B3:B1000="")+(F3:F1000="")+(G3:G1000=0), "", IFERROR(F3:F1000 * (VLOOKUP(EOMONTH(B3:B1000, 0) + 15, historic_data!$A$4:$B, 2, TRUE)/G3:G1000), "")))',
    ),
    (
        "J",
        "Poder Adq vs Aumento (CER)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR((D3:D1000/F3:F1000) / (VLOOKUP(EOMONTH(B3:B1000, 0) + 15, historic_data!$A$4:$B, 2, TRUE)/G3:G1000) - 1, "")))',
    ),
    # Comparación vs último aumento (REM) - basado en $/hora
    (
        "K",
        "REM Base",
        '=LET(s, SCAN(0, SEQUENCE(ROWS(B3:B1000)), LAMBDA(a, i, LET(f, INDEX(B3:B1000, i), asc, INDEX(Ingresos!Q3:Q1000, i), v, IFERROR(VLOOKUP(EOMONTH(f,-1)+1, REM!$A$4:$J, 10, TRUE), 0), IF(f="", 0, IF(OR(a=0, asc=TRUE), v, a))))), ARRAYFORMULA(IF(B3:B1000="", "", s)))',
    ),
    (
        "L",
        "Poder Adq vs Aumento (REM)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR((D3:D1000/F3:F1000) / (VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$J, 10, TRUE)/K3:K1000) - 1, "")))',
    ),
    # Variación mensual - basado en $/hora
    (
        "M",
        "Δ% CER MoM (Real)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR((VLOOKUP(EOMONTH(B3:B1000, 0) + 15, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(EOMONTH(B3:B1000, -1) + 15, historic_data!$A$4:$B, 2, TRUE)) - 1, "")))',
    ),
    (
        "N",
        "Δ% $/Hora vs CER Acum (Real)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR((C3:C1000/E3:E1000) / (VLOOKUP(EOMONTH(B3:B1000, 0) + 15, historic_data!$A$4:$B, 2, TRUE)/G3:G1000) - 1, "")))',
    ),
    (
        "O",
        "Δ% CER MoM (Publicado)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR((VLOOKUP(EOMONTH(B3:B1000, -1) + 15, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(EOMONTH(B3:B1000, -2) + 15, historic_data!$A$4:$B, 2, TRUE)) - 1, "")))',
    ),
    (
        "P",
        "Δ% $/Hora vs CER Acum (Publicado)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR((C3:C1000/E3:E1000) / (VLOOKUP(EOMONTH(B3:B1000, -1) + 15, historic_data!$A$4:$B, 2, TRUE)/G3:G1000) - 1, "")))',
    ),
    # Proyección REM - objetivos en $/hora
    (
        "Q",
        "REM 3m (%)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", (1+IFERROR(VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$I, 3, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$I, 4, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$I, 5, TRUE), 0))-1))',
    ),
    ("R", "Objetivo 3m Bruto/Hora", '=ARRAYFORMULA(IF((B3:B1000="")+(C3:C1000=""), "", IFERROR(C3:C1000 * (1+Q3:Q1000), "")))'),
    ("S", "Objetivo 3m Neto/Hora", '=ARRAYFORMULA(IF((B3:B1000="")+(D3:D1000=""), "", IFERROR(D3:D1000 * (1+Q3:Q1000), "")))'),
    (
        "T",
        "REM 6m (%)",
        '=ARRAYFORMULA(IF(B3:B1000="", "", (1+Q3:Q1000)*(1+IFERROR(VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$I, 6, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$I, 7, TRUE), 0))*(1+IFERROR(VLOOKUP(EOMONTH(B3:B1000,-1)+1, REM!$A$4:$I, 8, TRUE), 0))-1))',
    ),
    ("U", "Objetivo 6m Bruto/Hora", '=ARRAYFORMULA(IF((B3:B1000="")+(C3:C1000=""), "", IFERROR(C3:C1000 * (1+T3:T1000), "")))'),
    ("V", "Objetivo 6m Neto/Hora", '=ARRAYFORMULA(IF((B3:B1000="")+(D3:D1000=""), "", IFERROR(D3:D1000 * (1+T3:T1000), "")))'),
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
    "P": {"type": "PERCENT", "pattern": "0.00%"},
    "Q": {"type": "PERCENT", "pattern": "0.00%"},
    "R": {"type": "CURRENCY", "pattern": "$#,##0"},
    "S": {"type": "CURRENCY", "pattern": "$#,##0"},
    "T": {"type": "PERCENT", "pattern": "0.00%"},
    "U": {"type": "CURRENCY", "pattern": "$#,##0"},
    "V": {"type": "CURRENCY", "pattern": "$#,##0"},
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
    ("A", "Periodo", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!A3:A1000, ""))'),
    ("B", "Fecha", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!B3:B1000, ""))'),
    ("C", "Bruto ARS", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!C3:C1000, ""))'),
    ("D", "Neto ARS", '=ARRAYFORMULA(IF(Ingresos!B3:B1000<>"", Ingresos!G3:G1000, ""))'),
    # Sueldo USD Nominal
    (
        "E",
        "CCL",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR(LOOKUP(B3:B1000, historic_data!$A$4:$A, historic_data!$C$4:$C), "")))',
    ),
    (
        "F",
        "Δ% CCL MoM",
        '=ARRAYFORMULA(IF(E3:E1000="", "", IFERROR((E3:E1000 - LOOKUP(EOMONTH(B3:B1000, -1), historic_data!$A$4:$A, historic_data!$C$4:$C)) / LOOKUP(EOMONTH(B3:B1000, -1), historic_data!$A$4:$A, historic_data!$C$4:$C), "")))',
    ),
    (
        "G",
        "Bruto USD",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR(C3:C1000/E3:E1000,"")))',
    ),
    (
        "H",
        "Neto USD",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR(D3:D1000/E3:E1000,"")))',
    ),
    # Sueldo USD Real (ajustado por inflación)
    (
        "I",
        "CER",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR(VLOOKUP(EOMONTH(B3:B1000, 0) + 15, historic_data!$A$4:$B, 2, TRUE), "")))',
    ),
    (
        "J",
        "CCL Real",
        '=ARRAYFORMULA(IF((B3:B1000="")+(E3:E1000="")+(I3:I1000="")+(I$3=""), "", IFERROR(E3:E1000 * (I$3 / I3:I1000), "")))',
    ),
    (
        "K",
        "Bruto USD Real",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR(C3:C1000/J3:J1000,"")))',
    ),
    (
        "L",
        "Neto USD Real",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR(D3:D1000/J3:J1000,"")))',
    ),
    # VS Último Aumento - resetea cuando Ingresos!Q{r}=TRUE
    (
        "M",
        "CCL Base",
        '=SCAN(0, SEQUENCE(ROWS(E3:E1000)), LAMBDA(acc, i, LET(val, INDEX(E3:E1000, i), asc, INDEX(Ingresos!Q3:Q1000, i), IF(val="", "", IF(OR(acc=0, asc=TRUE), val, acc)))))',
    ),
    (
        "N",
        "Bruto USD Base",
        '=SCAN(0, SEQUENCE(ROWS(G3:G1000)), LAMBDA(acc, i, LET(val, INDEX(G3:G1000, i), asc, INDEX(Ingresos!Q3:Q1000, i), IF(val="", "", IF(OR(acc=0, asc=TRUE), val, acc)))))',
    ),
    (
        "O",
        "Neto USD Base",
        '=SCAN(0, SEQUENCE(ROWS(H3:H1000)), LAMBDA(acc, i, LET(val, INDEX(H3:H1000, i), asc, INDEX(Ingresos!Q3:Q1000, i), IF(val="", "", IF(OR(acc=0, asc=TRUE), val, acc)))))',
    ),
    (
        "P",
        "Paridad USD (Bruto)",
        "=ARRAYFORMULA(IF(B3:B1000=\"\", \"\", IFERROR('Análisis ARS'!C3:C1000 * (E3:E1000/M3:M1000), \"\")))",
    ),
    (
        "Q",
        "Paridad USD (Neto)",
        "=ARRAYFORMULA(IF(B3:B1000=\"\", \"\", IFERROR('Análisis ARS'!D3:D1000 * (E3:E1000/M3:M1000), \"\")))",
    ),
    (
        "R",
        "Atraso USD",
        '=ARRAYFORMULA(IF(B3:B1000="", "", IFERROR((H3:H1000/O3:O1000)-1, "")))',
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
    ("ÚLTIMO MES", 20, 25),
    ("TARGETS/OBJETIVOS", 26, 30),
    ("IMPACTO ECONÓMICO", 32, 38),
    ("CONTEXTO HISTÓRICO", 40, 48),
    ("PROYECCIONES INTELIGENTES", 49, 56),
    ("ALERTAS Y URGENCIA", 58, 62),
    ("VISUALIZACIÓN TENDENCIA", 2, 12, "E"),  # Columna E
    ("COMPARATIVA VISUAL", 14, 22, "E"),  # Columna E
    ("SIMULADOR DE AUMENTOS", 24, 38, "E"),  # Columna E
]

DASHBOARD_ROWS = [
    # RESUMEN EJECUTIVO (rows 2-6)
    (2, "A", "Métrica", None),
    (2, "B", "Valor", None),
    (2, "C", "Estado", None),
    (3, "A", "Pérdida vs CER desde último ascenso", None),
    (3, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!J3:J, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!J3:J<>"")), ROWS(FILTER(\'Análisis ARS\'!J3:J, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!J3:J<>"")))), "")', None),
    (3, "C", '=IF(OR(B3="", B3="-"), "", IF(B3<-0.1, "🔴", IF(B3<-0.05, "🟡", "🟢")))', None),
    (4, "A", "Meses desde último ascenso", None),
    (4, "B", '=IFERROR(DATEDIF(INDEX(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE), ROWS(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE))), TODAY(), "M"), "")', None),
    (5, "A", "Aumento necesario para empatar CER (%)", None),
    (5, "B", '=IF(OR(B3="", B3="-"), "", IFERROR(1/(1+B3)-1, ""))', None),

    # PODER ADQUISITIVO (rows 8-12)
    (8, "A", "Métrica", None),
    (8, "B", "Valor", None),
    (9, "A", "Neto/Hora actual", None),
    (9, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!D3:D, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!D3:D<>"")), ROWS(FILTER(\'Análisis ARS\'!D3:D, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!D3:D<>"")))), "")', None),
    (9, "C", '=IF(B9="", "", B9*8*20)', None),
    (9, "D", "Bruto mensual (8hs)", None),
    (10, "A", "Neto/Hora ajustado por CER (debería ser)", None),
    (10, "B", '=LOOKUP(2, 1/((\'Análisis ARS\'!I3:I<>0)*(\'Análisis ARS\'!I3:I<>"")), \'Análisis ARS\'!I3:I)', None),
    (10, "C", '=IF(B10="", "", B10*8*20)', None),
    (10, "D", "Bruto mensual (8hs)", None),
    (11, "A", "Brecha salarial ($/hora)", None),
    (11, "B", '=IF(OR(B9="", B10=""), "", B9-B10)', None),
    (12, "A", "Brecha salarial (%)", None),
    (12, "B", '=IF(OR(B9="", B10=""), "", (B9/B10)-1)', None),

    # COMPARATIVAS (rows 14-18)
    (14, "A", "Comparativa", None),
    (14, "B", "Pérdida %", None),
    (14, "C", "Debería ganar (Bruto 8hs)", None),
    (15, "A", "vs CER acumulado", None),
    (15, "B", '=B3', None),
    (15, "C", '=IF(B15="", "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")), ROWS(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>""))))/(1+B15)*8*20, ""))', None),
    (16, "A", "vs REM proyectado", None),
    (16, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!L3:L, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!L3:L<>"")), ROWS(FILTER(\'Análisis ARS\'!L3:L, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!L3:L<>"")))), "")', None),
    (16, "C", '=IF(B16="", "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")), ROWS(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>""))))/(1+B16)*8*20, ""))', None),
    (17, "A", "vs USD (CCL)", None),
    (17, "B", '=IFERROR(INDEX(FILTER(\'Análisis USD\'!R3:R, (\'Análisis USD\'!B3:B<>"") * (\'Análisis USD\'!R3:R<>"")), ROWS(FILTER(\'Análisis USD\'!R3:R, (\'Análisis USD\'!B3:B<>"") * (\'Análisis USD\'!R3:R<>"")))), "")', None),
    (17, "C", '=IF(B17="", "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")), ROWS(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>""))))/(1+B17)*8*20, ""))', None),

    # ÚLTIMO MES (rows 20-25)
    (20, "A", "Métrica", None),
    (20, "B", "Valor", None),
    (21, "A", "Inflación CER (Real - Mes Cobrado)", None),
    (21, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!M3:M, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!M3:M<>"")), ROWS(FILTER(\'Análisis ARS\'!M3:M, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!M3:M<>"")))), "")', None),
    (22, "A", "Inflación CER (Publicada - Mes Pasado)", None),
    (22, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!O3:O, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!O3:O<>"")), ROWS(FILTER(\'Análisis ARS\'!O3:O, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!O3:O<>"")))), "")', None),
    (23, "A", "Cambio $/Hora vs CER Real (Acum)", None),
    (23, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!N3:N, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!N3:N<>"")), ROWS(FILTER(\'Análisis ARS\'!N3:N, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!N3:N<>"")))), "")', None),
    (24, "A", "Cambio $/Hora vs CER Publ (Acum)", None),
    (24, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!P3:P, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!P3:P<>"")), ROWS(FILTER(\'Análisis ARS\'!P3:P, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!P3:P<>"")))), "")', None),
    (25, "A", "Tendencia últimos 3 meses", None),
    (25, "B", '=IFERROR(LET(datos, FILTER(\'Análisis ARS\'!J3:J, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!J3:J<>"")), n, ROWS(datos), IF(n<3, "", INDEX(datos, n) - INDEX(datos, MAX(1, n-3)))), "")', None),
    (25, "C", '=IF(B25="", "", IF(B25<0.001, "📉 Perdiendo", IF(B25<0.015, "➡️ Estable", "📈 Ganando")))', None),

    # TARGETS/OBJETIVOS (rows 26-30)
    (26, "A", "Objetivo", None),
    (26, "B", "Valor", None),
    (27, "A", "Aumento mínimo para empatar CER", None),
    (27, "B", '=B5', None),
    (28, "A", "Objetivo REM 3 meses", None),
    (28, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!Q3:Q, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!Q3:Q<>"")), ROWS(FILTER(\'Análisis ARS\'!Q3:Q, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!Q3:Q<>"")))), "")', None),
    (29, "A", "Objetivo REM 6 meses", None),
    (29, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!T3:T, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!T3:T<>"")), ROWS(FILTER(\'Análisis ARS\'!T3:T, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!T3:T<>"")))), "")', None),
    (30, "A", "Nuevo sueldo objetivo (Bruto 8hs CER)", None),
    (30, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!H3:H, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!H3:H<>"")), ROWS(FILTER(\'Análisis ARS\'!H3:H, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!H3:H<>""))))*8*20, "")', None),

    # IMPACTO ECONÓMICO (rows 32-38)
    (32, "A", "Impacto Económico", None),
    (32, "B", "Valor", None),
    (32, "C", "Estado", None),
    (33, "A", "Dinero perdido acumulado (ARS)", None),
    (33, "B", '=IF(OR(B11="", B4=""), "", ABS(B11)*8*20*B4)', None),
    (33, "C", '=LET(bruto_mensual, INDEX(FILTER(\'Análisis ARS\'!C:C, (\'Análisis ARS\'!B:B<>"") * (\'Análisis ARS\'!C:C<>"")), ROWS(FILTER(\'Análisis ARS\'!C:C, (\'Análisis ARS\'!B:B<>"") * (\'Análisis ARS\'!C:C<>""))))*8*20, IF(B33="", "", IF(B33>2*bruto_mensual, "🔴", IF(B33>bruto_mensual, "🟡", "🟢"))))', None),
    (34, "A", "Pérdida mensual actual (ARS/mes)", None),
    (34, "B", '=IF(B11="", "", ABS(B11)*20)', None),
    (35, "A", "Pérdida proyectada próximos 3 meses", None),
    (35, "B", '=IF(B34="", "", B34*3)', None),
    (36, "A", "Pérdida proyectada próximos 6 meses", None),
    (36, "B", '=IF(B34="", "", B34*6)', None),
    (37, "A", "Días sin ajuste por inflación", None),
    (37, "B", '=IF(B4="", "", B4*30)', None),
    (38, "A", "Meses de sueldo para recuperar pérdida", None),
    (38, "B", '=IF(OR(B33="", B9=""), "", ROUND(B33/(B9*20), 1))', None),

    # CONTEXTO HISTÓRICO (rows 40-47)
    (40, "A", "Contexto Histórico", None),
    (40, "B", "Valor", None),
    (41, "A", "Peor pérdida vs CER (histórica)", None),
    (41, "B", '=IFERROR(MIN(FILTER(\'Análisis ARS\'!J3:J, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!J3:J<>""))), "")', None),
    (41, "C", '=IF(B41="", "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!B3:B, (\'Análisis ARS\'!J3:J = B41)), 1), ""))', None),
    (41, "D", "Fecha peor momento", None),
    (42, "A", "Mejor momento vs CER (histórico)", None),
    (42, "B", '=IFERROR(MAX(FILTER(\'Análisis ARS\'!J3:J, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!J3:J<>""))), "")', None),
    (42, "C", '=IF(B42="", "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!B3:B, (\'Análisis ARS\'!J3:J = B42)), 1), ""))', None),
    (42, "D", "Fecha mejor momento", None),
    (43, "A", "Total de ascensos registrados", None),
    (43, "B", '=COUNTIF(Ingresos!Q:Q, TRUE)', None),
    (44, "A", "Promedio de meses entre ascensos", None),
    (44, "B", '=IF(B43<=1, "", IFERROR(DATEDIF(INDEX(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE), 1), INDEX(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE), ROWS(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE))), "M")/(B43-1), ""))', None),
    (45, "A", "Inflación CER acumulada desde ascenso", None),
    (45, "B", '=IF(B3="", "", IFERROR(ABS(B3), ""))', None),
    (46, "A", "Situación actual vs histórico", None),
    (46, "B", '=IF(OR(B3="", B41=""), "", IF(B3=B41, "🔴 Peor momento", IF(B3<B41*0.8, "🟡 Cerca del peor", "🟢 No es el peor")))', None),
    (47, "A", "Máximo histórico (nominal)", None),
    (47, "B", '=IFERROR(MAX(FILTER(\'Análisis ARS\'!D3:D, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!D3:D<>""))), "")', None),
    (47, "C", '=IFERROR(MAX(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")))*8*20, "")', None),
    (47, "D", "Bruto mensual nominal", None),
    (48, "A", "Máximo histórico ajustado por CER", None),
    (48, "B", '=IFERROR(MAX(FILTER(\'Análisis ARS\'!I3:I, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!I3:I<>""))), "")', None),
    (48, "C", '=IFERROR(MAX(FILTER(\'Análisis ARS\'!H3:H, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!H3:H<>"")))*8*20, "")', None),
    (48, "D", "Bruto mensual ajustado", None),

    # PROYECCIONES INTELIGENTES (rows 49-56)
    (49, "A", "Proyecciones", None),
    (49, "B", "Valor", None),
    (49, "C", "Contexto", None),
    (50, "A", "Fecha estimada próximo ascenso", None),
    (50, "B", '=IF(B44="", "", TEXT(EDATE(INDEX(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE), ROWS(FILTER(Ingresos!B:B, Ingresos!Q:Q=TRUE))), B44), "dd/mm/yyyy"))', None),
    (50, "C", '=B44', None),
    (50, "D", "Avg meses entre ascensos", None),
    (51, "A", "Aumento para estar +10% sobre CER", None),
    (51, "B", '=IF(B3="", "", (1.1/(1+B3))-1)', None),
    (51, "C", '=IF(OR(B51="", B9=""), "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")), ROWS(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")))) * (1+B51) * 8 * 20, ""))', None),
    (51, "D", "Bruto mensual (8hs)", None),
    (52, "A", "Aumento para estar +20% sobre CER", None),
    (52, "B", '=IF(B3="", "", (1.2/(1+B3))-1)', None),
    (52, "C", '=IF(OR(B52="", B9=""), "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")), ROWS(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")))) * (1+B52) * 8 * 20, ""))', None),
    (52, "D", "Bruto mensual (8hs)", None),
    (53, "A", "Meses para empatar CER (siguiendo REM)", None),
    (53, "B", '=IF(OR(B3="", B28=""), "", IFERROR(ROUND(LN(1+ABS(B3))/LN(1+(B28/3)), 1), ""))', None),
    (54, "A", "Inflación CER proyectada próximos 3 meses", None),
    (54, "B", '=B28', None),
    (55, "A", "Pico histórico BRUTO ajustado por CER", None),
    (55, "B", '=IFERROR(MAX(FILTER(\'Análisis ARS\'!H3:H, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!H3:H<>""))), "")', None),
    (55, "C", '=IF(B55="", "", IFERROR(INDEX(FILTER(\'Análisis ARS\'!B3:B, (\'Análisis ARS\'!H3:H = B55)), 1), ""))', None),
    (55, "D", "Fecha de ese pico", None),
    (56, "A", "Brecha vs mejor momento histórico (CER ajustado)", None),
    (56, "B", '=IFERROR(INDEX(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")), ROWS(FILTER(\'Análisis ARS\'!C3:C, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!C3:C<>"")))) - B55, "")', None),
    (56, "C", '=IF(B56="", "", B56 * 8 * 20)', None),
    (56, "D", "Brecha bruto mensual (8hs)", None),

    # ALERTAS Y URGENCIA (rows 58-62)
    (58, "A", "Alertas", None),
    (58, "B", "Estado", None),
    (59, "A", "Nivel de urgencia", None),
    (59, "B", '=IF(B3="", "", IF(B3<-0.15, "🚨 CRÍTICO", IF(B3<-0.10, "🔴 ALTO", IF(B3<-0.05, "🟡 MEDIO", "🟢 BAJO"))))', None),
    (60, "A", "Tiempo desde último ajuste", None),
    (60, "B", '=IF(OR(B37="", B37="-"), "", CONCATENATE(B37, " días sin ajuste"))', None),
    (61, "A", "Distancia vs peor momento histórico", None),
    (61, "B", '=IF(OR(B3="", B41=""), "", IF(B3<=B41, "EN PEOR MOMENTO", CONCATENATE(TEXT(ABS((B3/B41)-1), "0.0%"), " mejor que peor momento")))', None),
    (62, "A", "Recomendación", None),
    (62, "B", '=IF(B59="", "", IF(B59="🚨 CRÍTICO", "Negociar aumento URGENTE", IF(B59="🔴 ALTO", "Solicitar reunión pronto", IF(B59="🟡 MEDIO", "Monitorear y preparar", "Situación estable"))))', None),

    # VISUALIZACIÓN TENDENCIA (columnas E-H, rows 2-12)
    (2, "E", "TENDENCIA PODER ADQUISITIVO", None),
    (3, "E", "Últimos 12 meses", None),
    (3, "F", '=SPARKLINE(FILTER(\'Análisis ARS\'!J3:J, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!J3:J<>"")), {"charttype", "line"; "color1", "red"; "linewidth", 2})', None),
    (5, "E", "Evolución Neto/Hora", None),
    (5, "F", '=SPARKLINE(FILTER(\'Análisis ARS\'!D3:D, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!D3:D<>"")), {"charttype", "line"; "color1", "blue"; "linewidth", 2})', None),
    (7, "E", "Inflación CER mensual", None),
    (7, "F", '=SPARKLINE(FILTER(\'Análisis ARS\'!M3:M, (\'Análisis ARS\'!B3:B<>"") * (\'Análisis ARS\'!M3:M<>"")), {"charttype", "column"; "color1", "orange"})', None),
    (9, "E", "Resumen visual", None),
    (10, "E", "Actual", None),
    (10, "F", '=B9', None),
    (11, "E", "Debería ser (CER)", None),
    (11, "F", '=B10', None),
    (12, "E", "Brecha", None),
    (12, "F", '=B11', None),

    # COMPARATIVA VISUAL (columnas E-H, rows 14-22)
    (14, "E", "COMPARATIVA VISUAL", None),
    (15, "E", "Actual vs CER", None),
    (15, "F", '=IF(B3="", "", REPT("█", ROUND(ABS(B3)*100, 0)))', None),
    (15, "G", '=IF(B3="", "", TEXT(B3, "0.0%"))', None),
    (17, "E", "Actual vs REM", None),
    (17, "F", '=IF(B16="", "", REPT("█", ROUND(ABS(B16)*100, 0)))', None),
    (17, "G", '=IF(B16="", "", TEXT(B16, "0.0%"))', None),
    (19, "E", "Actual vs USD", None),
    (19, "F", '=IF(B17="", "", REPT("█", ROUND(ABS(B17)*100, 0)))', None),
    (19, "G", '=IF(B17="", "", TEXT(B17, "0.0%"))', None),
    (21, "E", "Nivel de urgencia", None),
    (21, "F", '=IF(B59="", "", B59)', None),

    # SIMULADOR DE AUMENTOS (columnas E-H, rows 24-38)
    (24, "E", "SIMULADOR DE AUMENTOS", None),
    (25, "E", "Aumento propuesto (%)", None),
    (25, "F", "0%", None),  # Input manual
    (27, "E", "Resultados:", None),
    (28, "E", "Nuevo Neto/Hora", None),
    (28, "F", '=IF(OR(B9="", F25=""), "", B9*(1+VALUE(SUBSTITUTE(F25, "%", ""))/100))', None),
    (29, "E", "Nueva posición vs CER", None),
    (29, "F", '=IF(OR(F28="", B10=""), "", (F28/B10)-1)', None),
    (30, "E", "¿Empatarías CER?", None),
    (30, "F", '=IF(F29="", "", IF(F29>=0, "✅ SÍ", "❌ NO"))', None),
    (31, "E", "Meses hasta próximo ajuste CER", None),
    (31, "F", '=IF(OR(F29="", B28=""), "", IF(F29>=0, ROUND(F29*12/(1+B28), 1), ""))', None),
    (33, "E", "Escenarios rápidos:", None),
    (34, "E", "Mínimo (empatar CER)", None),
    (34, "F", '=IF(B5="", "", TEXT(B5, "0.0%"))', None),
    (35, "E", "Conservador (+10% sobre CER)", None),
    (35, "F", '=IF(B51="", "", TEXT(B51, "0.0%"))', None),
    (36, "E", "Ambicioso (+20% sobre CER)", None),
    (36, "F", '=IF(B52="", "", TEXT(B52, "0.0%"))', None),
    (37, "E", "Seguir REM 3 meses", None),
    (37, "F", '=IF(B28="", "", TEXT(B28, "0.0%"))', None),
]
