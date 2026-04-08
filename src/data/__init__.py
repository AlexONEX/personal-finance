"""Módulo de datos para el Ingresos Tracker."""

from .loader import (
    load_sueldo_data,
    load_cer_data,
    load_inflacion_data,
    get_cer_for_date,
    get_cer_for_periodo,
    get_horas_trabajadas,
)

from .metrics import (
    calcular_metricas_cer,
    generar_reporte,
)

__all__ = [
    "load_sueldo_data",
    "load_cer_data",
    "load_inflacion_data",
    "get_cer_for_date",
    "get_cer_for_periodo",
    "get_horas_trabajadas",
    "calcular_metricas_cer",
    "generar_reporte",
]
