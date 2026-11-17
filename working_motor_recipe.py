"""Resolve all model geometry during populate; backends only consume saved nodes."""
import copy
import math


def box(**kwargs):
    size = kwargs["size"]
    pos = kwargs.get("pos", [0, 0, 0])
    rot = kwargs.get("rot", [0, 0, 0])
    return {
        "shape": "box",
        "size": size,
        "pos": pos,
        "rot": rot,
    }


def cylinder(**kwargs):
    diameter = kwargs["diameter"]
    depth = kwargs["depth"]
    pos = kwargs.get("pos", [0, 0, 0])
    rot = kwargs.get("rot", [0, 0, 0])
    return {
        "shape": "cylinder",
        "diameter": diameter,
        "depth": depth,
        "pos": pos,
        "rot": rot,
    }


def polygon(**kwargs):
    points = kwargs["points"]
    depth = kwargs["depth"]
    pos = kwargs.get("pos", [0, 0, 0])
    rot = kwargs.get("rot", [0, 0, 0])
    twist = kwargs.get("twist", 0)
    return {
        "shape": "polygon",
        "points": points,
        "depth": depth,
        "pos": pos,
        "rot": rot,
        "twist": twist,
        "slices": 12,
    }


def boolean(**kwargs):
    operation = kwargs.get("operation", "difference")
    children = kwargs["children"]
    return {
        "shape": operation,
        "children": children,
        "pos": kwargs.get("pos", [0, 0, 0]),
        "rot": kwargs.get("rot", [0, 0, 0]),
    }


def component(**kwargs):
    name = kwargs["name"]
    material = kwargs.get("material", "steel")
    node = kwargs["node"]
    return {
        "name": name,
        "material": material,
        "node": node,
    }


def shaft(**kwargs):
    d = kwargs["dimensions"]
    pos = kwargs.get("pos", [0, 0, d["body_depth"]])
    rot = kwargs.get("rot", [0, 0, 0])
    double_flat = kwargs.get("double_flat", False)
    diameter = d["shaft_diameter"]
    length = d["shaft_length"]
    flat_length = d["shaft_flat_length"]
    flat = d["shaft_flat_depth"]
    children = [cylinder(diameter=diameter, depth=length)]
    for side in ([-1, 1] if double_flat else [1]):
        children.append(box(
            size=[diameter * 2, diameter, flat_length + 0.02],
            pos=[0, side * (diameter - flat), length - flat_length - 0.01],
        ))
    return boolean(children=children, pos=pos, rot=rot)


def get_stepper(**kwargs):
    d = kwargs["dimensions"]
    w = d["body_width"] / 2
    h = d["body_height"] / 2
    depth = d["body_depth"]
    chamfer = d["corner_chamfer"]
    cap = d["cap_depth"]
    pitch = d["mounting_pitch"] / 2
    points = [[-w + chamfer, -h], [w - chamfer, -h], [w, -h + chamfer], [w, h - chamfer], [w - chamfer, h], [-w + chamfer, h], [-w, h - chamfer], [-w, -h + chamfer]]
    components = []
    for name, start, thickness, material in [
        ("rear_end_cap", 0, cap, "aluminium"),
        ("stator_stack", cap, depth - 2 * cap, "black_metal"),
        ("front_end_cap", depth - cap, cap, "aluminium"),
    ]:
        node = polygon(points=points, depth=thickness, pos=[0, 0, start])
        if name == "front_end_cap":
            holes = [node]
            for x in [-pitch, pitch]:
                for y in [-pitch, pitch]:
                    holes.append(cylinder(diameter=d["mounting_hole_diameter"], depth=d["mounting_hole_depth"] + 0.02, pos=[x, y, depth - d["mounting_hole_depth"]]))
            node = boolean(children=holes)
        components.append(component(name=name, material=material, node=node))
    components.append(component(name="pilot", material="aluminium", node=cylinder(diameter=d["pilot_diameter"], depth=d["pilot_height"], pos=[0, 0, depth])))
    components.append(component(name="output_d_shaft", node=shaft(dimensions=d)))
    for x in [-pitch, pitch]:
        for y in [-pitch, pitch]:
            screw = boolean(children=[
                cylinder(diameter=4.4, depth=0.7, pos=[x, y, 0]),
                box(size=[3, 0.7, 0.4], pos=[x, y, -0.01]),
                box(size=[0.7, 3, 0.4], pos=[x, y, -0.01]),
            ])
            components.append(component(name=f"rear_screw_{x}_{y}", node=screw))
    # A small connector on the rear side makes orientation readable.
    components.append(component(name="connector", material="black_plastic", node=box(size=[14, 3, 5], pos=[0, h, 2])))
    return components


