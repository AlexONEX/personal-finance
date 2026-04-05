"""Validadores de coherencia para Análisis ARS y USD.

Estos validadores verifican que los datos tengan sentido lógico:
- Columnas "Base" solo cambian en ascensos
- Índices son monotónicamente crecientes
- Variaciones porcentuales en rangos razonables
- No hay valores absurdos (NaN, Inf, negativos donde no deberían)
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Severidad de una validación fallida."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationIssue:
    """Representa un problema encontrado en la validación."""

    severity: Severity
    sheet: str
    row: int
    column: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


class AnalisisCoherenceValidator:
    """Validador de coherencia para sheets de Análisis."""

    def __init__(self):
        self.issues: List[ValidationIssue] = []

    def validate_base_columns_reset_on_ascenso(
        self,
        sheet_name: str,
        ascenso_col: List[bool],
        base_cols: Dict[str, List[float]],
        base_col_names: List[str],
    ) -> None:
        """Valida que columnas "Base" solo cambien cuando hay ascenso.

        Args:
            sheet_name: Nombre del sheet
            ascenso_col: Lista de booleanos indicando ascensos
            base_cols: Dict con nombre_columna -> valores
            base_col_names: Nombres de columnas base a validar
        """
        for col_name in base_col_names:
            if col_name not in base_cols:
                continue

            values = base_cols[col_name]
            prev_value = None

            for i, (is_ascenso, value) in enumerate(zip(ascenso_col, values)):
                row_num = i + 3  # Rows start at 3

                if value is None or value == "":
                    continue

                if prev_value is not None:
                    if value != prev_value and not is_ascenso:
                        self.issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                sheet=sheet_name,
                                row=row_num,
                                column=col_name,
                                message=f"Columna Base cambió sin ascenso",
                                expected=str(prev_value),
                                actual=str(value),
                            )
                        )

                if is_ascenso:
                    # En ascenso, la base DEBE cambiar al valor actual
                    prev_value = value
                else:
                    # Sin ascenso, la base debe mantenerse
                    if prev_value is None:
                        prev_value = value

    def validate_monotonic_increasing(
        self,
        sheet_name: str,
        column_name: str,
        values: List[float],
        allow_equal: bool = True,
    ) -> None:
        """Valida que una columna sea monotónicamente creciente.

        Args:
            sheet_name: Nombre del sheet
            column_name: Nombre de la columna
            values: Valores a validar
            allow_equal: Si permite valores iguales consecutivos
        """
        prev_value = None

        for i, value in enumerate(values):
            row_num = i + 3

            if value is None or value == "":
                continue

            if prev_value is not None:
                if allow_equal:
                    if value < prev_value:
                        self.issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                sheet=sheet_name,
                                row=row_num,
                                column=column_name,
                                message=f"Índice no es monotónicamente creciente",
                                expected=f">= {prev_value}",
                                actual=str(value),
                            )
                        )
                else:
                    if value <= prev_value:
                        self.issues.append(
                            ValidationIssue(
                                severity=Severity.ERROR,
                                sheet=sheet_name,
                                row=row_num,
                                column=column_name,
                                message=f"Índice no es estrictamente creciente",
                                expected=f"> {prev_value}",
                                actual=str(value),
                            )
                        )

            prev_value = value

    def validate_percentage_range(
        self,
        sheet_name: str,
        column_name: str,
        values: List[float],
        min_pct: float = -0.5,
        max_pct: float = 5.0,
        warning_threshold: float = 0.3,
    ) -> None:
        """Valida que porcentajes estén en rangos razonables.

        Args:
            sheet_name: Nombre del sheet
            column_name: Nombre de la columna
            values: Valores a validar (como decimales, ej: 0.05 = 5%)
            min_pct: Mínimo esperado (default: -50%)
            max_pct: Máximo esperado (default: 500%)
            warning_threshold: Umbral para warnings (default: 30%)
        """
        for i, value in enumerate(values):
            row_num = i + 3

            if value is None or value == "":
                continue

            if value < min_pct:
                self.issues.append(
                    ValidationIssue(
                        severity=Severity.CRITICAL,
                        sheet=sheet_name,
                        row=row_num,
                        column=column_name,
                        message=f"Porcentaje fuera de rango mínimo",
                        expected=f">= {min_pct*100:.1f}%",
                        actual=f"{value*100:.2f}%",
                    )
                )
            elif value > max_pct:
                self.issues.append(
                    ValidationIssue(
                        severity=Severity.CRITICAL,
                        sheet=sheet_name,
                        row=row_num,
                        column=column_name,
                        message=f"Porcentaje fuera de rango máximo",
                        expected=f"<= {max_pct*100:.1f}%",
                        actual=f"{value*100:.2f}%",
                    )
                )
            elif abs(value) > warning_threshold:
                self.issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        sheet=sheet_name,
                        row=row_num,
                        column=column_name,
                        message=f"Porcentaje inusualmente alto",
                        expected=f"< {warning_threshold*100:.1f}%",
                        actual=f"{value*100:.2f}%",
                    )
                )

    def validate_positive_values(
        self,
        sheet_name: str,
        column_name: str,
        values: List[float],
        allow_zero: bool = False,
    ) -> None:
        """Valida que valores sean positivos (ej: precios, índices).

        Args:
            sheet_name: Nombre del sheet
            column_name: Nombre de la columna
            values: Valores a validar
            allow_zero: Si permite ceros
        """
        for i, value in enumerate(values):
            row_num = i + 3

            if value is None or value == "":
                continue

            if allow_zero:
                if value < 0:
                    self.issues.append(
                        ValidationIssue(
                            severity=Severity.CRITICAL,
                            sheet=sheet_name,
                            row=row_num,
                            column=column_name,
                            message=f"Valor negativo cuando debe ser >= 0",
                            expected=">= 0",
                            actual=str(value),
                        )
                    )
            else:
                if value <= 0:
                    self.issues.append(
                        ValidationIssue(
                            severity=Severity.CRITICAL,
                            sheet=sheet_name,
                            row=row_num,
                            column=column_name,
                            message=f"Valor no positivo cuando debe ser > 0",
                            expected="> 0",
                            actual=str(value),
                        )
                    )

    def validate_no_absurd_values(
        self,
        sheet_name: str,
        column_name: str,
        values: List[float],
    ) -> None:
        """Valida que no haya valores absurdos (NaN, Inf).

        Args:
            sheet_name: Nombre del sheet
            column_name: Nombre de la columna
            values: Valores a validar
        """
        import math

        for i, value in enumerate(values):
            row_num = i + 3

            if value is None or value == "":
                continue

            if math.isnan(value):
                self.issues.append(
                    ValidationIssue(
                        severity=Severity.CRITICAL,
                        sheet=sheet_name,
                        row=row_num,
                        column=column_name,
                        message=f"Valor NaN (Not a Number)",
                        expected="número válido",
                        actual="NaN",
                    )
                )
            elif math.isinf(value):
                self.issues.append(
                    ValidationIssue(
                        severity=Severity.CRITICAL,
                        sheet=sheet_name,
                        row=row_num,
                        column=column_name,
                        message=f"Valor infinito",
                        expected="número finito",
                        actual="Inf" if value > 0 else "-Inf",
                    )
                )

    def get_issues_by_severity(self, severity: Severity) -> List[ValidationIssue]:
        """Filtra issues por severidad."""
        return [issue for issue in self.issues if issue.severity == severity]

    def has_critical_issues(self) -> bool:
        """Retorna True si hay issues críticos."""
        return len(self.get_issues_by_severity(Severity.CRITICAL)) > 0

    def has_errors(self) -> bool:
        """Retorna True si hay errors o críticos."""
        return len(self.get_issues_by_severity(Severity.ERROR)) > 0 or self.has_critical_issues()

    def print_report(self) -> None:
        """Imprime reporte de validación."""
        if not self.issues:
            print("✅ No se encontraron problemas de coherencia")
            return

        print("\n" + "=" * 80)
        print("REPORTE DE VALIDACIÓN DE COHERENCIA")
        print("=" * 80)

        by_severity = {
            Severity.CRITICAL: self.get_issues_by_severity(Severity.CRITICAL),
            Severity.ERROR: self.get_issues_by_severity(Severity.ERROR),
            Severity.WARNING: self.get_issues_by_severity(Severity.WARNING),
            Severity.INFO: self.get_issues_by_severity(Severity.INFO),
        }

        for severity, issues in by_severity.items():
            if not issues:
                continue

            icon = {
                Severity.CRITICAL: "🔴",
                Severity.ERROR: "❌",
                Severity.WARNING: "⚠️",
                Severity.INFO: "ℹ️",
            }[severity]

            print(f"\n{icon} {severity.value} ({len(issues)})")
            print("-" * 80)

            for issue in issues:
                print(f"  {issue.sheet}:{issue.row}:{issue.column} - {issue.message}")
                if issue.expected:
                    print(f"    Esperado: {issue.expected}")
                if issue.actual:
                    print(f"    Actual:   {issue.actual}")
                print()

        print("=" * 80)
        print(f"Total: {len(self.issues)} problemas encontrados")
        print("=" * 80)
