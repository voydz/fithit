from __future__ import annotations

import json
import zipfile
from pathlib import Path

from fithitcli.parse import parse_cmd


def _fake_dtable(path: Path) -> Path:
    content = {
        "tables": [
            {
                "name": "Yoga",
                "columns": [
                    {"key": "col_date", "name": "Date"},
                    {
                        "key": "col_dur",
                        "name": "Duration",
                        "data": {"options": [{"id": 1, "name": "20 min"}, {"id": 2, "name": "10 min"}]},
                    },
                    {
                        "key": "col_trainer",
                        "name": "Trainer",
                        "data": {"options": [{"id": 1, "name": "Dustin"}]},
                    },
                    {"key": "col_desc", "name": "Description"},
                    {"key": "col_name", "name": "Name"},
                    {"key": "col_link", "name": "Link"},
                ],
                "rows": [
                    {
                        "col_date": "2025-01-02",
                        "col_dur": 1,
                        "col_trainer": 1,
                        "col_desc": {"text": "Test yoga flow"},
                        "col_name": "Flow",
                        "col_link": "https://example.com",
                    },
                    {
                        "col_date": "2024-12-31",
                        "col_dur": 2,
                        "col_trainer": 1,
                        "col_desc": {"text": "Old flow"},
                        "col_name": "Old",
                        "col_link": "https://example.com/old",
                    },
                ],
            }
        ]
    }

    dtable_path = path / "Weekly Workouts.dtable"
    with zipfile.ZipFile(dtable_path, "w") as zf:
        zf.writestr("content.json", json.dumps(content))

    return dtable_path


def test_parse_cmd_outputs_json(tmp_path: Path):
    dtable_path = _fake_dtable(tmp_path)
    output_path = tmp_path / "workouts.json"

    parse_cmd(dtable_path=str(dtable_path), output=str(output_path))

    with output_path.open("r", encoding="utf-8") as f:
        workouts = json.load(f)

    assert len(workouts) == 2
    assert workouts[0]["date"] == "2025-01-02"
    assert workouts[0]["duration"] == "20 min"

    summary_path = output_path.parent / "summary.json"
    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["total_workouts"] == 2
    assert summary["categories"]["Yoga"] == 2