def get_dc_gearmotor_n20(**kwargs):
    d = kwargs["dimensions"]
    width = d["body_width"]
    height = d["body_height"]
    depth = d["body_depth"]
    rear = d["rear_cap_depth"]
    gearbox_start = depth - d["gearbox_depth"]
    plate = d["gearbox_plate_depth"]
    components = []
    for name, z, length, material in [
        ("rear_cap", 0, rear, "black_plastic"),
        ("motor_can", rear, gearbox_start - rear, "steel"),
    ]:
        node = boolean(operation="intersection", children=[
            cylinder(diameter=width, depth=length, pos=[0, 0, z]),
            box(size=[width, height, length], pos=[0, 0, z]),
        ])
        components.append(component(name=name, material=material, node=node))
    for index, z in enumerate([gearbox_start, depth - plate]):
        node = box(size=[width, height, plate], pos=[0, 0, z])
        if index == 1:
            holes = [node]
            for x in [-d["mounting_pitch"] / 2, d["mounting_pitch"] / 2]:
                holes.append(cylinder(diameter=d["mounting_hole_diameter"], depth=plate + 0.02, pos=[x, 0, z - 0.01]))
            node = boolean(children=holes)
        components.append(component(name=f"gearbox_plate_{index}", material="brass", node=node))
    for x in [-4.6, 4.6]:
        for y in [-3.6, 3.6]:
            components.append(component(name=f"gearbox_pillar_{x}_{y}", material="brass", node=cylinder(diameter=1.3, depth=d["gearbox_depth"] - 2 * plate, pos=[x, y, gearbox_start + plate])))
    for index in range(3):
        components.append(component(name=f"illustrative_gear_disc_{index}", material="brass", node=cylinder(diameter=6.4, depth=1.4, pos=[(-1 if index % 2 else 1) * 1.8, 0, gearbox_start + plate + index * 2])))
    components.append(component(name="output_d_shaft", node=shaft(dimensions=d)))
    for x in [-3, 3]:
        components.append(component(name=f"terminal_{x}", material="brass", node=box(size=[1.5, 0.4, 2.5], pos=[x, 0, -2.5])))
    return components


def get_dc_gearmotor_tt(**kwargs):
    d = kwargs["dimensions"]
    material = kwargs.get("housing_material", "yellow_plastic")
    width = d["body_width"]
    height = d["body_height"]
    depth = d["body_depth"]
    gear_length = d["gearbox_length"]
    left = -width / 2
    boundary = left + gear_length
    # Chamfered casing outline; output axis is Z, motor can axis X.
    points = [[left, -height / 2 + 4], [left + 4, -height / 2], [boundary - 4, -height / 2], [boundary, -height / 2 + 4], [boundary, height / 2 - 4], [boundary - 4, height / 2], [left + 4, height / 2], [left, height / 2 - 4]]
    components = []
    for index, z in enumerate([0, depth / 2 + 0.12]):
        holes = [polygon(points=points, depth=depth / 2 - 0.12, pos=[0, 0, z])]
        for y in [-d["mounting_pitch"] / 2, d["mounting_pitch"] / 2]:
            holes.append(cylinder(diameter=d["mounting_hole_diameter"], depth=depth + 0.2, pos=[boundary - 7, y, -0.1]))
        components.append(component(name=f"housing_half_{index}", material=material, node=boolean(children=holes)))
    motor_length = width - gear_length
    components.append(component(name="motor_can", node=cylinder(diameter=d["motor_diameter"], depth=motor_length - 3, pos=[boundary, 0, depth / 2], rot=[0, 90, 0])))
    components.append(component(name="motor_end_cap", material="black_plastic", node=cylinder(diameter=d["motor_diameter"], depth=3, pos=[width / 2 - 3, 0, depth / 2], rot=[0, 90, 0])))
    components.append(component(name="output_shaft", material="white_plastic", node=shaft(dimensions=d, double_flat=True, pos=[d["shaft_centre_x"], 0, depth])))
    if d["dual_shaft"]:
        components.append(component(name="opposite_output_shaft", material="white_plastic", node=shaft(dimensions=d, double_flat=True, pos=[d["shaft_centre_x"], 0, 0], rot=[180, 0, 0])))
    for y in [-4, 4]:
        components.append(component(name=f"terminal_{y}", material="brass", node=box(size=[2, 2, 0.5], pos=[width / 2 + 1, y, depth / 2])))
    return components


