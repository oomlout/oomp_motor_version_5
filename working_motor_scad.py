"""SCAD and optional STL stage, reading canonical records only."""
from motor_io import records
from motor_model_geometry import assembly_mesh, component_meshes, scad_source


def main(**kwargs):
    generate_stl = kwargs.get("generate_stl", kwargs.get("typ") == "all")
    count = 0
    for path, part in records(**kwargs):
        recipe = part["three_d_model_details"]
        (path.parent / "working.scad").write_text(scad_source(recipe=recipe), encoding="utf-8")
        if generate_stl:
            meshes = component_meshes(recipe=recipe)
            assembly_mesh(meshes=meshes, materials=recipe["materials"]).export(path.parent / "3dpr.stl")
        count += 1
    print(f"Generated {count} motor SCAD files", flush=True)
    return count
