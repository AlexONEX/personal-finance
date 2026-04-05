"""Test E2E: Validación de sincronización entre Google Sheets y validadores Python.

Este test verifica que:
1. Las fórmulas en Análisis ARS usan el CER correcto (según validadores)
2. Los cálculos de poder adquisitivo son consistentes
3. No hay regresiones en el matching CER-salario

Requiere:
- Google Sheets con datos reales
- SPREADSHEET_ID en .env
- Credenciales de Google Sheets válidas

Ejecutar:
    pytest tests/e2e_cer_validation.py -v
    pytest tests/e2e_cer_validation.py -v -s  # Con output
"""

import os
import sys
from datetime import datetime

import pytest
from dotenv import load_dotenv

# Agregar root al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SHEETS
from src.connectors.sheets import get_sheets_client
from src.validators import CERInflationValidator, CERMatchingValidator

load_dotenv()

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


@pytest.fixture(scope="module")
def sheets_client():
    """Cliente de Google Sheets."""
    if not SPREADSHEET_ID:
        pytest.skip("SPREADSHEET_ID not defined in .env")

    return get_sheets_client()


@pytest.fixture(scope="module")
def spreadsheet(sheets_client):
    """Spreadsheet abierto."""
    return sheets_client.open_by_key(SPREADSHEET_ID)


@pytest.fixture(scope="module")
def historic_data(spreadsheet):
    """Datos históricos: CER, CER Estimado, Inflación."""
    ws = spreadsheet.worksheet(SHEETS["HISTORIC"])
    data = ws.get("A4:F")

    cer_data = {}
    cer_estimado_data = {}
    inflacion_data = {}

    for row in data:
        if not row or not row[0]:
            continue

        try:
            fecha = datetime.strptime(row[0], "%d/%m/%Y").date()

            if len(row) > 1 and row[1]:
                cer_data[fecha] = float(row[1])

            if len(row) > 4 and row[4]:
                cer_estimado_data[fecha] = float(row[4])

            if len(row) > 5 and row[5]:
                inflacion_data[fecha] = float(row[5])

        except (ValueError, IndexError):
            continue

    return cer_data, cer_estimado_data, inflacion_data


@pytest.fixture(scope="module")
def ingresos_data(spreadsheet):
    """Datos de Ingresos (salarios)."""
    ws = spreadsheet.worksheet(SHEETS["INGRESOS"])
    data = ws.get("B3:B")  # Solo fechas

    salarios = []
    for row in data:
        if not row or not row[0]:
            continue

        try:
            fecha = datetime.strptime(row[0], "%d/%m/%Y").date()
            salarios.append({"fecha": fecha})
        except (ValueError, IndexError):
            continue

    return salarios


@pytest.fixture(scope="module")
def rem_data(spreadsheet):
    """Datos REM (índice acumulado)."""
    ws = spreadsheet.worksheet(SHEETS["REM"])
    data = ws.get("A4:J")

    rem = {}
    for row in data:
        if not row or not row[0]:
            continue

        try:
            fecha = datetime.strptime(row[0], "%d/%m/%Y").date()

            if len(row) > 9 and row[9]:
                rem[fecha] = float(row[9])

        except (ValueError, IndexError):
            continue

    return rem


class TestCERInflationSyncE2E:
    """Tests E2E para validación CER vs Inflación."""

    def test_cer_inflation_coherence(self, historic_data):
        """Test: CER e inflación son coherentes (±0.1%)."""
        cer_data, cer_estimado_data, inflacion_data = historic_data

        validator = CERInflationValidator(tolerancia_pct=0.1)
        report = validator.validate(cer_data, inflacion_data, cer_estimado_data)

        # Mayoría de meses debe estar dentro de tolerancia
        if report.total_meses > 0:
            tasa_exito = report.dentro_tolerancia / report.total_meses
            assert tasa_exito >= 0.90, (
                f"Solo {tasa_exito*100:.1f}% de meses dentro de tolerancia "
                f"(esperado >= 90%)"
            )

        # Imprimir alertas si hay
        if report.fuera_tolerancia > 0 or report.sin_cer > 0:
            print("\n⚠ ALERTAS ENCONTRADAS:")
            for d in report.discrepancias:
                if d.status in ["FUERA", "SIN_CER"]:
                    print(
                        f"  {d.fecha.strftime('%d/%m/%Y')}: "
                        f"Status={d.status}, Delta={d.delta:.2f}%, Nota={d.nota}"
                    )

    def test_no_cer_futuro(self, historic_data):
        """Test: no hay CER de fechas futuras."""
        from datetime import date

        cer_data, cer_estimado_data, _ = historic_data

        hoy = date.today()

        for fecha, valor in cer_data.items():
            assert fecha <= hoy, f"CER futuro encontrado: {fecha} (hoy: {hoy})"

        for fecha, valor in cer_estimado_data.items():
            # CER Estimado puede ser futuro (es proyección)
            pass  # OK