def get_pump_submersible(**kwargs):
    d = kwargs["dimensions"]
    width = d["body_width"]
    height = d["body_height"]
    depth = d["body_depth"]
    radius = width / 2
    circle_y = height / 2 - radius
    band = d["end_band_length"]
    middle = d["middle_band_length"]
    # Rounded upper half and flattened lower belly traced as a visual approximation.
    # Its outer envelope exactly matches the reference's 33.43 x 38.33 dimensions.
    outline = []
    for index in range(33):
        angle = math.pi * index / 32
        outline.append([radius * math.cos(angle), circle_y + radius * math.sin(angle)])
    outline.extend([
        [-radius, circle_y - 2],
        [-radius * 0.86, -height * 0.35],
        [-radius * 0.72, -height * 0.46],
        [-radius * 0.48, -height / 2],
        [radius * 0.48, -height / 2],
        [radius * 0.72, -height * 0.46],
        [radius * 0.86, -height * 0.35],
        [radius, circle_y - 2],
    ])
    inset = [[x * (width - 2*d["band_relief"]) / width, y * (height - 2*d["band_relief"]) / height] for x, y in outline]
    rear = [polygon(points=outline, depth=band)]
    # Rear openings are visible in the supplied end view, but no size is dimensioned.
    # Preserve their approximate visual dimensions separately from source measurements.
    for sign in [-1, 1]:
        rear.append(box(
            size=[6.5, 1.6, 2.2],
            pos=[sign * 8, 8, -0.1],
            rot=[0, 0, sign * 45],
        ))
    intake_arc = []
    for angle in range(215, 326, 5):
        intake_arc.append([radius * 0.86 * math.cos(math.radians(angle)), circle_y + radius * 1.15 * math.sin(math.radians(angle))])
    for angle in range(325, 214, -5):
        intake_arc.append([radius * 0.73 * math.cos(math.radians(angle)), circle_y + radius * 0.99 * math.sin(math.radians(angle))])
    rear.append(polygon(points=intake_arc, depth=2.2, pos=[0, 0, -0.1]))
    components = [
        component(name="rear_end_band_with_openings", material="grey_plastic", node=boolean(children=rear)),
        component(name="first_recessed_body_section", material="grey_plastic", node=polygon(points=inset, depth=(depth-middle)/2-band, pos=[0, 0, band])),
        component(name="middle_band", material="grey_plastic", node=polygon(points=outline, depth=middle, pos=[0, 0, (depth-middle)/2])),
        component(name="second_recessed_body_section", material="grey_plastic", node=polygon(points=inset, depth=(depth-middle)/2-band, pos=[0, 0, (depth+middle)/2])),
    ]
    front = [
        polygon(points=outline, depth=band, pos=[0, 0, depth-band]),
        cylinder(diameter=d["outlet_bore"], depth=4, pos=[0, d["outlet_offset_y"], depth-3.9]),
    ]
    components.append(component(name="front_end_band", material="grey_plastic", node=boolean(children=front)))
    for name, diameter, length, z in [
        ("outlet_collar", d["outlet_collar_diameter"], d["outlet_collar_length"], depth),
        ("outlet_tube", d["outlet_diameter"], d["outlet_length"]-d["outlet_collar_length"], depth+d["outlet_collar_length"]),
    ]:
        node = boolean(children=[
            cylinder(diameter=diameter, depth=length, pos=[0, d["outlet_offset_y"], z]),
            cylinder(diameter=d["outlet_bore"], depth=length+0.2, pos=[0, d["outlet_offset_y"], z-0.1]),
        ])
        components.append(component(name=name, material="grey_plastic", node=node))
    components.append(component(name="cable_gland_collar", material="grey_plastic", node=cylinder(diameter=14, depth=4.5, pos=[0, d["cable_gland_offset_y"], depth])))
    components.append(component(name="cable_gland", material="black_plastic", node=cylinder(diameter=d["cable_gland_diameter"], depth=d["cable_gland_length"]-4.5, pos=[0, d["cable_gland_offset_y"], depth+4.5])))
    for y in [-12.5, 13.5]:
        components.append(component(name=f"rear_projection_{y}", material="grey_plastic", node=cylinder(diameter=6, depth=d["rear_projection"], pos=[0, y, -d["rear_projection"]])))
    # Central circular rear recess shown in the reference, not a specified screw bore.
    components.append(component(name="rear_central_recess_rim", material="grey_plastic", node=boolean(children=[
        cylinder(diameter=10.0, depth=0.7, pos=[0, 0, -0.7]),
        cylinder(diameter=8.6, depth=0.9, pos=[0, 0, -0.8]),
    ])))
    return components



