"""Run in this folder to rebuild meshes without the catalogue or sibling repos."""
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
