# Ingresos Tracker

Sistema automatizado para el seguimiento de ingresos personales en Argentina, con ajuste por inflación (CER), proyecciones de mercado (REM) y comparativa en dólares (CCL).

## 📊 Diccionario de Columnas (Hoja 'Ingresos')

### 1. DATOS BASE & INGRESOS
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

### 2. INFLACIÓN (CER)
*   **M - Δ % CER MoM**: Inflación mensual oficial según la variación del Coeficiente de Estabilización de Referencia.
*   **N - Δ Sueldo MoM**: Variación porcentual de tu sueldo neto respecto al mes anterior.
*   **O - Poder Adq. MoM**: Diferencia real entre tu aumento y la inflación del mes. (Positivo = ganaste, Negativo = perdiste).
*   **P - Poder Adq. Acum.**: Variación del poder de compra real desde el primer registro (Neto vs CER acumulado).

### 3. VS ÚLTIMO AUMENTO
*   **Q - Bruto Base**: El sueldo bruto que tenías en el momento del último cambio de sueldo.
*   **R - CER Base**: Valor del CER en el momento del último aumento.
*   **S - Atraso Real ARS**: % que debería subir tu sueldo hoy para igualar la inflación desde tu último aumento.
*   **T - Paridad CER**: El sueldo bruto ideal que deberías cobrar hoy para empatar la inflación acumulada.

### 4. ANÁLISIS TOTAL
*   **U - Ingreso a Valor Hoy**: Tu sueldo pasado multiplicado por la inflación acumulada hasta hoy.
*   **V - Δ Real vs Año Ant.**: Comparativa interanual móvil. Crecimiento real respecto al mismo mes del año pasado.

### 5. PROYECCIONES REM (Expectativas de Mercado)
*   **W - REM 3m (%)**: Inflación proyectada por el BCRA para los próximos 3 meses.
*   **X - Objetivo 3m**: Sueldo bruto objetivo para dentro de 3 meses.
*   **Y - Δ 3m (%)**: Porcentaje de aumento sugerido hoy para cubrir los próximos 3 meses.
*   **Z - REM 6m (%)**: Inflación proyectada para los próximos 6 meses.
*   **AA - Objetivo 6m**: Sueldo bruto objetivo para dentro de 6 meses.
*   **AB - Δ 6m (%)**: Porcentaje de aumento sugerido hoy para cubrir los próximos 6 meses.

### 6. DÓLARES (CCL)
*   **AC - CCL**: Cotización del dólar Contado con Liquidación al cierre de mes.
*   **AD - Δ % CCL MoM**: Variación porcentual del dólar respecto al mes anterior.
*   **AE - Sueldo USD**: Tu "Total Neto" convertido a dólares a valor CCL.
*   **AF - Poder Adq. MoM (USD)**: Variación de tu sueldo en dólares respecto al mes anterior.
*   **AG - Poder Adq. Acum. (USD)**: Crecimiento acumulado de tus ingresos en dólares desde el primer registro.

### 7. VS ÚLTIMO AUMENTO USD
*   **AH - Atraso USD**: % de caída/subida en USD comparado con el valor del día del último aumento.
*   **AI - Paridad USD**: Sueldo en pesos necesario hoy para recuperar los mismos dólares que el día del aumento.
*   **AJ - Gap USD ($)**: Diferencia exacta en pesos (AI - B) para recuperar tu valor en dólares original.

---

## 🚀 Uso Rápido

1.  **Actualizar Datos**: Ejecutá `./update_daily.sh` para bajar CER, CCL y REM (actualiza historial desde 2022).
2.  **Cargar Sueldo**: Abrí la hoja `Ingresos` y cargá solo las columnas blancas (**Fecha**, **Bruto**, **SAC**, **Bonos**, **Beneficios**).
3.  **Configurar Tasas**: Si cambian los aportes de ley, editalos en la hoja `impuestos`.
