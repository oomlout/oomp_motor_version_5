"""Persisted studio settings and a headless Blender/Cycles render bridge."""

import copy
from functools import lru_cache
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def presentation_defaults(**kwargs):
    family = kwargs.get("family", "stepper")
    defaults = reference_presentation_defaults(family=family)
    palette = {
        "steel": {
            "name": "Satin steel",
            "base_colour_srgb": [0.62, 0.65, 0.69],
            "metallic": 1.0,
            "roughness": 0.26,
        },
        "aluminium": {
            "name": "Cast aluminium end plates",
            "base_colour_srgb": [0.72, 0.74, 0.76],
            "metallic": 0.9,
            "roughness": 0.32,
        },
        "brass": {
            "name": "Brass gearbox plates",
            "base_colour_srgb": [0.67, 0.48, 0.20],
            "metallic": 0.9,
            "roughness": 0.3,
        },
        "black_metal": {
            "name": "Black coated motor body",
            "base_colour_srgb": [0.12, 0.13, 0.15],
            "metallic": 0.65,
            "roughness": 0.33,
        },
        "black_plastic": {
            "name": "Black moulded polymer",
            "base_colour_srgb": [0.065, 0.075, 0.09],
            "metallic": 0.0,
            "roughness": 0.34,
        },
        "grey_plastic": {
            "name": "Grey pump housing",
            "base_colour_srgb": [0.42, 0.45, 0.48],
            "metallic": 0.0,
            "roughness": 0.36,
        },
        "yellow_plastic": {
            "name": "Yellow TT housing",
            "base_colour_srgb": [0.96, 0.68, 0.035],
            "metallic": 0.0,
            "roughness": 0.32,
        },
        "blue_plastic": {
            "name": "Blue TT housing",
            "base_colour_srgb": [0.075, 0.34, 0.68],
            "metallic": 0.0,
            "roughness": 0.32,
        },
        "white_plastic": {
            "name": "Natural nylon shaft",
            "base_colour_srgb": [0.86, 0.85, 0.81],
            "metallic": 0.0,
            "roughness": 0.38,
        },
    }
    materials = {}
    for name, settings in palette.items():
        materials[name] = copy.deepcopy(defaults["material"])
        materials[name].update(settings)
        materials[name]["note"] = "Visual material approximation; no exact alloy or polymer grade asserted."
    defaults["materials"] = materials
    defaults["studio"]["high_samples"] = 96
    defaults["studio"]["poses"]["product"]["resting_axis"] = "face"
    defaults["studio"]["poses"]["product"]["orientation"] = "resting on lower body face"
    for render in defaults["renders"].values():
        if render["pixels"] == 2048:
            render["pixels"] = 1024
    defaults["studio"]["reference"] = "OOMP hardware / bearing studio: same three softboxes, floor, AgX and metal microtexture; expanded material palette."
    return defaults


def reference_presentation_defaults(**kwargs):
    finish = kwargs.get("finish", "satin")
    family = kwargs.get("family", "mechanical")
    elongated = kwargs.get("elongated", False)
    black = finish == "black"
    defaults = {
        "material": {
            "name": "Black oxide steel" if black else "Satin steel",
            "base_colour_srgb": [0.205, 0.218, 0.235] if black else [0.62, 0.65, 0.69],
            "metallic": 0.8 if black else 1.0,
            "roughness": 0.31 if black else 0.26,
            "roughness_variation": 0.045,
            "coat_weight": 0.08 if black else 0.02,
            "coat_roughness": 0.28,
            "microtexture_spacing_mm": 0.025,
            "microtexture_height_um": 0.8,
            "note": "Visual finish approximation; catalogue specifies colour only.",
        },
        "studio": {
            "engine": "cycles",
            "device": "auto",
            "seed": 7991,
            "low_samples": 48,
            "high_samples": 160,
            "adaptive_threshold": 0.015,
            "denoise": True,
            "view_transform": "AgX",
            "look": "AgX - Medium High Contrast",
            "exposure": 0.0,
            "world_colour": [0.78, 0.82, 0.9],
            "world_strength": 0.35,
            "floor_colour_srgb": [0.93, 0.935, 0.94],
            "floor_roughness": 0.55,
            "framing_margin": 0.13,
            "lights": [
                {
                    "name": "Key softbox",
                    "position": [-3, -4, 6],
                    "power": 650.0,
                    "width": 4.0,
                    "height": 5.0,
                    "colour": [1.0, 0.96, 0.9],
                },
                {
                    "name": "Fill softbox",
                    "position": [4, -1, 3],
                    "power": 330.0,
                    "width": 3.0,
                    "height": 4.0,
                    "colour": [0.9, 0.95, 1.0],
                },
                {
                    "name": "Rim strip",
                    "position": [1, 4, 4],
                    "power": 850.0,
                    "width": 1.2,
                    "height": 5.0,
                    "colour": [1.0, 1.0, 1.0],
                },
            ],
            "poses": {
                "isometric": {
                    "camera_eye": [1, -1, 1],
                    "projection": "orthographic",
                    "orientation": "tip down, head up",
                },
                "product": {
                    "camera_eye": [-6, -10, 6],
                    "projection": "orthographic",
                    "orientation": "lying on side, head to left",
                    "yaw_degrees": -12.0,
                    "support": "Stable convex-hull support using actual mesh centre of mass.",
                },
            },
        },
        "renders": {
            "low": {
                "file": "render_low.png",
                "variant": "display",
                "pixels": 512,
                "view": "isometric",
            },
            "high": {
                "file": "render_high.png",
                "variant": "full",
                "pixels": 2048,
                "view": "isometric",
            },
            "product_low": {
                "file": "render_product_low.png",
                "variant": "display",
                "pixels": 512,
                "view": "product",
            },
            "product_high": {
                "file": "render_product_high.png",
                "variant": "full",
                "pixels": 2048,
                "view": "product",
            },
        },
    }
    defaults["studio"]["poses"]["isometric"]["orientation"] = "principal axis Z up"
    defaults["studio"]["poses"]["product"].update(
        resting_axis="side" if family == "bolt" or elongated else "face",
        orientation=(
            "lying on side, axial end to left"
            if family == "bolt" or elongated
            else "resting on lower face"
        ),
    )
    if finish == "nylon_white":
        defaults["material"].update(
            name="Natural white nylon",
            base_colour_srgb=[0.86, 0.85, 0.81],
            metallic=0.0,
            roughness=0.38,
            roughness_variation=0.025,
            coat_weight=0.025,
            microtexture_height_um=0.4,
            note="Visual natural nylon approximation; exact polymer grade and mould surface not supplied by catalogue.",
        )
    return defaults


