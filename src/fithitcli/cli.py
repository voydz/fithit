from __future__ import annotations

import typer
from rich.console import Console

from .fetch import fetch_cmd
from .parse import parse_cmd
from .search import search_cmd
from .info import info_cmd
from .validate import validate_cmd

app = typer.Typer(
    add_completion=False,
    help="fithit — Apple Fitness+ Workouts parsen & durchsuchen",
)

console = Console()


@app.command("search")
def _search(
    category: str | None = typer.Option(None, "--category", help="Workout-Kategorie (Yoga, Strength, Core, ...)."),
    categories: str | None = typer.Option(None, "--categories", help="Komma-separierte Kategorien."),
    duration: str | None = typer.Option(None, "--duration", help="Exakte Dauer, z.B. '20 min'."),
    max_duration: int | None = typer.Option(None, "--max-duration", help="Maximale Dauer in Minuten."),
    equipment_free: bool = typer.Option(False, "--equipment-free", help="Nur bodyweight/mat Workouts."),
    trainer: str | None = typer.Option(None, "--trainer", help="Trainer-Name."),
    body_focus: str | None = typer.Option(None, "--body-focus", help="Body Focus (Upper/Lower/Total Body)."),
    flow_style: str | None = typer.Option(None, "--flow-style", help="Yoga Flow Style (Slow, Energetic, ...)."),
    search: str | None = typer.Option(None, "--search", help="Textsuche in Beschreibung/Name."),
    limit: int = typer.Option(5, "--limit", help="Max. Ergebnisse (default 5)."),
    randomize: bool = typer.Option(False, "--random", help="Ergebnisse mischen."),
    format: str = typer.Option("compact", "--format", help="Ausgabeformat: compact|json."),
):
    """Workouts aus der lokalen DB filtern."""
    search_cmd(
        category=category,
        categories=categories,
        duration=duration,
        max_duration=max_duration,
        equipment_free=equipment_free,
        trainer=trainer,
        body_focus=body_focus,
        flow_style=flow_style,
        search=search,
        limit=limit,
        randomize=randomize,
        format=format,
    )


@app.command("parse")
def _parse(
    dtable_path: str = typer.Argument(..., help="Pfad zur .dtable Datei (ZIP mit content.json)."),
    output: str | None = typer.Option(None, "--output", help="Zielpfad für workouts.json (default: Standard-DB-Pfad)."),
):
    """.dtable parsen und workouts.json + summary.json schreiben."""
    parse_cmd(dtable_path=dtable_path, output=output)


@app.command("fetch")
def _fetch(
    url: str | None = typer.Option(
        None,
        "--url",
        help="SeaTable External-Link-URL (default: Master-List aus FINDINGS.md).",
    ),
    output: str | None = typer.Option(None, "--output", help="Zielpfad für workouts.json (default: Standard-DB-Pfad)."),
):
    """SeaTable .dtable per External-Link laden und direkt parsen."""
    fetch_cmd(url=url, output=output)


@app.command("info")
def _info(
    format: str = typer.Option("compact", "--format", help="Ausgabeformat: compact|json."),
):
    """Zeigt DB-Statistiken (Kategorien, Trainer, Durations)."""
    info_cmd(format=format)


@app.command("validate")
def _validate(
    format: str = typer.Option("compact", "--format", help="Ausgabeformat: compact|json."),
):
    """Validiert workouts.json gegen das public schema."""
    validate_cmd(format=format)
