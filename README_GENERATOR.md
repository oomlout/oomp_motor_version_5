# Building and extending the motor catalogue

Run commands from this repository. Python 3.12 and Blender 4.5+ are supported.
Install Python packages with `python -m pip install -r requirements_motor.txt`.
Set `OOMP_BLENDER_EXE` if Blender is not on PATH or in the usual Windows install
location. CairoSVG needs a Cairo runtime on systems where one is not supplied.
OpenSCAD is optional for editing / independently compiling the generated SCAD;
the normal mesh build uses Manifold directly.

## Ordered pipeline

```powershell
python working.py
# Also export the conventional root 3dpr.stl:
python action_make_all.py
# YAML + SCAD + drawings + documentation, without invoking Blender or STL export:
python action_make_all_no_stl.py
```

1. `working_oomp_populate.py` declares every family / variant. It resolves
   `working_motor_dimensions.py`, `working_motor_recipe.py` and the presentation
   defaults into complete `parts_source/<id>/working.yaml` records.
2. `working_oomp.py` materializes `parts/<id>/working.yaml`, preserving extra
   metadata and applying optional per-part `working_manual.yaml` overrides.
3. `working_scad.py` dispatches to `working_motor_scad.py`, consuming saved CSG
   recipes to produce editable `working.scad` and optionally `3dpr.stl`.
4. `working_svg.py` dispatches to `working_motor_drawing.py`, generating A4 front
   and side SVG drawings plus PNG previews from that same component recipe.
5. `working_three_d_model.py` exports full and display STL/GLB models, portable
   model scripts, saved parameters, Cycles studio scenes and four PNG renders.
6. `working_motor_documentation.py` rebuilds the catalogue, family navigation,
   part pages and `catalogue.json`. Generated markers preserve handwritten notes.

These stages run synchronously. Failures stop the pipeline. Nothing sends work
to external AI services or launches desktop project actions. The inherited
SolidCraft scaffold remains optional; motor records explicitly disable it
because this catalogue uses the persisted CSG route.

## Edit and rebuild

Definitions deliberately use multiline dictionaries and `**kwargs`, with routine
options at the top. Add a variant in `declarations()`, including source notes and
dimension authority. Add new dimensions in `working_motor_dimensions.py` and new
component logic in `working_motor_recipe.py`. Every geometry node is resolved
during population; downstream stages do not reconsult hidden dimension tables.
Materials, lighting, colours, camera poses and render sizes are saved in YAML.

```powershell
python -c "import working; working.main(filter='motor_stepper*')"
python -c "import working; working.main(run_oomp_populate=False, run_oomp=False, filter='motor_fan_computer*')"
python -c "import working_three_d_model as m; m.main(filter='motor_pump*', force=True)"
python -c "import working_motor_documentation as d; d.main()"
python -m pytest tests -q
```

The second example rebuilds directly from saved canonical YAML. To preserve local
presentation edits through normal regeneration, put nested overrides in
`parts/<id>/working_manual.yaml`; generated source fields otherwise win. Change
geometry dimensions at population time: altering only `dimensions_mm` in manual
YAML does not automatically reconstruct its already-resolved CSG nodes. Identity
changes belong in population, never manual overrides. Filtered builds do not
remove other parts. Removed/renamed declarations are not automatically deleted;
archive old canonical/source folders deliberately when changing IDs.

Each `three_d_model` folder includes `model.py`, `motor_model_geometry.py`,
`parameters.json` and `requirements.txt`. Copy that folder elsewhere, install its
requirements and run `python model.py` to rebuild both mesh variants. Open
`studio.blend` to inspect the lighting or rerender. This does not require another
OOMP repository. A recipe/code fingerprint skips unchanged builds; outputs are
assembled in a staging directory and the manifest is written last.

STL units are millimetres, with Z along the output axis. GLB units are metres and
Y-up: `(x, y, z) -> (x, z, -y)/1000`. Components are individually closed solids;
assembly STL files may contain touching/overlapping components and are not
print-ready unions. Thread bores, gear discs, blades and moulded casing details
are simplified. Pump envelope dimensions are transcribed from the preserved user-supplied image; unlabelled body curves and rear openings remain approximate.

## Presentation reference

The portable render helpers were adapted from the local OOMP bearing / hardware
studio: satin steel, physically based microtexture, three softboxes, a neutral
floor, orthographic framing, AgX and grounded product poses. The palette adds
aluminium, brass and coloured plastics. Low renders are 512 px; high renders are
1024 px. Geometry resolution differs between the full and display variants.
