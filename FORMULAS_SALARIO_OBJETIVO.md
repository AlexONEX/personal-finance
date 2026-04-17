# Fórmulas: Salario Objetivo y Variación Mensual

## 1. Salario Objetivo para Paridad con Inflación

**Desde último ascenso (julio 2025):**

```excel
=LET(
    periodos_texto, Ingresos!A3:A1000,
    sueldos, Ingresos!F3:F1000,
    ascensos, Ingresos!Q3:Q1000,

    periodos_fechas, MAP(periodos_texto, LAMBDA(pt,
        IF(pt="", "",
            LET(
                year, VALUE(RIGHT(pt, 4)),
                mes_texto, TRIM(LEFT(pt, LEN(pt)-5)),
                mes_num, SWITCH(LOWER(mes_texto),
                    "enero", 1, "febrero", 2, "marzo", 3, "abril", 4,
                    "mayo", 5, "junio", 6, "julio", 7, "agosto", 8,
                    "septiembre", 9, "octubre", 10, "noviembre", 11, "diciembre", 12,
                    0
                ),
                IF(mes_num=0, "", DATE(year, mes_num, 1))
            )
        )
    )),

    inflaciones_mensuales, MAP(periodos_fechas, LAMBDA(pf,
        IF(pf="", 0,
            IFERROR(
                VLOOKUP(
                    VALUE(pf),
                    ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$N$4:$N}),
                    2,
                    FALSE
                ),
                0
            )
        )
    )),

    ipc_mensuales, SCAN(0, SEQUENCE(ROWS(periodos_texto)), LAMBDA(acc, i,
        LET(
            inflacion, INDEX(inflaciones_mensuales, i),
            IF(inflacion=0, 0,
                IF(i=1,
                    100 * (1 + inflacion/100),
                    acc * (1 + inflacion/100)
                )
            )
        )
    )),

    bases, SCAN({Ingresos!F3, INDEX(ipc_mensuales, 1)},
        SEQUENCE(ROWS(periodos_texto)), LAMBDA(acc, i,
            IF(INDEX(ascensos, i)=TRUE,
                {INDEX(sueldos, i), INDEX(ipc_mensuales, i)},
                acc
            )
        )
    ),

    sueldos_base, CHOOSECOLS(bases, 1),
    ipc_base, CHOOSECOLS(bases, 2),

    ARRAYFORMULA(
        IF((periodos_texto="")+(ipc_base=0)+(ipc_mensuales=0), "",
            sueldos_base * (ipc_mensuales / ipc_base)
        )
    )
)
```

**Desde último aumento (noviembre 2025):**

Usa la misma fórmula pero cambia la lógica del SCAN para capturar **cualquier cambio de sueldo**:

```excel
=LET(
    periodos_texto, Ingresos!A3:A1000,
    sueldos, Ingresos!F3:F1000,

    periodos_fechas, MAP(periodos_texto, LAMBDA(pt,
        IF(pt="", "",
            LET(
                year, VALUE(RIGHT(pt, 4)),
                mes_texto, TRIM(LEFT(pt, LEN(pt)-5)),
                mes_num, SWITCH(LOWER(mes_texto),
                    "enero", 1, "febrero", 2, "marzo", 3, "abril", 4,
                    "mayo", 5, "junio", 6, "julio", 7, "agosto", 8,
                    "septiembre", 9, "octubre", 10, "noviembre", 11, "diciembre", 12,
                    0
                ),
                IF(mes_num=0, "", DATE(year, mes_num, 1))
            )
        )
    )),

    inflaciones_mensuales, MAP(periodos_fechas, LAMBDA(pf,
        IF(pf="", 0,
            IFERROR(
                VLOOKUP(
                    VALUE(pf),
                    ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$N$4:$N}),
                    2,
                    FALSE
                ),
                0
            )
        )
    )),

    ipc_mensuales, SCAN(0, SEQUENCE(ROWS(periodos_texto)), LAMBDA(acc, i,
        LET(
            inflacion, INDEX(inflaciones_mensuales, i),
            IF(inflacion=0, 0,
                IF(i=1,
                    100 * (1 + inflacion/100),
                    acc * (1 + inflacion/100)
                )
            )
        )
    )),

    bases, SCAN({Ingresos!F3, INDEX(ipc_mensuales, 1)},
        SEQUENCE(ROWS(periodos_texto)), LAMBDA(acc, i,
            IF(i=1,
                {INDEX(sueldos, 1), INDEX(ipc_mensuales, 1)},
                IF(INDEX(sueldos, i) <> INDEX(sueldos, i-1),
                    {INDEX(sueldos, i), INDEX(ipc_mensuales, i)},
                    acc
                )
            )
        )
    ),

    sueldos_base, CHOOSECOLS(bases, 1),
    ipc_base, CHOOSECOLS(bases, 2),

    ARRAYFORMULA(
        IF((periodos_texto="")+(ipc_base=0)+(ipc_mensuales=0), "",
            sueldos_base * (ipc_mensuales / ipc_base)
        )
    )
)
```

