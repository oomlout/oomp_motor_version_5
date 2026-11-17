"""Declare variants, then freeze dimensions, geometry, drawings and presentation."""
import copy
import fnmatch
from pathlib import Path

from motor_io import ROOT, build_oomp_id, write_yaml
from working_motor_dimensions import get_dimensions


def declarations(**kwargs):
    stepper_depths = kwargs.get("stepper_depths", [40, 48])
    n20_ratios = kwargs.get("n20_ratios", [30, 50, 100, 150, 298])
    n20_voltage = kwargs.get("n20_voltage", 6)
    tt_voltage = kwargs.get("tt_voltage", 6)
    options = []
    # Only depth changes between these NEMA entries.
    for depth in stepper_depths:
        options.append({
            "family": "stepper",
            "form_factor": "nema_17",
            "construction": "",
            "voltage_v": None,
            "reduction_ratio": None,
            "dimensions": {
                "body_depth": depth,
            },
            "description": "Generic NEMA 17 stepper; winding, current, torque and step angle unspecified.",
            "dimension_status": "nominal_generic",
            "dimension_note": "Selected common 42 mm face, 31 mm mounting pitch, 22 mm pilot and 5 x 24 mm shaft. Frame designation does not fix body or shaft length. Mounting threads represented by smooth holes.",
            "sources": [
                {
                    "url": "https://www.omc-stepperonline.com/nema-17-unipolar-1-8deg-26ncm-37oz-in-0-4a-12v-42x42x39mm-6-wires-17hs15-0406s",
                    "supports": "Example 42 mm frame, 40 mm body, 5 x 24 mm shaft. Electrical specifications not inherited.",
                },
            ],
        })
    # Common available options, not a claim about sales-volume ranking.
    for ratio in n20_ratios:
        options.append({
            "family": "dc_gearmotor_n20",
            "form_factor": "n20",
            "construction": "",
            "voltage_v": n20_voltage,
            "reduction_ratio": ratio,
            "dimensions": {},
            "description": "Generic N20 micro metal gearmotor; nominal voltage and reduction only. Winding, speed, torque and encoder unspecified.",
            "dimension_status": "nominal_generic",
            "dimension_note": "12 x 10 mm gearbox and 3 x 9 mm D shaft reference; 26 mm body is a layout choice. Exact ratio and length vary by supplier. Gearbox plates and visible gear discs are illustrative.",
            "sources": [
                {
                    "url": "https://www.pololu.com/category/60/micro-metal-gearmotors",
                    "supports": "Available 6 V family and nominal 30, 50, 100, 150 and 298:1 options; not a popularity ranking.",
                },
                {
                    "url": "https://www.pololu.com/product/2371",
                    "supports": "12 x 10 mm cross-section and 3 x 9 mm D shaft. Nominal 298:1 reference actual ratio is 297.92:1.",
                },
            ],
        })
    tt_variants = [
        {
            "construction": "plastic_gear",
            "ratio": 48,
            "width": 70.0,
            "depth": 18.0,
            "dual_shaft": True,
            "housing_material": "yellow_plastic",
            "source": "https://www.adafruit.com/product/3777",
        },
        {
            "construction": "bi_metal_gear",
            "ratio": 90,
            "width": 70.0,
            "depth": 22.0,
            "dual_shaft": False,
            "housing_material": "blue_plastic",
            "source": "https://www.adafruit.com/product/3801",
        },
        {
            "construction": "all_metal_gear",
            "ratio": 90,
            "width": 69.5,
            "depth": 20.7,
            "dual_shaft": False,
            "housing_material": "blue_plastic",
            "source": "https://www.adafruit.com/product/3802",
        },
    ]
    for variant in tt_variants:
        options.append({
            "family": "dc_gearmotor_tt",
            "form_factor": "tt",
            "construction": variant["construction"],
            "voltage_v": tt_voltage,
            "operating_voltage_range_v": [3, 6],
            "reduction_ratio": variant["ratio"],
            "housing_material": variant["housing_material"],
            "dimensions": {
                "body_width": variant["width"],
                "body_depth": variant["depth"],
                "dual_shaft": variant["dual_shaft"],
            },
            "description": "Generic TT right-angle gearmotor. Gear construction describes internal gears; all variants have a plastic housing.",
            "dimension_status": "nominal_generic",
            "dimension_note": "Reference body envelope excludes shaft. Shaft profile, mounting holes and casing details are illustrative layout choices.",
            "sources": [
                {
                    "url": variant["source"],
                    "supports": "Body dimensions, 3-6 V operating range, gear construction and nominal reduction.",
                },
            ],
        })
    options.append({
        "family": "pump_submersible",
        "form_factor": "jt_500",
        "construction": "",
        "voltage_v": None,
        "voltage_options_v": [12, 24],
        "reduction_ratio": None,
        "advertised_flow_l_h": 600,
        "advertised_head_m": 5,
        "dimensions": {},
        "description": "JT-500-style listing reference. 12 V and 24 V are advertised options, not a verified dual-voltage rating.",
        "dimension_status": "reference_image_nominal",
        "dimension_note": "User-supplied dimension image: body 79 mm, end profile 33.43 x 38.33 mm, outlet projection 21.2 mm, rear projections 5.7 mm, overall 105.9 mm, outlet OD 11.9 mm. Unlabelled profile curves, bands, gland, outlet bore and rear openings are visual approximations. Rear openings are shown at user request as mounting/retention references; the image does not establish their screw sizes, spacing or intended function.",
        "dimension_reference": {
            "source_file": "source_file/dimension/jt_500_dimension_reference.avif",
            "part_file": "dimension_reference.avif",
            "authority": "User-supplied product dimension image, transcribed 2026-11-17; no tolerances shown.",
            "explicit_dimension_keys": [
                "body_width",
                "body_height",
                "body_depth",
                "overall_length",
                "outlet_length",
                "outlet_diameter",
                "rear_projection",
            ],
        },
        "sources": [
            {
                "url": "https://www.alibaba.com/product-detail/JT-500-12V-24V-600L-H_1601326199745.html",
                "supports": "User-supplied title: JT-500, 12/24 V options, 600 L/h. No readable specification table on 2026-11-17.",
            },
            {
                "url": "dimension_reference.avif",
                "supports": "User-supplied dimension image: 105.9 overall, 79 housing, 21.2 outlet, 5.7 rear projections, 33.43 width, 38.33 height and 11.9 outlet diameter (mm). Table advertises separate 12/24 V options, 5 m head and 600 L/h; these are not one simultaneous operating point. Power cell contains no numeric rating.",
            },
        ],
    })
    fan_variants = [
        {
            "size": 40,
            "depth": 10,
            "pitch": 32,
            "source": "https://www.noctua.at/en/products/nf-a4x10-pwm/specifications",
        },
        {
            "size": 60,
            "depth": 25,
            "pitch": 50,
            "source": "https://www.noctua.at/en/products/nf-a6x25-flx/specifications",
        },
        {
            "size": 80,
            "depth": 25,
            "pitch": 71.5,
            "source": "https://www.noctua.at/en/products/nf-a8-pwm/specifications",
        },
        {
            "size": 92,
            "depth": 25,
            "pitch": 82.5,
            "source": "https://support.arctic.de/products/f9/techdocs/92mm_fan-Mounting_hole_pattern.pdf",
        },
        {
            "size": 120,
            "depth": 25,
            "pitch": 105,
            "source": "https://www.noctua.at/en/products/nf-a12x25-pwm/specifications",
        },
        {
            "size": 140,
            "depth": 25,
            "pitch": 124.5,
            "source": "https://www.noctua.at/en/products/nf-a14-pwm/specifications",
        },
    ]
    for variant in fan_variants:
        options.append({
            "family": "fan_computer",
            "form_factor": "square_axial",
            "construction": "",
            "voltage_v": 12,
            "reduction_ratio": None,
            "dimensions": {
                "body_width": variant["size"],
                "body_height": variant["size"],
                "body_depth": variant["depth"],
                "mounting_pitch": variant["pitch"],
                "frame_wall": min(3.0, variant["size"] * 0.04),
                "flange_depth": min(3.0, variant["depth"] / 5),
            },
            "description": "Generic square computer fan; speed, airflow, bearing, connector and control unspecified.",
            "dimension_status": "nominal_generic",
            "dimension_note": "Nominal envelope and mounting pattern. Hub and blades are illustrative, not aerodynamic designs. The 40 x 10 mm label is nominal (reference physical depth can be 11 mm). Confirm actual supplier before mounting.",
            "sources": [
                {
                    "url": variant["source"],
                    "supports": "Reference form factor / mounting pattern only; branded performance and geometry not inherited.",
                },
            ],
        })
    return options


