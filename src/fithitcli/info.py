from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .schema import SCHEMA_VERSION

console = Console()


def _default_db_path() -> Path:
    env = os.environ.get("FITHIT_DB_PATH")
    if env:
        return Path(env).expanduser()
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    base = (
        Path(xdg_data_home).expanduser()
        if xdg_data_home
        else (Path.home() / ".local" / "share")
    )
    return base / "fithit" / "workouts.json"


def _load(db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        raise typer.BadParameter(
            f"Datenbank nicht gefunden: {db_path}\n"
            "Tipp: `fithit parse <dtable>` ausführen oder FITHIT_DB_PATH setzen."
        )
    with db_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _compute_summary(workouts: list[dict[str, Any]]) -> dict[str, Any]:
    categories = Counter(str(w.get("category")) for w in workouts if w.get("category"))
    trainers = sorted(
        {
            w.get("trainer")
            for w in workouts
            if isinstance(w.get("trainer"), str) and w.get("trainer")
        }
    )
    durations = sorted({w.get("duration") for w in workouts if w.get("duration")})
    return {
        "schema_version": SCHEMA_VERSION,
        "total_workouts": len(workouts),
        "categories": dict(sorted(categories.items(), key=lambda kv: (-kv[1], kv[0]))),
        "trainers": trainers,
        "durations": durations,
    }


def info_cmd(*, format: str = "compact") -> None:
    db_path = _default_db_path()
    workouts = _load(db_path)
    summary = _compute_summary(workouts)

    fmt = (format or "compact").lower()
    if fmt == "json":
        console.print_json(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    if fmt != "compact":
        raise typer.BadParameter("--format muss 'compact' oder 'json' sein")

    console.print(f"DB: {db_path}")
    console.print(f"Schema: v{SCHEMA_VERSION}")
    console.print(f"Total: {summary['total_workouts']}\n")

    cat_table = Table(title="Kategorien", show_header=True, header_style="bold")
    cat_table.add_column("Kategorie", style="cyan")
    cat_table.add_column("Anzahl", justify="right")
    for cat, count in summary["categories"].items():
        cat_table.add_row(str(cat), str(count))
    console.print(cat_table)

    console.print()
    console.print(
        f"Trainer ({len(summary['trainers'])}): {', '.join(summary['trainers'])}"
    )
    console.print(
        f"Durations ({len(summary['durations'])}): {', '.join(summary['durations'])}"
    )
