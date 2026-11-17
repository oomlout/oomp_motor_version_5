"""A4 orthographic SVG drawings from the same persisted component meshes."""
from html import escape
import math
import textwrap
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
import cairosvg

from motor_io import records
from motor_model_geometry import component_meshes


def nema_dimensions(**kwargs):
    d = kwargs["dimensions"]
    scale = kwargs.get("scale", 1)
    centre = kwargs.get("centre", [76, 104])
    model_centre = kwargs.get("model_centre", [0, 0])
    accent = kwargs.get("accent", "#147d83")
    x = centre[0] - model_centre[0] * scale
    y = centre[1] + model_centre[1] * scale
    pitch = d["mounting_pitch"]
    half_pitch = pitch * scale / 2
    half_width = d["body_width"] * scale / 2
    half_height = d["body_height"] * scale / 2
    offset = (d["body_width"] - pitch) / 2
    bolt_radius = pitch / math.sqrt(2)
    items = [f'<g fill="none" stroke="{accent}" stroke-width="0.25">']
    # Centre axes and construction pitch circle measured through all four bores.
    items.append(f'<path d="M{x-half_width-4} {y} H{x+half_width+4} M{x} {y-half_height-4} V{y+half_height+4}" stroke-dasharray="3 1 0.5 1"/>')
    items.append(f'<circle cx="{x}" cy="{y}" r="{bolt_radius*scale}" stroke-dasharray="2 1"/>')
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            hx, hy = x + sx*half_pitch, y + sy*half_pitch
            items.append(f'<path d="M{hx-2} {hy} H{hx+2} M{hx} {hy-2} V{hy+2}"/>')
    # Hole centre-to-centre dimensions with extension lines and arrowheads.
    dim_y = y - half_height - 9
    dim_x = x + half_width + 9
    items.append(f'<path d="M{x-half_pitch} {y-half_pitch-2} V{dim_y-2} M{x+half_pitch} {y-half_pitch-2} V{dim_y-2} M{x+half_pitch+2} {y-half_pitch} H{dim_x+2} M{x+half_pitch+2} {y+half_pitch} H{dim_x+2}"/>')
    items.append(f'<path d="M{x-half_pitch} {dim_y} H{x+half_pitch}" marker-start="url(#arrow)" marker-end="url(#arrow)"/>')
    items.append(f'<path d="M{dim_x} {y-half_pitch} V{y+half_pitch}" marker-start="url(#arrow)" marker-end="url(#arrow)"/>')
    items.append('</g>')
    items.append(f'<text x="{x}" y="{dim_y-2}" text-anchor="middle" font-size="3.3">{pitch:g} C–C</text>')
    items.append(f'<text x="{dim_x+4}" y="{y}" transform="rotate(-90 {dim_x+4} {y})" text-anchor="middle" font-size="3.3">{pitch:g} C–C</text>')
    # Radius leaders point to the actual circular interfaces.
    leaders = [
        {
            "start": [x-half_pitch-d["mounting_hole_diameter"]/2*scale, y-half_pitch],
            "elbow": [27, 76],
            "end": [14, 76],
            "label": f"4 × R{d['mounting_hole_diameter']/2:g} holes",
        },
        {
            "start": [x-d["pilot_diameter"]/2*scale, y],
            "elbow": [28, 104],
            "end": [14, 104],
            "label": f"R{d['pilot_diameter']/2:g} pilot",
        },
        {
            "start": [x-d["shaft_diameter"]/2*scale, y+1],
            "elbow": [28, 126],
            "end": [14, 126],
            "label": f"R{d['shaft_diameter']/2:g} shaft",
        },
        {
            "start": [x+bolt_radius*scale*0.7071, y+bolt_radius*scale*0.7071],
            "elbow": [119, 140],
            "end": [143, 140],
            "label": f"R{bolt_radius:.2f} bolt circle",
        },
    ]
    for leader in leaders:
        sx, sy = leader["start"]
        ex, ey = leader["elbow"]
        tx, ty = leader["end"]
        items.append(f'<path d="M{sx} {sy} L{ex} {ey} L{tx} {ty}" fill="none" stroke="{accent}" stroke-width="0.25" marker-start="url(#arrow)"/>')
        text_x = min(ex, tx)
        items.append(f'<text x="{text_x}" y="{ty-2}" font-size="2.8">{escape(leader["label"])}</text>')
    # Edge offset references a left-hand hole centre and the nominal frame edge.
    edge_y = y + half_height + 8
    items.append(f'<path d="M{x-half_width} {y+half_height+1} V{edge_y+2} M{x-half_pitch} {y+half_pitch+2} V{edge_y+2} M{x-half_width} {edge_y} H{x-half_pitch}" fill="none" stroke="{accent}" stroke-width="0.25"/>')
    items.append(f'<text x="{x-half_width-2}" y="{edge_y+1}" text-anchor="end" font-size="2.8">{offset:g} edge</text>')
    return "\n".join(items)


