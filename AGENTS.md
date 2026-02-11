# AGENTS.md (fithit)

Dieses Repo ist eine kleine Typer/Rich-CLI zum Parsen und Durchsuchen einer Apple Fitness+ Workout-Datenbank.

## Quickstart

- Setup: `make setup`
- Help: `uv run fithit --help`
- DB befüllen: `uv run fithit parse /path/to/Weekly\ Workouts.dtable`
- Suchen: `uv run fithit search --category Yoga --duration "20 min" --random --limit 3`

## Datenbank-Pfad

Standard: `~/.local/share/fithit/workouts.json`

Überschreiben via Environment:

- `FITHIT_DB_PATH=/tmp/workouts.json uv run fithit info`

## Commands

- `fithit parse <dtable>`: extrahiert `content.json` aus der `.dtable` (ZIP) und schreibt `workouts.json` + `summary.json`.
- `fithit search ...`: filtert Workouts 1:1 wie das ursprüngliche Script `filter_workouts.py`.
- `fithit info`: Live-Statistiken aus `workouts.json`.
