"""Render the persisted primitive tree as Manifold meshes or editable OpenSCAD."""
import json
import numpy as np
import manifold3d as manifold
import trimesh


def twisted_polyhedron(**kwargs):
    node = kwargs["node"]
    points = np.asarray(node["points"], dtype=float)
    slices = node["slices"]
    count = len(points)
    vertices = []
    faces = []
    for layer in range(slices + 1):
        angle = np.deg2rad(node["twist"] * layer / slices)
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        for x, y in points @ rotation.T:
            vertices.append([x, y, node["depth"] * layer / slices])
    for a, b, c in manifold.triangulate([points]):
        faces.append([int(c), int(b), int(a)])
        faces.append([int(a) + slices * count, int(b) + slices * count, int(c) + slices * count])
    for layer in range(slices):
        for index in range(count):
            a = layer * count + index
            b = layer * count + (index + 1) % count
            faces.extend([[a, b, b + count], [a, b + count, a + count]])
    return vertices, faces


def solid(**kwargs):
    node = kwargs["node"]
    segments = kwargs.get("segments", 96)
    shape = node["shape"]
    if shape == "box":
        size = node["size"]
        result = manifold.Manifold.cube(size).translate([-size[0] / 2, -size[1] / 2, 0])
    elif shape == "cylinder":
        result = manifold.Manifold.cylinder(node["depth"], node["diameter"] / 2, circular_segments=segments)
    elif shape == "polygon":
        if node["twist"]:
            vertices, faces = twisted_polyhedron(node=node)
            result = manifold.Manifold(manifold.Mesh(np.asarray(vertices, dtype=np.float32), np.asarray(faces, dtype=np.uint32)))
        else:
            result = manifold.CrossSection([node["points"]]).extrude(node["depth"])
    else:
        children = [solid(node=child, segments=segments) for child in node["children"]]
        result = children[0]
        for child in children[1:]:
            if shape == "difference":
                result = result - child
            elif shape == "union":
                result = result + child
            elif shape == "intersection":
                result = result ^ child
            else:
                raise ValueError(f"Unsupported geometry: {shape}")
    return result.rotate(node["rot"]).translate(node["pos"])


def component_meshes(**kwargs):
    recipe = kwargs["recipe"]
    variant = kwargs.get("variant", "full")
    segments = recipe["variants"][variant]["angular_segments"]
    meshes = []
    for item in recipe["components"]:
        body = solid(node=item["node"], segments=segments)
        data = body.to_mesh()
        mesh = trimesh.Trimesh(vertices=np.asarray(data.vert_properties)[:, :3], faces=np.asarray(data.tri_verts), process=True)
        if mesh.is_empty or not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f"Invalid {variant} component: {item['name']}")
        mesh.metadata = {
            "name": item["name"],
            "material": item["material"],
        }
        meshes.append(mesh)
    return meshes


def assembly_mesh(**kwargs):
    meshes = kwargs["meshes"]
    materials = kwargs["materials"]
    names = list(materials)
    combined = trimesh.util.concatenate(meshes)
    combined.metadata["components"] = [
        {
            "name": mesh.metadata["name"],
            "faces": len(mesh.faces),
            "material_index": names.index(mesh.metadata["material"]),
        }
        for mesh in meshes
    ]
    return combined


def scad_node(**kwargs):
    node = kwargs["node"]
    shape = node["shape"]
    prefix = f"translate({json.dumps(node['pos'])}) rotate({json.dumps(node['rot'])}) "
    if shape == "box":
        size = node["size"]
        body = f"translate({[-size[0] / 2, -size[1] / 2, 0]}) cube({size});"
    elif shape == "cylinder":
        body = f"cylinder(d={node['diameter']}, h={node['depth']});"
    elif shape == "polygon":
        if node["twist"]:
            # Explicit faces prevent backends choosing different diagonals on twisted quads.
            vertices, faces = twisted_polyhedron(node=node)
            body = f"polyhedron(points={json.dumps(vertices)}, faces={json.dumps([face[::-1] for face in faces])}, convexity=10);"
        else:
            body = f"linear_extrude(height={node['depth']}) polygon({json.dumps(node['points'])});"
    else:
        body = shape + "() {\n" + "\n".join(scad_node(node=child) for child in node["children"]) + "\n}"
    return prefix + body


def scad_source(**kwargs):
    recipe = kwargs["recipe"]
    lines = [
        "// Generated from persisted three_d_model_details. Dimensions in millimetres.",
        "// Nominal layout assembly, not manufacturing geometry.",
        f"$fn = {recipe['variants']['full']['angular_segments']};",
    ]
    for item in recipe["components"]:
        colour = recipe["materials"][item["material"]]["base_colour_srgb"]
        lines.extend(["// " + item["name"], f"color({colour}) " + scad_node(node=item["node"])])
    return "\n".join(lines) + "\n"


def export_glb(**kwargs):
    meshes = kwargs["meshes"]
    recipe = kwargs["recipe"]
    path = kwargs["path"]
    scene = trimesh.Scene()
    transform = np.array([[0.001, 0, 0, 0], [0, 0, 0.001, 0], [0, -0.001, 0, 0], [0, 0, 0, 1]])
    for source in meshes:
        mesh = source.copy()
        settings = recipe["materials"][source.metadata["material"]]
        mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            name=settings["name"],
            baseColorFactor=[round(v * 255) for v in settings["base_colour_srgb"]] + [255],
            metallicFactor=settings["metallic"],
            roughnessFactor=settings["roughness"],
        ))
        mesh.apply_transform(transform)
        scene.add_geometry(mesh, node_name=source.metadata["name"])
    path.write_bytes(scene.export(file_type="glb"))
