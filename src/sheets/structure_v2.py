"""Estructura de sheets del Ingresos Tracker - V2 con fórmulas simplificadas.

Esta versión usa fórmulas simples (sin ARRAYFORMULA) para facilitar debugging y validación.
Una vez validadas, se pueden optimizar con ARRAYFORMULA.

Cambios vs V1:
- Análisis ARS: Agregada columna auxiliar K_BASE (oculta) para trackear índice INDEC
- Análisis USD: Eliminadas columnas P-Q (Paridad USD) - reducido a 16 columnas
- Fórmulas simplificadas sin SCAN/ARRAYFORMULA para facilitar debugging
"""

from src.config import TAX_RATES

# =============================================================================
# INGRESOS - Sin cambios respecto a V1
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
    ("D", "Jubilacion", '=IF(OR(ISBLANK(C{r}), C{r}=0), "", ROUND(C{r}*impuestos!$B$2,0))'),
    ("E", "PAMI", '=IF(OR(ISBLANK(C{r}), C{r}=0), "", ROUND(C{r}*impuestos!$B$3,0))'),
    ("F", "Obra Social", '=IF(OR(ISBLANK(C{r}), C{r}=0), "", ROUND(C{r}*impuestos!$B$4,0))'),
    ("G", "Neto", '=IF(OR(ISBLANK(C{r}), C{r}=0), "", C{r}-D{r}-E{r}-F{r})'),
    ("H", "SAC Bruto", None),
    ("I", "SAC Neto", '=IF(OR(ISBLANK(H{r}), H{r}=0), "", H{r}-ROUND(H{r}*impuestos!$B$2,0)-ROUND(H{r}*impuestos!$B$3,0)-ROUND(H{r}*impuestos!$B$4,0))'),
    ("J", "Bono Neto", None),
    ("K", "Tarjeta Corporativa", None),
    ("L", "Otros Beneficios", None),
    ("M", "Total Neto", '=IF(OR(ISBLANK(G{r}), G{r}=""), "", IFERROR(IF(SUM(G{r}:L{r})=0, "", SUM(G{r}:L{r})), ""))'),
    ("N", "Horas Diarias", None),
    ("O", "Bruto/Hora", '=IF(OR(ISBLANK(C{r}), C{r}=0, ISBLANK(N{r}), N{r}=0), "", ROUND(C{r}/(N{r}*20), 2))'),
    ("P", "Neto/Hora", '=IF(OR(ISBLANK(G{r}), G{r}="", ISBLANK(N{r}), N{r}=0), "", ROUND(G{r}/(N{r}*20), 2))'),
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
    "N": "Horas diarias trabajadas (input manual: 6, 7, 8, etc.)",
    "O": "Bruto por hora = Bruto / (Horas * 20 días)",
    "P": "Neto por hora = Neto / (Horas * 20 días)",
    "Q": "Marca TRUE en ascensos para resetear bases de comparación",
}

# =============================================================================
# ANÁLISIS ARS - V2 con columna auxiliar K_BASE
# =============================================================================

ANALISIS_ARS_GROUPS = [
    ("A", "B", "PERIODO"),
    ("C", "E", "SUELDO"),
    ("F", "K", "VS ÚLTIMO AUMENTO (CER)"),
    ("L", "O", "VS ÚLTIMO AUMENTO (INDEC)"),
    ("P", "S", "VARIACIÓN MENSUAL"),
    ("T", "Y", "PROYECCIÓN REM"),
]

# Definición de columnas con soporte para fórmulas multi-fila
# Formato: (letra, título, fórmula_o_dict, metadata)
# Si fórmula es dict: {"row_3": formula, "row_4_plus": formula, "hidden": bool}