def populate(**kwargs):
    declaration = copy.deepcopy(kwargs["declaration"])
    manufacturer = kwargs.get("manufacturer", "")
    part_number = kwargs.get("part_number", "")
    from working_motor_recipe import make_recipe
    from motor_model_render import presentation_defaults
    family = declaration["family"]
    dimensions = get_dimensions(family=family, overrides=declaration["dimensions"])
    part = copy.deepcopy(declaration)
    part.pop("dimensions")
    part["catalogue_schema"] = "oomp_motor_v5"
    part["dimensions_mm"] = dimensions
    part["source_checked"] = "2026-11-17"
    part["taxonomy_1"] = "motor"
    part["taxonomy_2"] = "dc_gearmotor" if family.startswith("dc_gearmotor_") else family
    part["taxonomy_3"] = declaration["form_factor"]
    part["taxonomy_4"] = declaration["construction"]
    part["taxonomy_5"] = f"{dimensions['body_width']:g}_mm_width" if family == "fan_computer" else ""
    part["taxonomy_6"] = ""
    part["taxonomy_7"] = f"{dimensions['body_depth']:g}_mm_depth" if family in ("stepper", "fan_computer") else ""
    part["taxonomy_8"] = f"{declaration['voltage_v']:g}_volt" if declaration["voltage_v"] else ""
    part["taxonomy_9"] = f"{declaration['reduction_ratio']:g}_to_1_reduction" if declaration["reduction_ratio"] else ""
    part["taxonomy_10"] = ""
    part["taxonomy_11"] = ""
    part["taxonomy_12"] = ""
    part["taxonomy_13"] = ""
    part["taxonomy_14"] = manufacturer
    part["taxonomy_15"] = part_number
    part["taxonomy_descriptions"] = {
        "taxonomy_1": "Class: motor, including driven pumps and fans.",
        "taxonomy_2": "Functional family.",
        "taxonomy_3": "Frame, form factor or generic model series.",
        "taxonomy_4": "Construction variant, e.g. gearbox gear material.",
        "taxonomy_5": "Nominal body width / frame size where needed.",
        "taxonomy_6": "Reserved: body height / diameter or secondary envelope.",
        "taxonomy_7": "Nominal body depth excluding shaft / outlet.",
        "taxonomy_8": "Nominal voltage; empty for unknown or unselected options.",
        "taxonomy_9": "Nominal input-to-output gear reduction.",
        "taxonomy_10": "Reserved: winding / step angle / electrical variant.",
        "taxonomy_11": "Reserved: speed / torque / flow performance grade.",
        "taxonomy_12": "Reserved: shaft / mounting / outlet configuration.",
        "taxonomy_13": "Reserved: encoder / connector / control / bearing option.",
        "taxonomy_14": "Manufacturer placeholder; empty until selected.",
        "taxonomy_15": "Manufacturer part number placeholder; empty until verified.",
    }
    part["specification_placeholders"] = {
        "manufacturer": manufacturer,
        "manufacturer_part_number": part_number,
        "rated_current_a": None,
        "no_load_speed_rpm": None,
        "torque_nm": None,
        "step_angle_degrees": None,
        "winding": None,
        "encoder": None,
        "connector": None,
        "bearing": None,
    }
    part["oomp_id"] = build_oomp_id(part=part)
    part["id"] = part["oomp_id"]
    part["name"] = part["oomp_id"].replace("_", " ")
    part["name_proper"] = part["name"].replace("nema 17", "NEMA 17").replace("n20", "N20").replace("jt 500", "JT-500")
    part["directory"] = "parts/" + part["oomp_id"]
    part["model_note"] = "Nominal external assembly for identification and layout; internal motor construction, exact gears, windings and flexible leads omitted. Not manufacturing geometry. " + part["dimension_note"]
    recipe = make_recipe(part=part)
    recipe.update(presentation_defaults(family=family))
    part["three_d_model_details"] = recipe
    part["oobb_type"] = "motor"
    part["oobb_details"] = {
        "oobb_type": "motor",
        "oobb_name": family,
        "run_scad": True,
        "run_solidcraft": False,
        "recipe_source": "three_d_model_details",
        "units": "mm",
    }
    part["svg_details"] = {
        "svg_name": "motor_mechanical_drawing",
        "filename": "working_mechanical_drawing",
        "sheet_width_mm": 297,
        "sheet_height_mm": 210,
        "ink": "#183336",
        "accent": "#147d83",
        "muted": "#61767a",
        "paper": "#ffffff",
        "font_family": "Arial, sans-serif",
        "line_width_mm": 0.35,
        "dimensions_mm": copy.deepcopy(dimensions),
    }
    return part


def main(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    pattern = kwargs.get("filter", "*") or "*"
    options = [populate(declaration=item) for item in declarations(**kwargs)]
    import working_oomp_populate_extra_detail
    working_oomp_populate_extra_detail.main(extras=options, details_by_id=kwargs.get("details_by_id", {}))
    ids = [part["oomp_id"] for part in options]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate motor taxonomy IDs")
    selected = [part for part in options if fnmatch.fnmatchcase(part["oomp_id"], pattern)]
    for part in selected:
        write_yaml(path=root / "parts_source" / part["oomp_id"] / "working.yaml", data=part)
    print(f"Populated {len(selected)} motor records", flush=True)
    return selected


if __name__ == "__main__":
    main()
