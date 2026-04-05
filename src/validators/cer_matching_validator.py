"""Validador de matching temporal entre salarios y CER.

Verifica que para cada sueldo se está usando el CER correcto aplicando la heurística:
- CER objetivo = EOMONTH(fecha_sueldo, 0) + 13 días
- Busca CER exacto o más cercano anterior
- Detecta edge cases (CER faltante, futuro, gaps grandes)
"""

import calendar
import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class SalaryMatchingRecord:
    """Registro de matching de un salario con CER."""

    fecha_salario: date
    fecha_cer_objetivo: date
    fecha_cer_real: date | None
    cer_valor: float | None
    gap_dias: int  # Días entre CER objetivo y CER real
    status: Literal["OK", "REM_FALLBACK", "SIN_CER", "GAP_GRANDE", "CER_FUTURO"]
    sugerencia: str = ""


@dataclass
class MatchingReport:
    """Reporte de validación de matching salario→CER."""

    matchings: list[SalaryMatchingRecord] = field(default_factory=list)
    total_salarios: int = 0
    salarios_ok: int = 0
    salarios_rem_fallback: int = 0
    salarios_sin_cer: int = 0
    salarios_gap_grande: int = 0
    salarios_cer_futuro: int = 0


class CERMatchingValidator:
    """Validador de matching temporal salario→CER."""

    def __init__(self, max_gap_dias: int = 30):
        """Inicializa el validador.

        Args:
            max_gap_dias: Máximo gap permitido entre CER objetivo y real (default 30)
        """
        self.max_gap_dias = max_gap_dias

    def validate_salary_matching(
        self,
        salarios: list[dict],
        cer_data: dict[date, float],
        cer_estimado_data: dict[date, float] | None = None,
        rem_data: dict[date, float] | None = None,
    ) -> MatchingReport:
        """Valida matching de salarios con CER.

        Args:
            salarios: Lista de diccionarios con 'fecha' (date) como mínimo
            cer_data: Diccionario fecha → valor CER oficial
            cer_estimado_data: Diccionario fecha → CER estimado (opcional)
            rem_data: Diccionario fecha → índice REM (opcional)

        Returns:
            MatchingReport con resultados de validación
        """
        report = MatchingReport()

        for salario in salarios:
            fecha_salario = salario.get("fecha")
            if not fecha_salario or not isinstance(fecha_salario, date):
                logger.warning(f"Salario sin fecha válida: {salario}")
                continue

            # Calcular fecha CER objetivo: EOMONTH(fecha_salario, 0) + 13
            fecha_cer_objetivo = self._calcular_fecha_cer_objetivo(fecha_salario)

            # Buscar CER (oficial > estimado > REM)
            cer_valor, fecha_cer_real, source = self._find_cer(
                fecha_cer_objetivo, cer_data, cer_estimado_data, rem_data
            )

            # Calcular gap
            gap_dias = 0
            if fecha_cer_real:
                gap_dias = (fecha_cer_objetivo - fecha_cer_real).days

            # Determinar status
            status, sugerencia = self._determine_status(
                fecha_cer_objetivo, fecha_cer_real, cer_valor, gap_dias, source, rem_data
            )

            record = SalaryMatchingRecord(
                fecha_salario=fecha_salario,
                fecha_cer_objetivo=fecha_cer_objetivo,
                fecha_cer_real=fecha_cer_real,
                cer_valor=cer_valor,
                gap_dias=gap_dias,
                status=status,
                sugerencia=sugerencia,
            )

            report.matchings.append(record)
            report.total_salarios += 1

            # Actualizar contadores
            if status == "OK":
                report.salarios_ok += 1
            elif status == "REM_FALLBACK":
                report.salarios_rem_fallback += 1
            elif status == "SIN_CER":
                report.salarios_sin_cer += 1
            elif status == "GAP_GRANDE":
                report.salarios_gap_grande += 1
            elif status == "CER_FUTURO":
                report.salarios_cer_futuro += 1

        logger.info(
            f"Validación de matching completada: "
            f"{report.salarios_ok}/{report.total_salarios} salarios OK"
        )

        return report

    def _calcular_fecha_cer_objetivo(self, fecha_salario: date) -> date:
        """Calcula la fecha CER objetivo usando fechas reales de publicación INDEC.

        Args:
            fecha_salario: Fecha del salario

        Returns:
            Fecha CER objetivo (fecha real de publicación INDEC)
        """
        from src.data.indec_publication_dates import get_cer_date_for_salary

        # Intentar usar fecha real de publicación INDEC
        fecha_real = get_cer_date_for_salary(fecha_salario)

        if fecha_real:
            return fecha_real

        # Fallback a heurística EOMONTH+13 si no hay fecha conocida
        ultimo_dia_mes = date(
            fecha_salario.year,
            fecha_salario.month,
            calendar.monthrange(fecha_salario.year, fecha_salario.month)[1],
        )

        return ultimo_dia_mes + timedelta(days=13)

    def _find_cer(
        self,
        fecha_objetivo: date,
        cer_data: dict[date, float],
        cer_estimado_data: dict[date, float] | None,
        rem_data: dict[date, float] | None,
    ) -> tuple[float | None, date | None, str]:
        """Encuentra valor CER con precedencia: oficial > estimado > REM.

        Args:
            fecha_objetivo: Fecha CER objetivo
            cer_data: CER oficial
            cer_estimado_data: CER estimado
            rem_data: REM índice

        Returns:
            Tupla (valor, fecha_real, source)
        """
        # 1. Intentar CER oficial exacto
        if fecha_objetivo in cer_data:
            return cer_data[fecha_objetivo], fecha_objetivo, "oficial"

        # 2. CER oficial más cercano anterior
        fecha_cer_oficial = self._find_closest_before(fecha_objetivo, cer_data)
        if fecha_cer_oficial:
            return cer_data[fecha_cer_oficial], fecha_cer_oficial, "oficial"

        # 3. CER estimado exacto
        if cer_estimado_data and fecha_objetivo in cer_estimado_data:
            return cer_estimado_data[fecha_objetivo], fecha_objetivo, "estimado"

        # 4. CER estimado más cercano anterior
        if cer_estimado_data:
            fecha_cer_estimado = self._find_closest_before(fecha_objetivo, cer_estimado_data)
            if fecha_cer_estimado:
                return cer_estimado_data[fecha_cer_estimado], fecha_cer_estimado, "estimado"

        # 5. REM como último fallback
        if rem_data:
            # REM se matchea por primer día del mes anterior
            # (para sueldo de marzo, usar REM de febrero)
            fecha_rem = date(fecha_objetivo.year, fecha_objetivo.month, 1)
            if fecha_objetivo.month > 1:
                fecha_rem = date(fecha_objetivo.year, fecha_objetivo.month - 1, 1)
            else:
                fecha_rem = date(fecha_objetivo.year - 1, 12, 1)

            fecha_rem_real = self._find_closest_before(fecha_rem, rem_data)
            if fecha_rem_real and fecha_rem_real in rem_data:
                return rem_data[fecha_rem_real], fecha_rem_real, "rem"

        return None, None, "none"

    def _find_closest_before(
        self, fecha_objetivo: date, data: dict[date, float]
    ) -> date | None:
        """Encuentra la fecha más cercana anterior a la fecha objetivo.

        Args:
            fecha_objetivo: Fecha objetivo
            data: Diccionario de datos

        Returns:
            Fecha encontrada o None
        """
        fechas_anteriores = [f for f in data.keys() if f <= fecha_objetivo]
        if not fechas_anteriores:
            return None
        return max(fechas_anteriores)

    def _determine_status(
        self,
        fecha_cer_objetivo: date,
        fecha_cer_real: date | None,
        cer_valor: float | None,
        gap_dias: int,
        source: str,
        rem_data: dict[date, float] | None,
    ) -> tuple[str, str]:
        """Determina el status del matching.

        Args:
            fecha_cer_objetivo: Fecha CER objetivo
            fecha_cer_real: Fecha CER real encontrada
            cer_valor: Valor CER
            gap_dias: Gap en días
            source: Fuente del CER ('oficial', 'estimado', 'rem', 'none')
            rem_data: Datos REM (para sugerencias)

        Returns:
            Tupla (status, sugerencia)
        """
        # Sin CER disponible
        if cer_valor is None or fecha_cer_real is None:
            sugerencia = "Usar REM proyección M"
            if rem_data:
                # Calcular REM sugerido
                fecha_rem = date(fecha_cer_objetivo.year, fecha_cer_objetivo.month, 1)
                if fecha_cer_objetivo.month > 1:
                    fecha_rem = date(fecha_cer_objetivo.year, fecha_cer_objetivo.month - 1, 1)
                else:
                    fecha_rem = date(fecha_cer_objetivo.year - 1, 12, 1)

                if fecha_rem in rem_data:
                    sugerencia = f"Usar REM proyección M: {rem_data[fecha_rem]:.4f}"

            return "SIN_CER", sugerencia

        # CER futuro (no debería ocurrir)
        if gap_dias < 0:
            return "CER_FUTURO", f"CER de fecha futura: {fecha_cer_real.strftime('%d/%m/%Y')}"

        # REM fallback
        if source == "rem":
            return "REM_FALLBACK", f"Usando REM como fallback (valor: {cer_valor:.4f})"

        # Gap grande
        if gap_dias > self.max_gap_dias:
            return (
                "GAP_GRANDE",
                f"Gap de {gap_dias} días entre objetivo y CER disponible (máx {self.max_gap_dias})",
            )

        # OK
        return "OK", ""