ANALISIS_ARS_COLUMNS = [
    # PERIODO
    ("A", "Periodo", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!A{r}, "")'}),
    (
        "B",
        "Periodo (fecha)",
        {
            "row_3": "=DATE(2023, 10, 1)",
            "row_4_plus": "=EDATE(B{r-1}, 1)",
            "hidden": True,
        },
    ),

    # SUELDO
    ("C", "Fecha", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!B{r}, "")'}),
    ("D", "Bruto/Hora", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!O{r}, "")'}),
    ("E", "Neto/Hora", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!P{r}, "")'}),

    # VS ÚLTIMO AUMENTO (CER)
    (
        "F",
        "Bruto/Hora Base",
        {
            "row_3": '=IF(D3="", "", D3)',
            "row_4_plus": '=IF(D{r}="", "", IF(Ingresos!Q{r-1}=TRUE, D{r-1}, F{r-1}))',
        },
    ),
    (
        "G",
        "Neto/Hora Base",
        {
            "row_3": '=IF(E3="", "", E3)',
            "row_4_plus": '=IF(E{r}="", "", IF(Ingresos!Q{r-1}=TRUE, E{r-1}, G{r-1}))',
        },
    ),
    (
        "H",
        "CER Base",
        {
            "row_3": '=IF(B3="", "", IFERROR(VLOOKUP(EOMONTH(B3,1)+15, historic_data!$A$4:$B, 2, TRUE), 0))',
            "row_4_plus": '=IF(B{r}="", "", IF(Ingresos!Q{r-1}=TRUE, IFERROR(VLOOKUP(EOMONTH(B{r-1},1)+15, historic_data!$A$4:$B, 2, TRUE), 0), H{r-1}))',
        },
    ),
    (
        "I",
        "Paridad CER (Bruto/Hora)",
        {
            "single": '=IF(OR(B{r}="", D{r}="", F{r}="", H{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", F{r} * (cer/H{r}))))',
        },
    ),
    (
        "J",
        "Paridad CER (Neto/Hora)",
        {
            "single": '=IF(OR(B{r}="", E{r}="", G{r}="", H{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", G{r} * (cer/H{r}))))',
        },
    ),
    (
        "K",
        "Poder Adq vs Aumento (CER)",
        {
            "single": '=IF(OR(B{r}="", E{r}="", G{r}="", H{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", (E{r}/G{r}) / (cer/H{r}) - 1)))',
        },
    ),

    # VS ÚLTIMO AUMENTO (INDEC)
    (
        "L",
        "Índice INDEC Actual",
        {
            "row_3": '=IF(B3="", "", LET(mes, B3, infl, IFERROR(VLOOKUP(VALUE(mes), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$N$4:$N}), 2, FALSE), 0), 100 * (1 + infl/100)))',
            "row_4_plus": '=IF(B{r}="", "", LET(mes, B{r}, infl, IFERROR(VLOOKUP(VALUE(mes), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$N$4:$N}), 2, FALSE), 0), L{r-1} * (1 + infl/100)))',
        },
    ),
    # COLUMNA AUXILIAR - SE OCULTARÁ
    (
        "M",
        "INDEC Base",
        {
            "row_3": '=IF(L3="", "", L3)',
            "row_4_plus": '=IF(L{r}="", "", IF(Ingresos!Q{r-1}=TRUE, L{r-1}, M{r-1}))',
            "hidden": True,
        },
    ),
    ("N", "Poder Adq vs REM (%)", {"single": '=IF(E{r}="", "", 0)'}),  # TODO
    (
        "O",
        "Poder Adq vs INDEC (%)",
        {
            "row_3": '=IF(OR(E3="", G3="", L3="", M3=""), "", 0)',
            "row_4_plus": '=IF(OR(E{r}="", G{r}="", L{r}="", M{r}=""), "", (E{r}/G{r}) / (L{r}/M{r}) - 1)',
        },
    ),

    # VARIACIÓN MENSUAL
    (
        "P",
        "Δ% CER MoM",
        {
            "row_3": '=IF(B3="", "", "")',
            "row_4_plus": '=IF(B{r}="", "", LET(d_act, EOMONTH(B{r},1)+15, d_ant, EOMONTH(B{r-1},1)+15, cer_act, IFERROR(VLOOKUP(d_act, historic_data!$A$4:$B, 2, TRUE), 0), cer_ant, IFERROR(VLOOKUP(d_ant, historic_data!$A$4:$B, 2, TRUE), 0), IF(OR(cer_act=0, cer_ant=0), "", (cer_act/cer_ant)-1)))',
        },
    ),
    (
        "Q",
        "Δ% $/Hora vs CER Acum",
        {
            "single": '=IF(OR(B{r}="", D{r}="", F{r}="", H{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", (D{r}/F{r}) / (cer/H{r}) - 1)))',
        },
    ),
    (
        "R",
        "CER Actual",
        {
            "single": '=IF(B{r}="", "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", cer)))',
        },
    ),
    ("S", "CER Base", {"single": '=IF(B{r}="", "", H{r})'}),

    # PROYECCIÓN REM
    (
        "T",
        "REM 3m (%)",
        {
            "single": '=IF(OR(B{r}="", D{r}=""), "", LET(f, B{r}, i1, IFERROR(VLOOKUP(f, REM!$A$4:$I, 3, TRUE), 0), i2, IFERROR(VLOOKUP(f, REM!$A$4:$I, 4, TRUE), 0), i3, IFERROR(VLOOKUP(f, REM!$A$4:$I, 5, TRUE), 0), (1+i1)*(1+i2)*(1+i3)-1))',
        },
    ),
    ("U", "Objetivo 3m Bruto/Hora", {"single": '=IF(OR(B{r}="", D{r}="", T{r}=""), "", D{r} * (1+T{r}))'}),
    ("V", "Objetivo 3m Neto/Hora", {"single": '=IF(OR(B{r}="", E{r}="", T{r}=""), "", E{r} * (1+T{r}))'}),
    (
        "W",
        "REM 6m (%)",
        {
            "single": '=IF(OR(B{r}="", D{r}="", T{r}=""), "", LET(f, B{r}, i4, IFERROR(VLOOKUP(f, REM!$A$4:$I, 6, TRUE), 0), i5, IFERROR(VLOOKUP(f, REM!$A$4:$I, 7, TRUE), 0), i6, IFERROR(VLOOKUP(f, REM!$A$4:$I, 8, TRUE), 0), (1+T{r})*(1+i4)*(1+i5)*(1+i6)-1))',
        },
    ),
    ("X", "Objetivo 6m Bruto/Hora", {"single": '=IF(OR(B{r}="", D{r}="", W{r}=""), "", D{r} * (1+W{r}))'}),
    ("Y", "Objetivo 6m Neto/Hora", {"single": '=IF(OR(B{r}="", E{r}="", W{r}=""), "", E{r} * (1+W{r}))'}),
]

