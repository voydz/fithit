# fithit

[![Release](https://img.shields.io/github/v/release/voydz/fithit)](https://github.com/voydz/fithit/releases)
[![Homebrew Tap](https://img.shields.io/badge/homebrew-voydz%2Fhomebrew--tap-blue?logo=homebrew)](https://github.com/voydz/homebrew-tap)

**CLI for parsing and searching Apple Fitness+ workouts.**  
Fast, deterministic, and ideal for scripts, notebooks, or a personal training database.

## Highlights

- `.dtable` → `workouts.json` + `summary.json` in one step
- Search like the original script (`filter_workouts.py`), but as a CLI
- JSON output for automations and skills
- Validation for stable public schemas

## Installation

```bash
brew install voydz/tap/fithit
```

Or install from source with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/voydz/fithit.git
cd fithit
uv sync
uv run fithit --help
```

## Quickstart (dev)

```bash
make setup
uv run fithit --help
```

## Database

Default path:

- `$XDG_DATA_HOME/fithit/workouts.json` (falls back to the standard XDG data dir)

Override:

- `FITHIT_DB_PATH=/path/to/workouts.json`

## Commands

- `fithit parse <dtable>`: extracts `content.json` from the `.dtable` (ZIP) and writes `workouts.json` + `summary.json`
- `fithit search ...`: filters workouts 1:1 like the original script `filter_workouts.py`
- `fithit info`: live stats from `workouts.json`
- `fithit validate`: schema checks for stable public fields
- `fithit fetch`: downloads `workouts.json` via URL (e.g. SeaTable External Link)

## Examples

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

The tap repo is `voydz/homebrew-tap`, and the formula lives at `Formula/fithit.rb`.  
Before publishing, update `homepage`, `url`, and `sha256`.

## Skill Integration

The Fitness Coach skill should only call the binary:

- `fithit info` (DB present?)
- `fithit search ... --format json`

## Schema (workouts.json)

Minimal, stable public schema:

- Required fields: `category`, `duration`, `trainer` (strings, not empty)
- At least one of: `name` or `description` (string)

Optional fields (string or list of strings, depending on field):

- `equipment`, `body_focus`, `flow_style`, `dumbbells`, `muscle_groups`, `move_types`, `strikes`
- `date`, `episode`, `music`, `link`, `playlist`, `detailed_moves`, `notes`, `format`
- `workout_details`, `resistance_band`, `theme`, `topic`, `workout_type`
- `prenatal` (boolean)
