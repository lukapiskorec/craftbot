# Experiment 02 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-22, two sessions: v01–v02 model from the images, v03 after a
reference comparison and structural review). Kept because Claude Code transcripts redact the model's
thinking; only messages, tool calls and tool results survive in the `.jsonl`.

## 0. About this document

Same structure as `experiments/13_Hip_Roof_Sheathing_Blender_Python/Fable/
experiment_13_fable_design_rationale.md` (§0 there lists the sections). §3/§4
of that template ("reading the reference code" / "why the frame had to change")
do not apply here – this run started from scratch, the `ChatGPT 5.1/` scripts
were deliberately not opened – so they are merged into a short §3.

## 1. How to run / outputs

Every iteration `experiment_02_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, object colour per collection,
cavity shading, black object outlines so coplanar members stay
distinguishable), producing `*_blender_view_NN.png` and a `.blend`. Run from
this folder:

```
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render_fable.py -- experiment_02_fable_v03.py ../input <abs_out_prefix> [01,05,...]
```

The renderer also runs a numeric **overlap check** after rendering: every
member is an oriented box, so each pair is tested with the separating-axis
theorem and pairs penetrating more than 1 mm are printed (see §7).

Views: 01/02 orbit (NE / SW), 03 bent elevation (gable, roof layers hidden),
04 long elevation (roof layers hidden), 05 top, 06 frame only, 07 purlins +
commons (battens hidden), 08 truss close-up, 09 X-brace crossing, 10 eave
joint (post / hammer beam / plate / rafter foot), 11 ridge, 12 eave with all
roof layers.

Collections (assembly order): `Foundation` (slab, post plinths), `Posts` (posts, jowls), `Bents` (hammer
beams, hanging queen posts + finials, knee braces, collars, X braces, king
posts, principal rafters, ridge), `Plates_and_Braces` (eave plates,
longitudinal V braces), `Purlins` (purlins + cleats), `Common_Rafters`, `Battens`.
Final model: v03, 198 members.

## 2. Reading the inputs

Only the two images were available (no manual for this experiment). From
`carport_model_example_02_1.png` (bent section with two people for scale,
≈1.75 m ≈ 255 px → ≈145 px/m):

- posts ≈ 5.4 m outer-to-outer, post top ≈ 3.3 m, apex ≈ 6.8 m → **posts at
  y = ±2.6, POST_H = 3.3, pitch 50°** (measured 51° from the rafter line).
- the tie beam is **split**: two hammer beams, each running from the eave
  past its post to a **hanging queen post** (pendant with a finial below the
  beam), the middle free. Queen posts at ≈ ±165 px → **QUEEN_Y = 1.15**.
- **collar** between the queen posts at ≈ 4.9 m → `COLLAR_Z = 4.80` (underside).
- **St Andrew's cross** under the collar, feet just above the hammer beams
  on the queen posts, heads on the collar underside; braces at ≈28°.
- **king post** from the collar to the ridge; purlin squares at the eave, two
  on each slope and at the ridge → purlins at |y| = 0.9, 1.8, 2.8 plus ridge.
- long **knee braces** from ≈45 % post height to the hammer beam next to the
  pendant → foot z = 1.7, head |y| = 1.4.

From `carport_model_example_02_2.png` (axon): 4 bents / 3 bays, eave plates
on the posts with **V knee braces** along the eaves (long, reaching roughly
a third of the bay), purlins on the principals, common rafters up the slope,
battens across the commons, small gable overhang → bents at 2.4 m, gable
overhang 0.4 m, commons at 0.6 m, battens at 0.35 m along the slope.

Deliberate deviations: the reference posts are jowled (flared at the top) and
the pendants are turned – both reduced to boxes. The reference purlins are
trenched into the principals' backs; boxes cannot be notched, so purlins are
laid **on** the backs, rotated to the slope (§5.2).

## 3. Reference code and conventions

`craftbot_lib.place_element()` was used unchanged (cube scaled/rotated/
translated). The `box()` / `member()` helpers and the "inset at a bearing
plane so the square-cut end touches on one edge instead of penetrating"
rule were carried over from the experiment 01 Fable run
(`experiment_01_fable_v02.py`), which uses the same axes convention
(X along the building, Y across the span, Z up, slab top z = 0).

## 4. Load path as modelled

slab → posts (to 3.3) → hammer beams on the post tops (3.30–3.55), tenoned
into the hanging queen posts at their inner ends → eave plates along the
building on the hammer beams (3.55–3.75) → principal rafters bear on the
plate's outer top edge, foot overhanging to |y| = 3.05 → queen posts rise to
the rafter underside, collar between them, cross under the collar, king post
collar → ridge piece (7.19–7.39) → purlins on the principals' backs → commons
on the purlins, meeting on the ridge piece's top arrises → battens.

## 5. Core modelling decisions

### 5.1 Everything is a `place_element` box
All 158 members are boxes, as the prompt requires. Consequence: no notches,
mitres or birdsmouths. Every joint is therefore designed so that the square-
cut member *touches* its bearing plane on one edge (the `member()` inset
rule) instead of being cut to it. Rejected alternative: building polygon
meshes for mitred ends (used in experiment 13) – it would abandon the
library function the experiment is about.

### 5.2 Purlins rotated to the slope, laid on the principals' backs
A square purlin set level under a 50° rafter would penetrate it (outer top
corner 0.24 m above the rafter underside for a 0.2 m purlin). Options:
level purlins with the rafter birdsmouthed (impossible with boxes), level
purlins touching the rafter on one edge (leaves wedge gaps and breaks the
common-rafter bearing), or purlins rotated parallel to the slope lying on the
principals' backs. The last gives a clean, continuous bearing plane for the
common rafters (`common_underside_z = principal_top_z + PURLIN_depth / cos`),
so that was chosen for all purlins including the eave one (|y| = 2.8).

### 5.3 Eave: plate on the hammer beams, rafter on the plate's outer edge
The rafter underside is defined as the plane through the eave plate's outer
top edge (|y| = 2.70, z = 3.75). The hammer beam tail is then cut at
|y| = 2.85, just inside the point where the rafter underside would cross the
beam top (2.87, asserted in the script), and the rafter tail overhangs to
|y| = 3.05 below the beam-top level – the same "rafter foot past the beam
end" look as the reference section. Rejected: rafter foot on the beam's
outer corner (then the plate under it would have to be 0.45 m tall to touch).

### 5.4 Halving joint at the X-brace crossing
Two braces in the same bent plane must cross. Rejected: offsetting them in X
(not what the reference shows, and makes them two independent braces).
Chosen: a halving joint modelled as three boxes per brace – full section
below and above the crossing, a half-width (60 mm) middle segment kept on
its own side of the bent plane. Lap length along the axis
`L = d (1 + cos φ) / sin φ + 0.04` where d = 0.15 (in-plane depth) and
φ = 52° is the angle between the braces → 0.35 m; the lap is centred where
the two centrelines cross (y = 0 by symmetry).

### 5.5 Ridge piece on the king post, rafters stopped at its faces
Principal rafters are inset at the planes |y| = 0.1 (ridge faces) so they
end beside the king post / ridge piece rather than mitring into each other.
The ridge piece top is set where the commons' underside plane crosses
|y| = 0.1 (`RIDGE_TOP = common_underside_z(0.1)`), so the commons bear on its
top arrises; its underside (7.19) clears the rafters' top corners (7.16).
King post runs collar top (5.05) → ridge underside.

### 5.6 Hanging queen post as one member
The queen post is a single box from the pendant (0.35 m below the beam) to
the rafter underside at its outer face (5.48); the hammer beam butts into it
(tenon), the collar butts into its inner face, the X-brace foot bears on the
inner face. A finial box (0.12 m) sits under the pendant.

### 5.7 Reference comparison after v02 (→ v03)
Measured against the section image (145 px/m): collar centre 4.93 vs
reference ≈ 5.02 m, queen posts ±1.15 vs ±1.14, X-brace head |y| 0.90 vs
≈ 0.88, foot 0.30 vs ≈ 0.28 above the beam, knee-brace geometry and the
queen post continuing ≈ 0.4 m above the collar to the rafter – all within
~0.1 m, left unchanged. Differences acted on: (a) the reference posts are
**jowled** (flare on the inner face under the beam) → a 0.08 × 0.50 m jowl
box, a step instead of the taper; (b) the reference's eave purlin sits
**over the post line**, mine was at |y| = 2.8 near the rafter tail → moved to
2.6 so the commons' reaction goes straight down into plate/post. Differences
not reproducible with boxes: trenched purlins, turned pendants, pegs.

### 5.8 Structural review independent of the reference (→ v03)
- Purlins laid loose on a 50° slope would slide → **cleats** on the
  downslope side of every purlin at every principal (box on the principal's
  back, up-slope face touching the purlin). Alternative rejected: trenching
  (impossible with boxes) or steel straps (not modelled).
- Posts directly on the slab wick moisture → **plinths** 0.36 sq × 0.10
  (stand-in for concrete upstands / steel post shoes); all other levels kept
  absolute so nothing else moved.
- Rafter foot bears on the plate's outer arris only (line contact): the real
  fix is a birdsmouth; cannot be modelled with boxes, kept as is (§9).
- Knee braces at ≈ 56° and V braces at ≈ 54° are close to the 45–60° range
  normally used; not changed. No roof-plane wind bracing was added – the
  reference shows none and the purlin/common/batten grid with cleats gives
  some diaphragm action; noted as a possible addition.

## 6. Detailed geometry (key numbers)

| item | value |
|------|-------|
| bents | x = 0, 2.4, 4.8, 7.2 m; gable overhang 0.4 |
| posts | 0.24 × 0.24, y = ±2.6, h 3.30 |
| hammer beams | 0.20 × 0.25, from |y| = 2.85 to the queen post (1.25), z 3.30–3.55 |
| queen posts | 0.20 sq, |y| = 1.15, z 2.95–5.48; finial 0.12 sq × 0.10 |
| knee braces | 0.12 × 0.15, post face z 1.70 → beam underside |y| = 1.40 (≈56°) |
| eave plates | 0.20 × 0.20, z 3.55–3.75, full bent length |
| V braces | 0.12 × 0.15, post face z 2.20 → plate underside 1.0 m from the post |
| collar | 0.20 × 0.25, z 4.80–5.05, between queen-post inner faces (|y| ≤ 1.05) |
| X braces | 0.12 × 0.15, foot (|y| 1.05, z 3.85) → head (|y| 0.90, z 4.80), lap 0.35 |
| king post | 0.20 sq, z 5.05–7.19 |
| principals | 0.15 × 0.20, underside through (2.70, 3.75), 50°, tail |y| = 3.05 |
| ridge | 0.20 sq, z 7.19–7.39, x −0.4…7.6 |
| purlins | 0.15 × 0.15 rotated, |y| = 0.9, 1.8, 2.6 (over the post line) |
| cleats | 0.10 along slope × 0.08 deep × 0.15 (principal width), downslope of every purlin on every principal (24) |
| plinths | 0.36 sq × 0.10, posts start at z = 0.10 |
| jowls | 0.08 projection × 0.50 high on the post's inner face under the hammer beam |
| commons | 0.06 × 0.12, 14 pairs at x = −0.3 + 0.6 k, tail |y| = 3.10 |
| battens | 0.05 × 0.04, 0.35 m along the slope, 11 per side |

Derived levels: `principal_underside_z(y) = 3.75 + (2.70 − |y|)·tan 50°`;
ridge underside of the principals 6.97, top 7.28; commons' underside at the
ridge 7.51.

## 7. Verification

- **Numeric:** SAT box–box overlap check over all 12 403 member pairs after
  each render (`render_fable.py`; 19 503 pairs for v03). v01 first run: 16 penetrating pairs, all in
  the X-brace laps (60 mm = both lap segments on the same side, plus 7.6 mm
  lap-too-short) → fixed (§5.4) → 0 pairs in v01 (re-run) and v02. Tolerance
  1 mm; edge-touching joints register as 0. v03: 0 pairs.
- **Script asserts:** rafter clears the hammer-beam tail, principals clear the
  ridge piece, collar clears the rafters.
- **Visual:** 12 views per version, including close-ups of the crossing,
  eave joint and ridge with roof layers hidden.
- **Not verified:** structural adequacy (sections are visual estimates from
  the images), any joinery beyond "members do not penetrate each other".
  False positive to be aware of: wedge-shaped gaps at square-cut brace ends
  look like floating members in elevation but are contact-on-one-edge joints.

## 8. Iterations

| v | change | renders / checks showed |
|---|--------|-------------------------|
| 01 | full model from the image analysis | halving joint wrong (laps coincident, off-centre: 16 overlaps); everything else clean. Fixed in place → 0 overlaps. |
| 02 | V braces longer (foot 2.2, reach 1.0), knee brace head at |y| = 1.4 | matches the reference proportions; 0 overlaps. |
| 03 | jowls, plinths, purlin cleats (24), eave purlin moved to |y| = 2.6 (§5.7–5.8) | cleats tight below each purlin, plinths/jowls clear of braces; 198 members, 0 overlaps; final. |

## 9. Scope and known simplifications

- Jowls are stepped boxes, not tapers; no chamfers, turned pendants, pegs or any joinery cuts – boxes only.
- Square-cut member ends at inclined bearings (visible wedge gaps at the knee
  braces, rafter ends at the ridge, X-brace ends).
- Purlins laid on the principals (held by cleats) instead of trenched in; commons therefore
  sit one purlin depth above the principals (roof build-up 0.20 + 0.15 +
  0.12 + 0.04 m).
- No roof covering, no gable framing; footings reduced to plinth blocks on the slab; rafter feet have no birdsmouth (line bearing on the plate arris).
- Sections and spacings are estimates from the two images, not from a
  manual; the reference's actual dimensions are unknown.