ANALISIS_ARS_FORMATS = {
    "A": {"type": "TEXT", "pattern": "mmmm yyyy"},
    "B": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "C": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "D": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "E": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "F": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "G": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "H": {"type": "NUMBER", "pattern": "0.0000"},
    "I": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "J": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "K": {"type": "PERCENT", "pattern": "0.00%"},
    "L": {"type": "NUMBER", "pattern": "0.00"},
    "M": {"type": "NUMBER", "pattern": "0.00"},
    "N": {"type": "PERCENT", "pattern": "0.00%"},
    "O": {"type": "PERCENT", "pattern": "0.00%"},
    "P": {"type": "PERCENT", "pattern": "0.00%"},
    "Q": {"type": "PERCENT", "pattern": "0.00%"},
    "R": {"type": "NUMBER", "pattern": "0.0000"},
    "S": {"type": "NUMBER", "pattern": "0.0000"},
    "T": {"type": "PERCENT", "pattern": "0.00%"},
    "U": {"type": "CURRENCY", "pattern": "$#,##0"},
    "V": {"type": "CURRENCY", "pattern": "$#,##0"},
    "W": {"type": "PERCENT", "pattern": "0.00%"},
    "X": {"type": "CURRENCY", "pattern": "$#,##0"},
    "Y": {"type": "CURRENCY", "pattern": "$#,##0"},
}

# =============================================================================
# ANÁLISIS USD - V2 sin Paridad USD (16 columnas)
# =============================================================================

ANALISIS_USD_GROUPS = [
    ("A", "B", "PERIODO"),
    ("C", "E", "SUELDO ARS"),
    ("F", "I", "SUELDO USD NOMINAL"),
    ("J", "M", "SUELDO USD REAL"),
    ("N", "Q", "VS ÚLTIMO AUMENTO"),
]

ANALISIS_USD_COLUMNS = [
    # PERIODO
    ("A", "Periodo", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!A{r}, "")'}),
    (
        "B",
        "Periodo (fecha)",
        {
            "row_3": "=DATE(2023, 10, 1)",
            "row_4_plus": "=EDATE(B{r-1}, 1)",
            "hidden": True,
        },
    ),

    # SUELDO ARS
    ("C", "Fecha", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!B{r}, "")'}),
    ("D", "Bruto ARS", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!C{r}, "")'}),
    ("E", "Neto ARS", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!G{r}, "")'}),

    # SUELDO USD NOMINAL
    ("F", "CCL", {"single": '=IF(C{r}="", "", IFERROR(LOOKUP(C{r}, historic_data!$A$4:$A, historic_data!$C$4:$C), ""))'}),
    (
        "G",
        "Δ% CCL MoM",
        {
            "row_3": '=""',
            "row_4_plus": '=IF(F{r}="", "", IFERROR((F{r} - LOOKUP(EOMONTH(C{r},-1), historic_data!$A$4:$A, historic_data!$C$4:$C)) / LOOKUP(EOMONTH(C{r},-1), historic_data!$A$4:$A, historic_data!$C$4:$C), ""))',
        },
    ),
    ("H", "Bruto USD", {"single": '=IF(OR(C{r}="", D{r}="", F{r}=""), "", D{r}/F{r})'}),
    ("I", "Neto USD", {"single": '=IF(OR(C{r}="", E{r}="", F{r}=""), "", E{r}/F{r})'}),

    # SUELDO USD REAL
    (
        "J",
        "CER",
        {
            "single": '=IF(B{r}="", "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", cer)))',
        },
    ),
    ("K", "CCL Real", {"single": '=IF(OR(C{r}="", F{r}="", J{r}="", J$3=""), "", F{r} * (J$3 / J{r}))'}),
    ("L", "Bruto USD Real", {"single": '=IF(OR(C{r}="", D{r}="", K{r}=""), "", D{r}/K{r})'}),
    ("M", "Neto USD Real", {"single": '=IF(OR(C{r}="", E{r}="", K{r}=""), "", E{r}/K{r})'}),

    # VS ÚLTIMO AUMENTO
    (
        "N",
        "CCL Base",
        {
            "row_3": '=IF(F3="", "", F3)',
            "row_4_plus": '=IF(F{r}="", "", IF(Ingresos!Q{r-1}=TRUE, F{r-1}, N{r-1}))',
        },
    ),
    (
        "O",
        "Bruto USD Base",
        {
            "row_3": '=IF(H3="", "", H3)',
            "row_4_plus": '=IF(H{r}="", "", IF(Ingresos!Q{r-1}=TRUE, H{r-1}, O{r-1}))',
        },
    ),
    (
        "P",
        "Neto USD Base",
        {
            "row_3": '=IF(I3="", "", I3)',
            "row_4_plus": '=IF(I{r}="", "", IF(Ingresos!Q{r-1}=TRUE, I{r-1}, P{r-1}))',
        },
    ),
    ("Q", "Variación USD (%)", {"single": '=IF(OR(C{r}="", I{r}="", P{r}=""), "", (I{r}/P{r})-1)'}),
]

