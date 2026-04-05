# PLAN EJECUTABLE - Migración a Análisis V2

**Objetivo:** Implementar sistema de análisis de ingresos con fórmulas correctas y validaciones.

**Duración estimada:** 30-45 minutos

---

## PREREQUISITOS

```bash
# 1. Verificar que tengas las variables de entorno
cat .env | grep SPREADSHEET_ID
cat .env | grep GOOGLE_CREDENTIALS_FILE

# 2. Verificar que el archivo de credenciales existe
ls -la service_account.json

# 3. Instalar dependencias si no están
pip install -r requirements.txt
```

---

## PASO 1: BACKUP 📦

**Duración:** 2 minutos

```bash
# Hacer backup del spreadsheet actual
# Ir a: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
# Menu → Archivo → Hacer una copia → Nombrar "BACKUP - [FECHA]"
```

**Verificación:**
- ✅ Tienes una copia de seguridad con fecha de hoy

---

## PASO 2: LIMPIAR CÓDIGO VIEJO 🧹

**Duración:** 1 minuto

```bash
# Eliminar archivos de validación temporal (no los necesitamos)
rm -f validar_*.py
rm -f debug_*.py
rm -f detectar_*.py
rm -f test_*.py
rm -f populate_*.py
rm -f validate_cer_calcs.py

# Eliminar scripts de setup viejos (reemplazados por V2)
rm -f update_analisis_ars.py
rm -f update_analisis_usd.py
rm -f update_ingresos_and_analisis.py

# Verificar qué queda
ls *.py
```

**Deben quedar solo estos:**
- `main.py` - Orquestador principal
- `fetch_data.py` - Fetch de datos históricos
- `setup_sheet.py` - Setup general
- `mark_ascensos.py` - Marcar ascensos en Ingresos
- `setup_analisis_v2.py` - **NUEVO** Setup Análisis V2
- `validate_analisis.py` - **NUEVO** Validador
- `bootstrap.py` - Setup inicial
- `upload_to_inversiones.py` - Upload a otra sheet
- `fetch_portfolio_evolution.py` - Portfolio data
- `setup_dashboard.py` - Dashboard
- `generate_columnas_doc.py` - Documentación
- `plot_rem_curves.py` - Gráficos REM

---

## PASO 3: MARCAR ASCENSOS 📌

**Duración:** 2 minutos

**¿Por qué?** Las fórmulas V2 necesitan saber cuándo hubo ascensos para resetear bases.

```bash
# Ejecutar script que marca los 2 ascensos
python mark_ascensos.py
```

**Verificación en Google Sheets:**
1. Ir a tab "Ingresos"
2. Verificar columna Q (¿Ascenso?)
3. Debe haber TRUE en:
   - Fila donde fecha = 02/12/2024 (Dic 2024)
   - Fila donde fecha = 01/08/2025 (Ago 2025)

**Si no aparecen:**
```bash
# Ver las fechas en el script
grep "ASCENSOS = " mark_ascensos.py

# Verificar formato en tu sheet Ingresos columna B (Fecha)
# Debe ser dd/mm/yyyy (ej: 02/12/2024)
```

---

## PASO 4: SETUP ANÁLISIS V2 🚀

**Duración:** 15-20 minutos

```bash
# Ejecutar setup completo
python setup_analisis_v2.py --all
```

**¿Qué hace esto?**
1. Crea/actualiza tab "Análisis ARS" con 24 columnas
2. Crea/actualiza tab "Análisis USD" con 16 columnas
3. Genera ~2000 fórmulas individuales
4. Oculta columna auxiliar K_BASE
5. Aplica formatos y colores

**Progreso esperado:**
```
Configurando Análisis ARS V2...
  Limpiando fórmulas viejas...
  Generando fórmulas por fila...
  Aplicando 120 bloques de fórmulas...
    Aplicado batch 1/2
    Aplicado batch 2/2
  Aplicando formatos...
  Ocultando columna K_BASE
✅ Análisis ARS V2 configurado correctamente

Configurando Análisis USD V2...
  [similar output]
✅ Análisis USD V2 configurado correctamente
```

**Verificación:**
1. Ir a Google Sheets
2. Abrir tab "Análisis ARS"
3. Debe tener headers en rows 1-2
4. Debe tener datos desde row 3
5. Columna K_BASE NO debe ser visible (está oculta)
6. Los números deben aparecer después de ~2 minutos (Google Sheets calculando)

---

## PASO 5: ESPERAR CÁLCULO ⏳

**Duración:** 2-3 minutos

Google Sheets necesita tiempo para calcular todas las fórmulas.

**Indicadores de que está calculando:**
- Spinner arriba a la derecha en Google Sheets
- Algunas celdas muestran "Loading..."
- CPU alta en tu navegador

**¿Cuándo está listo?**
- Todas las celdas muestran números
- No hay "Loading..." ni "#N/A" (salvo errores reales)
- El spinner desapareció

---

