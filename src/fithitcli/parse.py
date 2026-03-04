from __future__ import annotations

import concurrent.futures
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable

import typer
from rich.console import Console

console = Console()

RELEVANT_TABLES = [
    "Strength",
    "Yoga",
    "Core",
    "HIIT",
    "Pilates",
    "Kickboxing",
    "Dance",
    "Cycling",
    "Mindful Cooldown",
    "Meditation",
]
LINK_CHECK_TIMEOUT_SECONDS = 10
LINK_CHECK_MAX_WORKERS = 16
LINK_CHECK_RETRIES = 2
RETRYABLE_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}


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


def _extract_link_value(row: dict[str, Any], link_keys: list[str]) -> str | None:
    for key in link_keys:
        raw = row.get(key)
        if isinstance(raw, str):
            link = raw.strip()
            if link:
                return link
        elif isinstance(raw, dict):
            link = str(raw.get("text") or raw.get("link") or "").strip()
            if link:
                return link
    return None


def _check_link_works(link: str, timeout: int) -> bool:
    parsed = urllib.parse.urlparse(link)
    if parsed.scheme.lower() not in {"http", "https"}:
        # Unsupported schemes cannot be checked via urllib HTTP requests.
        return True

    attempts = LINK_CHECK_RETRIES + 1
    for attempt in range(attempts):
        req = urllib.request.Request(link, headers={"User-Agent": "fithit-cli"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", None) or resp.getcode()
                if isinstance(status, int) and status >= 400:
                    if (
                        status in RETRYABLE_HTTP_STATUS_CODES
                        and attempt < LINK_CHECK_RETRIES
                    ):
                        time.sleep(0.25 * (2**attempt))
                        continue
                    return False
                return True
        except urllib.error.HTTPError as exc:
            if (
                exc.code in RETRYABLE_HTTP_STATUS_CODES
                and attempt < LINK_CHECK_RETRIES
            ):
                time.sleep(0.25 * (2**attempt))
                continue
            return False
        except urllib.error.URLError:
            if attempt < LINK_CHECK_RETRIES:
                time.sleep(0.25 * (2**attempt))
                continue
            return False
        except ValueError:
            return False

    return False


def _validate_links(
    links: set[str],
    *,
    timeout: int,
    checker: Callable[[str, int], bool],
) -> dict[str, bool]:
    results: dict[str, bool] = {}
    if not links:
        return results

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(max(len(links), 1), LINK_CHECK_MAX_WORKERS)
    ) as executor:
        futures = {executor.submit(checker, link, timeout): link for link in links}
        for future in concurrent.futures.as_completed(futures):
            link = futures[future]
            try:
                results[link] = bool(future.result())
            except Exception:
                results[link] = False
    return results


def _filter_unreachable_link_rows(
    content: dict[str, Any],
    *,
    timeout: int = LINK_CHECK_TIMEOUT_SECONDS,
    checker: Callable[[str, int], bool] = _check_link_works,
) -> tuple[int, int]:
    prepared_tables: list[tuple[dict[str, Any], list[tuple[dict[str, Any], str | None]]]] = (
        []
    )
    unique_links: set[str] = set()

    for table in content.get("tables", []):
        if table.get("name") not in RELEVANT_TABLES:
            continue

        link_keys = [
            col.get("key")
            for col in table.get("columns", [])
            if str(col.get("name", "")).strip().lower() == "link"
            and isinstance(col.get("key"), str)
        ]
        if not link_keys:
            continue

        rows = table.get("rows", [])
        if not isinstance(rows, list):
            continue

        row_links: list[tuple[dict[str, Any], str | None]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            link = _extract_link_value(row, link_keys)
            if link:
                unique_links.add(link)
            row_links.append((row, link))
        prepared_tables.append((table, row_links))

    link_status = _validate_links(unique_links, timeout=timeout, checker=checker)

    removed_rows = 0
    for table, row_links in prepared_tables:
        kept_rows: list[dict[str, Any]] = []
        for row, link in row_links:
            if link and not link_status.get(link, False):
                removed_rows += 1
                continue
            kept_rows.append(row)
        table["rows"] = kept_rows

    return len(unique_links), removed_rows


def build_option_map(columns: list[dict[str, Any]]):
    """Build lookup: column_key -> column_name and column_name -> option_id -> option_name."""
    col_map: dict[str, str] = {}
    opt_map: dict[str, dict[str | int, str]] = {}
    for c in columns:
        name = c["name"]
        col_map[c["key"]] = name
        data = c.get("data") or {}
        if "options" in data:
            option_lookup: dict[str | int, str] = {}
            for o in data["options"]:
                option_lookup[o["id"]] = o["name"]
            opt_map[name] = option_lookup
    return col_map, opt_map


def resolve_value(val: Any, opt_map: dict[str, dict[str | int, str]], col_name: str):
    """Resolve option IDs to human-readable names."""
    lookup = opt_map.get(col_name, {})
    if isinstance(val, list):
        resolved = [lookup.get(v, lookup.get(str(v), str(v))) for v in val]
        return resolved if len(resolved) > 1 else (resolved[0] if resolved else None)
    if isinstance(val, (int, float)):
        as_int = int(val)
        return lookup.get(as_int, lookup.get(str(as_int), val))
    if isinstance(val, str) and val in lookup:
        return lookup[val]
    return val


def extract_text(val: Any):
    """Extract text from rich-text fields."""
    if isinstance(val, dict):
        return (val.get("text", val.get("preview", "")) or "").strip()
    return val


def parse_row(
    row: dict[str, Any],
    col_map: dict[str, str],
    opt_map: dict[str, str],
    table_name: str,
):
    """Parse a single row into a clean workout dict."""
    mapped: dict[str, Any] = {}
    for key, val in row.items():
        if key.startswith("_") or val is None or val == "" or val == []:
            continue
        col_name = col_map.get(key, key)
        # Skip internal/test columns
        if (
            col_name.startswith("~")
            or col_name.startswith("TEST")
            or "(copy)" in col_name
        ):
            continue
        mapped[col_name] = val

    workout: dict[str, Any] = {"category": table_name}

    # Date
    if "Date" in mapped:
        workout["date"] = mapped["Date"]

    # Duration — resolve from option
    if "Duration" in mapped:
        dur = resolve_value(mapped["Duration"], opt_map, "Duration")
        workout["duration"] = str(dur) if dur else None

    # Trainer
    if "Trainer" in mapped:
        workout["trainer"] = resolve_value(mapped["Trainer"], opt_map, "Trainer")

    # Episode
    if "Ep" in mapped:
        workout["episode"] = mapped["Ep"]

    # Music genre
    if "Music" in mapped:
        workout["music"] = resolve_value(mapped["Music"], opt_map, "Music")

    # Link
    if "Link" in mapped:
        workout["link"] = mapped["Link"]

    # Playlist
    if "Playlist" in mapped:
        workout["playlist"] = mapped["Playlist"]

    # Description
    for field in ["Description", "Preview"]:
        if field in mapped:
            text = extract_text(mapped[field])
            if text:
                workout["description"] = text
                break

    # Detailed moves
    if "Detailed Moves" in mapped:
        workout["detailed_moves"] = extract_text(mapped["Detailed Moves"])

    # Notes
    if "Notes" in mapped:
        workout["notes"] = extract_text(mapped["Notes"])

    # Format
    if "Format" in mapped:
        workout["format"] = extract_text(mapped["Format"])

    # Category-specific fields
    # Strength
    if "Body Focus" in mapped:
        workout["body_focus"] = resolve_value(
            mapped["Body Focus"], opt_map, "Body Focus"
        )
    if "Equipment" in mapped:
        workout["equipment"] = resolve_value(mapped["Equipment"], opt_map, "Equipment")
    if "Dumbbells" in mapped:
        workout["dumbbells"] = resolve_value(mapped["Dumbbells"], opt_map, "Dumbbells")
    if "Muscle Groups" in mapped:
        workout["muscle_groups"] = resolve_value(
            mapped["Muscle Groups"], opt_map, "Muscle Groups"
        )
    if "Types of Moves" in mapped:
        workout["move_types"] = resolve_value(
            mapped["Types of Moves"], opt_map, "Types of Moves"
        )

    # Yoga
    if "Flow Style" in mapped:
        workout["flow_style"] = resolve_value(
            mapped["Flow Style"], opt_map, "Flow Style"
        )

    # HIIT / Kickboxing
    if "Workout Details" in mapped:
        workout["workout_details"] = extract_text(mapped["Workout Details"])
    if "Strikes" in mapped:
        workout["strikes"] = resolve_value(mapped["Strikes"], opt_map, "Strikes")

    # Pilates
    if "Resistance Band" in mapped:
        workout["resistance_band"] = resolve_value(
            mapped["Resistance Band"], opt_map, "Resistance Band"
        )

    # Meditation
    if "Theme" in mapped:
        workout["theme"] = resolve_value(mapped["Theme"], opt_map, "Theme")
    if "Topic/Theme" in mapped:
        workout["topic"] = resolve_value(mapped["Topic/Theme"], opt_map, "Topic/Theme")

    # Prenatal
    if mapped.get("Prenatal"):
        workout["prenatal"] = True

    # Workout Type (sub-type within category)
    if "Workout Type" in mapped:
        workout["workout_type"] = resolve_value(
            mapped["Workout Type"], opt_map, "Workout Type"
        )

    # Name
    if "Name" in mapped:
        workout["name"] = extract_text(mapped["Name"])

    return workout


def parse_content(*, content: dict[str, Any], source: str, output: str | None) -> None:
    out_path = Path(output).expanduser() if output else _default_db_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    console.print(f"Parsing: {source}")
    checked_links, removed_rows = _filter_unreachable_link_rows(content)
    if checked_links:
        console.print(
            f"Link-Check: {checked_links} URL(s) geprüft, {removed_rows} Workout(s) entfernt."
        )
    else:
        console.print("Link-Check: keine Links gefunden.")

    all_workouts: list[dict[str, Any]] = []
    stats: dict[str, int] = {}

    for table in content.get("tables", []):
        name = table.get("name")
        if name not in RELEVANT_TABLES:
            continue

        col_map, opt_map = build_option_map(table.get("columns", []))
        rows = table.get("rows", [])
        count = 0

        for row in rows:
            workout = parse_row(row, col_map, opt_map, name)
            if workout.get("link") or workout.get("description"):
                all_workouts.append(workout)
                count += 1

        stats[name] = count
        console.print(f"  {name}: {count} Workouts")

    all_workouts.sort(key=lambda w: w.get("date", ""), reverse=True)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(all_workouts, f, indent=2, ensure_ascii=False)

    console.print(f"\nTotal: {len(all_workouts)} Workouts → {out_path}")

    summary = {
        "source": source,
        "total_workouts": len(all_workouts),
        "categories": stats,
        "trainers": sorted(
            set(w["trainer"] for w in all_workouts if isinstance(w.get("trainer"), str))
        ),
        "durations": sorted(
            set(w["duration"] for w in all_workouts if w.get("duration"))
        ),
    }

    summary_path = out_path.parent / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    console.print(f"Summary → {summary_path}")


def parse_cmd(*, dtable_path: str, output: str | None) -> None:
    dtable = Path(dtable_path).expanduser()
    if not dtable.exists():
        raise typer.BadParameter(f"Datei nicht gefunden: {dtable}")

    with zipfile.ZipFile(dtable) as zf:
        with zf.open("content.json") as f:
            content = json.load(f)

    parse_content(content=content, source=str(dtable), output=output)
