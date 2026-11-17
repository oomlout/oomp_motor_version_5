# Motor taxonomy

IDs concatenate nonempty taxonomy slots 1–15 using the base OOMP convention;
decimal points become underscores. Empty placeholders do not add ID segments.

| Slot | Purpose | First catalogue |
| --- | --- | --- |
| 1 | Class | `motor` |
| 2 | Functional family | `stepper`, `dc_gearmotor`, `pump_submersible`, `fan_computer` |
| 3 | Frame / form factor / generic series | `nema_17`, `n20`, `tt`, `jt_500`, `square_axial` |
| 4 | Construction | TT plastic, bi-metal or all-metal gears |
| 5 | Body width / frame size | Fan width in mm |
| 6 | Secondary envelope | Reserved |
| 7 | Body depth excluding shafts/outlets | NEMA and fan depth in mm |
| 8 | Nominal voltage | 6 V gearmotors, 12 V fans; empty when unspecified |
| 9 | Nominal input-to-output reduction | 30, 50, 100, 150, 298:1 N20; 48 / 90:1 TT |
| 10 | Winding / step angle / electrical variant | Reserved |
| 11 | Speed / torque / flow grade | Reserved |
| 12 | Shaft / mounting / outlet configuration | Reserved |
| 13 | Encoder / connector / control / bearing | Reserved |
| 14 | Manufacturer | Empty placeholder |
| 15 | Manufacturer part number | Empty placeholder |

`family` is an internal geometry dispatch key and can be more specific than slot
2 (for example `dc_gearmotor_n20`). `jt_500` in slot 3 identifies the generic pump
series advertised in the supplied link; it does not establish a manufacturer or
verified manufacturer part number.

The NEMA entries differ only in body depth (40 / 48 mm) and derived identity and
geometry. Electrical values stay null. The five N20 ratios are common available
choices supported by the reference catalogue, not a statistical popularity
ranking; nominal reduction is not the exact tooth-count ratio. TT records use
6 V nominal with a referenced 3–6 V operating range. All-metal TT describes the
gears, not the housing. The pump has unselected advertised 12 V and 24 V options;
there is no claim that one pump accepts both, nor that 600 L/h is a verified duty
point. The six fan frames are 40×10, 60×25, 80×25, 92×25, 120×25 and 140×25 mm.

The pump's 105.9 mm overall envelope, 79 mm housing, 21.2 mm outlet,
5.7 mm rear projections, 33.43 × 38.33 mm end profile and Ø11.9 mm outlet are
transcribed from the preserved user-supplied dimension image. Rear openings are
drawn directly as requested, but their dimensions and mounting function are not
established by the image. They remain explicitly unmeasured in the drawing.

Use new populated records when future specifications distinguish variants. Keep
generic records available rather than silently turning them into branded parts.
