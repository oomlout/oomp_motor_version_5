"""Nominal layout dimensions: selected generic patterns, not tolerances."""
import copy
import math


def get_dimensions(**kwargs):
    family = kwargs["family"]
    overrides = copy.deepcopy(kwargs.get("overrides", {}))
    defaults = {
        "stepper": {
            "body_width": 42.0,
            "body_height": 42.0,
            "body_depth": 40.0,
            "corner_chamfer": 3.0,
            "cap_depth": 8.0,
            "mounting_pitch": 31.0,
            "mounting_hole_diameter": 3.0,
            "mounting_hole_depth": 4.5,
            "pilot_diameter": 22.0,
            "pilot_height": 2.0,
            "shaft_diameter": 5.0,
            "shaft_length": 24.0,
            "shaft_flat_depth": 0.5,
            "shaft_flat_length": 15.0,
        },
        "dc_gearmotor_n20": {
            "body_width": 12.0,
            "body_height": 10.0,
            "body_depth": 26.0,
            "motor_depth": 15.0,
            "gearbox_depth": 9.0,
            "rear_cap_depth": 2.0,
            "gearbox_plate_depth": 1.0,
            "shaft_diameter": 3.0,
            "shaft_length": 9.0,
            "shaft_flat_depth": 0.5,
            "shaft_flat_length": 8.0,
            "mounting_pitch": 9.0,
            "mounting_hole_diameter": 1.6,
            "mounting_hole_depth": 1.0,
        },
        "dc_gearmotor_tt": {
            "body_width": 70.0,
            "body_height": 22.0,
            "body_depth": 18.0,
            "gearbox_length": 38.0,
            "motor_diameter": 18.0,
            "shaft_diameter": 5.4,
            "shaft_length": 9.0,
            "shaft_flat_depth": 0.9,
            "shaft_flat_length": 9.0,
            "shaft_centre_x": -23.0,
            "mounting_pitch": 17.5,
            "mounting_hole_diameter": 3.0,
            "dual_shaft": True,
        },
        "pump_submersible": {
            "body_width": 33.43,
            "body_height": 38.33,
            "body_depth": 79.0,
            "overall_length": 105.9,
            "outlet_length": 21.2,
            "outlet_diameter": 11.9,
            "outlet_bore": 9.7,
            "outlet_offset_x": 0.0,
            "outlet_offset_y": 9.0,
            "outlet_collar_length": 4.5,
            "outlet_collar_diameter": 14.0,
            "rear_projection": 5.7,
            "end_band_length": 13.5,
            "middle_band_length": 13.0,
            "band_relief": 0.8,
            "cable_gland_diameter": 11.0,
            "cable_gland_length": 19.0,
            "cable_gland_offset_y": -9.0,
        },
        "fan_computer": {
            "body_width": 120.0,
            "body_height": 120.0,
            "body_depth": 25.0,
            "mounting_pitch": 105.0,
            "mounting_hole_diameter": 4.3,
            "frame_wall": 3.0,
            "flange_depth": 3.0,
            "blade_count": 7,
        },
    }
    dimensions = copy.deepcopy(defaults[family])
    dimensions.update(overrides)
    for key in ("body_width", "body_height", "body_depth"):
        if dimensions[key] <= 0:
            raise ValueError(f"{family}: {key} must be positive")
    if family == "stepper":
        dimensions["mounting_hole_radius"] = dimensions["mounting_hole_diameter"] / 2
        dimensions["mounting_circle_radius"] = dimensions["mounting_pitch"] / math.sqrt(2)
        dimensions["mounting_circle_diameter"] = dimensions["mounting_pitch"] * math.sqrt(2)
        dimensions["mounting_axis_offset"] = dimensions["mounting_pitch"] / 2
        dimensions["mounting_edge_offset_x"] = (dimensions["body_width"] - dimensions["mounting_pitch"]) / 2
        dimensions["mounting_edge_offset_y"] = (dimensions["body_height"] - dimensions["mounting_pitch"]) / 2
        dimensions["pilot_radius"] = dimensions["pilot_diameter"] / 2
        dimensions["shaft_radius"] = dimensions["shaft_diameter"] / 2
    return dimensions
