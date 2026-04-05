# Análisis V2 - Sistema de Fórmulas y Validaciones

## Resumen

Sistema rediseñado para análisis de ingresos con:
- **Fórmulas simplificadas** (sin ARRAYFORMULA) para facilitar debugging
- **Columna auxiliar** K_BASE para trackear índice INDEC en ascensos
- **Análisis USD reducido** de 18 a 16 columnas (eliminadas Paridad USD)
- **Validadores de coherencia** automatizados
- **Validación contra cálculos manuales**

## Estructura de Archivos

```
src/
├── sheets/
│   ├── structure.py           # V1 (legacy con ARRAYFORMULA)
│   └── structure_v2.py         # V2 (fórmulas simplificadas) ✨ NUEVO
├── setup/
│   ├── analisis_ars.py        # V1
│   ├── analisis_usd.py        # V1
│   └── analisis_v2.py          # V2 ✨ NUEVO
└── validators/
    ├── analisis_coherence.py   # Validador de coherencia ✨ NUEVO
    └── __init__.py

docs/
├── CALCULO_MANUAL_METRICAS.md  # Cálculos de referencia
├── DEFINICION_COLUMNAS_ANALISIS.md  # Spec completa
├── STRUCTURE_SUMMARY.md        # Resumen de estructura
└── ANALISIS_V2_README.md       # Este archivo

Scripts raíz:
├── setup_analisis_v2.py        # Script principal de setup ✨ NUEVO
└── validate_analisis.py        # Script de validación ✨ NUEVO
```

## Cambios vs V1

### Análisis ARS (24 columnas)
- ✅ **Agregada:** Columna auxiliar `K_BASE` (INDEC Base) - se oculta
- ✅ **Simplificadas:** Fórmulas sin SCAN/ARRAYFORMULA
- ✅ **Mejorado:** Matching correcto de CER (día 15 mes M+1)

### Análisis USD (16 columnas, antes 18)
- ✅ **Eliminadas:** Columnas P-Q (Paridad USD) - no tenían sentido
- ✅ **Simplificadas:** Fórmulas sin SCAN
- ✅ **Renombrada:** Columna R → P (Variación USD %)

## Uso

### 1. Setup Inicial

```bash
# Setup completo (ambas sheets)
python setup_analisis_v2.py --all

# Solo Análisis ARS
python setup_analisis_v2.py --ars

# Solo Análisis USD
python setup_analisis_v2.py --usd
```

**IMPORTANTE:** El script genera ~1000 fórmulas individuales. Puede tardar 5-10 minutos.

### 2. Validación

```bash
# Validar coherencia de datos
python validate_analisis.py
```

El validador verifica:
- ✅ Columnas "Base" solo cambian en ascensos
- ✅ Índices (CER, INDEC) son monotónicamente crecientes
- ✅ Porcentajes en rangos razonables (-50% a +500%)
- ✅ No hay valores absurdos (NaN, Inf)
- ✅ Valores positivos donde corresponde

### 3. Workflow Recomendado

```bash
# 1. Setup
python setup_analisis_v2.py --all

# 2. Esperar a que Google Sheets calcule (~1-2 min)

# 3. Validar
python validate_analisis.py

# 4. Si hay errores, revisar y corregir

# 5. Re-validar
python validate_analisis.py
```

## Columnas Clave

### Análisis ARS

| Columna | Nombre | Propósito | Reset en Ascenso |
|---------|--------|-----------|------------------|
| **E** | Bruto/Hora Base | Sueldo base del último ascenso | ✅ SÍ |
| **F** | Neto/Hora Base | Sueldo neto base | ✅ SÍ |
| **G** | CER Base | CER del último ascenso | ✅ SÍ |
| **J** | Poder Adq vs CER | **MÉTRICA PRINCIPAL** | ❌ NO |
| **K** | Índice INDEC Actual | Inflación acumulada (base 100) | ❌ NO |
| **K_BASE** | INDEC Base (oculta) | Índice del último ascenso | ✅ SÍ |
| **M** | Poder Adq vs INDEC | Variación real vs IPC Nacional | ❌ NO |
| **P** | CER Actual | CER del período | ❌ NO |

### Análisis USD

