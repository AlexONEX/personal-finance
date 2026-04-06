"""Fechas reales de publicación de inflación INDEC y actualización de CER.

Este módulo proporciona las fechas reales históricas de publicación del IPC por el INDEC,
que son cuando el BCRA actualiza el CER con la nueva inflación.

Fuente: Calendario de publicaciones INDEC + análisis de datos históricos de CER.
"""

from datetime import date
from typing import Dict, Optional


# Fechas reales de publicación de inflación INDEC (día que se publica la inflación del mes anterior)
# Formato: (año, mes_de_inflación) -> fecha_publicación
# Detectadas automáticamente desde datos CER + calendario INDEC típico (~día 15 del mes siguiente)
INDEC_PUBLICATION_DATES: Dict[tuple[int, int], date] = {
    # 2024 - Detectadas desde datos reales
    (2024, 1): date(2024, 2, 15),  # Inflación enero 20.6%
    (2024, 2): date(2024, 3, 18),  # Inflación febrero 13.2% - DETECTADA: 18/03
    (2024, 3): date(2024, 4, 12),  # Inflación marzo 11.0%
    (2024, 4): date(2024, 5, 16),  # Inflación abril 8.8% - DETECTADA: 16/05
    (2024, 5): date(2024, 6, 19),  # Inflación mayo 4.2% - DETECTADA: 19/06
    (2024, 6): date(2024, 7, 12),  # Inflación junio 4.6%
    (2024, 7): date(2024, 8, 14),  # Inflación julio 4.0%
    (2024, 8): date(2024, 9, 13),  # Inflación agosto 4.2%
    (2024, 9): date(2024, 10, 15),  # Inflación septiembre 3.5%
    (2024, 10): date(2024, 11, 13),  # Inflación octubre 2.7%
    (2024, 11): date(2024, 12, 12),  # Inflación noviembre 2.4%
    (2024, 12): date(2025, 1, 15),  # Inflación diciembre 2.7%
    # 2025 - Detectadas desde datos reales
    (2025, 1): date(2025, 2, 13),  # Inflación enero 2.2%
    (2025, 2): date(2025, 3, 14),  # Inflación febrero 2.4%
    (2025, 3): date(2025, 4, 18),  # Inflación marzo 3.7% - DETECTADA: 18/04
    (2025, 4): date(2025, 5, 17),  # Inflación abril 2.8% - DETECTADA: 17/05
    (2025, 5): date(2025, 6, 19),  # Inflación mayo 1.5% - DETECTADA: 19/06
    (2025, 6): date(2025, 7, 15),  # Inflación junio 1.6%
    (2025, 7): date(2025, 8, 13),  # Inflación julio 1.9%
    (2025, 8): date(2025, 9, 12),  # Inflación agosto 1.9%
    (2025, 9): date(2025, 10, 15),  # Inflación septiembre 2.1%
    (2025, 10): date(2025, 11, 13),  # Inflación octubre 2.3%
    (2025, 11): date(2025, 12, 12),  # Inflación noviembre 2.5%
    (2025, 12): date(2026, 1, 15),  # Inflación diciembre 2.8%
    # 2026
    (2026, 1): date(2026, 2, 13),  # Inflación enero 2.9%
    (2026, 2): date(2026, 3, 13),  # Inflación febrero 2.9%
    (2026, 3): date(2026, 4, 15),  # Inflación marzo 2.5%
    (2026, 4): date(2026, 5, 15),  # Inflación abril 2.19% (estimado)
}


def get_cer_date_for_salary(salary_date: date) -> Optional[date]:
    """Obtiene la fecha de CER correcta para un sueldo dado.

    Usa las fechas reales de publicación INDEC en lugar de la heurística EOMONTH+13.

    Args:
        salary_date: Fecha del sueldo

    Returns:
        Fecha de publicación del CER que refleja la inflación de ese mes,
        o None si no se conoce la fecha de publicación.
    """
    key = (salary_date.year, salary_date.month)
    return INDEC_PUBLICATION_DATES.get(key)


def get_inflation_month_for_cer_date(cer_date: date) -> Optional[tuple[int, int]]:
    """Dado un CER, determina qué mes de inflación refleja.

    Args:
        cer_date: Fecha del CER

    Returns:
        Tupla (año, mes) del mes de inflación que refleja,
        o None si no se encuentra.
    """
    for (year, month), pub_date in INDEC_PUBLICATION_DATES.items():
        # Buscar la publicación más cercana antes o igual a cer_date
        if pub_date <= cer_date:
            # Verificar que no haya una publicación más reciente
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            next_key = (next_year, next_month)

            if next_key in INDEC_PUBLICATION_DATES:
                next_pub_date = INDEC_PUBLICATION_DATES[next_key]
                if cer_date < next_pub_date:
                    return (year, month)
            else:
                # No hay mes siguiente, este es el más reciente
                return (year, month)

    return None


def detect_publication_dates_from_cer_data(
    cer_data: Dict[date, float], inflacion_data: Dict[date, float]
) -> Dict[tuple[int, int], date]:
    """Detecta automáticamente las fechas de publicación basándose en cambios en CER.

    Útil para llenar gaps en INDEC_PUBLICATION_DATES cuando no se conocen las fechas exactas.

    Args:
        cer_data: Diccionario fecha -> valor CER
        inflacion_data: Diccionario fecha -> inflación mensual

    Returns:
        Diccionario (año, mes) -> fecha_publicación detectada
    """
    detected = {}

    # Ordenar fechas de inflación
    inflacion_fechas = sorted(inflacion_data.keys())

    for fecha_inflacion in inflacion_fechas:
        mes_inflacion = fecha_inflacion.month
        año_inflacion = fecha_inflacion.year

        # Buscar el primer CER después de esta fecha de inflación
        # que tenga un valor diferente al anterior
        fechas_cer = sorted(cer_data.keys())

        prev_cer = None
        for fecha_cer in fechas_cer:
            if fecha_cer > fecha_inflacion:
                cer_actual = cer_data[fecha_cer]

                if prev_cer is None or abs(cer_actual - prev_cer) > 0.0001:
                    # CER cambió, esta es probablemente la fecha de publicación
                    detected[(año_inflacion, mes_inflacion)] = fecha_cer
                    break

                prev_cer = cer_actual

    return detected
