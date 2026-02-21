# Diccionario de Columnas - Hoja 'Ingresos'

Este documento describe todas las columnas de la hoja de cálculo "Ingresos".

## 1. DATOS BASE & INGRESOS

*   **A - Fecha**: Mes del registro (dd/mm/aaaa). Se recomienda usar el día 1 de cada mes.
*   **B - Bruto**: Sueldo bruto mensual (input manual).
*   **C - Jubilación**: Descuento automático (11% del bruto).
*   **D - PAMI**: Descuento automático (3% del bruto).
*   **E - Obra Social**: Descuento automático (3% del bruto).
*   **F - Neto**: El sueldo "en mano" (Bruto - Descuentos).
*   **G - SAC Bruto**: Monto del aguinaldo bruto (input manual, 2 veces al año).
*   **H - SAC Neto**: Aguinaldo con descuentos aplicados automáticamente.
*   **I - Bono Neto**: Bonos extraordinarios recibidos en el mes (input manual).
*   **J - Comida**: Beneficio de comida mensual (input manual).
*   **K - Otros Beneficios**: Valores monetarios de otros beneficios (input manual).
*   **L - Total Neto**: La suma de todo lo que efectivamente entró a tu cuenta ese mes.

## 2. INFLACIÓN (CER)

*   **M - Δ% CER MoM**: Inflación mensual oficial según la variación del Coeficiente de Estabilización de Referencia.
*   **N - Δ Bruto MoM**: Variación porcentual de tu sueldo bruto respecto al mes anterior.
*   **O - Poder Adq. Bruto MoM**: Diferencia real entre tu aumento de sueldo bruto y la inflación del mes.
*   **P - Δ Neto MoM**: Variación porcentual de tu sueldo neto respecto al mes anterior.
*   **Q - Poder Adq. Neto MoM**: Diferencia real entre tu aumento de sueldo neto y la inflación del mes.

## 3. VS ÚLTIMO AUMENTO ARS

*   **R - Bruto Base**: El sueldo bruto que tenías en el momento del último cambio de sueldo.
*   **S - Neto Base**: El sueldo neto que tenías en el momento del último cambio de sueldo.
*   **T - CER Base**: Valor del CER en el momento del último aumento.
*   **U - Atraso Real (Bruto)**: % que debería subir tu sueldo bruto hoy para igualar la inflación desde tu último aumento.
*   **V - Paridad CER (Bruto)**: El sueldo bruto ideal que deberías cobrar hoy para empatar la inflación acumulada.
*   **W - Atraso Real (Neto)**: % que debería subir tu sueldo neto hoy para igualar la inflación desde tu último aumento.
*   **X - Paridad CER (Neto)**: El sueldo neto ideal que deberías cobrar hoy para empatar la inflación acumulada.
*   **Y - Poder Adq. vs Aumento**: Poder adquisitivo acumulado (Neto vs CER) desde el último aumento.

## 4. PROYECCIONES REM (Expectativas de Mercado)

*   **Z - REM 3m (%)**: Inflación proyectada por el BCRA para los próximos 3 meses.
*   **AA - Objetivo 3m Bruto**: Sueldo bruto objetivo para dentro de 3 meses.
*   **AB - Objetivo 3m Neto**: Sueldo neto objetivo para dentro de 3 meses.
*   **AC - Δ 3m (%)**: Porcentaje de aumento sugerido hoy para cubrir los próximos 3 meses.
*   **AD - REM 6m (%)**: Inflación proyectada para los próximos 6 meses.
*   **AE - Objetivo 6m Bruto**: Sueldo bruto objetivo para dentro de 6 meses.
*   **AF - Objetivo 6m Neto**: Sueldo neto objetivo para dentro de 6 meses.
*   **AG - Δ 6m (%)**: Porcentaje de aumento sugerido hoy para cubrir los próximos 6 meses.

## 5. DÓLAR

*   **AH - CCL**: Cotización del dólar Contado con Liquidación al cierre de mes.
*   **AI - Δ % CCL MoM**: Variación porcentual del dólar respecto al mes anterior.
*   **AJ - Sueldo USD Bruto**: Tu sueldo bruto convertido a dólares a valor CCL.
*   **AK - Sueldo USD Neto**: Tu sueldo neto convertido a dólares a valor CCL.
*   **AL - Poder Adq. MoM (USD) Bruto**: Variación de tu sueldo bruto en dólares respecto al mes anterior.
*   **AM - Poder Adq. MoM (USD) Neto**: Variación de tu sueldo neto en dólares respecto al mes anterior.

## 6. VS ÚLTIMO AUMENTO USD

*   **AN - CCL Base**: Cotización del CCL en el momento del último aumento.
*   **AO - Sueldo USD Bruto Base**: Sueldo bruto en USD al momento del último aumento.
*   **AP - Sueldo USD Neto Base**: Sueldo neto en USD al momento del último aumento.
*   **AQ - Atraso USD (Bruto)**: % de caída/subida en USD (Bruto) comparado con el valor del día del último aumento.
*   **AR - Paridad USD (Bruto)**: Sueldo en pesos necesario hoy para recuperar los mismos dólares (Bruto) que el día del aumento.
*   **AS - Atraso USD (Neto)**: % de caída/subida en USD (Neto) comparado con el valor del día del último aumento.
*   **AT - Paridad USD (Neto)**: Sueldo en pesos necesario hoy para recuperar los mismos dólares (Neto) que el día del aumento.

---

## Fórmulas y Lógica

Todas las columnas calculadas se actualizan automáticamente. Solo necesitás completar las columnas de input manual (marcadas arriba).

Las tasas de descuentos (Jubilación, PAMI, Obra Social) se configuran en la hoja `impuestos`.
