"""Catalogue invariants, physical interfaces and persistence regression tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import trimesh
import yaml

from motor_io import records, write_yaml
import working_oomp
import working_oomp_populate
from motor_model_geometry import component_meshes, export_glb


@pytest.fixture(scope="module")
def catalogue():
    return [working_oomp_populate.populate(declaration=item) for item in working_oomp_populate.declarations()]


def test_taxonomy_scope_and_unknown_values(catalogue):
    assert len(catalogue) == 17
    assert len({part["oomp_id"] for part in catalogue}) == 17
    for part in catalogue:
        assert part["taxonomy_14"] == part["taxonomy_15"] == ""
        assert len(part["taxonomy_descriptions"]) == 15
        assert part["specification_placeholders"]["torque_nm"] is None
        assert part["sources"]
    n20 = [part for part in catalogue if part["family"] == "dc_gearmotor_n20"]
    assert {part["reduction_ratio"] for part in n20} == {30, 50, 100, 150, 298}
    assert {part["voltage_v"] for part in n20} == {6}
    pump = next(part for part in catalogue if part["family"] == "pump_submersible")
    assert pump["dimension_status"] == "reference_image_nominal"
    assert pump["dimensions_mm"]["overall_length"] == pytest.approx(105.9)
    assert pump["dimensions_mm"]["body_depth"] + pump["dimensions_mm"]["outlet_length"] + pump["dimensions_mm"]["rear_projection"] == pytest.approx(105.9)
    assert pump["voltage_v"] is None
    assert pump["voltage_options_v"] == [12, 24]


def test_nema_declarations_change_only_depth():
    options = [copy.deepcopy(item) for item in working_oomp_populate.declarations() if item["family"] == "stepper"]
    assert [item["dimensions"].pop("body_depth") for item in options] == [40, 48]
    assert options[0] == options[1]


def test_every_component_is_closed_and_interface_dimensions_hold(catalogue):
    for part in catalogue:
        recipe = part["three_d_model_details"]
        meshes = component_meshes(recipe=recipe)
        assert all(mesh.is_watertight and mesh.volume > 0 for mesh in meshes)
        assert all(np.isfinite(mesh.vertices).all() for mesh in meshes)
        by_name = {mesh.metadata["name"]: mesh for mesh in meshes}
        d = part["dimensions_mm"]
        if part["family"] == "pump_submersible":
            combined = trimesh.util.concatenate(meshes)
            assert combined.extents == pytest.approx([d["body_width"], d["body_height"], d["overall_length"]], abs=0.001)
        if "output_d_shaft" in by_name:
            shaft = by_name["output_d_shaft"]
            assert shaft.extents[0] == pytest.approx(d["shaft_diameter"], abs=0.001)
            assert shaft.extents[2] == pytest.approx(d["shaft_length"], abs=0.001)
            assert shaft.bounds[0, 2] == pytest.approx(d["body_depth"], abs=0.001)
        if part["family"] == "fan_computer":
            frame = by_name["mounting_flange_0"]
            assert frame.extents[:2] == pytest.approx([d["body_width"], d["body_height"]])
            for mesh in meshes:
                if mesh.metadata["name"].startswith("blade_"):
                    assert np.linalg.norm(mesh.vertices[:, :2], axis=1).max() < (d["body_width"] - 2*d["frame_wall"])/2


def test_persisted_recipe_rebuild_and_filtered_manual_metadata(tmp_path, catalogue):
    source = catalogue[0]
    folder = tmp_path / "parts" / source["oomp_id"]
    write_yaml(path=tmp_path / "parts_source" / source["oomp_id"] / "working.yaml", data=source)
    write_yaml(path=folder / "working.yaml", data={"specialist_note": "keep this"})
    write_yaml(path=folder / "working_manual.yaml", data={
        "three_d_model_details": {
            "materials": {
                "steel": {
                    "roughness": 0.4,
                },
            },
        },
    })
    working_oomp.main(root=tmp_path)
    result = next(records(root=tmp_path))[1]
    assert result["specialist_note"] == "keep this"
    assert result["three_d_model_details"]["materials"]["steel"]["roughness"] == 0.4
    before = (folder / "working.yaml").read_bytes()
    working_oomp.main(root=tmp_path)
    assert (folder / "working.yaml").read_bytes() == before
    working_oomp_populate.main(root=tmp_path, filter="motor_fan_computer*40_mm_width*")
    assert (tmp_path / "parts_source" / source["oomp_id"] / "working.yaml").is_file()
    frozen = yaml.safe_load(yaml.safe_dump(result["three_d_model_details"]))
    assert len(component_meshes(recipe=frozen)) == len(frozen["components"])


def test_glb_metres_y_up_and_materials(tmp_path, catalogue):
    recipe = catalogue[0]["three_d_model_details"]
    meshes = component_meshes(recipe=recipe)
    output = tmp_path / "model.glb"
    export_glb(meshes=meshes, recipe=recipe, path=output)
    scene = trimesh.load(output, force="scene")
    original = trimesh.util.concatenate(meshes)
    assert scene.extents == pytest.approx(original.extents[[0, 2, 1]] / 1000, abs=0.000001)
    assert len(scene.geometry) == len(meshes)


def test_portable_model_rebuild_without_parent_checkout(tmp_path, catalogue):
    from working_three_d_model import generate_assets
    generate_assets(recipe=catalogue[0]["three_d_model_details"], folder=tmp_path, render=False)
    output = tmp_path / "three_d_model"
    (output / "model_full.glb").unlink()
    result = subprocess.run([sys.executable, str(output / "model.py")], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (output / "model_full.glb").is_file()
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["geometry"]["full"]["all_components_watertight"]
