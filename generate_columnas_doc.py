"""generate_columnas_doc.py

Auto-genera docs/COLUMNAS.md desde src/sheets/structure.py
Asegura que la documentación esté siempre sincronizada con el código.

Uso:
    uv run python generate_columnas_doc.py
"""

from src.sheets.structure import (
    COLUMN_DESCRIPTIONS,
    COLUMN_FORMATS,
    INCOME_COLUMNS,
    INCOME_GROUPS,
    IMPUESTOS_ROWS,
)


def col_to_index(col: str) -> int:
    """Convierte letra de columna (A, B, ..., AA, AB) a índice numérico."""
    res = 0
    for char in col.upper():
        res = res * 26 + (ord(char) - ord("A") + 1)
    return res - 1


def generate_columnas_md():
    """Genera el archivo COLUMNAS.md desde las definiciones en structure.py."""

    lines = []

    # Header
    lines.append("# Diccionario de Columnas - Sheet Ingresos")
    lines.append("")
    lines.append(
        "**Generado automáticamente desde `src/sheets/structure.py`**"
    )
    lines.append("")
    lines.append("## Grupos de Columnas")
    lines.append("")

    # Grupos
    for start, end, label in INCOME_GROUPS:
        if label:
            lines.append(f"### {label} ({start} - {end})")
            lines.append("")

            # Buscar columnas en este grupo
            start_idx = col_to_index(start)
            end_idx = col_to_index(end)

            group_cols = []
            for col_let, title, *rest in INCOME_COLUMNS:
                col_idx = col_to_index(col_let)
                if start_idx <= col_idx <= end_idx:
                    group_cols.append((col_let, title, rest))

            for col_let, title, rest in group_cols:
                formula = rest[0] if rest and rest[0] else None
                desc = COLUMN_DESCRIPTIONS.get(col_let, "")
                fmt = COLUMN_FORMATS.get(col_let, {})

                lines.append(f"#### Columna {col_let}: {title}")
                lines.append("")

                if desc:
                    lines.append(f"**Descripción:** {desc}")
                    lines.append("")

                if formula:
                    lines.append("**Fórmula:**")
                    lines.append("```excel")
                    # Mostrar fórmula sin placeholders
                    lines.append(formula.replace("{r}", "ROW").replace("{r-1}", "ROW-1"))
                    lines.append("```")
                    lines.append("")

                if fmt:
                    lines.append(f"**Formato:** {fmt.get('type')} - `{fmt.get('pattern')}`")
                    lines.append("")

                # Manual input o auto-calculado
                if formula:
                    lines.append("**Tipo:** Auto-calculado")
                else:
                    lines.append("**Tipo:** Input manual")

                lines.append("")
                lines.append("---")
                lines.append("")

    # Tabla resumen
    lines.append("## Tabla Resumen")
    lines.append("")
    lines.append("| Col | Nombre | Tipo | Formato |")
    lines.append("|-----|--------|------|---------|")

    for col_let, title, *rest in INCOME_COLUMNS:
        formula = rest[0] if rest and rest[0] else None
        tipo = "Auto" if formula else "Manual"
        fmt = COLUMN_FORMATS.get(col_let, {})
        fmt_str = fmt.get("type", "TEXT") if fmt else "TEXT"

        lines.append(f"| {col_let} | {title} | {tipo} | {fmt_str} |")

    lines.append("")

    # Impuestos
    lines.append("## Tasas de Impuestos")
    lines.append("")
    lines.append("| Impuesto | Tasa | Ley |")
    lines.append("|----------|------|-----|")

    for name, rate, ley in IMPUESTOS_ROWS:
        lines.append(f"| {name} | {rate*100:.0f}% | {ley} |")

    lines.append("")

    # Inputs necesarios
    lines.append("## Inputs Manuales Requeridos")
    lines.append("")
    lines.append("Para cada mes, debes ingresar manualmente:")
    lines.append("")

    manual_cols = []
    for col_let, title, *rest in INCOME_COLUMNS:
        formula = rest[0] if rest and rest[0] else None
        if not formula:
            manual_cols.append(f"- **{col_let}** ({title})")

    lines.extend(manual_cols)
    lines.append("")

    # Metadata
    lines.append("---")
    lines.append("")
    lines.append("*Última actualización: Auto-generado*")
    lines.append("")
    lines.append("Para actualizar este archivo, ejecutá:")
    lines.append("```bash")
    lines.append("uv run python generate_columnas_doc.py")
    lines.append("```")

    return "\n".join(lines)


def main():
    """Genera y guarda docs/COLUMNAS.md."""
    content = generate_columnas_md()

    output_path = "docs/COLUMNAS.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ {output_path} generado exitosamente")
    print(f"  Total columnas: {len(INCOME_COLUMNS)}")
    print(f"  Grupos: {len(INCOME_GROUPS)}")


if __name__ == "__main__":
    main()