## 2. Salario Objetivo Real +10%

Multiplica el resultado anterior por 1.10:

```excel
=IF(COLUMNA_PARIDAD="", "", COLUMNA_PARIDAD * 1.10)
```

O integrado en la fórmula (última línea):

```excel
ARRAYFORMULA(
    IF((periodos_texto="")+(ipc_base=0)+(ipc_mensuales=0), "",
        sueldos_base * (ipc_mensuales / ipc_base) * 1.10
    )
)
```

## 3. Salario Objetivo Real +20%

```excel
=IF(COLUMNA_PARIDAD="", "", COLUMNA_PARIDAD * 1.20)
```

O integrado:

```excel
ARRAYFORMULA(
    IF((periodos_texto="")+(ipc_base=0)+(ipc_mensuales=0), "",
        sueldos_base * (ipc_mensuales / ipc_base) * 1.20
    )
)
```

## 4. Δ% Sueldo MoM (Variación Mensual)

Calcula el cambio porcentual del sueldo respecto al mes anterior:

```excel
=ARRAYFORMULA(
    IF(Ingresos!F3:F1000="", "",
        IF(ROW(Ingresos!F3:F1000)=ROW(Ingresos!F3), "",
            (Ingresos!F3:F1000 / OFFSET(Ingresos!F3:F1000, -1, 0, ROWS(Ingresos!F3:F1000), 1)) - 1
        )
    )
)
```

**Versión más simple:**

```excel
=ARRAYFORMULA(
    IF(Ingresos!F3:F1000="", "",
        IF(ROW(Ingresos!F3:F1000)=3, "",
            (Ingresos!F3:F1000 / OFFSET(Ingresos!F3:F1000, -1, 0)) - 1
        )
    )
)
```

**Versión con LAMBDA y MAP:**

```excel
=LET(
    sueldos, Ingresos!F3:F1000,

    MAP(SEQUENCE(ROWS(sueldos)), LAMBDA(i,
        IF(INDEX(sueldos, i)="", "",
            IF(i=1, "",
                (INDEX(sueldos, i) / INDEX(sueldos, i-1)) - 1
            )
        )
    ))
)
```

## Resumen de Columnas

| Columna | Descripción | Base |
|---------|-------------|------|
| **Salario Paridad (Ascenso)** | Sueldo para mantener poder adquisitivo desde último ascenso | Julio 2025 |
| **Salario +10% (Ascenso)** | Paridad × 1.10 | Julio 2025 |
| **Salario +20% (Ascenso)** | Paridad × 1.20 | Julio 2025 |
| **Salario Paridad (Aumento)** | Sueldo para mantener poder adquisitivo desde último aumento | Noviembre 2025 |
| **Salario +10% (Aumento)** | Paridad × 1.10 | Noviembre 2025 |
| **Salario +20% (Aumento)** | Paridad × 1.20 | Noviembre 2025 |
| **Δ% Sueldo MoM** | Variación % del sueldo vs mes anterior | - |

## Ejemplos

**Marzo 2026:**
- Último ascenso: julio 2025 ($2,200,919)
- Último aumento: noviembre 2025 ($2,421,011)
- Inflación acumulada jul 2025 → mar 2026: ~14.5%
- Inflación acumulada nov 2025 → mar 2026: ~8.5%

**Resultados esperados:**
- Salario Paridad (Ascenso): $2,200,919 × 1.145 ≈ $2,520,052
- Salario +10% (Ascenso): $2,520,052 × 1.10 ≈ $2,772,057
- Salario Paridad (Aumento): $2,421,011 × 1.085 ≈ $2,626,797
- Δ% Sueldo feb→mar 2026: 0% (sin cambio)
