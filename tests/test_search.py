from __future__ import annotations

import json
from pathlib import Path

from fithitcli.search import SearchArgs, matches

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "workouts.sample.json"


def load_fixture() -> list[dict[str, object]]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def make_args(**overrides):
    base = dict(
        category=None,
        categories=None,
        duration=None,
        max_duration=None,
        equipment_free=False,
        trainer=None,
        body_focus=None,
        flow_style=None,
        search=None,
    )
    base.update(overrides)
    return SearchArgs(**base)


def apply(workouts, **kwargs):
    args = make_args(**kwargs)
    return [w for w in workouts if matches(w, args)]


def test_category_filter():
    workouts = load_fixture()
    results = apply(workouts, category="Yoga")
    assert {w["category"] for w in results} == {"Yoga"}


def test_categories_list_filter():
    workouts = load_fixture()
    results = apply(workouts, categories="Yoga, Core")
    assert {w["category"] for w in results} == {"Yoga", "Core"}


def test_equipment_free_filter_allows_mat_and_none():
    workouts = load_fixture()
    results = apply(workouts, equipment_free=True)
    categories = {w["category"] for w in results}
    assert "Yoga" in categories
    assert "Core" in categories
    assert "Mindful Cooldown" in categories
    assert "Strength" not in categories
    assert "HIIT" not in categories


def test_duration_exact_and_max_duration():
    workouts = load_fixture()
    exact = apply(workouts, duration="20 min")
    assert {w["category"] for w in exact} == {"Yoga", "HIIT"}

    maxed = apply(workouts, max_duration=20)
    assert {w["category"] for w in maxed} == {"Yoga", "Core", "Mindful Cooldown", "HIIT"}


def test_trainer_body_focus_flow_style():
    workouts = load_fixture()

    trainers = apply(workouts, trainer="Dustin")
    assert {w["category"] for w in trainers} == {"Yoga", "Mindful Cooldown"}

    body_focus = apply(workouts, body_focus="Upper Body")
    assert {w["category"] for w in body_focus} == {"Strength"}

    flow_style = apply(workouts, flow_style="Slow")
    assert {w["category"] for w in flow_style} == {"Yoga"}


def test_text_search():
    workouts = load_fixture()
    results = apply(workouts, search="hip opener")
    assert {w["category"] for w in results} == {"Yoga"}