def projection_paths(**kwargs):
    meshes = kwargs["meshes"]
    axes = kwargs.get("axes", [0, 1])
    depth_axis = kwargs.get("depth_axis", 2)
    scale = kwargs.get("scale", 1)
    centre = kwargs.get("centre", [75, 100])
    model_centre = kwargs.get("model_centre", [0, 0])
    signs = kwargs.get("signs", [1, 1])
    depth_sign = kwargs.get("depth_sign", 1)
    paths = []
    for mesh in sorted(meshes, key=lambda item: item.bounds[1 if depth_sign > 0 else 0, depth_axis] * depth_sign):
        projected = mesh.vertices[:, axes] * signs
        faces = projected[mesh.faces]
        polygons = [Polygon(points) for points in faces if abs((points[1, 0] - points[0, 0]) * (points[2, 1] - points[0, 1]) - (points[1, 1] - points[0, 1]) * (points[2, 0] - points[0, 0])) > 0.00001]
        silhouette = unary_union(polygons).simplify(0.015)
        geometries = list(silhouette.geoms) if hasattr(silhouette, "geoms") else [silhouette]
        commands = []
        for geometry in geometries:
            if geometry.geom_type != "Polygon":
                continue
            for ring in [geometry.exterior, *geometry.interiors]:
                points = [[centre[0] + (x - model_centre[0]) * scale, centre[1] - (y - model_centre[1]) * scale] for x, y in ring.coords]
                commands.append("M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in points) + " Z")
        paths.append('<path d="' + " ".join(commands) + '" fill="#edf3f3" fill-rule="evenodd" stroke-width="0.22"/>')
    return "\n".join(paths)


def horizontal_dimension(**kwargs):
    x1 = kwargs["x1"]
    x2 = kwargs["x2"]
    y = kwargs["y"]
    start_y = kwargs["start_y"]
    label = kwargs["label"]
    accent = kwargs.get("accent", "#147d83")
    return f'''<g stroke="{accent}" fill="none" stroke-width="0.25"><path d="M{x1} {start_y} V{y-2} M{x2} {start_y} V{y-2}"/><path d="M{x1} {y} H{x2}" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g><text x="{(x1+x2)/2}" y="{y-2}" font-size="3.2" text-anchor="middle">{escape(label)}</text>'''


def vertical_dimension(**kwargs):
    y1 = kwargs["y1"]
    y2 = kwargs["y2"]
    x = kwargs["x"]
    start_x = kwargs["start_x"]
    label = kwargs["label"]
    accent = kwargs.get("accent", "#147d83")
    return f'''<g stroke="{accent}" fill="none" stroke-width="0.25"><path d="M{start_x} {y1} H{x+2} M{start_x} {y2} H{x+2}"/><path d="M{x} {y1} V{y2}" marker-start="url(#arrow)" marker-end="url(#arrow)"/></g><text x="{x-2}" y="{(y1+y2)/2}" transform="rotate(-90 {x-2} {(y1+y2)/2})" font-size="3.2" text-anchor="middle">{escape(label)}</text>'''


def pump_drawing(**kwargs):
    part = kwargs["part"]
    d = part["svg_details"]["dimensions_mm"]
    settings = part["svg_details"]
    accent = settings["accent"]
    scale = 1.35
    side = [99, 109]
    rear = [237, 109]
    depth = d["body_depth"]
    overall = d["overall_length"]
    axial_centre = (depth + d["outlet_length"] - d["rear_projection"]) / 2
    meshes = component_meshes(recipe=part["three_d_model_details"], variant="full")
    items = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">
<rect width="297" height="210" fill="white"/>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{accent}"/></marker></defs>
<g font-family="{settings['font_family']}" fill="{settings['ink']}">
<text x="12" y="15" font-size="4" fill="{accent}">OOMP / MOTOR / DIMENSION REFERENCE</text>
<text x="12" y="26" font-size="7">JT-500 / SUBMERSIBLE PUMP</text>
<text x="12" y="34" font-size="3.2">{part['oomp_id']}</text>
<text x="12" y="43" font-size="3.4">{overall:g} mm OVERALL • USER-SUPPLIED DIMENSION IMAGE • UNITS mm</text>
<path d="M12 48 H285" stroke="{accent}" stroke-width="0.6"/>
<text x="99" y="56" text-anchor="middle" font-size="3.5">SIDE / OUTLET LEFT</text>
<text x="237" y="56" text-anchor="middle" font-size="3.5">END PROFILE / OPENINGS</text>
<g stroke="{settings['ink']}" stroke-linejoin="round">''']
    items.append(projection_paths(meshes=meshes, axes=[2, 1], signs=[-1, 1], depth_axis=0, scale=scale, centre=side, model_centre=[-axial_centre, 0]))
    end_meshes = [mesh for mesh in meshes if mesh.metadata["name"] in ("rear_end_band_with_openings", "rear_central_recess_rim")]
    items.append(projection_paths(meshes=end_meshes, axes=[0, 1], depth_axis=2, depth_sign=-1, scale=scale, centre=rear))
    # Blind openings disappear in silhouette projections; draw their mouths directly.
    for sign in [-1, 1]:
        x = rear[0] + sign * 8 * scale
        y = rear[1] - 8 * scale
        items.append(f'<rect x="{x-6.5*scale/2}" y="{y-1.6*scale/2}" width="{6.5*scale}" height="{1.6*scale}" rx="0.4" transform="rotate({-sign*45} {x} {y})" fill="white" stroke-width="0.3"/>')
    items.append(f'<circle cx="{rear[0]}" cy="{rear[1]}" r="{8.6/2*scale}" fill="white" stroke-width="0.3"/>')
    rear_component = next(item for item in part["three_d_model_details"]["components"] if item["name"] == "rear_end_band_with_openings")
    arc = next(node for node in rear_component["node"]["children"][1:] if node["shape"] == "polygon")
    arc_points = [[rear[0] + x*scale, rear[1] - y*scale] for x, y in arc["points"]]
    items.append('<path d="M ' + ' L '.join(f'{x:.3f},{y:.3f}' for x, y in arc_points) + ' Z" fill="white" stroke-width="0.3"/>')
    items.append('</g>')
    outlet_x = side[0] - (depth + d["outlet_length"] - axial_centre) * scale
    front_x = side[0] - (depth - axial_centre) * scale
    back_x = side[0] + axial_centre * scale
    end_x = side[0] + (axial_centre + d["rear_projection"]) * scale
    top = side[1] - d["body_height"] * scale / 2
    bottom = side[1] + d["body_height"] * scale / 2
    items.append(horizontal_dimension(x1=outlet_x, x2=end_x, y=64, start_y=top-1, label=f"{overall:g} overall", accent=accent))
    items.append(horizontal_dimension(x1=front_x, x2=back_x, y=76, start_y=top-1, label=f"{depth:g} housing", accent=accent))
    items.append(horizontal_dimension(x1=outlet_x, x2=front_x, y=146, start_y=bottom+1, label=f"{d['outlet_length']:g}", accent=accent))
    items.append(horizontal_dimension(x1=back_x, x2=end_x, y=146, start_y=bottom+1, label=f"{d['rear_projection']:g}", accent=accent))
    items.append(horizontal_dimension(x1=rear[0]-d["body_width"]*scale/2, x2=rear[0]+d["body_width"]*scale/2, y=76, start_y=top-1, label=f"{d['body_width']:g}", accent=accent))
    items.append(vertical_dimension(y1=top, y2=bottom, x=272, start_x=rear[0]+d["body_width"]*scale/2+1, label=f"{d['body_height']:g}", accent=accent))
    outlet_y = side[1] - d["outlet_offset_y"] * scale
    items.append(vertical_dimension(y1=outlet_y-d["outlet_diameter"]*scale/2, y2=outlet_y+d["outlet_diameter"]*scale/2, x=18, start_x=outlet_x-1, label=f"Ø{d['outlet_diameter']:g}", accent=accent))
    items.append(f'<path d="M{rear[0]-8*scale} {rear[1]-8*scale} L202 88 H186" fill="none" stroke="{accent}" stroke-width="0.3"/>')
    items.append('<text x="186" y="84" font-size="2.8">2 rear slots / unmeasured</text>')
    items.append(f'<path d="M{rear[0]} {rear[1]} L211 145 H186" fill="none" stroke="{accent}" stroke-width="0.3"/>')
    items.append('<text x="186" y="151" font-size="2.8">Central recess / unmeasured</text>')
    items.append(f'<text x="12" y="163" font-size="3.3">Dimension chain: {d["outlet_length"]:g} outlet + {depth:g} housing + {d["rear_projection"]:g} rear projections = {overall:g} mm overall.</text>')
    items.append('<text x="12" y="169" font-size="3.3">Rear openings drawn directly as mounting/retention references at user request; screw sizes and spacing unspecified.</text>')
    note = "Dimensions transcribed from dimension_reference.avif. Profile curves, bands, gland, bore and rear openings are visual approximations. Rear openings are not certified screw mounts. 12 V / 24 V are separate advertised options; 5 m head and 600 L/h are not a simultaneous operating point."
    for index, line in enumerate(textwrap.wrap(note, width=145)):
        items.append(f'<text x="12" y="{179+index*4}" font-size="2.8" fill="{settings["muted"]}">{escape(line)}</text>')
    items.append(f'<path d="M12 198 H285" stroke="{accent}" stroke-width="0.4"/><text x="12" y="204" font-size="2.8">mm • scale {scale:g}:1 at A4 • supplied reference retained with part and source data • no tolerances supplied</text></g></svg>')
    return "\n".join(items)


def drawing(**kwargs):
    part = kwargs["part"]
    if part["family"] == "pump_submersible":
        return pump_drawing(part=part)
    settings = part["svg_details"]
    d = settings["dimensions_mm"]
    meshes = component_meshes(recipe=part["three_d_model_details"], variant="display")
    bounds = np.array([np.min([mesh.bounds[0] for mesh in meshes], axis=0), np.max([mesh.bounds[1] for mesh in meshes], axis=0)])
    extent = bounds[1] - bounds[0]
    centre = (bounds[1] + bounds[0]) / 2
    scale = min(2.5, 85 / max(extent))
    front = [76, 104]
    side = [215, 104]
    items = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">
<rect width="297" height="210" fill="{settings['paper']}"/>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{settings['accent']}"/></marker></defs>
<g font-family="{settings['font_family']}" fill="{settings['ink']}" stroke="none">
<text x="12" y="15" font-size="4" fill="{settings['accent']}">OOMP / MOTOR / NOMINAL LAYOUT</text>
<text x="12" y="26" font-size="7">{escape(part['form_factor'].replace('_', ' ').upper())} / {escape(part['family'].replace('_', ' ').upper())}</text>
<text x="12" y="34" font-size="3.2">{escape(part['oomp_id'])}</text>
<text x="12" y="43" font-size="3.4">BODY {d['body_width']:g} × {d['body_height']:g} × {d['body_depth']:g} mm • {escape(part['dimension_status'].replace('_', ' ').upper())}</text>
<path d="M12 48 H285" stroke="{settings['accent']}" stroke-width="0.6"/>
<text x="76" y="56" text-anchor="middle" font-size="3.5">FRONT / +Z</text>
<text x="215" y="56" text-anchor="middle" font-size="3.5">SIDE / +Y</text>
<g stroke="{settings['ink']}" stroke-linejoin="round">''']
    items.append(projection_paths(meshes=meshes, axes=[0, 1], depth_axis=2, scale=scale, centre=front, model_centre=centre[[0, 1]]))
    # A silhouette contains the floor of a blind bore; show its mouth explicitly.
    if "mounting_pitch" in d:
        pitch = d["mounting_pitch"] / 2
        if part["family"] in ("stepper", "fan_computer"):
            holes = [(x, y) for x in [-pitch, pitch] for y in [-pitch, pitch]]
        elif part["family"] == "dc_gearmotor_n20":
            holes = [(-pitch, 0), (pitch, 0)]
        else:
            holes = [(-d["body_width"] / 2 + d["gearbox_length"] - 7, y) for y in [-pitch, pitch]]
        for x, y in holes:
            items.append(f'<circle cx="{front[0] + (x-centre[0])*scale}" cy="{front[1] - (y-centre[1])*scale}" r="{d["mounting_hole_diameter"]/2*scale}" fill="white" stroke-width="0.3"/>')
    items.append(projection_paths(meshes=meshes, axes=[0, 2], depth_axis=1, scale=scale, centre=side, model_centre=centre[[0, 2]]))
    items.append('</g>')
    if part["family"] == "stepper":
        items.append(nema_dimensions(dimensions=d, scale=scale, centre=front, model_centre=centre[[0, 1]], accent=settings["accent"]))
    if part["family"] == "dc_gearmotor_n20":
        cx = front[0] - centre[0] * scale
        cy = front[1] + centre[1] * scale
        p = d["mounting_pitch"] * scale / 2
        dim_y = cy - d["body_height"] * scale / 2 - 8
        items.append(horizontal_dimension(x1=cx-p, x2=cx+p, y=dim_y, start_y=cy-2, label=f"{d['mounting_pitch']:g} C–C", accent=settings["accent"]))
        for x in [cx-p, cx+p]:
            items.append(f'<path d="M{x-2} {cy} H{x+2} M{x} {cy-2} V{cy+2}" stroke="{settings["accent"]}" stroke-width="0.25"/>')
        items.append(f'<path d="M{cx-p-d["mounting_hole_diameter"]/2*scale} {cy} L55 120 H14" fill="none" stroke="{settings["accent"]}" stroke-width="0.25"/>')
        items.append(f'<text x="14" y="117" font-size="3.2">2 × Ø{d["mounting_hole_diameter"]:g} mounting holes</text>')
    # Dimension the declared body, not protruding shafts, terminals or connectors.
    x1 = front[0] + (-d["body_width"] / 2 - centre[0]) * scale
    x2 = x1 + d["body_width"] * scale
    y = 152
    items.append(f'<path d="M{x1} {y-4} V{y+2} M{x2} {y-4} V{y+2} M{x1} {y} H{x2}" fill="none" stroke="{settings["accent"]}" stroke-width="0.3"/>')
    items.append(f'<text x="{(x1+x2)/2}" y="{y-2}" text-anchor="middle" font-size="3.3">{d["body_width"]:g} body width</text>')
    z1 = side[1] - (0 - centre[2]) * scale
    z2 = side[1] - (d["body_depth"] - centre[2]) * scale
    items.append(f'<path d="M266 {z1} H278 M266 {z2} H278 M275 {z1} V{z2}" fill="none" stroke="{settings["accent"]}" stroke-width="0.3"/>')
    items.append(f'<text x="280" y="{(z1+z2)/2}" transform="rotate(-90 280 {(z1+z2)/2})" text-anchor="middle" font-size="3.3">{d["body_depth"]:g} body depth</text>')
    specifications = []
    if "shaft_diameter" in d:
        specifications.append(f"Shaft Ø{d['shaft_diameter']:g} × {d['shaft_length']:g} mm (exposed from body face)")
    if "mounting_pitch" in d:
        pattern = "square" if part["family"] in ("stepper", "fan_computer") else "linear"
        specifications.append(f"Mounting {d['mounting_pitch']:g} mm {pattern} pitch / Ø{d['mounting_hole_diameter']:g} mm")
    if part["family"] == "stepper":
        specifications.append(f"Hole centres ±{d['mounting_pitch']/2:g} mm from each axis; {(d['body_width']-d['mounting_pitch'])/2:g} mm from each nominal edge; bolt circle Ø{d['mounting_pitch']*math.sqrt(2):.2f} mm")
    if "outlet_diameter" in d:
        specifications.append(f"Provisional outlet Ø{d['outlet_diameter']:g} / bore Ø{d['outlet_bore']:g} mm; overall height {d['body_depth']+d['outlet_length']:g} mm")
    for index, line in enumerate(specifications):
        items.append(f'<text x="12" y="{163+index*5}" font-size="3.4">{escape(line)}</text>')
    note = "ILLUSTRATIVE MODEL. " + part["dimension_note"]
    for index, line in enumerate(textwrap.wrap(note, width=145)):
        items.append(f'<text x="12" y="{178+index*4}" font-size="2.8" fill="{settings["muted"]}">{escape(line)}</text>')
    items.append(f'<path d="M12 198 H285" stroke="{settings["accent"]}" stroke-width="0.4"/><text x="12" y="204" font-size="2.8">mm • scale {scale:.3f}:1 at A4 • simplified component projections • source notes in working.yaml</text></g></svg>')
    return "\n".join(items)


def main(**kwargs):
    rasterize = kwargs.get("rasterize", True)
    count = 0
    for path, part in records(**kwargs):
        svg = drawing(part=part)
        destination = path.parent / "working_mechanical_drawing.svg"
        destination.write_text(svg, encoding="utf-8")
        if rasterize:
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(destination.with_suffix(".png")), output_width=1485, output_height=1050)
        count += 1
    print(f"Generated {count} motor drawings", flush=True)
    return count