ANALISIS_USD_FORMATS = {
    "A": {"type": "TEXT", "pattern": "mmmm yyyy"},
    "B": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "C": {"type": "DATE", "pattern": "dd/mm/yyyy"},
    "D": {"type": "CURRENCY", "pattern": "$#,##0"},
    "E": {"type": "CURRENCY", "pattern": "$#,##0"},
    "F": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "G": {"type": "PERCENT", "pattern": "0.00%"},
    "H": {"type": "NUMBER", "pattern": "#,##0.00"},
    "I": {"type": "NUMBER", "pattern": "#,##0.00"},
    "J": {"type": "NUMBER", "pattern": "0.0000"},
    "K": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "L": {"type": "NUMBER", "pattern": "#,##0.00"},
    "M": {"type": "NUMBER", "pattern": "#,##0.00"},
    "N": {"type": "CURRENCY", "pattern": "$#,##0.00"},
    "O": {"type": "NUMBER", "pattern": "#,##0.00"},
    "P": {"type": "NUMBER", "pattern": "#,##0.00"},
    "Q": {"type": "PERCENT", "pattern": "0.00%"},
}

# =============================================================================
# Helpers para procesar fórmulas multi-fila
# =============================================================================


def get_formula_for_row(col_def: tuple, row_num: int) -> str:
    """Obtiene la fórmula correcta para una fila específica.

    Args:
        col_def: Tupla (letra, título, fórmula_o_dict, ...)
        row_num: Número de fila (3, 4, 5, ...)

    Returns:
        Fórmula con placeholders {r} reemplazados por el número de fila
    """
    col_letter, title, formula_spec = col_def[:3]

    if formula_spec is None:
        return None

    if isinstance(formula_spec, str):
        # Fórmula simple (legacy)
        return formula_spec.replace("{r}", str(row_num))

    if isinstance(formula_spec, dict):
        # Nueva estructura con soporte multi-fila
        if "single" in formula_spec:
            # Una sola fórmula para todas las filas
            formula = formula_spec["single"]
        elif row_num == 3 and "row_3" in formula_spec:
            # Fórmula específica para fila 3
            formula = formula_spec["row_3"]
        elif "row_4_plus" in formula_spec:
            # Fórmula para filas 4+
            formula = formula_spec["row_4_plus"]
        else:
            return None

        # Reemplazar placeholders
        formula = formula.replace("{r}", str(row_num))
        formula = formula.replace("{r-1}", str(row_num - 1))

        return formula

    return None


def is_column_hidden(col_def: tuple) -> bool:
    """Determina si una columna debe ocultarse.

    Args:
        col_def: Tupla (letra, título, fórmula_o_dict, ...)

    Returns:
        True si la columna debe ocultarse
    """
    if len(col_def) < 3:
        return False

    formula_spec = col_def[2]

    if isinstance(formula_spec, dict):
        return formula_spec.get("hidden", False)

    return False


# =============================================================================
# Otras estructuras (sin cambios)
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
    (None, "CER Estimado", None),
    (27, "Inflación Mensual %", "INFLACION_MENSUAL"),
]

SIMULADOR_INFLACION_ROWS = [
    ("Mes (1-12)", "Año", "CER % Estimada", "Estado"),
    (None, None, None, "Ingresá los datos arriba y ejecutá el script"),
]
