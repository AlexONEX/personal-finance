#!/usr/bin/env python3
"""Import historical salary data into SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path("/srv/data/personal-finance/personal-finance.db")

# fmt: off
# (fecha DD/MM/YYYY, bruto, horas_diarias, ascenso, sac_bruto, bono_neto, tarjeta_corporativa)
DATA: list[tuple[str, float, float, bool, float | None, float | None, float | None]] = [
    ("30/10/2023", 240_000,   6, False, None,      None,        40_000),
    ("30/11/2023", 260_000,   6, False, None,      None,        40_000),
    ("30/12/2023", 260_000,   6, False, None,      None,        60_000),
    ("30/01/2024", 360_000,   6, False, None,      None,        60_000),
    ("29/02/2024", 360_000,   6, False, None,      None,        75_000),
    ("30/03/2024", 525_000,   6, False, None,      None,        75_000),
    ("30/04/2024", 525_000,   6, False, None,      None,        95_000),
    ("30/05/2024", 725_000,   6, False, None,      None,        95_000),
    ("30/06/2024", 725_000,   6, False, 362_500,   None,       110_000),  # SAC jun 2024
    ("30/07/2024", 884_500,   6, False, None,      None,       110_000),
    ("30/08/2024", 884_500,   6, False, None,      None,       110_000),
    ("01/10/2024", 884_500,   6, False, None,      None,       125_000),  # periodo sep 2024
    ("01/11/2024", 955_260,   6, False, None,      None,       125_000),  # periodo oct 2024
    ("02/12/2024", 1_528_416, 6, True,  764_208,   None,       125_000),  # periodo nov 2024 — ASCENSO; SAC dic 2024
    ("02/01/2025", 1_528_417, 6, False, None,      None,       125_000),
    ("03/02/2025", 1_528_417, 6, False, None,      1_528_416,  125_000),  # bono neto feb 2025
    ("05/03/2025", 1_528_416, 6, False, None,      None,       150_000),
    ("06/04/2025", 1_528_417, 6, False, None,      None,       150_000),
    ("05/05/2025", 1_834_100, 6, False, None,      None,       150_000),
    ("02/06/2025", 1_834_099, 6, False, 917_050,   None,       150_000),  # SAC jun 2025
    ("01/07/2025", 1_834_099, 6, False, None,      None,       165_000),
    ("01/08/2025", 2_200_919, 6, True,  None,      None,       165_000),  # periodo jul 2025 — ASCENSO
    ("01/09/2025", 2_200_919, 6, False, None,      None,       165_000),
    ("01/10/2025", 2_200_919, 6, False, None,      None,       165_000),
    ("03/11/2025", 2_200_919, 6, False, None,      None,       165_000),
    ("01/12/2025", 2_421_011, 6, False, 1_051_607, None,       180_000),  # SAC dic 2025
    ("02/01/2026", 2_421_011, 6, False, None,      None,       180_000),
    ("01/02/2026", 2_421_011, 6, False, None,      4_760_000,  180_000),  # bono neto feb 2026
    ("02/03/2026", 2_421_011, 6, False, None,      None,       180_000),
    ("06/04/2026", 2_421_011, 6, False, None,      None,       205_000),  # periodo mar 2026
    ("04/05/2026", 3_615_376, 8, False, None,      None,       205_000),  # periodo abr 2026 — 8h desde aquí
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
    for fecha_raw, bruto, horas, ascenso, sac_bruto, bono_neto, tarjeta in DATA:
        fecha = parse_fecha(fecha_raw)
        try:
            cur.execute(
                """INSERT INTO salary_entries
                       (fecha, bruto, horas_diarias, ascenso, sac_bruto, bono_neto, tarjeta_corporativa)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (fecha, bruto, horas, int(ascenso), sac_bruto, bono_neto, tarjeta),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()
    print(f"Done: {inserted} inserted, {skipped} skipped (already existed).")


if __name__ == "__main__":
    main()
