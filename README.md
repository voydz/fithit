# fithit

**CLI zum Parsen und Durchsuchen von Apple Fitness+ Workouts.**  
Schnell, deterministisch und ideal für Skripte, Notebooks oder eine persönliche Trainings-DB.

## Highlights

- `.dtable` → `workouts.json` + `summary.json` in einem Schritt
- Suche wie im Original-Script (`filter_workouts.py`), aber als CLI
- JSON-Ausgabe für Automationen und Skills
- Validierung für stabile öffentliche Schemata

## Quickstart (dev)

```bash
make setup
uv run fithit --help
```

## Datenbank

Standard-Pfad:

- `$XDG_DATA_HOME/fithit/workouts.json` (falls back to the standard XDG data dir)

Override:

- `FITHIT_DB_PATH=/path/to/workouts.json`

## Commands

- `fithit parse <dtable>`: extrahiert `content.json` aus der `.dtable` (ZIP) und schreibt `workouts.json` + `summary.json`
- `fithit search ...`: filtert Workouts 1:1 wie das ursprüngliche Script `filter_workouts.py`
- `fithit info`: Live-Statistiken aus `workouts.json`
- `fithit validate`: Schema-Checks für stabile öffentliche Felder
- `fithit fetch`: lädt `workouts.json` via URL (z. B. SeaTable External Link)

## Beispiele

```bash
uv run fithit --help
uv run fithit search --category Yoga --duration "20 min" --random --limit 3
uv run fithit search --categories "Yoga,Core,Mindful Cooldown" --equipment-free
uv run fithit search --trainer "Dustin" --body-focus "Total Body"
uv run fithit search --max-duration 20 --category HIIT
uv run fithit search --search "hip opener" --format json

uv run fithit parse /path/to/Weekly\ Workouts.dtable
uv run fithit parse --output /tmp/workouts.json /path/to/Weekly\ Workouts.dtable
uv run fithit fetch
uv run fithit fetch --url "https://cloud.seatable.io/dtable/external-links/..." --output /tmp/workouts.json

uv run fithit info
uv run fithit info --format json
uv run fithit validate
uv run fithit validate --format json
```

## Tests

```bash
make test
```

## Homebrew (Tap)

Die Formel liegt im Tap unter `homebrew-tap/Formula/fithit.rb`.  
Vor dem Publish bitte `homepage`, `url` und `sha256` anpassen.

## Skill Integration

Der Fitness-Coach Skill sollte ausschließlich das Binary aufrufen:

- `fithit info` (DB vorhanden?)
- `fithit search ... --format json`

## Schema (workouts.json)

Minimaler, stabiler public schema:

- Pflichtfelder: `category`, `duration`, `trainer` (Strings, nicht leer)
- Mindestens eines von: `name` oder `description` (String)

Optionale Felder (String oder Liste von Strings, je nach Feld):

- `equipment`, `body_focus`, `flow_style`, `dumbbells`, `muscle_groups`, `move_types`, `strikes`
- `date`, `episode`, `music`, `link`, `playlist`, `detailed_moves`, `notes`, `format`
- `workout_details`, `resistance_band`, `theme`, `topic`, `workout_type`
- `prenatal` (Boolean)