def get_fan_computer(**kwargs):
    d = kwargs["dimensions"]
    width = d["body_width"]
    depth = d["body_depth"]
    wall = d["frame_wall"]
    flange = d["flange_depth"]
    pitch = d["mounting_pitch"] / 2
    opening = width - 2 * wall
    hub = width * 0.33
    components = []
    for index, z in enumerate([0, depth - flange]):
        nodes = [box(size=[width, width, flange], pos=[0, 0, z])]
        nodes.append(cylinder(diameter=opening, depth=flange + 0.2, pos=[0, 0, z - 0.1]))
        for x in [-pitch, pitch]:
            for y in [-pitch, pitch]:
                nodes.append(cylinder(diameter=d["mounting_hole_diameter"], depth=flange + 0.2, pos=[x, y, z - 0.1]))
        components.append(component(name=f"mounting_flange_{index}", material="black_plastic", node=boolean(children=nodes)))
    ring = boolean(children=[
        cylinder(diameter=width, depth=depth - 2 * flange, pos=[0, 0, flange]),
        cylinder(diameter=opening, depth=depth, pos=[0, 0, 0]),
    ])
    components.append(component(name="fan_duct", material="black_plastic", node=ring))
    for index in range(4):
        angle = index * 90 + 45
        node = box(size=[width / 2, wall, flange], pos=[width / 4, 0, 0])
        components.append(component(name=f"rear_support_{index}", material="black_plastic", node=boolean(operation="union", children=[node], rot=[0, 0, angle])))
    components.append(component(name="motor_hub", material="black_plastic", node=cylinder(diameter=hub, depth=depth - flange * 1.5, pos=[0, 0, flange])))
    # Swept polygon blades with a small twist, entirely inside the duct.
    radius = opening / 2 - max(1, width * 0.015)
    profile = []
    for r, angle in [(hub * 0.43, -12), (radius * 0.8, -7), (radius, 8), (radius, 26), (radius * 0.85, 28), (hub * 0.43, 17)]:
        profile.append([r * math.cos(math.radians(angle)), r * math.sin(math.radians(angle))])
    for index in range(d["blade_count"]):
        components.append(component(name=f"blade_{index + 1}", material="black_plastic", node=polygon(points=profile, depth=max(1.1, depth * 0.32), pos=[0, 0, flange * 1.3], rot=[0, 0, index * 360 / d["blade_count"]], twist=18)))
    return components


def make_recipe(**kwargs):
    part = kwargs["part"]
    dimensions = copy.deepcopy(part["dimensions_mm"])
    family = part["family"]
    generators = {
        "stepper": get_stepper,
        "dc_gearmotor_n20": get_dc_gearmotor_n20,
        "dc_gearmotor_tt": get_dc_gearmotor_tt,
        "pump_submersible": get_pump_submersible,
        "fan_computer": get_fan_computer,
    }
    return {
        "schema_version": 1,
        "generator": "motor_csg_v1",
        "units": "mm",
        "output_folder": "three_d_model",
        "coordinate_system": {
            "origin": "Body XY centre at lower body face; TT long body axis X.",
            "axis": "+Z towards output shaft, pump outlet or fan front.",
            "stl_units": "mm",
            "glb_units": "metres",
            "glb_up_axis": "Y",
            "glb_conversion": "(x,y,z) mm -> (x,z,-y)/1000 metres",
        },
        "parameters": {
            "family": family,
            "dimensions_mm": dimensions,
            "characteristic_dimension_mm": max(dimensions["body_width"], dimensions["body_height"], dimensions["body_depth"]),
            "characteristic_dimension_basis": "maximum nominal body dimension",
        },
        "modelling_note": part["model_note"],
        "variants": {
            "full": {
                "angular_segments": 96,
            },
            "display": {
                "angular_segments": 32,
            },
        },
        "components": generators[family](dimensions=dimensions, housing_material=part.get("housing_material", "yellow_plastic")),
    }
