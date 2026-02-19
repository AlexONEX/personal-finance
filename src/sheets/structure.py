"""Definiciones de estructura de sheets para Ingresos Tracker."""

# Row 1: Group headers (with merged ranges)
INCOME_GROUPS = [
    ("A", "A", ""),  # Fecha (sin merge)
    ("B", "F", "SUELDO"),
    ("G", "G", ""),  # SAC Bruto input (sin header en row 1)
    ("H", "H", "AGUINALDO"),
    ("I", "I", "BONOS"),
    ("J", "J", "BENEFICIOS EMPRESA"),
    ("K", "K", "TOTAL"),
    ("L", "N", "CCL"),
    ("O", "P", "CER"),
    ("Q", "X", "ANALISIS REAL (Sueldo y Poder Adquisitivo)"),
]

# Row 2: Column headers with formulas
INCOME_COLUMNS = [
    ("A", "Fecha", None),
    ("B", "Bruto", None),
    ("C", "Jubilacion", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$2,0))'),
    ("D", "PAMI", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$3,0))'),
    ("E", "Obra Social", '=IF(ISBLANK(B{r}),"",ROUND(B{r}*impuestos!$B$4,0))'),
    ("F", "Neto", '=IF(ISBLANK(B{r}),"",B{r}-C{r}-D{r}-E{r})'),
    ("G", "", None),  # SAC Bruto (input manual, sin header)
    (
        "H",
        "SAC Neto",
        '=IF(ISBLANK(G{r}),"",G{r}-ROUND(G{r}*impuestos!$B$2,0)-ROUND(G{r}*impuestos!$B$3,0)-ROUND(G{r}*impuestos!$B$4,0))',
    ),
    ("I", "Bono Neto", None),
    ("J", "Comida", None),
    ("K", "Total Neto", '=IFERROR(IF(SUM(F{r}:J{r})=0, "", SUM(F{r}:J{r})), "")'),
    (
        "L",
        "CCL",
        '=IFERROR(INDEX(FILTER(historic_data!$C$4:$C, historic_data!$C$4:$C <> ""), MATCH(A{r}, FILTER(historic_data!$A$4:$A, historic_data!$C$4:$C <> ""), 1)), "")',
    ),
    ("M", "Sueldo USD", '=IFERROR(K{r}/L{r},"")'),
    ("N", "Delta % CCL MoM", '=IFERROR((L{r}-L{r-1})/L{r-1}, "-")'),
    (
        "O",
        "Sueldo Ajustado CER (Base Oct-23)",
        '=IFERROR($K$3 * (VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP($A$3, historic_data!$A$4:$B, 2, TRUE)), "")',
    ),
    (
        "P",
        "Delta % CER MoM",
        '=IFERROR((VLOOKUP(A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(A{r-1}, historic_data!$A$4:$B, 2, TRUE)) - 1, "-")',
    ),
    ("Q", "Delta Sueldo MoM", '=IFERROR(F{r}/F{r-1}-1,"-")'),
    ("R", "Poder Adq. MoM", '=IFERROR((1+Q{r})/(1+P{r})-1,"-")'),
    ("S", "Sueldo Real idx", None),  # Special: primero es 1, resto es formula
    ("T", "CER idx", None),  # Special: primero es =100, resto es formula
    (
        "U",
        "CER Acum. (Total)",
        '=IFERROR((VLOOKUP($A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP($A$3, historic_data!$A$4:$B, 2, TRUE)) - 1, "")',
    ),
    (
        "V",
        "CER Anual (YTD)",
        '=IFERROR((VLOOKUP($A{r}, historic_data!$A$4:$B, 2, TRUE) / VLOOKUP(DATE(YEAR($A{r}), 1, 1), historic_data!$A$4:$B, 2, TRUE)) - 1, "")',
    ),
    ("W", "Delta % Sueldo USD MoM", '=IFERROR(($M{r}/$M{r-1})-1, "-")'),
    (
        "X",
        "Sueldo USD Anual (YTD)",
        '=IFERROR(($M{r} / IFERROR(VLOOKUP(DATE(YEAR($A{r}), 1, 1), $A$3:$M, 12, TRUE), $M{r})) - 1, "")',
    ),
]

# Impuestos sheet rows
IMPUESTOS_ROWS = [
    ("Jubilacion", 0.11, "Ley 24241"),
    ("PAMI", 0.03, "Ley 19032"),
    ("Obra Social", 0.03, "Ley 23660"),
    ("Otro", 0.00, "—"),
]

# Historic data variables
HISTORIC_VARIABLES = [
    (None, "Fecha", None),
    (30, "CER", "CER"),  # BCRA var 30 - CER diario
    ("IOL/dolarapi", "CCL", "CCL"),  # CCL source label
]

# Market data columns
MARKET_COLUMNS = [
    ("A", "Fecha", None, None),
    ("B", "CER", "CER", None),
    ("C", "Delta MoM", "CER", '=IFERROR(B{r}/B{r-1}-1,"")'),
    ("D", "Delta 6m", "CER", '=IFERROR(B{r}/OFFSET(B{r},-6,0)-1,"")'),
    ("E", "Delta 12m", "CER", '=IFERROR(B{r}/OFFSET(B{r},-12,0)-1,"")'),
    ("F", "CCL", "CCL", None),
    ("G", "Delta CCL MoM", "CCL", '=IFERROR(F{r}/F{r-1}-1,"")'),
]

MARKET_GROUPS = [
    ("A", "A", ""),
    ("B", "E", "CER"),
    ("F", "G", "CCL"),
]