@lru_cache(maxsize=1)
def blender_executable():
    configured = os.environ.get("OOMP_BLENDER_EXE")
    if configured:
        path = Path(configured)
        if not path.is_file():
            raise FileNotFoundError(f"OOMP_BLENDER_EXE not found: {configured}")
        return path
    available = shutil.which("blender")
    if available:
        return Path(available)
    candidates = list(
        (
            Path(os.environ.get("ProgramFiles", "C:/Program Files"))
            / "Blender Foundation"
        ).glob("Blender */blender.exe")
    )
    candidates += [Path("/Applications/Blender.app/Contents/MacOS/Blender")]
    existing = sorted((p for p in candidates if p.is_file()), reverse=True)
    if existing:
        import re

        return max(
            existing,
            key=lambda p: tuple(int(v) for v in re.findall(r"\d+", str(p.parent.name))),
        )
    raise FileNotFoundError(
        "Studio rendering requires Blender 4.5 or newer. Install Blender, "
        "add it to PATH, or set OOMP_BLENDER_EXE to its executable."
    )


def renderer_identity():
    path = blender_executable()
    stat = path.stat()
    result = subprocess.run(
        [str(path), "--version"], capture_output=True, text=True, encoding="utf-8"
    )
    import re

    match = re.search(r"Blender (\d+)\.(\d+)", result.stdout)
    if result.returncode or not match or tuple(map(int, match.groups())) < (4, 5):
        raise RuntimeError("Studio rendering requires Blender 4.5 or newer")
    return {
        "executable": str(path),
        "size": stat.st_size,
        "modified_ns": stat.st_mtime_ns,
        "version": result.stdout.splitlines()[0],
    }


def render_studio(**kwargs):
    """Transfer mesh geometry with sharp-edge normals; render all poses in one process."""
    meshes = kwargs["meshes"]
    p = kwargs["p"]
    recipe = kwargs["recipe"]
    output = kwargs["output"]
    import math
    import numpy as np
    import trimesh
    from motor_model_pose import product_pose

    output = Path(output)
    transfer = output / "_render_meshes.npz"
    arrays = {}
    for variant, mesh in meshes.items():
        shaded = trimesh.graph.smooth_shade(mesh, angle=math.pi / 5)
        arrays[f"{variant}_vertices"] = shaded.vertices
        arrays[f"{variant}_faces"] = shaded.faces
        arrays[f"{variant}_normals"] = shaded.vertex_normals
        if mesh.metadata.get("components"):
            from scipy.spatial import cKDTree

            original_materials = np.concatenate(
                [
                    np.full(
                        c["faces"], c["material_index"], dtype=np.int32
                    )
                    for c in mesh.metadata["components"]
                ]
            )
            distances, indices = cKDTree(mesh.triangles_center).query(
                shaded.triangles_center
            )
            if distances.max() > 1e-7:
                raise ValueError(
                    "Shading changed triangle geometry; cannot map component materials"
                )
            arrays[f"{variant}_materials"] = original_materials[indices]
    np.savez(transfer, **arrays)
    job = output / "_render_job.json"
    product_transforms, product_supports = {}, {}
    for variant, mesh in meshes.items():
        transform, support = product_pose(
            mesh=mesh, settings=recipe["studio"]["poses"]["product"]
        )
        product_transforms[variant] = transform.tolist()
        product_supports[variant] = support
    job.write_text(
        json.dumps(
            {
                "parameters": p,
                "material": recipe["material"],
                "materials": recipe["materials"],
                "studio": recipe["studio"],
                "renders": recipe["renders"],
                "output": str(output.resolve()),
                "product_transforms": product_transforms,
                "product_supports": product_supports,
                "meshes": str(transfer.resolve()),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    command = [
        str(blender_executable()),
        "--background",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python",
        str(ROOT / "motor_model_blender.py"),
        "--",
        str(job.resolve()),
    ]
    # Captured output keeps catalogue logs readable; failures retain useful diagnostics.
    result = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode:
        raise RuntimeError(
            f"Blender studio rendering failed ({result.returncode}):\n"
            f"{(result.stdout + result.stderr)[-12000:]}"
        )
    missing = [
        r["file"]
        for r in recipe["renders"].values()
        if not (output / r["file"]).is_file()
    ]
    if (
        missing
        or not (output / "studio.blend").is_file()
        or not (output / "render_scene.json").is_file()
    ):
        raise RuntimeError(
            f"Blender did not produce the complete studio asset set: {missing}"
        )
    transfer.unlink()
    job.unlink()
