"""Materialize populated records without launching background project actions."""
import copy
import shutil
from pathlib import Path
import yaml
from motor_io import ROOT, records, write_yaml


def merge(**kwargs):
    original = copy.deepcopy(kwargs.get("original", {}))
    updates = kwargs.get("updates", {})
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            original[key] = merge(original=original[key], updates=value)
        else:
            original[key] = copy.deepcopy(value)
    return original


def main(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    options = dict(kwargs)
    options["store"] = "parts_source"
    count = 0
    for path, source in records(**options):
        destination = root / "parts" / source["oomp_id"] / "working.yaml"
        previous = yaml.safe_load(destination.read_text(encoding="utf-8")) if destination.exists() else {}
        part = merge(original=previous or {}, updates=source)
        manual = destination.parent / "working_manual.yaml"
        if manual.exists():
            overrides = yaml.safe_load(manual.read_text(encoding="utf-8")) or {}
            if any(key in overrides for key in ("id", "oomp_id", "directory")) or any(key.startswith("taxonomy_") for key in overrides):
                raise ValueError("Change identity in populate, not working_manual.yaml")
            part = merge(original=part, updates=overrides)
        write_yaml(path=destination, data=part)
        reference = source.get("dimension_reference")
        if reference:
            reference_source = root / reference["source_file"]
            reference_destination = destination.parent / reference["part_file"]
            if reference_source.is_file() and not reference_destination.exists():
                shutil.copyfile(reference_source, reference_destination)
        count += 1
    print(f"Materialized {count} motor records", flush=True)
    return count


def load_parts(**kwargs):
    return main(**kwargs)


if __name__ == "__main__":
    main()