| Columna | Nombre | Propósito | Reset en Ascenso |
|---------|--------|-----------|------------------|
| **G** | Bruto USD | Sueldo en USD nominal | ❌ NO |
| **H** | Neto USD | Neto en USD nominal | ❌ NO |
| **K** | Bruto USD Real | Ajustado por inflación | ❌ NO |
| **L** | Neto USD Real | Ajustado por inflación | ❌ NO |
| **M** | CCL Base | CCL del último ascenso | ✅ SÍ |
| **N** | Bruto USD Base | Bruto USD base | ✅ SÍ |
| **O** | Neto USD Base | Neto USD base | ✅ SÍ |
| **P** | Variación USD (%) | **MÉTRICA PRINCIPAL** | ❌ NO |

## Matching de Datos

### CER (Coeficiente de Estabilización de Referencia)

**Lógica:** Sueldo mes M → CER día 15 del mes M+1

```
Ejemplo:
Sueldo cobrado: 30/10/2023
CER a usar: 15/12/2023

¿Por qué? El CER incorpora la inflación de octubre recién a mediados de diciembre
(hay ~2 meses de rezago en la publicación del BCRA)
```

**Fórmula:**
```excel
=LET(
  fecha_cer, EOMONTH(fecha_sueldo, 1) + 15,
  cer, VLOOKUP(fecha_cer, historic_data!$A$4:$B, 2, TRUE),
  cer
)
```

### IPC INDEC (Índice de Precios al Consumidor)

**Lógica:** Sueldo mes M → IPC mes M

```
Ejemplo:
Sueldo cobrado: 30/10/2023
IPC a usar: Inflación de octubre 2023 (8.3%)

Dato en CPI!A: 01/10/2023
```

**Fórmula:**
```excel
=LET(
  mes, DATE(YEAR(fecha_sueldo), MONTH(fecha_sueldo), 1),
  inflacion, VLOOKUP(VALUE(mes), ARRAYFORMULA({VALUE(CPI!$A$4:$A), CPI!$C$4:$C}), 2, FALSE),
  inflacion
)
```

**IMPORTANTE:** Usamos `VALUE()` para convertir fechas a números y hacer matching exacto.

## Fórmulas con Variantes

Algunas columnas tienen fórmulas diferentes para fila 3 vs fila 4+:

### Ejemplo: Bruto/Hora Base (Columna E)

```python
{
    "row_3": '=IF(C3="", "", C3)',  # Primera fila: copiar valor actual
    "row_4_plus": '=IF(C{r}="", "", IF(Ingresos!Q{r}=TRUE, C{r}, E{r-1}))'  # Filas siguientes: resetear si hay ascenso, sino mantener anterior
}
```

**Traducción fila 4:**
```excel
=IF(C4="", "", IF(Ingresos!Q4=TRUE, C4, E3))
```

Si hay ascenso (Q4=TRUE), usar valor actual (C4).
Sino, mantener base anterior (E3).

## Columna Auxiliar K_BASE

**Problema:** Necesitamos saber el índice INDEC del último ascenso para calcular variación real.

**Solución:** Columna auxiliar que se resetea en ascensos.

**Fórmula fila 4+:**
```excel
=IF(K4="", "", IF(Ingresos!Q4=TRUE, K4, K_BASE3))
```

**Uso en columna M (Poder Adq vs INDEC):**
```excel
=IF(OR(D4="", F4="", K4="", K_BASE4=""), "",
   (D4/F4) / (K4/K_BASE4) - 1
)
```

**Práctica Excel:** Las columnas auxiliares se crean y se ocultan visualmente, pero permanecen en el sheet. Son transparentes para el usuario final pero esenciales para cálculos.

## Validadores

### 1. AnalisisCoherenceValidator

Valida coherencia lógica de datos:

```python
from src.validators.analisis_coherence import AnalisisCoherenceValidator, Severity

validator = AnalisisCoherenceValidator()

# Validar que bases solo cambien en ascensos
validator.validate_base_columns_reset_on_ascenso(
    sheet_name="Análisis ARS",
    ascenso_col=ascensos,
    base_cols={"E": bruto_base, "F": neto_base, "G": cer_base},
    base_col_names=["E", "F", "G"]
)

# Validar índice monotónicamente creciente
validator.validate_monotonic_increasing(
    sheet_name="Análisis ARS",
    column_name="K",
    values=indice_indec,
    allow_equal=True
)

# Validar porcentajes razonables
validator.validate_percentage_range(
    sheet_name="Análisis ARS",
    column_name="J",
    values=poder_adq_cer,
    min_pct=-0.5,  # -50%
    max_pct=5.0,   # +500%
    warning_threshold=0.3  # Warning si > 30%
)
```

### 2. Severidades

