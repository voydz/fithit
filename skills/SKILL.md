# SKILL: fithit CLI usage for AI agents

## Purpose
Use this skill when an AI agent needs to parse, fetch, validate, or search the Apple Fitness+ workouts database via the `fithit` CLI. This skill describes the full workflow, from setup to queries, with safe defaults and JSON-friendly output for automation.

## When to use
- You need to create or update `workouts.json` from a `.dtable` export.
- You need to fetch a published `workouts.json` from a URL.
- You need to search/filter workouts and return machine-readable results.
- You need stats or schema validation for the dataset.

## Database path
- Default path:
  - `$XDG_DATA_HOME/fithit/workouts.json` (falls back to the standard XDG data dir)
- Override via environment variable:
  - `FITHIT_DB_PATH=/path/to/workouts.json`

Use `FITHIT_DB_PATH` in automation to avoid ambiguous global state.

## Core commands
- Parse a `.dtable` export (ZIP) into JSON:
  - `fithit parse /path/to/Weekly\ Workouts.dtable`
  - Optional: `--output /path/to/workouts.json`
  - Writes `workouts.json` and `summary.json`
- Search workouts (filters match the original `filter_workouts.py` logic):
  - `fithit search --category Yoga --duration "20 min" --random --limit 3`
- Live stats for the current DB:
  - `fithit info`
- Validate public schema fields:
  - `fithit validate`
- Fetch a SeaTable `.dtable` via External-Link (or download-zip) URL and parse it:
  - `fithit fetch` (uses the default External-Link URL)
  - `fithit fetch --url "https://..."`
  - Optional: `--output /path/to/workouts.json`
  - Writes `workouts.json` and `summary.json`

## JSON-first automation
Prefer `--format json` when a structured response is needed.

Examples:
- `fithit search --search "hip opener" --format json`
- `fithit info --format json`
- `fithit validate --format json`

## Recommended agent workflow
1. Check whether a DB exists (and is the right one):
   - `fithit info` (set `FITHIT_DB_PATH` if needed)
2. If missing or stale, create or fetch it:
   - Parse: `fithit parse /path/to/Weekly\ Workouts.dtable` (optional `--output`)
   - Fetch: `fithit fetch` or `fithit fetch --url "https://..."` (optional `--output`)
3. Validate if you rely on public schema stability:
   - `fithit validate`
4. Run searches using filters; return JSON when automating:
   - `fithit search ... --format json`

## Notes for agents
- Use `FITHIT_DB_PATH` to avoid writing to the user’s global XDG data by default.
- Prefer deterministic queries (avoid `--random`) unless randomness is explicitly requested.
- If the user wants examples, reuse the CLI patterns from this skill.
- If the dataset is not available, ask the user for a `.dtable` path or a fetch URL.