## PASO 6: VALIDACIÓN VISUAL 👀

**Duración:** 5 minutos

### Check Análisis ARS - Fila 3 (Oct 2023)

Ir a tab "Análisis ARS", fila 3:

| Col | Nombre | Valor Esperado | ¿Correcto? |
|-----|--------|----------------|------------|
| A | Periodo | "octubre 2023" | ⬜ |
| C | Bruto/Hora | ~2,000 | ⬜ |
| E | Bruto/Hora Base | = C3 (igual a Bruto/Hora) | ⬜ |
| G | CER Base | ~173.79 | ⬜ |
| K | Índice INDEC | ~108.3 | ⬜ |
| J | Poder Adq vs CER | 0% (primera fila) | ⬜ |
| M | Poder Adq vs INDEC | 0% (primera fila) | ⬜ |

### Check Análisis ARS - Fila 15 (Dic 2024 - Primer Ascenso)

| Col | Nombre | Valor Esperado | ¿Correcto? |
|-----|--------|----------------|------------|
| E | Bruto/Hora Base | ≠ fila anterior (RESET) | ⬜ |
| G | CER Base | ~535.55 (RESET) | ⬜ |
| J | Poder Adq vs CER | ~100% a 120% (muy positivo) | ⬜ |

### Check Análisis USD - Fila 3 (Oct 2023)

| Col | Nombre | Valor Esperado | ¿Correcto? |
|-----|--------|----------------|------------|
| E | CCL | Valor del CCL (~$300-400) | ⬜ |
| G | Bruto USD | Bruto ARS / CCL | ⬜ |
| M | CCL Base | = E3 | ⬜ |

**¿Hay errores?**
- Si ves `#REF!` → Problema con referencias entre sheets
- Si ves `#VALUE!` → Problema con tipo de datos
- Si ves `#N/A` → VLOOKUP no encuentra el valor

---

## PASO 7: VALIDACIÓN AUTOMÁTICA 🤖

**Duración:** 3 minutos

```bash
# Ejecutar validador
python validate_analisis.py
```

**Output esperado:**
```
VALIDACIÓN DE ANÁLISIS ARS Y USD
================================================================================

Conectando a spreadsheet: {SPREADSHEET_ID}

--------------------------------------------------------------------------------
1. VALIDACIONES DE COHERENCIA
--------------------------------------------------------------------------------
✅ Análisis ARS leído correctamente
✅ Análisis USD leído correctamente

✅ No se encontraron problemas de coherencia

--------------------------------------------------------------------------------
2. VALIDACIONES CONTRA CÁLCULOS MANUALES
--------------------------------------------------------------------------------
✅ Todos los cálculos manuales coinciden

================================================================================
RESUMEN FINAL
================================================================================
✅ ÉXITO: Todas las validaciones pasaron
```

**Si hay errores:**
1. Lee el output detalladamente
2. Identifica la fila/columna con problema
3. Ve al spreadsheet y revisa manualmente
4. Busca en `docs/DEFINICION_COLUMNAS_ANALISIS.md` la definición de esa columna
5. Verifica que la fórmula sea correcta

**Errores comunes:**

| Error | Causa | Solución |
|-------|-------|----------|
| "Columna Base cambió sin ascenso" | Fórmula incorrecta | Revisar fórmula de columna E/F/G |
| "Índice no es monotónicamente creciente" | Dato de inflación faltante | Ejecutar `python fetch_data.py --since 2023-10-01` |
| "Porcentaje fuera de rango" | Fórmula incorrecta o dato malo | Revisar fórmula y datos source |

---

## PASO 8: VALIDACIÓN MANUAL (OPCIONAL) 🔍

**Duración:** 10 minutos

Si querés estar 100% seguro, validar contra los cálculos manuales:

```bash
# Abrir el documento con cálculos de referencia
cat docs/CALCULO_MANUAL_METRICAS.md
```

**Verificar Período 1 (Oct 23 → Dic 24):**

En Análisis ARS, encontrar la fila de Dic 2024 (fila ~15):

```
Valor esperado columna J (Poder Adq vs CER):
Según docs: +106.6%

Valor en sheet: _______%

¿Coinciden? ⬜ SÍ  ⬜ NO (diferencia <5% es aceptable)
```

**Verificar Período 2 (Dic 24 → Ago 25):**

En Análisis ARS, encontrar la fila de Ago 2025 (fila ~23):

```
Valor esperado columna J (Poder Adq vs CER):
Según docs: +20.5%

Valor en sheet: _______%

¿Coinciden? ⬜ SÍ  ⬜ NO (diferencia <5% es aceptable)
```

---

## PASO 9: COMMIT CAMBIOS 💾

**Duración:** 2 minutos

```bash
# Ver cambios
git status

# Agregar archivos nuevos y modificados
git add .

# Commit
git commit -m "feat: implement Análisis V2 with simplified formulas and validators

- Added structure_v2.py with multi-row formula support
- Added K_BASE auxiliary column for INDEC tracking
- Removed Paridad USD columns (P-Q) from Análisis USD
- Created coherence validators
- Created manual validation script
- Cleaned up temporary debug/test files

Closes #[número-de-issue]"

# Push
git push origin improve-refactor
```

