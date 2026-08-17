# AGENTS.md (fithit)

Dieses Repo ist eine kleine Typer/Rich-CLI zum Parsen und Durchsuchen einer Apple Fitness+ Workout-Datenbank.

## Quickstart

- Setup: `make setup`
- Help: `uv run fithit --help`
- DB befüllen: `uv run fithit parse /path/to/Weekly\ Workouts.dtable`
- Suchen: `uv run fithit search --category Yoga --duration "20 min" --random --limit 3`

## Datenbank-Pfad

Standard: `$XDG_DATA_HOME/fithit/workouts.json` (falls back to the standard XDG data dir)

Überschreiben via Environment:

- `FITHIT_DB_PATH=/tmp/workouts.json uv run fithit info`

## Commands

- `fithit parse <dtable>`: extrahiert `content.json` aus der `.dtable` (ZIP) und schreibt `workouts.json` + `summary.json`.
- `fithit search ...`: filtert Workouts 1:1 wie das ursprüngliche Script `filter_workouts.py`.
- `fithit info`: Live-Statistiken aus `workouts.json`.

## Build & Release

- `make build` baut die Binary via `fithit.spec` (PyInstaller, immer für die Host-Architektur — Cross-Compiling gibt es nicht).
- `make package` erzeugt `dist/fithit-cli-<version>-<os>-<arch>.tar.gz` für die Host-Plattform.
- Unterstützte Release-Ziele: macOS `arm64`, Linux `x86_64`, Linux `arm64`. Kein Intel-macOS.
- Linux wird bewusst auf Ubuntu 22.04 gebaut (nicht 24.04): PyInstaller-Binaries sind nur vorwärtskompatibel. Das Ergebnis läuft ab glibc 2.28 (getestet: Rocky 8, Debian 11, Ubuntu 20.04/22.04).
- Die Homebrew-Formula wird generiert. `packaging/fithit.rb.tmpl` ist die Quelle; nicht direkt im Tap editieren.
