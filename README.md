# fithit

CLI zum Parsen (aus `.dtable`) und Durchsuchen von Apple Fitness+ Workouts.

## Installation (dev)

```bash
cd ~/Code/tinkering/fithit
make setup
```

## Datenbank

Standard-Pfad (XDG-konform):

- `~/.local/share/fithit/workouts.json`

Override:

- `FITHIT_DB_PATH=/path/to/workouts.json`

Für initiales Testen:

```bash
mkdir -p ~/.local/share/fithit
cp ~/lumi/skills/fitness-coach/data/workouts.json ~/.local/share/fithit/workouts.json
```

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

## Homebrew (Tap)

Die Formel liegt im Tap unter `/opt/homebrew/Library/Taps/voydz/homebrew-tap/Formula/fithit.rb`. Vor dem Publish bitte `homepage`, `url` und `sha256` anpassen.

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
