#!/usr/bin/env python3
"""Import historical salary data into SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path("/srv/data/personal-finance/personal-finance.db")

# fmt: off
# (fecha DD/MM/YYYY, bruto, horas_diarias, ascenso)
DATA: list[tuple[str, float, float, bool]] = [
    ("30/10/2023", 240_000,   6, False),
    ("30/11/2023", 260_000,   6, False),
    ("30/12/2023", 260_000,   6, False),
    ("30/01/2024", 360_000,   6, False),
    ("29/02/2024", 360_000,   6, False),
    ("30/03/2024", 525_000,   6, False),
    ("30/04/2024", 525_000,   6, False),
    ("30/05/2024", 725_000,   6, False),
    ("30/06/2024", 725_000,   6, False),
    ("30/07/2024", 884_500,   6, False),
    ("30/08/2024", 884_500,   6, False),
    ("01/10/2024", 884_500,   6, False),  # periodo sep 2024
    ("01/11/2024", 955_260,   6, False),  # periodo oct 2024
    ("02/12/2024", 1_528_416, 6, True),   # periodo nov 2024 — ASCENSO
    ("02/01/2025", 1_528_417, 6, False),
    ("03/02/2025", 1_528_417, 6, False),
    ("05/03/2025", 1_528_416, 6, False),
    ("06/04/2025", 1_528_417, 6, False),
    ("05/05/2025", 1_834_100, 6, False),
    ("02/06/2025", 1_834_099, 6, False),
    ("01/07/2025", 1_834_099, 6, False),
    ("01/08/2025", 2_200_919, 6, True),   # periodo jul 2025 — ASCENSO
    ("01/09/2025", 2_200_919, 6, False),
    ("01/10/2025", 2_200_919, 6, False),
    ("03/11/2025", 2_200_919, 6, False),
    ("01/12/2025", 2_421_011, 6, False),
    ("02/01/2026", 2_421_011, 6, False),
    ("01/02/2026", 2_421_011, 6, False),
    ("02/03/2026", 2_421_011, 6, False),
    ("06/04/2026", 2_421_011, 6, False),  # periodo mar 2026
    ("04/05/2026", 3_615_376, 8, False),  # periodo abr 2026 — 8h desde aquí
]
# fmt: on


def parse_fecha(s: str) -> str:
    d, m, y = s.split("/")
    return f"{y}-{m}-{d}"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0
    skipped = 0
    for fecha_raw, bruto, horas, ascenso in DATA:
        fecha = parse_fecha(fecha_raw)
        try:
            cur.execute(
                """INSERT INTO salary_entries (fecha, bruto, horas_diarias, ascenso)
                   VALUES (?, ?, ?, ?)""",
                (fecha, bruto, horas, int(ascenso)),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()
    print(f"Done: {inserted} inserted, {skipped} skipped (already existed).")


if __name__ == "__main__":
    main()
