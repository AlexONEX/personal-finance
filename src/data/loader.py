"""Módulo para cargar y parsear datos de archivos .txt."""

from datetime import date
from pathlib import Path
from typing import List, Dict, Optional


def parse_currency(value: str) -> float:
    """Convierte un string de moneda a float.

    Ejemplos:
        "$240,000" -> 240000.0
        "$1,528,417" -> 1528417.0
    """
    if not value or value == "":
        return 0.0

    # Remover símbolo de moneda y comas
    cleaned = value.replace("$", "").replace(",", "").strip()
    return float(cleaned)


def parse_date(date_str: str) -> date:
    """Convierte un string de fecha a objeto date.

    Formato esperado: dd/mm/yyyy
    Ejemplo: "30/10/2023" -> date(2023, 10, 30)
    """
    if not date_str or date_str == "":
        raise ValueError(f"Fecha vacía: {date_str}")

    day, month, year = date_str.split("/")
    return date(int(year), int(month), int(day))


def load_sueldo_data(file_path: str = "sueldo.txt") -> List[Dict]:
    """Carga los datos de sueldo desde el archivo.

    Returns:
        Lista de diccionarios con:
        - periodo: str (ej: "octubre 2023")
        - fecha: date
        - bruto: float
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    data = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        # Saltar header
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 3:
                continue

            periodo = parts[0].strip()
            fecha_str = parts[1].strip()
            bruto_str = parts[2].strip()

            if not fecha_str or not bruto_str:
                continue

            try:
                data.append(
                    {
                        "periodo": periodo,
                        "fecha": parse_date(fecha_str),
                        "bruto": parse_currency(bruto_str),
                    }
                )
            except (ValueError, IndexError) as e:
                print(f"Error parseando línea '{line}': {e}")
                continue

    return data


def load_cer_data(file_path: str = "cer.txt") -> List[Dict]:
    """Carga los datos de CER desde el archivo.

    Returns:
        Lista de diccionarios con:
        - fecha: date
        - cer: float
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    data = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        # Saltar header
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                continue

            fecha_str = parts[0].strip()
            cer_str = parts[1].strip()

            if not fecha_str or not cer_str:
                continue

            try:
                data.append(
                    {
                        "fecha": parse_date(fecha_str),
                        "cer": float(cer_str),
                    }
                )
            except (ValueError, IndexError) as e:
                print(f"Error parseando línea '{line}': {e}")
                continue

    return data


def load_inflacion_data(file_path: str = "inflacion.txt") -> List[float]:
    """Carga los datos de inflación mensual desde el archivo.

    El archivo contiene valores de inflación mensual desde octubre 2023.

    Returns:
        Lista de floats con inflación mensual (8.3, 12.8, 25.5, etc.)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                value = float(line)
                data.append(value)
            except ValueError as e:
                print(f"Error parseando inflación '{line}': {e}")
                continue

    return data


def get_cer_for_date(
    cer_data: List[Dict], target_date: date, allow_future: bool = False
) -> Optional[float]:
    """Obtiene el valor CER para una fecha específica usando VLOOKUP.

    Si no hay valor exacto, retorna el último valor disponible antes de esa fecha.
    Si la fecha objetivo es posterior al último CER disponible, retorna None (no hay datos).

    Args:
        cer_data: Lista de diccionarios con fecha y cer
        target_date: Fecha objetivo
        allow_future: Si True, permite usar el último CER disponible incluso si
                      target_date es posterior. Si False, retorna None en ese caso.

    Returns:
        Valor CER, None si no hay datos disponibles, o 0.0 si la lista está vacía
    """
    if not cer_data:
        return 0.0

    # Ordenar por fecha
    sorted_data = sorted(cer_data, key=lambda x: x["fecha"])

    # Obtener último CER disponible
    ultimo_cer_fecha = sorted_data[-1]["fecha"]

    # Si buscamos una fecha futura y no permitimos extrapolación, retornar None
    if not allow_future and target_date > ultimo_cer_fecha:
        return None

    # Buscar el último valor antes o igual a target_date
    last_cer = 0.0
    for entry in sorted_data:
        if entry["fecha"] <= target_date:
            last_cer = entry["cer"]
        else:
            break

    return last_cer if last_cer > 0 else None


def get_cer_for_periodo(
    periodo: str, cer_data: List[Dict], allow_future: bool = False
) -> Optional[float]:
    """Obtiene el CER para un periodo trabajado.

    El CER se publica con delay de ~30 días (t-1):
    - CER del 15 de abril refleja inflación de febrero
    - Para periodo "febrero 2026" necesito CER del 15/04/2026

    Args:
        periodo: String del periodo trabajado (ej: "febrero 2026")
        cer_data: Lista de datos de CER
        allow_future: Si True, usa último CER disponible si no existe el necesario

    Returns:
        Valor CER o None si no hay datos
    """
    MESES = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }

    # Parsear periodo
    partes = periodo.lower().strip().split()
    if len(partes) < 2:
        return None

    mes_str = partes[0]
    year = int(partes[1])

    if mes_str not in MESES:
        return None

    mes_periodo = MESES[mes_str]

    # CER se publica 2 meses después del periodo trabajado
    # Periodo febrero 2026 → CER del 15/04/2026
    mes_cer = mes_periodo + 2
    year_cer = year
    if mes_cer > 12:
        mes_cer -= 12
        year_cer += 1

    # Fecha del CER: día 15 del mes
    cer_date = date(year_cer, mes_cer, 15)

    # Buscar ese CER
    return get_cer_for_date(cer_data, cer_date, allow_future=allow_future)


def get_cer_base_date(periodo_fecha: date) -> date:
    """Calcula la fecha para buscar el CER base (DEPRECADO - usar get_cer_for_periodo).

    Según la fórmula: EOMONTH(B{r},1)+15
    Es decir: día 15 del mes siguiente al cierre del mes

    Ejemplo: para 30/10/2023 -> 15/12/2023
    """
    from calendar import monthrange

    # EOMONTH: último día del mes siguiente
    year = periodo_fecha.year
    month = periodo_fecha.month + 1
    if month > 12:
        month = 1
        year += 1

    # Último día del mes
    last_day = monthrange(year, month)[1]
    eomonth = date(year, month, last_day)

    # +15 días
    from datetime import timedelta

    return eomonth + timedelta(days=15)


def get_horas_trabajadas(fecha: date) -> int:
    """Retorna las horas trabajadas por día según la fecha.

    Regla:
    - Hasta abril 2025: 6 horas
    - Desde mayo 2025: 8 horas
    """
    # Mayo 2025 = fecha >= 2025-05-01
    if fecha >= date(2025, 5, 1):
        return 8
    return 6
