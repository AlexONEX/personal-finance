"""Calculador de métricas CER para análisis de ingresos."""

from datetime import date
from typing import List, Dict, Optional
from .loader import (
    load_sueldo_data,
    load_cer_data,
    get_cer_for_date,
    get_cer_for_periodo,
    get_horas_trabajadas,
)


# Constantes
TASA_IMPUESTOS = 0.17  # 11% jubilación + 3% PAMI + 3% obra social
DIAS_LABORABLES_MES = 20

# Fechas de ascensos (según usuario: noviembre 2024 y julio 2025)
ASCENSOS = [
    date(2024, 11, 1),  # Noviembre 2024
    date(2025, 7, 1),   # Julio 2025
]


def calcular_neto(bruto: float) -> float:
    """Calcula el sueldo neto aplicando descuentos.

    Neto = Bruto - (17% de descuentos)
    Neto = Bruto * 0.83
    """
    return bruto * (1 - TASA_IMPUESTOS)


def calcular_por_hora(monto: float, horas_diarias: int) -> float:
    """Calcula el valor por hora.

    Fórmula: monto / (horas_diarias * 20 días)
    """
    if horas_diarias == 0:
        return 0.0
    return monto / (horas_diarias * DIAS_LABORABLES_MES)


def parse_periodo_to_date(periodo: str) -> date:
    """Convierte un string de periodo a fecha (primer día del mes).

    Args:
        periodo: String como "octubre 2023", "noviembre 2024"

    Returns:
        Fecha del primer día del mes (ej: date(2023, 10, 1))
    """
    MESES = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    }

    partes = periodo.lower().strip().split()
    if len(partes) < 2:
        raise ValueError(f"Formato de periodo inválido: {periodo}")

    mes_str = partes[0]
    year = int(partes[1])

    if mes_str not in MESES:
        raise ValueError(f"Mes desconocido: {mes_str}")

    mes = MESES[mes_str]
    return date(year, mes, 1)


def es_ascenso(periodo: str) -> bool:
    """Verifica si un periodo corresponde a un ascenso.

    Args:
        periodo: String del periodo trabajado (ej: "noviembre 2024")

    Returns:
        True si es un ascenso
    """
    try:
        periodo_fecha = parse_periodo_to_date(periodo)
        # Verificar si el periodo está en el mes de algún ascenso
        for ascenso_fecha in ASCENSOS:
            if periodo_fecha.year == ascenso_fecha.year and periodo_fecha.month == ascenso_fecha.month:
                return True
    except (ValueError, IndexError):
        return False

    return False


def calcular_metricas_cer(
    sueldo_file: str = "sueldo.txt",
    cer_file: str = "cer.txt",
) -> List[Dict]:
    """Calcula las 3 métricas CER para todos los periodos.

    Métricas:
    1. Paridad CER (Bruto/Hora)
    2. Paridad CER (Neto/Hora)
    3. Poder Adquisitivo vs Aumento (CER)

    Returns:
        Lista de diccionarios con todas las métricas por periodo
    """
    # Cargar datos
    sueldo_data = load_sueldo_data(sueldo_file)
    cer_data = load_cer_data(cer_file)

    if not sueldo_data:
        raise ValueError("No hay datos de sueldo")
    if not cer_data:
        raise ValueError("No hay datos de CER")

    resultados = []

    # Variables de estado para tracking de bases
    bruto_hora_base: Optional[float] = None
    neto_hora_base: Optional[float] = None
    cer_base: Optional[float] = None

    for i, registro in enumerate(sueldo_data):
        periodo = registro["periodo"]
        fecha = registro["fecha"]
        bruto = registro["bruto"]

        # Calcular valores básicos
        horas = get_horas_trabajadas(fecha)
        neto = calcular_neto(bruto)
        bruto_hora = calcular_por_hora(bruto, horas)
        neto_hora = calcular_por_hora(neto, horas)

        # Obtener CER para el periodo trabajado
        # El CER refleja la inflación del periodo trabajado (con delay de ~30 días)
        # Ejemplo: periodo "febrero 2026" usa CER del 15/04/2026
        cer_actual = get_cer_for_periodo(periodo, cer_data, allow_future=False)

        # Determinar si es ascenso
        # Según la lógica de Google Sheets, checkeamos el periodo ANTERIOR
        # Si el periodo anterior tiene ascenso=TRUE, reseteamos las bases
        es_reset = False
        if i == 0:
            # Primer periodo: inicializar bases
            es_reset = True
        else:
            # Verificar si el periodo ANTERIOR fue ascenso
            periodo_anterior = sueldo_data[i - 1]["periodo"]
            if es_ascenso(periodo_anterior):
                es_reset = True

        # Resetear bases si corresponde (solo si tenemos CER actual)
        if es_reset and cer_actual is not None:
            bruto_hora_base = bruto_hora
            neto_hora_base = neto_hora
            cer_base = cer_actual

        # Calcular métricas solo si tenemos CER actual y bases válidas
        paridad_cer_bruto = None
        paridad_cer_neto = None
        poder_adq_vs_aumento = None

        if cer_actual is not None and cer_base is not None and cer_base > 0:
            # 1. Paridad CER (Bruto/Hora)
            if bruto_hora_base:
                paridad_cer_bruto = bruto_hora_base * (cer_actual / cer_base)

            # 2. Paridad CER (Neto/Hora)
            if neto_hora_base:
                paridad_cer_neto = neto_hora_base * (cer_actual / cer_base)

            # 3. Poder Adquisitivo vs Aumento (CER)
            # Formula: (Neto_Hora_actual / Base_Neto_Hora) / (CER_actual / CER_base) - 1
            if neto_hora_base and neto_hora_base > 0:
                ratio_neto = neto_hora / neto_hora_base
                ratio_cer = cer_actual / cer_base
                poder_adq_vs_aumento = (ratio_neto / ratio_cer) - 1

        # Agregar resultado
        resultados.append({
            "periodo": periodo,
            "fecha": fecha,
            "bruto": bruto,
            "neto": neto,
            "horas_diarias": horas,
            "bruto_hora": bruto_hora,
            "neto_hora": neto_hora,
            "bruto_hora_base": bruto_hora_base,
            "neto_hora_base": neto_hora_base,
            "cer_actual": cer_actual,
            "cer_base": cer_base,
            "paridad_cer_bruto_hora": paridad_cer_bruto,
            "paridad_cer_neto_hora": paridad_cer_neto,
            "poder_adq_vs_aumento_cer": poder_adq_vs_aumento,
            "es_ascenso": es_ascenso(periodo),
        })

    return resultados


