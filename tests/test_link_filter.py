from __future__ import annotations

import json
from pathlib import Path

import fithitcli.parse as parse_module


def _sample_content() -> dict:
    return {
        "tables": [
            {
                "name": "Yoga",
                "columns": [
                    {"key": "col_link", "name": "Link"},
                    {"key": "col_desc", "name": "Description"},
                    {"key": "col_name", "name": "Name"},
                ],
                "rows": [
                    {
                        "col_link": "https://ok.test/workout",
                        "col_desc": {"text": "Good"},
                        "col_name": "Good",
                    },
                    {
                        "col_link": "https://bad.test/missing",
                        "col_desc": {"text": "Bad"},
                        "col_name": "Bad",
                    },
                    {
                        "col_link": "https://bad.test/missing",
                        "col_desc": {"text": "Bad 2"},
                        "col_name": "Bad 2",
                    },
                    {
                        "col_desc": {"text": "No link"},
                        "col_name": "No link",
                    },
                ],
            }
        ]
    }


def test_filter_unreachable_link_rows_removes_broken_rows():
    content = _sample_content()

    def checker(link: str, timeout: int) -> bool:
        return "ok.test" in link

    checked_links, removed_rows = parse_module._filter_unreachable_link_rows(
        content,
        checker=checker,
    )

    assert checked_links == 2
    assert removed_rows == 2
    assert len(content["tables"][0]["rows"]) == 2
    assert content["tables"][0]["rows"][0]["col_name"] == "Good"
    assert content["tables"][0]["rows"][1]["col_name"] == "No link"


def test_parse_content_applies_link_filter(tmp_path: Path, monkeypatch):
    content = _sample_content()
    output_path = tmp_path / "workouts.json"

    monkeypatch.setattr(
        parse_module,
        "_validate_links",
        lambda links, timeout, checker: {
            link: "ok.test" in link for link in links
        },
    )

    parse_module.parse_content(content=content, source="test", output=str(output_path))

    with output_path.open("r", encoding="utf-8") as f:
        workouts = json.load(f)

    assert len(workouts) == 2
    assert all("bad.test" not in str(w.get("link", "")) for w in workouts)
