from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .schema import REQUIRED_FIELDS, SCHEMA_VERSION

console = Console()


def _default_db_path() -> Path:
    env = os.environ.get("FITHIT_DB_PATH")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".local" / "share" / "fithit" / "workouts.json"


def _load(db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        raise typer.BadParameter(
            f"Datenbank nicht gefunden: {db_path}\n"
            "Tipp: `fithit parse <dtable>` ausführen oder FITHIT_DB_PATH setzen."
        )
    with db_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise typer.BadParameter("workouts.json muss eine Liste von Workouts sein.")
    return data


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_str_or_str_list(value: Any) -> bool:
    if isinstance(value, str):
        return True
    if isinstance(value, list):
        return all(isinstance(v, str) and v.strip() != "" for v in value)
    return False


def _validate_workout(workout: Any, index: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not isinstance(workout, dict):
        errors.append({"index": index, "field": "*", "issue": "workout ist kein Objekt"})
        return errors, warnings

    for field in REQUIRED_FIELDS:
        if not _is_non_empty_str(workout.get(field)):
            errors.append({"index": index, "field": field, "issue": "fehlend oder leer"})

    if not (_is_non_empty_str(workout.get("name")) or _is_non_empty_str(workout.get("description"))):
        warnings.append({"index": index, "field": "name/description", "issue": "keine Beschreibung oder Name"})

    for field in ("equipment", "body_focus", "flow_style", "dumbbells", "muscle_groups", "move_types", "strikes"):
        if field in workout and not _is_str_or_str_list(workout[field]):
            errors.append({"index": index, "field": field, "issue": "muss string oder liste von strings sein"})

    if "episode" in workout and not isinstance(workout["episode"], (str, int)):
        errors.append({"index": index, "field": "episode", "issue": "muss string oder int sein"})

    if "prenatal" in workout and not isinstance(workout["prenatal"], bool):
        errors.append({"index": index, "field": "prenatal", "issue": "muss boolean sein"})

    return errors, warnings


def validate_cmd(*, format: str = "compact") -> None:
    db_path = _default_db_path()
    workouts = _load(db_path)

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for idx, workout in enumerate(workouts):
        err, warn = _validate_workout(workout, idx)
        errors.extend(err)
        warnings.extend(warn)

    summary = {
        "schema_version": SCHEMA_VERSION,
        "total_workouts": len(workouts),
        "errors": errors,
        "warnings": warnings,
        "ok": len(errors) == 0,
    }

    fmt = (format or "compact").lower()
    if fmt == "json":
        console.print_json(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    if fmt != "compact":
        raise typer.BadParameter("--format muss 'compact' oder 'json' sein")

    console.print(f"DB: {db_path}")
    console.print(f"Schema: v{SCHEMA_VERSION}")
    console.print(f"Total: {summary['total_workouts']}")
    console.print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")

    if not errors and not warnings:
        console.print("\nOK: Keine Probleme gefunden.")
        return

    if errors:
        table = Table(title="Fehler", show_header=True, header_style="bold")
        table.add_column("Index", justify="right")
        table.add_column("Feld")
        table.add_column("Issue")
        for item in errors[:50]:
            table.add_row(str(item["index"]), str(item["field"]), str(item["issue"]))
        console.print("\n")
        console.print(table)
        if len(errors) > 50:
            console.print(f"Weitere Fehler: {len(errors) - 50}")

    if warnings:
        table = Table(title="Warnungen", show_header=True, header_style="bold")
        table.add_column("Index", justify="right")
        table.add_column("Feld")
        table.add_column("Issue")
        for item in warnings[:50]:
            table.add_row(str(item["index"]), str(item["field"]), str(item["issue"]))
        console.print("\n")
        console.print(table)
        if len(warnings) > 50:
            console.print(f"Weitere Warnungen: {len(warnings) - 50}")
