"""Validate all assets and independently compile representative SCAD geometry."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import manifold3d as manifold
import numpy as np
from PIL import Image
import trimesh

from motor_io import ROOT, records, write_json
from motor_model_geometry import solid


def main(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    compile_scad = kwargs.get("compile_scad", True)
    executable = kwargs.get("openscad", shutil.which("openscad"))
    results = []
    representatives = set()
    with tempfile.TemporaryDirectory(prefix="oomp_motor_validation_") as temporary:
        for path, part in records(root=root):
            folder = path.parent
            recipe = part["three_d_model_details"]
            manifest = json.loads((folder / "three_d_model/manifest.json").read_text())
            result = {
                "id": part["oomp_id"],
                "components_closed": all(item["all_components_watertight"] for item in manifest["geometry"].values()),
                "render_count": 0,
            }
            assert result["components_closed"]
            assert part["taxonomy_14"] == part["taxonomy_15"] == ""
            ET.parse(folder / "working_mechanical_drawing.svg")
            for spec in recipe["renders"].values():
                with Image.open(folder / "three_d_model" / spec["file"]) as image:
                    assert image.size == (spec["pixels"], spec["pixels"])
                    assert np.asarray(image).std() > 5
                result["render_count"] += 1
            frame = json.loads((folder / "three_d_model/render_scene.json").read_text())
            for pose in frame["poses"].values():
                assert abs(pose["ground_clearance_mm"]) < 0.001
                assert all(item["max_frame_fraction"] < 1 for item in pose["framing"].values())
            representative = part["family"]
            if part["family"] == "dc_gearmotor_tt":
                representative += part["construction"]
            if part["family"] == "fan_computer" and part["dimensions_mm"]["body_width"] in [40, 140]:
                representative += str(part["dimensions_mm"]["body_width"])
            if compile_scad and representative not in representatives:
                if not executable:
                    raise RuntimeError("OpenSCAD required for independent SCAD validation")
                representatives.add(representative)
                destination = Path(temporary) / (representative + ".stl")
                run = subprocess.run([executable, "--backend=Manifold", "-o", str(destination), str(folder / "working.scad")], capture_output=True, text=True)
                if run.returncode:
                    raise RuntimeError(run.stderr)
                compiled_mesh = trimesh.load(destination, force="mesh")
                compiled = manifold.Manifold(manifold.Mesh(
                    vert_properties=np.asarray(compiled_mesh.vertices, dtype=np.float32),
                    tri_verts=np.asarray(compiled_mesh.faces, dtype=np.uint32),
                ))
                expected = manifold.Manifold()
                for component in recipe["components"]:
                    expected = expected + solid(node=component["node"], segments=recipe["variants"]["full"]["angular_segments"])
                assert compiled_mesh.is_watertight
                discrepancy = ((expected - compiled).volume() + (compiled - expected).volume()) / expected.volume()
                result["openscad_symmetric_difference_fraction"] = discrepancy
                assert discrepancy < 0.0002, (part["oomp_id"], discrepancy)
                print(f"OpenSCAD agrees: {part['oomp_id']} ({discrepancy:.8f})", flush=True)
            results.append(result)
    report = {
        "checked_on": "2026-11-17",
        "parts_checked": len(results),
        "renders_checked": sum(item["render_count"] for item in results),
        "scad_representatives": len(representatives),
        "results": results,
    }
    write_json(path=root / "validation.json", data=report)
    print(f"Validated {len(results)} parts and {report['renders_checked']} renders", flush=True)
    return report


if __name__ == "__main__":
    main()
