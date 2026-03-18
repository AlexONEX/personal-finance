"""plot_rem_curves.py

Plotea las curvas de expectativas REM para cada mes.
Muestra cómo la forma de la curva de inflación esperada cambia mes a mes.

Cada curva tiene 7 puntos: M, M+1, M+2, M+3, M+4, M+5, M+6

Uso:
    uv run python plot_rem_curves.py
    uv run python plot_rem_curves.py --save rem_curves.png
    uv run python plot_rem_curves.py --recent 12  # Solo últimos 12 meses
"""

import argparse
import os
from datetime import datetime

import matplotlib.pyplot as plt
from dotenv import load_dotenv

from src.config import MONTHS_MAP_SHORT, SHEETS
from src.connectors.sheets import get_sheets_client

load_dotenv()
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def parse_rem_date(date_str: str) -> datetime:
    """Parsea fecha formato 'ene-22' a datetime."""
    try:
        parts = date_str.lower().split("-")
        month_str = parts[0]
        year_short = parts[1]

        if month_str in MONTHS_MAP_SHORT:
            month = MONTHS_MAP_SHORT[month_str]
            year = 2000 + int(year_short)
            return datetime(year, month, 1)
    except (ValueError, IndexError) as e:
        print(f"Warning: Could not parse date '{date_str}': {e}")
        return None


def parse_percentage(pct_str: str) -> float:
    """Convierte '3.80%' a 3.8 (float en %)."""
    try:
        if not pct_str or pct_str == "":
            return None
        return float(pct_str.replace("%", ""))
    except (ValueError, AttributeError):
        return None


def fetch_rem_curves():
    """Obtiene todas las curvas REM desde Google Sheets."""
    client = get_sheets_client()
    ss = client.open_by_key(SPREADSHEET_ID)
    ws = ss.worksheet(SHEETS["REM"])

    data = ws.get_all_values()
    headers = data[2]
    rows = data[3:]

    # Columnas: Mes Reporte, M, M+1, M+2, M+3, M+4, M+5, M+6, Próx. 12m
    # Índices:  0,           1, 2,   3,   4,   5,   6,   7,   8

    results = []
    seen_months = {}  # Para trackear duplicados

    for row in rows:
        if len(row) < 8 or not row[0]:
            continue

        mes_reporte = row[0].strip()
        fecha = parse_rem_date(mes_reporte)

        if not fecha:
            continue

        proyecciones = []
        for i in range(1, 8):
            val = parse_percentage(row[i]) if len(row) > i else None
            proyecciones.append(val)

        if any(p is not None for p in proyecciones):
            seen_months[mes_reporte] = {
                "fecha": fecha,
                "mes": mes_reporte,
                "proyecciones": proyecciones,
            }

    # Convertir dict a lista y ordenar
    results = list(seen_months.values())
    return sorted(results, key=lambda x: x["fecha"])


def plot_rem_curves(data, recent_months=None, save_path=None, custom_title=None):
    """Plotea las curvas de expectativas REM."""
    if not data:
        print("No hay datos para graficar")
        return

    # Filtrar últimos N meses si se solicita
    if recent_months:
        data = data[-recent_months:]

    # Preparar datos
    horizons = ["M", "M+1", "M+2", "M+3", "M+4", "M+5", "M+6"]
    x_positions = list(range(len(horizons)))

    # Crear figura
    fig, ax = plt.subplots(figsize=(16, 9))

    # Paleta de colores primarios y secundarios bien diferenciados
    color_palette = [
        "#1f77b4",  # Azul
        "#ff7f0e",  # Naranja
        "#2ca02c",  # Verde
        "#d62728",  # Rojo oscuro
        "#9467bd",  # Púrpura
        "#8c564b",  # Marrón
        "#e377c2",  # Rosa
        "#7f7f7f",  # Gris
        "#bcbd22",  # Verde lima
        "#17becf",  # Cyan
        "#aec7e8",  # Azul claro
        "#ffbb78",  # Naranja claro
    ]

    n_curves = len(data)

    # Plotear cada curva (todas, incluyendo la última)
    for idx, curve_data in enumerate(data):
        proyecciones = curve_data["proyecciones"]
        mes = curve_data["mes"]

        if any(p is not None for p in proyecciones):
            # Asignar color de la paleta (ciclar si hay más curvas que colores)
            color = color_palette[idx % len(color_palette)]

            # La última curva más gruesa
            if idx == n_curves - 1:
                linewidth = 3.5
                markersize = 7
                alpha = 1.0
                zorder = 1000
            else:
                linewidth = 2.0
                markersize = 5
                alpha = 0.9
                zorder = idx

            ax.plot(
                x_positions,
                proyecciones,
                marker="o",
                markersize=markersize,
                linewidth=linewidth,
                color=color,
                alpha=alpha,
                zorder=zorder,
                label=mes,
            )

    # Formateo
    ax.set_xlabel("Horizonte Temporal", fontsize=13, fontweight="bold")
    ax.set_ylabel("Inflación Esperada (%)", fontsize=13, fontweight="bold")

    title = (
        custom_title
        if custom_title
        else (
            f"Curvas de Expectativas de Inflación REM\n"
            f"Evolución: {data[0]['mes']} → {data[-1]['mes']} ({len(data)} meses)"
        )
    )
    ax.set_title(title, fontsize=15, fontweight="bold", pad=20)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(horizons, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.8)

    # Leyenda arriba fuera del gráfico
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=min(6, len(data)),
        fontsize=10,
        frameon=True,
        fancybox=True,
        shadow=True,
    )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Gráfico guardado en: {save_path}")
    else:
        plt.show()