---

## PASO 10: DOCUMENTAR RESULTADOS 📝

**Duración:** 5 minutos

Crear un archivo con los resultados de validación:

```bash
# Copiar output de validación
python validate_analisis.py > validation_results.txt

# Ver resumen en Análisis ARS
# Anotar métricas clave:
```

**Template de resultados:**

```markdown
# Resultados Validación Análisis V2
**Fecha:** $(date +%Y-%m-%d)

## Poder Adquisitivo Real (columna J - Análisis ARS)

### Período 1: Oct 2023 → Dic 2024
- Variación vs CER: _____%
- Estado: ✅ Ganancia / ❌ Licuación

### Período 2: Dic 2024 → Ago 2025
- Variación vs CER: _____%
- Estado: ✅ Ganancia / ❌ Licuación

### Período 3: Ago 2025 → Hoy
- Variación vs CER: _____%
- Estado: ✅ Ganancia / ❌ Licuación

## Acumulado Total (Oct 2023 → Hoy)
- Variación vs CER: _____%
- Variación vs INDEC: _____%

## Sueldo en USD (columna P - Análisis USD)

### Variación USD desde último ascenso:
- Variación: _____%
- Estado: ✅ Ganancia / ❌ Licuación cambiaria
```

---

## TROUBLESHOOTING 🔧

### Error: "SPREADSHEET_ID not found"
```bash
# Verificar .env
cat .env | grep SPREADSHEET_ID

# Si no existe, crear:
echo 'SPREADSHEET_ID="tu-spreadsheet-id"' >> .env
```

### Error: "Permission denied" al ejecutar scripts
```bash
# Dar permisos de ejecución
chmod +x *.py
```

### Error: Fórmulas no calculan en Google Sheets
1. Refrescar la página (Ctrl+R / Cmd+R)
2. Esperar 2-3 minutos
3. Si persiste, verificar que no haya referencias circulares

### Error: Columna K_BASE visible
```bash
# Re-ejecutar setup para ocultarla
python setup_analisis_v2.py --ars
```

### Error: Valores muy diferentes a los esperados
1. Verificar que los datos de `historic_data` estén completos:
```bash
# Fetch datos desde Oct 2023
python fetch_data.py --since 2023-10-01
```

2. Verificar que el matching de fechas sea correcto:
   - CER: sueldo mes M → CER día 15 mes M+1
   - IPC: sueldo mes M → IPC mes M

---

## CHECKLIST FINAL ✅

Antes de dar por terminado:

- ⬜ Backup del spreadsheet creado
- ⬜ Archivos temporales eliminados
- ⬜ Ascensos marcados correctamente (2 TRUE en Ingresos!Q)
- ⬜ Setup V2 ejecutado sin errores
- ⬜ Google Sheets terminó de calcular (sin "Loading...")
- ⬜ Validación visual pasada (fila 3, fila 15, fila 23)
- ⬜ Validación automática pasada (0 errores críticos)
- ⬜ Columna K_BASE oculta
- ⬜ Métricas principales tienen sentido:
  - ⬜ Período 1: +100% a +120% poder adquisitivo
  - ⬜ Período 2: +15% a +25% poder adquisitivo
  - ⬜ Período 3: Verificar si hay licuación
- ⬜ Cambios committeados
- ⬜ Resultados documentados

---

## SIGUIENTES PASOS 🚀

Una vez completado este plan:

1. **Usar las métricas** para negociaciones salariales
2. **Monitorear trimestral:** Re-ejecutar validaciones cada 3 meses
3. **Optimizar (opcional):** Convertir a ARRAYFORMULA si performance es problema
4. **Extender:** Implementar columna L (Poder Adq vs REM)

---

## AYUDA 🆘

Si algo no funciona:

1. **Revisar documentación:**
   - `docs/ANALISIS_V2_README.md` - Manual completo
   - `docs/DEFINICION_COLUMNAS_ANALISIS.md` - Spec de cada columna
   - `docs/CALCULO_MANUAL_METRICAS.md` - Valores de referencia

2. **Verificar logs:**
   ```bash
   # Re-ejecutar con más output
   python setup_analisis_v2.py --all 2>&1 | tee setup.log
   ```

3. **Validar datos source:**
   ```bash
   # Ver si hay datos de CER e IPC
   python -c "
   from src.connectors.sheets import get_sheets_client
   import os
   ss = get_sheets_client().open_by_key(os.getenv('SPREADSHEET_ID'))
   print('CER rows:', len(ss.worksheet('historic_data').get_all_values()))
   print('IPC rows:', len(ss.worksheet('CPI').get_all_values()))
   "
   ```

---

**FIN DEL PLAN**

¿Todo OK? ✅ Celebrá 🎉
