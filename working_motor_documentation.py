"""Generate root, family and exact-part documentation from canonical records."""
from collections import defaultdict
from pathlib import Path
import re

from motor_io import ROOT, records, write_json


def natural_key(**kwargs):
    value = kwargs["value"]
    return [int(token) if token.isdigit() else token for token in re.split(r"(\d+)", value)]


def page(**kwargs):
    path = Path(kwargs["path"])
    body = kwargs["body"]
    start = "<!-- OOMP MOTOR GENERATED START -->"
    end = "<!-- OOMP MOTOR GENERATED END -->"
    generated = start + "\n" + body.rstrip() + "\n" + end
    if path.exists():
        old = path.read_text(encoding="utf-8")
        if start in old or end in old:
            if old.count(start) != 1 or old.count(end) != 1 or old.index(start) > old.index(end):
                raise ValueError(f"Malformed generated markers in {path}")
            content = old[:old.index(start)] + generated + old[old.index(end) + len(end):]
        else:
            content = generated + "\n\n" + old
    else:
        content = generated + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(**kwargs):
    root = Path(kwargs.get("root", ROOT))
    # Navigation always covers every active record, even after a filtered build.
    parts = [part for _, part in records(root=root)]
    parts.sort(key=lambda part: natural_key(value=part["oomp_id"]))
    families = defaultdict(list)
    for part in parts:
        families[part["family"]].append(part)
        directory = root / part["directory"]
        dimensions = part["dimensions_mm"]
        rows = ["| Dimension | mm |", "| --- | ---: |"]
        for name, value in dimensions.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool) and name not in ("blade_count",):
                rows.append(f"| {name.replace('_', ' ')} | {value:g} |")
        taxonomy = ["| Slot | Value | Purpose |", "| --- | --- | --- |"]
        for index in range(1, 16):
            key = f"taxonomy_{index}"
            taxonomy.append(f"| {index} | {part[key] or '(empty)'} | {part['taxonomy_descriptions'][key]} |")
        links = []
        for label, filename in [
            ("OpenSCAD", "working.scad"),
            ("SVG drawing", "working_mechanical_drawing.svg"),
            ("Full STL (mm)", "three_d_model/model_full.stl"),
            ("Full GLB (metres)", "three_d_model/model_full.glb"),
            ("Blender studio", "three_d_model/studio.blend"),
            ("Portable model script", "three_d_model/model.py"),
            ("Saved recipe", "three_d_model/parameters.json"),
        ]:
            if (directory / filename).is_file():
                links.append(f"[{label}]({filename})")
        image = "![Nominal motor assembly render](three_d_model/render_product_high.png)\n\nGenerated layout model; not a product photograph.\n" if (directory / "three_d_model/render_product_high.png").exists() else ""
        source_lines = [f"- [Reference {index + 1}]({source['url']}): {source['supports']}" for index, source in enumerate(part["sources"])]
        text = f"# {part['name_proper']}\n\n## Summary\n\n{part['description']}\n\n{image}\n## Details\n\nID: `{part['oomp_id']}`\n\nStatus: **{part['dimension_status']}**. {part['dimension_note']}\n\n"
        voltage = part.get("voltage_v")
        text += f"Nominal voltage: {str(voltage) + ' V' if voltage else 'unspecified'}. Nominal reduction: {str(part['reduction_ratio']) + ':1' if part.get('reduction_ratio') else 'not specified'}.\n\n"
        if part.get("voltage_options_v"):
            text += "Listing advertises separate 12 V / 24 V options and 600 L/h. The supplied image also advertises 5 m head; this is not a simultaneous duty point with 600 L/h. Exact electrical variant remains unselected.\n\n"
        text += "\n".join(rows) + "\n\n" + "\n".join(taxonomy)
        text += "\n\nSources checked 2026-11-17:\n\n" + "\n".join(source_lines)
        text += "\n\n<details><summary>Complete saved record</summary>\n\n```yaml\n" + (directory / "working.yaml").read_text(encoding="utf-8") + "```\n\n</details>\n\n[Canonical YAML](working.yaml)\n\n## Parts\n\n" + " · ".join(links)
        text += "\n\nThese are alternate representations of one purchased component, not separate BOM items.\n\n## Assembly\n\n" + part["model_note"] + " No supplier-specific assembly or wiring procedure has been established.\n\n[Catalogue](../../README.md) · [Regeneration](../../README_GENERATOR.md)\n"
        page(path=directory / "README.md", body=text)
    table = ["| Family | Records | Browse |", "| --- | ---: | --- |"]
    for family, entries in families.items():
        table.append(f"| {family.replace('_', ' ')} | {len(entries)} | [Parts](navigation/{family}/README.md) |")
        lines = [f"# {family.replace('_', ' ').title()}", "", "[Catalogue](../../README.md)", "", "| Variant | Preview |", "| --- | --- |"]
        for part in entries:
            prefix = "../../" + part["directory"]
            preview = f"[![{part['name_proper']}]({prefix}/three_d_model/render_product_low.png)]({prefix}/README.md)" if (root / part["directory"] / "three_d_model/render_product_low.png").exists() else "Not rendered"
            lines.append(f"| [{part['name_proper']}]({prefix}/README.md) | {preview} |")
        page(path=root / "navigation" / family / "README.md", body="\n".join(lines))
    representative = next((part for part in parts if part["family"] == "stepper"), None)
    image = f"![NEMA 17 nominal layout render]({representative['directory']}/three_d_model/render_product_high.png)\n\nGenerated nominal layout model.\n" if representative and (root / representative["directory"] / "three_d_model/render_product_high.png").exists() else ""
    body = "# OOMP motors\n\n## Summary\n\nA persistent catalogue of stepper motors, DC gearmotors, submersible pumps and computer fans. The first release contains " + str(len(parts)) + " generic records, with editable geometry, drawings and studio renders.\n\n" + image
    body += "\n## Details\n\n[OOMP base directory](https://github.com/oomlout/oomlout_oomp_version_5) · [Build and editing guide](README_GENERATOR.md) · [Taxonomy](TAXONOMY.md)\n\nManufacturer and part-number slots 14 and 15 are empty placeholders. N20 ratios are five common available options, not a measured popularity ranking. Pump envelope dimensions follow the supplied reference image; unlabelled rear features remain approximate. Its listing advertises separate voltage options, not a confirmed dual-voltage device.\n\n## Parts\n\n" + "\n".join(table)
    body += "\n\n## Assembly\n\nChoose the closest nominal envelope, then verify the actual supplier, dimensions, voltage and interface before mechanical integration. No universal wiring or installation procedure is implied. Models identify purchased parts; they are not printable working motors.\n"
    page(path=root / "README.md", body=body)
    write_json(path=root / "catalogue.json", data={
        "schema_version": 1,
        "parts": [
            {
                "id": part["oomp_id"],
                "family": part["family"],
                "directory": part["directory"],
                "dimension_status": part["dimension_status"],
            }
            for part in parts
        ],
    })
    print(f"Documented {len(parts)} motor records", flush=True)


if __name__ == "__main__":
    main()
