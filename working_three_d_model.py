"""Build portable mesh, studio and render bundles from saved population recipes."""
import hashlib
import json
from pathlib import Path
import shutil

from motor_io import ROOT, records, write_json
from motor_model_geometry import assembly_mesh, component_meshes, export_glb
from motor_model_render import render_studio


def fingerprint(**kwargs):
    recipe = kwargs["recipe"]
    digest = hashlib.sha256(json.dumps(recipe, sort_keys=True).encode())
    for name in ["motor_model_geometry.py", "motor_model_render.py", "motor_model_blender.py", "motor_model_pose.py", "working_three_d_model.py"]:
        digest.update((ROOT / name).read_bytes())
    return digest.hexdigest()


def generate_assets(**kwargs):
    recipe = kwargs["recipe"]
    folder = Path(kwargs["folder"])
    force = kwargs.get("force", False)
    render = kwargs.get("render", True)
    output = folder / "three_d_model"
    expected = ["model_full.stl", "model_display.stl", "model_full.glb", "model_display.glb", "parameters.json", "model.py", "motor_model_geometry.py", "requirements.txt"]
    if render:
        expected += [item["file"] for item in recipe["renders"].values()] + ["studio.blend", "render_scene.json"]
    signature = fingerprint(recipe=recipe)
    manifest_path = output / "manifest.json"
    if not force and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("fingerprint") == signature and (not render or manifest.get("rendered")) and all((output / name).is_file() for name in expected):
            return manifest
    output.mkdir(parents=True, exist_ok=True)
    # Keep complete old output until the replacement has been built and verified.
    stage = output / "_build"
    stage.mkdir(exist_ok=True)
    for item in stage.iterdir():
        if item.is_file():
            item.unlink()
    meshes = {}
    bounds = {}
    for variant in recipe["variants"]:
        components = component_meshes(recipe=recipe, variant=variant)
        mesh = assembly_mesh(meshes=components, materials=recipe["materials"])
        meshes[variant] = mesh
        mesh.export(stage / f"model_{variant}.stl")
        export_glb(meshes=components, recipe=recipe, path=stage / f"model_{variant}.glb")
        bounds[variant] = {
            "bounds_mm": mesh.bounds.tolist(),
            "components": len(components),
            "triangles": len(mesh.faces),
            "all_components_watertight": all(item.is_watertight for item in components),
            "assembly_note": "Separate closed visual components may touch or overlap; STL is an assembly, not a printable union.",
        }
    write_json(path=stage / "parameters.json", data=recipe)
    (stage / "requirements.txt").write_text("numpy>=1.26\ntrimesh>=4\nmanifold3d>=3\nscipy>=1.11\n", encoding="utf-8")
    shutil.copyfile(ROOT / "motor_model_geometry.py", stage / "motor_model_geometry.py")
    (stage / "model.py").write_text('''"""Run in this folder to rebuild meshes without the catalogue or sibling repos."""
import json
from pathlib import Path
from motor_model_geometry import component_meshes, assembly_mesh, export_glb


def main(**kwargs):
    root = Path(kwargs.get("root", Path(__file__).resolve().parent))
    recipe = json.loads((root / "parameters.json").read_text(encoding="utf-8"))
    for variant in recipe["variants"]:
        meshes = component_meshes(recipe=recipe, variant=variant)
        assembly_mesh(meshes=meshes, materials=recipe["materials"]).export(root / f"model_{variant}.stl")
        export_glb(meshes=meshes, recipe=recipe, path=root / f"model_{variant}.glb")


if __name__ == "__main__":
    main()
''', encoding="utf-8")
    if render:
        # The Blender script skips existing files, so stale stage renders must go.
        for item in recipe["renders"].values():
            (stage / item["file"]).unlink(missing_ok=True)
        render_studio(meshes=meshes, p=recipe["parameters"], recipe=recipe, output=stage)
    manifest = {
        "fingerprint": signature,
        "schema_version": 1,
        "units": "mm; GLB metres/Y-up",
        "geometry": bounds,
        "rendered": render,
        "files": sorted(item.name for item in stage.iterdir() if item.is_file()),
    }
    for item in stage.iterdir():
        if item.is_file():
            item.replace(output / item.name)
    stage.rmdir()
    # Write manifest last, so incomplete exports can never count as fresh.
    write_json(path=manifest_path, data=manifest)
    if render:
        shutil.copyfile(output / "render_product_low.png", folder / "image.png")
    return manifest


def main(**kwargs):
    force = kwargs.get("force", False)
    render = kwargs.get("render", True)
    count = 0
    for path, part in records(**kwargs):
        print(f"Building models: {part['oomp_id']}", flush=True)
        generate_assets(recipe=part["three_d_model_details"], folder=path.parent, force=force, render=render)
        count += 1
    return count


if __name__ == "__main__":
    main()
