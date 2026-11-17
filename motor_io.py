"""Deterministic file helpers shared by every motor build stage."""
import fnmatch
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent


def write_yaml(**kwargs):
    path = Path(kwargs["path"])
    data = kwargs["data"]
    path.parent.mkdir(parents=True, exist_ok=True)
    content = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        temporary = path.with_suffix(".yaml.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)


def write_json(**kwargs):
    path = Path(kwargs["path"])
    data = kwargs["data"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def records(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    store = kwargs.get("store", "parts")
    pattern = kwargs.get("filter", "*") or "*"
    for path in sorted((root / store).glob("*/working.yaml")):
        if fnmatch.fnmatchcase(path.parent.name, pattern):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data.get("catalogue_schema") == "oomp_motor_v5":
                yield path, data


def build_oomp_id(**kwargs):
    part = kwargs["part"]
    return "_".join(
        str(part.get(f"taxonomy_{index}", "")).strip().replace(" ", "_").replace(".", "_")
        for index in range(1, 16)
        if part.get(f"taxonomy_{index}")
    )
