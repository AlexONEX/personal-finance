"""Validador de CER vs Inflación INDEC.

Compara la variación mensual del CER con la inflación mensual publicada por INDEC
para detectar discrepancias que excedan la tolerancia configurada.
"""

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class DiscrepancyRecord:
    """Registro de una discrepancia entre CER e inflación."""

    fecha: date
    cer_pct: float  # Variación CER mensual como %
    inflacion_pct: float  # Inflación INDEC como %
    delta: float  # Diferencia absoluta en puntos porcentuales
    status: Literal["OK", "FUERA", "SIN_CER", "SIN_INFLACION", "CER_ESTIMADO"]
    nota: str = ""


@dataclass
class CERValidationReport:
    """Reporte completo de validación CER vs Inflación."""

    discrepancias: list[DiscrepancyRecord] = field(default_factory=list)
    total_meses: int = 0
    dentro_tolerancia: int = 0
    fuera_tolerancia: int = 0
    sin_cer: int = 0
    sin_inflacion: int = 0
    usando_cer_estimado: int = 0
    tolerancia_pct: float = 0.1


class CERInflationValidator:
    """Validador de coherencia entre CER e inflación INDEC."""

    def __init__(self, tolerancia_pct: float = 0.1):
        """Inicializa el validador.

        Args:
            tolerancia_pct: Tolerancia en puntos porcentuales (default 0.1%)
        """
        self.tolerancia_pct = tolerancia_pct

    def validate(
        self,
        cer_data: dict[date, float],
        inflacion_data: dict[date, float],
        cer_estimado_data: dict[date, float] | None = None,
    ) -> CERValidationReport:
        """Valida CER vs Inflación INDEC.

        Args:
            cer_data: Diccionario fecha -> valor CER (índice)
            inflacion_data: Diccionario fecha (último día mes) -> inflación mensual (decimal, ej: 0.027)
            cer_estimado_data: Diccionario fecha -> CER estimado (opcional)

        Returns:
            CERValidationReport con discrepancias detectadas
        """
        report = CERValidationReport(tolerancia_pct=self.tolerancia_pct)

        # Ordenar fechas de inflación (último día de cada mes)
        fechas_inflacion = sorted(inflacion_data.keys())

        if len(fechas_inflacion) < 2:
            logger.warning("Se necesitan al menos 2 meses de datos de inflación para validar")
            return report

        # Para cada mes con inflación, calcular variación CER correspondiente
        # IMPORTANTE: NO comparar CER entre fechas de publicación, sino variación mensual del CER
        # Ej: Inflación febrero = 13.2% → Comparar CER(29/feb) vs CER(1/feb)

        for i in range(1, len(fechas_inflacion)):
            fecha_inflacion = fechas_inflacion[i]  # Último día del mes (ej: 29/02/2024)

            inflacion_mensual = inflacion_data[fecha_inflacion]
            inflacion_pct = inflacion_mensual * 100  # Convertir decimal a %

            # Calcular fechas de inicio y fin del mes
            primer_dia_mes = date(fecha_inflacion.year, fecha_inflacion.month, 1)
            ultimo_dia_mes = fecha_inflacion  # Ya es el último día

            # Buscar CER del primer y último día del mes
            # Si no hay exacto, buscar el más cercano
            cer_inicio = self._find_closest_before(primer_dia_mes, cer_data)
            cer_fin = self._find_closest_before(ultimo_dia_mes, cer_data)

            if cer_inicio is None:
                # Buscar el primer CER del mes (puede ser día 2, 3, etc.)
                fechas_mes = [f for f in cer_data.keys()
                             if f.year == fecha_inflacion.year and f.month == fecha_inflacion.month]
                if fechas_mes:
                    fecha_cer_inicio = min(fechas_mes)
                    cer_inicio = cer_data[fecha_cer_inicio]

            if cer_fin is None:
                # Buscar el último CER del mes
                fechas_mes = [f for f in cer_data.keys()
                             if f.year == fecha_inflacion.year and f.month == fecha_inflacion.month]
                if fechas_mes:
                    fecha_cer_fin = max(fechas_mes)
                    cer_fin = cer_data[fecha_cer_fin]


            # Validar disponibilidad de datos
            if cer_inicio is None or cer_fin is None:
                report.discrepancias.append(
                    DiscrepancyRecord(
                        fecha=fecha_inflacion,
                        cer_pct=0.0,
                        inflacion_pct=inflacion_pct,
                        delta=0.0,
                        status="SIN_CER",
                        nota=f"Falta CER para {fecha_inflacion.strftime('%b %Y')}",
                    )
                )
                report.sin_cer += 1
                report.total_meses += 1
                continue

            # Calcular variación mensual del CER (durante el mes)
            cer_variacion_pct = ((cer_fin / cer_inicio) - 1) * 100

            # Calcular discrepancia absoluta
            delta = abs(cer_variacion_pct - inflacion_pct)

            # Determinar status
            if delta <= self.tolerancia_pct:
                status = "OK"
                report.dentro_tolerancia += 1
            else:
                status = "FUERA"
                report.fuera_tolerancia += 1

            # Verificar si se usó CER estimado
            # (no tenemos tracking de esto en esta versión simplificada)

            report.discrepancias.append(
                DiscrepancyRecord(
                    fecha=fecha_inflacion,
                    cer_pct=round(cer_variacion_pct, 2),
                    inflacion_pct=round(inflacion_pct, 2),
                    delta=round(delta, 2),
                    status=status,
                    nota="",
                )
            )
            report.total_meses += 1

        logger.info(
            f"Validación CER vs Inflación completada: "
            f"{report.dentro_tolerancia}/{report.total_meses} dentro de tolerancia ±{self.tolerancia_pct}%"
        )

        return report

    def _get_cer_value(
        self,
        fecha_objetivo: date,
        cer_data: dict[date, float],
        cer_estimado_data: dict[date, float] | None,
    ) -> tuple[float | None, bool]:
        """Obtiene valor CER para una fecha, con fallback a CER estimado.

        Args:
            fecha_objetivo: Fecha objetivo para buscar CER
            cer_data: Datos CER oficial
            cer_estimado_data: Datos CER estimado (opcional)

        Returns:
            Tupla (valor_cer, usando_estimado)
        """
        # Intentar CER oficial exacto
        if fecha_objetivo in cer_data:
            return cer_data[fecha_objetivo], False

        # Buscar CER oficial más cercano anterior (VLOOKUP con TRUE)
        cer_oficial = self._find_closest_before(fecha_objetivo, cer_data)
        if cer_oficial is not None:
            return cer_oficial, False

        # Fallback a CER estimado
        if cer_estimado_data:
            if fecha_objetivo in cer_estimado_data:
                return cer_estimado_data[fecha_objetivo], True

            cer_estimado = self._find_closest_before(fecha_objetivo, cer_estimado_data)
            if cer_estimado is not None:
                return cer_estimado, True

        return None, False

    def _find_closest_before(
        self, fecha_objetivo: date, data: dict[date, float]
    ) -> float | None:
        """Encuentra el valor CER más cercano anterior o igual a la fecha objetivo.

        Args:
            fecha_objetivo: Fecha objetivo
            data: Diccionario de datos CER

        Returns:
            Valor CER encontrado o None
        """
        fechas_anteriores = [f for f in data.keys() if f <= fecha_objetivo]
        if not fechas_anteriores:
            return None

        fecha_mas_cercana = max(fechas_anteriores)
        return data[fecha_mas_cercana]
