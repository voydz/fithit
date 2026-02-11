from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def _default_db_path() -> Path:
    env = os.environ.get("FITHIT_DB_PATH")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".local" / "share" / "fithit" / "workouts.json"


def load_workouts(db_path: Path | None = None) -> list[dict[str, Any]]:
    path = db_path or _default_db_path()
    if not path.exists():
        raise typer.BadParameter(
            f"Datenbank nicht gefunden: {path}\n" 
            "Tipp: `fithit parse <dtable>` ausführen oder FITHIT_DB_PATH setzen."
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class SearchArgs:
    category: str | None
    categories: str | None
    duration: str | None
    max_duration: int | None
    equipment_free: bool
    trainer: str | None
    body_focus: str | None
    flow_style: str | None
    search: str | None


def _to_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if v is not None and str(v).strip() != ""]
    text = str(value).strip()
    return [text] if text else []


def _parse_minutes(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def matches(workout: dict[str, Any], args: SearchArgs) -> bool:
    # Category filter
    if args.category and str(workout.get("category", "")).lower() != args.category.lower():
        return False
    if args.categories:
        cats = [c.strip().lower() for c in args.categories.split(",")]
        if str(workout.get("category", "")).lower() not in cats:
            return False

    # Duration filter
    if args.duration and str(workout.get("duration", "")).lower() != args.duration.lower():
        return False

    # Max duration filter
    if args.max_duration:
        dur_min = _parse_minutes(workout.get("duration"))
        if dur_min is None or dur_min > args.max_duration:
            return False

    # Equipment-free filter
    if args.equipment_free:
        equip = _to_str_list(workout.get("equipment"))
        if equip:
            allowed = {"mat", "yoga mat", "no equipment", "bodyweight"}
            non_mat = [e for e in equip if e.lower() not in allowed]
            if non_mat:
                return False
        dumbbells = _to_str_list(workout.get("dumbbells"))
        if dumbbells and any(d.lower() != "bodyweight" for d in dumbbells):
            return False

    # Trainer filter
    if args.trainer:
        trainers = _to_str_list(workout.get("trainer"))
        if not any(t.lower() == args.trainer.lower() for t in trainers):
            return False

    # Body focus filter
    if args.body_focus:
        body_focus = _to_str_list(workout.get("body_focus"))
        if not any(b.lower() == args.body_focus.lower() for b in body_focus):
            return False

    # Flow style filter (Yoga)
    if args.flow_style:
        flow_style = _to_str_list(workout.get("flow_style"))
        if not any(f.lower() == args.flow_style.lower() for f in flow_style):
            return False

    # Text search in description
    if args.search:
        desc = (str(workout.get("description", "")) + " " + str(workout.get("name", ""))).lower()
        if args.search.lower() not in desc:
            return False

    return True


def _compact_table(results: Iterable[dict[str, Any]]) -> Table:
    table = Table(title=None, show_header=True, header_style="bold")
    table.add_column("Kategorie", style="cyan", no_wrap=True)
    table.add_column("Dauer", style="magenta", no_wrap=True)
    table.add_column("Trainer", style="green")
    table.add_column("Ep", style="yellow", no_wrap=True)
    table.add_column("Titel")

    for w in results:
        table.add_row(
            str(w.get("category", "?")),
            str(w.get("duration", "?")),
            str(w.get("trainer", "?")),
            str(w.get("episode", "")),
            str(w.get("name", "")) or (str(w.get("description", ""))[:80] if w.get("description") else ""),
        )
    return table


def search_cmd(
    *,
    category: str | None,
    categories: str | None,
    duration: str | None,
    max_duration: int | None,
    equipment_free: bool,
    trainer: str | None,
    body_focus: str | None,
    flow_style: str | None,
    search: str | None,
    limit: int,
    randomize: bool,
    format: str,
) -> None:
    workouts = load_workouts()
    args = SearchArgs(
        category=category,
        categories=categories,
        duration=duration,
        max_duration=max_duration,
        equipment_free=equipment_free,
        trainer=trainer,
        body_focus=body_focus,
        flow_style=flow_style,
        search=search,
    )

    results = [w for w in workouts if matches(w, args)]
    if randomize:
        random.shuffle(results)
    results = results[: max(limit, 0)]

    fmt = (format or "compact").lower()
    if fmt == "json":
        console.print_json(json.dumps(results, ensure_ascii=False, indent=2))
        return
    if fmt != "compact":
        raise typer.BadParameter("--format muss 'compact' oder 'json' sein")

    if not results:
        console.print("Keine passenden Workouts gefunden.")
        return

    console.print(f"Gefunden: {len(results)} Workout(s)\n")
    console.print(_compact_table(results))

    # optional: show link/equipment as extra lines after table
    for w in results:
        link = w.get("link")
        equip = w.get("equipment")
        if link or equip:
            console.print()
            console.print(f"[bold]{w.get('category','?')}[/bold] {w.get('duration','?')} — {w.get('trainer','?')} (Ep {w.get('episode','')})")
            if equip:
                console.print(f"  Equipment: {equip}")
            if link:
                console.print(f"  → {link}")