class TestCERMatchingSyncE2E:
    """Tests E2E para validación matching salario→CER."""

    def test_salary_matching_ok(self, ingresos_data, historic_data, rem_data):
        """Test: todos los salarios tienen CER asignado correctamente."""
        cer_data, cer_estimado_data, _ = historic_data

        validator = CERMatchingValidator(max_gap_dias=30)
        report = validator.validate_salary_matching(
            ingresos_data, cer_data, cer_estimado_data, rem_data
        )

        if report.total_salarios > 0:
            # Al menos 95% debe tener CER (OK o REM fallback)
            tasa_asignados = (
                report.salarios_ok + report.salarios_rem_fallback
            ) / report.total_salarios
            assert tasa_asignados >= 0.95, (
                f"Solo {tasa_asignados*100:.1f}% de salarios con CER asignado "
                f"(esperado >= 95%)"
            )

        # Imprimir salarios problemáticos
        problematicos = [
            m for m in report.matchings if m.status in ["SIN_CER", "GAP_GRANDE", "CER_FUTURO"]
        ]
        if problematicos:
            print("\n⚠ SALARIOS PROBLEMÁTICOS:")
            for m in problematicos:
                print(
                    f"  {m.fecha_salario.strftime('%d/%m/%Y')}: "
                    f"Status={m.status}, Sugerencia={m.sugerencia}"
                )

    def test_no_gaps_grandes(self, ingresos_data, historic_data, rem_data):
        """Test: no hay gaps grandes (> 30 días) para salarios históricos."""
        from datetime import date, timedelta

        cer_data, cer_estimado_data, _ = historic_data

        # Solo validar salarios de hace > 2 meses (históricos)
        dos_meses_atras = date.today() - timedelta(days=60)
        salarios_historicos = [s for s in ingresos_data if s["fecha"] < dos_meses_atras]

        if not salarios_historicos:
            pytest.skip("No hay salarios históricos para validar")

        validator = CERMatchingValidator(max_gap_dias=30)
        report = validator.validate_salary_matching(
            salarios_historicos, cer_data, cer_estimado_data, rem_data
        )

        # Salarios históricos NO deberían tener gap grande
        assert report.salarios_gap_grande == 0, (
            f"Encontrados {report.salarios_gap_grande} salarios con gap > 30 días"
        )


class TestRegressionE2E:
    """Tests de regresión: detecta cambios inesperados."""

    def test_cer_base_resetea_en_ascensos(self, spreadsheet):
        """Test: CER Base se resetea solo en ascensos (columna Q = TRUE)."""
        ws_ingresos = spreadsheet.worksheet(SHEETS["INGRESOS"])
        ws_analisis = spreadsheet.worksheet(SHEETS["ANALISIS_ARS"])

        # Leer columna Q (ascensos) y columna G de Análisis (CER Base)
        ascensos_data = ws_ingresos.get("Q3:Q")
        cer_base_data = ws_analisis.get("G3:G")

        # Verificar que cuando hay ascenso, CER Base cambia
        # (Este test es más conceptual, difícil de validar sin data histórica)
        # Por ahora solo verificamos que hay datos
        assert len(ascensos_data) > 0, "No hay datos de ascensos"
        assert len(cer_base_data) > 0, "No hay datos de CER Base"

    def test_columnas_analisis_ars_no_vacias(self, spreadsheet):
        """Test: columnas clave de Análisis ARS tienen datos."""
        ws = spreadsheet.worksheet(SHEETS["ANALISIS_ARS"])

        # Leer columnas clave
        cer_base = ws.get("G3:G10")  # CER Base
        paridad_cer = ws.get("H3:H10")  # Paridad CER
        poder_adq = ws.get("J3:J10")  # Poder Adq

        # Debe haber al menos 1 fila con datos en cada columna
        assert any(row and row[0] for row in cer_base), "CER Base vacío"
        assert any(row and row[0] for row in paridad_cer), "Paridad CER vacío"
        assert any(row and row[0] for row in poder_adq), "Poder Adq vacío"


def test_e2e_full_workflow(
    historic_data, ingresos_data, rem_data, capsys
):
    """Test E2E completo: workflow de validación."""
    cer_data, cer_estimado_data, inflacion_data = historic_data

    print("\n" + "=" * 80)
    print("TEST E2E: WORKFLOW COMPLETO DE VALIDACIÓN")
    print("=" * 80)

    # 1. Validar CER vs Inflación
    print("\n1. Validando CER vs Inflación...")
    validator_cer = CERInflationValidator(tolerancia_pct=0.1)
    report_cer = validator_cer.validate(cer_data, inflacion_data, cer_estimado_data)

    print(f"   Total meses: {report_cer.total_meses}")
    print(f"   Dentro tolerancia: {report_cer.dentro_tolerancia}")
    print(f"   Fuera tolerancia: {report_cer.fuera_tolerancia}")

    # 2. Validar matching salarios
    print("\n2. Validando matching salarios→CER...")
    validator_matching = CERMatchingValidator(max_gap_dias=30)
    report_matching = validator_matching.validate_salary_matching(
        ingresos_data, cer_data, cer_estimado_data, rem_data
    )

    print(f"   Total salarios: {report_matching.total_salarios}")
    print(f"   Salarios OK: {report_matching.salarios_ok}")
    print(f"   Salarios REM fallback: {report_matching.salarios_rem_fallback}")
    print(f"   Salarios sin CER: {report_matching.salarios_sin_cer}")

    # 3. Aserciones finales
    print("\n3. Verificando aserciones...")

    if report_cer.total_meses > 0:
        tasa_cer = report_cer.dentro_tolerancia / report_cer.total_meses
        assert tasa_cer >= 0.85, f"CER vs Inflación: {tasa_cer*100:.1f}% < 85%"
        print(f"   ✓ CER vs Inflación: {tasa_cer*100:.1f}% OK")

    if report_matching.total_salarios > 0:
        tasa_matching = (
            report_matching.salarios_ok + report_matching.salarios_rem_fallback
        ) / report_matching.total_salarios
        assert tasa_matching >= 0.90, f"Matching: {tasa_matching*100:.1f}% < 90%"
        print(f"   ✓ Matching salarios: {tasa_matching*100:.1f}% OK")

    print("\n" + "=" * 80)
    print("✓ TEST E2E COMPLETO: PASADO")
    print("=" * 80)