def plot_rem_evolution_by_horizon(data, save_path=None):
    """Plotea cómo cada horizonte (M, M+1, etc.) evoluciona en el tiempo."""
    if not data:
        print("No hay datos para graficar")
        return

    fechas = [d["fecha"] for d in data]
    horizons = ["M", "M+1", "M+2", "M+3", "M+4", "M+5", "M+6"]

    # Crear figura
    fig, ax = plt.subplots(figsize=(14, 8))

    colors = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#FFA07A",
        "#98D8C8",
        "#F7DC6F",
        "#BB8FCE",
    ]

    for idx, horizon in enumerate(horizons):
        values = [d["proyecciones"][idx] for d in data]
        ax.plot(
            fechas,
            values,
            marker="o",
            markersize=3,
            linewidth=2,
            color=colors[idx],
            label=horizon,
            alpha=0.8,
        )

    ax.set_xlabel("Fecha del Reporte REM", fontsize=12, fontweight="bold")
    ax.set_ylabel("Inflación Esperada (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Evolución de Expectativas por Horizonte Temporal\n"
        "¿Cómo cambió la expectativa para cada horizonte mes a mes?",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="best", fontsize=10)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Gráfico guardado en: {save_path}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plotea curvas de expectativas REM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Últimos 6 meses, guardar en archivo
  %(prog)s --months 6 --output rem_6m.png

  # Evolución temporal por horizonte
  %(prog)s --evolution --output rem_evolution.png

  # Últimos 12 meses, mostrar sin guardar
  %(prog)s --months 12

  # Todos los meses desde 2022
  %(prog)s --output rem_all.png
        """,
    )
    parser.add_argument(
        "-o",
        "--output",
        "--save",
        type=str,
        dest="output",
        help="Guardar gráfico en archivo (ej: rem_curves.png)",
    )
    parser.add_argument(
        "-m",
        "--months",
        "--recent",
        type=int,
        dest="months",
        help="Mostrar solo últimos N meses (default: todos)",
    )
    parser.add_argument(
        "-e",
        "--evolution",
        action="store_true",
        help="Plotear evolución por horizonte en lugar de curvas",
    )
    parser.add_argument(
        "-t", "--title", type=str, help="Título customizado para el gráfico"
    )
    args = parser.parse_args()

    print("Obteniendo datos de REM desde Google Sheets...")
    data = fetch_rem_curves()

    if data:
        print(f"✓ Obtenidos {len(data)} meses de datos REM")
        print(f"  Desde: {data[0]['mes']}")
        print(f"  Hasta: {data[-1]['mes']}")

        print("\nGenerando gráfico...")

        if args.evolution:
            plot_rem_evolution_by_horizon(data, save_path=args.output)
        else:
            plot_rem_curves(
                data,
                recent_months=args.months,
                save_path=args.output,
                custom_title=args.title,
            )
    else:
        print("No se encontraron datos REM")


if __name__ == "__main__":
    main()
