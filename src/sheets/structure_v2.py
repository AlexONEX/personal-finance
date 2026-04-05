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
    ("A", "A", "PERIODO"),
    ("B", "D", "SUELDO"),
    ("E", "J", "VS ÚLTIMO AUMENTO (CER)"),
    ("K", "N", "VS ÚLTIMO AUMENTO (INDEC)"),
    ("O", "R", "VARIACIÓN MENSUAL"),
    ("S", "X", "PROYECCIÓN REM"),
]

# Definición de columnas con soporte para fórmulas multi-fila
# Formato: (letra, título, fórmula_o_dict, metadata)
# Si fórmula es dict: {"row_3": formula, "row_4_plus": formula, "hidden": bool}

ANALISIS_ARS_COLUMNS = [
    # PERIODO
    ("A", "Periodo", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!A{r}, "")'}),

    # SUELDO
    ("B", "Fecha", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!B{r}, "")'}),
    ("C", "Bruto/Hora", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!O{r}, "")'}),
    ("D", "Neto/Hora", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!P{r}, "")'}),

    # VS ÚLTIMO AUMENTO (CER)
    (
        "E",
        "Bruto/Hora Base",
        {
            "row_3": '=IF(C3="", "", C3)',
            "row_4_plus": '=IF(C{r}="", "", IF(Ingresos!Q{r-1}=TRUE, C{r-1}, E{r-1}))',
        },
    ),
    (
        "F",
        "Neto/Hora Base",
        {
            "row_3": '=IF(D3="", "", D3)',
            "row_4_plus": '=IF(D{r}="", "", IF(Ingresos!Q{r-1}=TRUE, D{r-1}, F{r-1}))',
        },
    ),
    (
        "G",
        "CER Base",
        {
            "row_3": '=IF(B3="", "", IFERROR(VLOOKUP(EOMONTH(B3,1)+15, historic_data!$A$4:$B, 2, TRUE), 0))',
            "row_4_plus": '=IF(B{r}="", "", IF(Ingresos!Q{r-1}=TRUE, IFERROR(VLOOKUP(EOMONTH(B{r-1},1)+15, historic_data!$A$4:$B, 2, TRUE), 0), G{r-1}))',
        },
    ),
    (
        "H",
        "Paridad CER (Bruto/Hora)",
        {
            "single": '=IF(OR(B{r}="", C{r}="", E{r}="", G{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", E{r} * (cer/G{r}))))',
        },
    ),
    (
        "I",
        "Paridad CER (Neto/Hora)",
        {
            "single": '=IF(OR(B{r}="", D{r}="", F{r}="", G{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", F{r} * (cer/G{r}))))',
        },
    ),
    (
        "J",
        "Poder Adq vs Aumento (CER)",
        {
            "single": '=IF(OR(B{r}="", D{r}="", F{r}="", G{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", (D{r}/F{r}) / (cer/G{r}) - 1)))',
        },
    ),

    # VS ÚLTIMO AUMENTO (INDEC)
    (
        "K",
        "Índice INDEC Actual",
        {
            "row_3": '=IF(B3="", "", LET(mes, DATE(YEAR(B3), MONTH(B3), 1), infl, IFERROR(VLOOKUP(VALUE(mes), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$N$4:$N}), 2, FALSE), 0), 100 * (1 + infl/100)))',
            "row_4_plus": '=IF(B{r}="", "", LET(mes, DATE(YEAR(B{r}), MONTH(B{r}), 1), infl, IFERROR(VLOOKUP(VALUE(mes), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$N$4:$N}), 2, FALSE), 0), K{r-1} * (1 + infl/100)))',
        },
    ),
    # COLUMNA AUXILIAR - SE OCULTARÁ
    (
        "L",
        "INDEC Base",
        {
            "row_3": '=IF(K3="", "", K3)',
            "row_4_plus": '=IF(K{r}="", "", IF(Ingresos!Q{r-1}=TRUE, K{r-1}, L{r-1}))',
            "hidden": True,
        },
    ),
    ("M", "Poder Adq vs REM (%)", {"single": '=IF(D{r}="", "", 0)'}),  # TODO
    (
        "N",
        "Poder Adq vs INDEC (%)",
        {
            "row_3": '=IF(OR(D3="", F3="", K3="", L3=""), "", 0)',
            "row_4_plus": '=IF(OR(D{r}="", F{r}="", K{r}="", L{r}=""), "", (D{r}/F{r}) / (K{r}/L{r}) - 1)',
        },
    ),

    # VARIACIÓN MENSUAL
    (
        "O",
        "Δ% CER MoM",
        {
            "row_3": '=IF(B3="", "", "")',
            "row_4_plus": '=IF(B{r}="", "", LET(d_act, EOMONTH(B{r},1)+15, d_ant, EOMONTH(B{r-1},1)+15, cer_act, IFERROR(VLOOKUP(d_act, historic_data!$A$4:$B, 2, TRUE), 0), cer_ant, IFERROR(VLOOKUP(d_ant, historic_data!$A$4:$B, 2, TRUE), 0), IF(OR(cer_act=0, cer_ant=0), "", (cer_act/cer_ant)-1)))',
        },
    ),
    (
        "P",
        "Δ% $/Hora vs CER Acum",
        {
            "single": '=IF(OR(B{r}="", C{r}="", E{r}="", G{r}=0), "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", (C{r}/E{r}) / (cer/G{r}) - 1)))',
        },
    ),
    (
        "Q",
        "CER Actual",
        {
            "single": '=IF(B{r}="", "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", cer)))',
        },
    ),
    ("R", "CER Base", {"single": '=IF(B{r}="", "", G{r})'}),

    # PROYECCIÓN REM
    (
        "S",
        "REM 3m (%)",
        {
            "single": '=IF(OR(B{r}="", C{r}=""), "", LET(f, EOMONTH(B{r},-1)+1, i1, IFERROR(VLOOKUP(f, REM!$A$4:$I, 3, TRUE), 0), i2, IFERROR(VLOOKUP(f, REM!$A$4:$I, 4, TRUE), 0), i3, IFERROR(VLOOKUP(f, REM!$A$4:$I, 5, TRUE), 0), (1+i1)*(1+i2)*(1+i3)-1))',
        },
    ),
    ("T", "Objetivo 3m Bruto/Hora", {"single": '=IF(OR(B{r}="", C{r}="", S{r}=""), "", C{r} * (1+S{r}))'}),
    ("U", "Objetivo 3m Neto/Hora", {"single": '=IF(OR(B{r}="", D{r}="", S{r}=""), "", D{r} * (1+S{r}))'}),
    (
        "V",
        "REM 6m (%)",
        {
            "single": '=IF(OR(B{r}="", C{r}="", S{r}=""), "", LET(f, EOMONTH(B{r},-1)+1, i4, IFERROR(VLOOKUP(f, REM!$A$4:$I, 6, TRUE), 0), i5, IFERROR(VLOOKUP(f, REM!$A$4:$I, 7, TRUE), 0), i6, IFERROR(VLOOKUP(f, REM!$A$4:$I, 8, TRUE), 0), (1+S{r})*(1+i4)*(1+i5)*(1+i6)-1))',
        },
    ),
    ("W", "Objetivo 6m Bruto/Hora", {"single": '=IF(OR(B{r}="", C{r}="", V{r}=""), "", C{r} * (1+V{r}))'}),
    ("X", "Objetivo 6m Neto/Hora", {"single": '=IF(OR(B{r}="", D{r}="", V{r}=""), "", D{r} * (1+V{r}))'}),
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
    "K": {"type": "NUMBER", "pattern": "0.00"},
    "L": {"type": "NUMBER", "pattern": "0.00"},
    "M": {"type": "PERCENT", "pattern": "0.00%"},
    "N": {"type": "PERCENT", "pattern": "0.00%"},
    "O": {"type": "PERCENT", "pattern": "0.00%"},
    "P": {"type": "PERCENT", "pattern": "0.00%"},
    "Q": {"type": "NUMBER", "pattern": "0.0000"},
    "R": {"type": "NUMBER", "pattern": "0.0000"},
    "S": {"type": "PERCENT", "pattern": "0.00%"},
    "T": {"type": "CURRENCY", "pattern": "$#,##0"},
    "U": {"type": "CURRENCY", "pattern": "$#,##0"},
    "V": {"type": "PERCENT", "pattern": "0.00%"},
    "W": {"type": "CURRENCY", "pattern": "$#,##0"},
    "X": {"type": "CURRENCY", "pattern": "$#,##0"},
}