def generar_reporte(resultados: List[Dict]) -> str:
    """Genera un reporte en formato texto con las métricas.

    Args:
        resultados: Lista de diccionarios con métricas

    Returns:
        String con el reporte formateado
    """
    lineas = []
    lineas.append("=" * 120)
    lineas.append("REPORTE DE MÉTRICAS CER - ANÁLISIS DE INGRESOS")
    lineas.append("=" * 120)
    lineas.append("")

    # Header
    header = (
        f"{'Periodo':<20} "
        f"{'Fecha':<12} "
        f"{'Bruto/H':<12} "
        f"{'Neto/H':<12} "
        f"{'Paridad CER':<15} "
        f"{'Paridad CER':<15} "
        f"{'Poder Adq':<12} "
        f"{'Ascenso':<8}"
    )
    lineas.append(header)

    subheader = (
        f"{'':<20} "
        f"{'':<12} "
        f"{'Actual':<12} "
        f"{'Actual':<12} "
        f"{'(Bruto/H)':<15} "
        f"{'(Neto/H)':<15} "
        f"{'vs Aumento':<12} "
        f"{'':<8}"
    )
    lineas.append(subheader)
    lineas.append("-" * 120)

    # Datos
    for r in resultados:
        periodo = r["periodo"]
        fecha_str = r["fecha"].strftime("%d/%m/%Y")
        bruto_h = f"${r['bruto_hora']:,.2f}" if r["bruto_hora"] else "—"
        neto_h = f"${r['neto_hora']:,.2f}" if r["neto_hora"] else "—"

        paridad_b = (
            f"${r['paridad_cer_bruto_hora']:,.2f}"
            if r["paridad_cer_bruto_hora"]
            else "—"
        )
        paridad_n = (
            f"${r['paridad_cer_neto_hora']:,.2f}"
            if r["paridad_cer_neto_hora"]
            else "—"
        )
        poder_adq = (
            f"{r['poder_adq_vs_aumento_cer']*100:+.2f}%"
            if r["poder_adq_vs_aumento_cer"] is not None
            else "—"
        )
        ascenso = "SÍ" if r["es_ascenso"] else ""

        linea = (
            f"{periodo:<20} "
            f"{fecha_str:<12} "
            f"{bruto_h:>12} "
            f"{neto_h:>12} "
            f"{paridad_b:>15} "
            f"{paridad_n:>15} "
            f"{poder_adq:>12} "
            f"{ascenso:<8}"
        )
        lineas.append(linea)

    lineas.append("=" * 120)
    lineas.append("")
    lineas.append("NOTAS:")
    lineas.append("- Paridad CER: Valor que debería tener tu sueldo/hora ajustado por inflación (CER)")
    lineas.append("- Poder Adq vs Aumento: % de ganancia/pérdida real vs inflación desde último ascenso")
    lineas.append("  * Positivo (+): Ganaste poder adquisitivo (aumento > inflación)")
    lineas.append("  * Negativo (-): Perdiste poder adquisitivo (aumento < inflación)")
    lineas.append("")

    return "\n".join(lineas)
