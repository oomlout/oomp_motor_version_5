"""Exercise public build entry points without running rendering or CAD."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
BACKENDS = (
    "working_oomp_populate",
    "working_oomp",
    "working_scad",
    "working_svg",
    "working_action",
    "working_solidcraft",
    "working_three_d_model",
    "working_motor_documentation",
)


def load(filename):
    spec = importlib.util.spec_from_file_location("entry_test_" + filename, PROJECT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_entry(filename, **kwargs):
    calls = []
    def record(name):
        return SimpleNamespace(main=lambda **options: calls.append((name, options)))
    modules = {name: record(name) for name in BACKENDS}
    modules["working"] = load("working.py")
    with patch.dict(sys.modules, modules):
        load(filename).main(**kwargs)
    return calls


def test_make_all_runs_motor_stages_in_order():
    calls = run_entry("action_make_all.py", filter="motor_stepper*")
    assert [name for name, _ in calls] == [
        "working_oomp_populate",
        "working_oomp",
        "working_scad",
        "working_svg",
        "working_three_d_model",
        "working_motor_documentation",
    ]
    assert calls[2][1]["typ"] == "all"
    assert all(options.get("filter") == "motor_stepper*" for _, options in calls)


def test_working_default_runs_complete_progression():
    calls = run_entry("working.py")
    assert [name for name, _ in calls] == [
        "working_oomp_populate",
        "working_oomp",
        "working_scad",
        "working_svg",
        "working_three_d_model",
        "working_motor_documentation",
    ]


def test_no_stl_entry_has_no_mesh_or_render_stage():
    calls = run_entry("action_make_all_no_stl.py")
    assert [name for name, _ in calls] == [
        "working_oomp_populate", "working_oomp", "working_scad",
        "working_svg", "working_motor_documentation",
    ]
    assert calls[2][1].get("typ") != "all"


def test_saved_yaml_rebuild_skips_population_and_materialization():
    calls = run_entry("working.py", run_oomp_populate=False, run_oomp=False)
    assert [name for name, _ in calls] == [
        "working_scad", "working_svg", "working_three_d_model",
        "working_motor_documentation",
    ]


def test_scad_entries_exclude_other_backends():
    for filename in ["action_make_scad.py", "action_make_scad_no_stl.py"]:
        calls = run_entry(filename, run_solidcraft=True)
        assert [name for name, _ in calls] == [
            "working_oomp_populate", "working_oomp", "working_scad",
        ]


def test_invalid_solidcraft_mode_fails_before_mutation():
    import pytest
    with pytest.raises(ValueError, match="run_solidcraft"):
        run_entry("action_make_all.py", run_solidcraft="false")


def test_native_only_keeps_existing_explicit_entry_contract():
    calls = run_entry("action_make_solidcraft.py", run_solidcraft="working_scad")
    assert [name for name, _ in calls] == [
        "working_oomp_populate", "working_oomp", "working_solidcraft",
    ]
    assert calls[-1][1]["solidcraft_context"]["recipe_source"] == "working_scad"