# =============================================================================
# ANÁLISIS USD - V2 sin Paridad USD (16 columnas)
# =============================================================================

ANALISIS_USD_GROUPS = [
    ("A", "A", "PERIODO"),
    ("B", "D", "SUELDO ARS"),
    ("E", "H", "SUELDO USD NOMINAL"),
    ("I", "L", "SUELDO USD REAL"),
    ("M", "P", "VS ÚLTIMO AUMENTO"),  # Eliminadas columnas P-Q
]

ANALISIS_USD_COLUMNS = [
    # PERIODO
    ("A", "Periodo", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!A{r}, "")'}),

    # SUELDO ARS
    ("B", "Fecha", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!B{r}, "")'}),
    ("C", "Bruto ARS", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!C{r}, "")'}),
    ("D", "Neto ARS", {"single": '=IF(Ingresos!B{r}<>"", Ingresos!G{r}, "")'}),

    # SUELDO USD NOMINAL
    ("E", "CCL", {"single": '=IF(B{r}="", "", IFERROR(LOOKUP(B{r}, historic_data!$A$4:$A, historic_data!$C$4:$C), ""))'}),
    (
        "F",
        "Δ% CCL MoM",
        {
            "row_3": '=""',
            "row_4_plus": '=IF(E{r}="", "", IFERROR((E{r} - LOOKUP(EOMONTH(B{r},-1), historic_data!$A$4:$A, historic_data!$C$4:$C)) / LOOKUP(EOMONTH(B{r},-1), historic_data!$A$4:$A, historic_data!$C$4:$C), ""))',
        },
    ),
    ("G", "Bruto USD", {"single": '=IF(OR(B{r}="", C{r}="", E{r}=""), "", C{r}/E{r})'}),
    ("H", "Neto USD", {"single": '=IF(OR(B{r}="", D{r}="", E{r}=""), "", D{r}/E{r})'}),

    # SUELDO USD REAL
    (
        "I",
        "CER",
        {
            "single": '=IF(B{r}="", "", LET(d, EOMONTH(B{r},1)+15, cer, IFERROR(VLOOKUP(d, historic_data!$A$4:$B, 2, TRUE), 0), IF(cer=0, "", cer)))',
        },
    ),
    ("J", "CCL Real", {"single": '=IF(OR(B{r}="", E{r}="", I{r}="", I$3=""), "", E{r} * (I$3 / I{r}))'}),
    ("K", "Bruto USD Real", {"single": '=IF(OR(B{r}="", C{r}="", J{r}=""), "", C{r}/J{r})'}),
    ("L", "Neto USD Real", {"single": '=IF(OR(B{r}="", D{r}="", J{r}=""), "", D{r}/J{r})'}),

    # VS ÚLTIMO AUMENTO
    (
        "M",
        "CCL Base",
        {
            "row_3": '=IF(E3="", "", E3)',
            "row_4_plus": '=IF(E{r}="", "", IF(Ingresos!Q{r-1}=TRUE, E{r-1}, M{r-1}))',
        },
    ),
    (
        "N",
        "Bruto USD Base",
        {
            "row_3": '=IF(G3="", "", G3)',
            "row_4_plus": '=IF(G{r}="", "", IF(Ingresos!Q{r-1}=TRUE, G{r-1}, N{r-1}))',
        },
    ),
    (
        "O",
        "Neto USD Base",
        {
            "row_3": '=IF(H3="", "", H3)',
            "row_4_plus": '=IF(H{r}="", "", IF(Ingresos!Q{r-1}=TRUE, H{r-1}, O{r-1}))',
        },
    ),
    ("P", "Variación USD (%)", {"single": '=IF(OR(B{r}="", H{r}="", O{r}=""), "", (H{r}/O{r})-1)'}),
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
    "P": {"type": "PERCENT", "pattern": "0.00%"},
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
