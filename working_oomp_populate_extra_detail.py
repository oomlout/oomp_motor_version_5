"""Optional persistent metadata additions keyed by complete motor ID."""
import copy


def main(**kwargs):
    extras = kwargs.get("extras", [])
    details_by_id = kwargs.get("details_by_id", {})
    # Add multiline per-ID dictionaries above, or supply details_by_id explicitly.
    # Geometry changes belong in the declarations/dimensions/recipe stage.
    for part in extras:
        details = copy.deepcopy(details_by_id.get(part["oomp_id"], {}))
        if any(key.startswith("taxonomy_") or key in ("id", "oomp_id", "directory") for key in details):
            raise ValueError("Change identity in population declarations")
        part.update(details)
    return extras