| Severidad | Descripción | Bloquea Deploy |
|-----------|-------------|----------------|
| **CRITICAL** | Valores absurdos (NaN, Inf, negativos donde no corresponde) | ✅ SÍ |
| **ERROR** | Lógica incorrecta (base cambia sin ascenso, índice decrece) | ✅ SÍ |
| **WARNING** | Valores inusuales pero posibles (variación >30%) | ❌ NO |
| **INFO** | Información para revisar | ❌ NO |

## Troubleshooting

### Error: "Fórmulas muy lentas"

**Causa:** Google Sheets está calculando 1000+ fórmulas.

**Solución:**
1. Esperar 2-3 minutos después del setup
2. Verificar que no haya errores circulares
3. Si persiste, reducir MAX_ROWS en src/config.py

### Error: "Columna K_BASE no se encuentra"

**Causa:** La columna auxiliar está oculta.

**Solución:**
1. En Google Sheets, click derecho en header de columna L
2. "Mostrar columna K_BASE"
3. Verificar que tiene datos
4. Volver a ocultar

### Error: "CER no se encuentra para fecha X"

**Causa:** Datos faltantes en historic_data.

**Solución:**
```bash
# Fetch datos faltantes
python fetch_data.py --since 2023-10-01
```

### Warning: "Porcentaje inusualmente alto"

**Causa:** Variación >30% en poder adquisitivo.

**¿Es esperado?**
- Período 1 (Oct 23 → Dic 24): SÍ, +100% es correcto (ascenso grande + inflación alta)
- Período 2-3: Probablemente NO, revisar fórmulas

## Testing Manual

### Checklist de Validación

Verificar estos valores manualmente en el spreadsheet:

**Fila 3 (Oct 2023):**
- [ ] E3 (Bruto/Hora Base) = C3 (debe copiar)
- [ ] F3 (Neto/Hora Base) = D3 (debe copiar)
- [ ] G3 (CER Base) ≈ 173.79 (CER del 15/12/2023)
- [ ] K3 (INDEC) ≈ 108.3 (100 × 1.083)
- [ ] K_BASE3 = K3 (debe copiar)
- [ ] J3 (Poder Adq CER) = 0 (primera fila)
- [ ] M3 (Poder Adq INDEC) = 0 (primera fila)

**Fila 15 (Dic 2024 - Primer Ascenso):**
- [ ] Ingresos!Q15 = TRUE (ascenso marcado)
- [ ] E15 = C15 (RESET: nuevo base)
- [ ] F15 = D15 (RESET: nuevo base)
- [ ] G15 ≈ 535.55 (RESET: CER del 15/01/2025)
- [ ] K_BASE15 = K15 (RESET: nuevo índice base)
- [ ] J15 ≈ 1.06 (+106% poder adq desde Oct 2023)

**Fila 23 (Ago 2025 - Segundo Ascenso):**
- [ ] Ingresos!Q23 = TRUE (ascenso marcado)
- [ ] E23 = C23 (RESET)
- [ ] G23 ≈ 639.78 (RESET)
- [ ] K_BASE23 = K23 (RESET)
- [ ] J23 ≈ 0.20 (+20% desde Dic 2024)

**Fila 30 (Abr 2026 - Actual):**
- [ ] E30 = E23 (sin cambios desde Ago 2025)
- [ ] J30 < 0 (licuación esperada)
- [ ] M30 < 0 (licuación vs INDEC)

## Próximos Pasos

### Fase 1: Validación ✅
- [x] Documentar columnas
- [x] Crear fórmulas V2
- [x] Crear validadores
- [ ] Testear con datos reales
- [ ] Validar contra cálculos manuales

### Fase 2: Optimización (Futuro)
- [ ] Convertir a ARRAYFORMULA columna por columna
- [ ] Validar que ARRAYFORMULA da mismos resultados
- [ ] Benchmark performance (V1 vs V2)
- [ ] Decidir si mantener V2 o migrar a V1 optimizada

### Fase 3: Features Adicionales
- [ ] Implementar columna L (Poder Adq vs REM)
- [ ] Agregar gráficos automatizados
- [ ] Dashboard de alertas (licuación >5%)
- [ ] Notificaciones automáticas

## Referencias

- **Cálculos Manuales:** `docs/CALCULO_MANUAL_METRICAS.md`
- **Spec Completa:** `docs/DEFINICION_COLUMNAS_ANALISIS.md`
- **Estructura:** `docs/STRUCTURE_SUMMARY.md`
- **Código:** `src/sheets/structure_v2.py`
