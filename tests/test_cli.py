from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from fithitcli.cli import app

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "workouts.sample.json"

runner = CliRunner()


def test_cli_info_json(monkeypatch):
    monkeypatch.setenv("FITHIT_DB_PATH", str(FIXTURE_PATH))
    result = runner.invoke(app, ["info", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total_workouts"] == 6
    assert "schema_version" in data


def test_cli_search_json(monkeypatch):
    monkeypatch.setenv("FITHIT_DB_PATH", str(FIXTURE_PATH))
    result = runner.invoke(app, ["search", "--format", "json", "--category", "Yoga"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["category"] == "Yoga"
