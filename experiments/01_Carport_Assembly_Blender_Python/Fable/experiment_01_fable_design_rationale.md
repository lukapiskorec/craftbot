# Experiment 01 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-22; first pass v01–v02, reference-comparison pass v03–v04).
Kept because Claude Code transcripts redact the model's thinking; only
messages, tool calls and tool results survive in the `.jsonl`.

## 0. About this document

Follows the template of
`experiments/13_Hip_Roof_Sheathing_Blender_Python/Fable/experiment_13_fable_design_rationale.md`
(§0 there lists the sections). Sections 3 and 4 of that template ("reading the
reference code", "why the inherited frame had to change") do not apply here —
experiment 01 starts from scratch with only two reference images — so §3 covers
the reference *library* conventions instead and §4 the construction logic that
had to be settled before any geometry could be placed.

## 1. How to run / outputs

Every iteration `experiment_01_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, object colour per collection,
object outlines on so coplanar members stay distinguishable), producing
`*_blender_view_NN.png` and a `.blend`. Run from this folder:

```
blender -b --python render_fable.py -- experiment_01_fable_v04.py ../input <abs_out_prefix> [01,05,...]
```

`render_fable.py` also runs a separating-axis overlap test on every pair of
members (all members are scaled cubes, so OBB-vs-OBB is exact) and prints
interpenetrating pairs above 1 mm before rendering.

Views: 01 reference-image-1 angle, 02 reference-image-2 angle, 03 gable
elevation, 04 side elevation, 05 top, 06 frame without common rafters,
07 posts + bents only, 08/09 eave & post head close-up (with/without commons),
10 apex from below, 11 purlin/strut close-up, 12 truss elevation (commons
hidden). v01 views 03/04/10/12 were re-rendered after a camera-azimuth fix;
the v01 model itself is unchanged.

Collections: `Foundation` (slab), `Structure_Posts` (posts, longitudinal knee
braces), `Structure_Bents` (tie beams, tie braces, king posts, principal
rafters, struts, ridge braces), `Roof_Longitudinal` (plates, raising plates,
purlins, ridge), `Roof_Rafters` (common rafters). Final model: v04, 102
members, 0 overlaps.

## 2. Reading the inputs

The `input/` folder holds only the two reference renders (plus the library and
template); there is no manual for this experiment, so construction rules come
from the images and general post-and-beam practice.

What the images show (both agree):

- Open pavilion on a concrete slab, **4 bents / 3 bays**, two posts per bent.
- Each bent is a **king-post truss**: tie beam with ends projecting past the
  posts, king post to the ridge, two struts from low on the king post up to
  the principal rafters.
- A longitudinal **plate** on the post tops with a knee brace at every post;
  knee braces from post to tie beam in the bent plane too.
- **Purlins** at mid-slope and a **ridge beam**, with closely spaced **common
  rafters riding over** purlins and ridge, overhanging the eaves *and* the
  gables (the last rafter sits on the cantilevered purlins/ridge/plate).
- Pitch visually ≈ 40–45°; gable-end bent identical to the inner ones.

Numbers chosen (carport for two cars): bents at x = 0/3/6/9 m, posts at
y = ±3.0 m (6 m span), posts 200×200 × 2.6 m, pitch 40°, slab 11 × 8.4 × 0.15 m
(1 m beyond the posts along the building, under the 1.0 m eaves across).
Sections: plate 200×200, tie 200×250, principal 150×200, king post 150×150,
purlins/ridge 150×200, raising plate 200×200, commons 50×150 @ 600 mm, braces
100×150, struts 150×150. The reference's curved knee braces are straight here
(boxes).

### 2.1 Second pass – close reading of the reference (v03/v04)

After v02 the reference images were cropped and upscaled (eave, gable truss,
far gable). Differences found and what was done:

| Reference detail | v02 | Change |
|---|---|---|
| Commons bear on a longitudinal member carried by the **projecting tie-beam ends**, above the post-top plate | tilted eave purlin on the principal feet | v03: horizontal **raising plate** 200×200 on the tie ends, positioned so its outer top arris lies on the commons' plane (\|y\| = 3.384, tie ends at 3.45); clears the principal foot by 55 mm |
| Longitudinal braces from king posts to the ridge beam | none | v03: ridge braces, 45°, 0.6 m legs, both directions at inner bents, inward only at end bents |
| Struts as wide as the principal rafters | 100×150 | v03: 150×150 |
| Rafter tails project well past the tie-beam ends | 0.35 m past | v04: eave overhang 1.0 m from the post (0.55 m past the tie ends); slab widened to ±4.2 m |
| Principal foot sits on the tie-beam *end* (bird's-mouthed over it) | foot at the post centre-line | kept: with boxes, a foot at the tie end would raise the whole roof 0.38 m or require a 0.58 m raising plate; the foot is hidden behind the raising plate anyway |
| Curved knee braces | straight | kept (boxes) |

Already consistent before the pass: 4 bents / 3 bays, purlin ≈ 55 % up the
slope, 0.6 m rafter spacing, gable outrigger rafter on cantilevered
purlins/ridge/plates, post height ≈ 2.6 m, plate below the tie beam with the
knee braces on the plate.

### 2.2 Improvements as a timber structure (independent of the reference)

- **Ridge braces** give the roof a braced line at the apex; before v03 only the
  plate line was braced longitudinally, so the ridge/king-post tops relied on
  the commons for longitudinal stability.
- **Raising plate on the tie ends** puts the common-rafter thrust into the tie
  beam (the member designed to take it) instead of into a purlin sitting on
  the principal foot; every rafter foot is now over a member supported at each
  bent.
- **Struts land directly under the purlins** (from v02), so purlin load goes
  strut → king-post base → tie beam without bending the principal.
- Struts widened to the principal width so the strut-to-rafter bearing is the
  full rafter width.
- Considered and rejected: a collar tie (not in the reference, and the struts
  already restrain the principals at mid-span); purlin wind braces (the
  reference has none; the ridge braces plus plate braces already give two
  braced lines).

## 3. Reading the reference library

`craftbot_lib.place_element(name, loc, axis, angle, scale)` makes a 2×2×2 cube,
so `scale` is the *half*-size, and orientation is a single axis–angle. Two
helpers wrap it:

- `box(lo, hi)` – axis-aligned member from two corners (posts, plates, tie
  beams, king posts, ridge, raising plates, slab).
- `member(p0, p1, width, depth, width_dir, n0, n1, on_underside)` – oriented
  member along p0→p1. The full rotation (local Z = axis, local X = width
  direction) is built as a matrix and converted to axis–angle with
  `to_quaternion().to_axis_angle()`, so any roll is expressible through the
  library's single axis–angle parameter.

Objects are linked to the scene collection by the library; `link_to` moves
them into the named collection.

## 4. Construction logic settled before placing geometry

The difficult question was the **stacking order at the eave and at the
ridge**: the commons must bear on something at the eave, on the purlins at
mid-slope and on the ridge, and all three bearings must lie in one plane,
while the principals (deeper than the commons) must also bear on the bents.
Options considered:

1. *Commons and principals share one top plane, purlins trenched flush into
   the principals.* Real practice, but boxes cannot be notched, so the purlins
   would have to be interrupted at every bent and the commons would still hit
   the tie beam at the bents. Rejected.
2. *Commons on a plate at post-top level, purlins on the principals.* The
   purlin-top plane at the eave is ≈ 0.5 m above the plate; the plate would
   need to be 0.8 m tall or the commons would float. Rejected.
3. **Chosen: post → plate → tie beam → principal rafters → (purlins, ridge,
   and — from v03 — a raising plate on the tie ends) → commons.** The
   commons' underside plane is the principal's underside plane offset by
   *two* member depths (principal + purlin, 0.4 / cos 40° = 0.52 m
   vertically). In v01/v02 the eave bearing was a tilted eave purlin on the
   principal's foot; in v03 it became the raising plate, whose height (200 mm)
   happens to put its outer top arris on that plane 66 mm inside the tie end.
   The ridge height is derived so its top arrises lie in the commons' plane
   (ridge bottom = king-post top).

Bird's-mouths, tenons and notches cannot be expressed with uncut boxes, so two
rules replace them and keep the model free of interpenetration:

- **Arris bearing**: a sloped member's underside passes exactly through the
  top arris of its horizontal support (principal foot on the tie beam at the
  post centre-line; commons on the raising plate's outer arris and on the
  ridge's top corners). Geometrically a knife-edge; physically a
  bird's-mouth.
- **End-face inset**: a member whose square-cut end meets a face (strut → king
  post, strut → rafter underside, brace → post face / beam underside,
  principal and common heads → king post / ridge plane) is shortened along
  its axis by `(|e1·n|·w/2 + |e2·n|·d/2) / |axis·n|`, so no corner of the end
  face crosses the bearing plane and the end touches it on one edge. This is
  generic — no per-member hand tuning — and leaves the small wedge gaps that a
  carpenter would close with a housing.

## 5. Core modelling decisions

- **One parametric roof plane.** `principal_underside_z(y)` and
  `common_underside_z(y)` define everything sloped; purlin centres, ridge
  levels, raising-plate position, strut targets and king-post height are
  derived from them, so a pitch or section change regenerates a consistent
  frame.
- **Depth axis always points up.** `member()` flips (e1, e2) together when e2
  has negative z, so `on_underside=True` means the same thing on both slopes.
  Without it the left-hand members were offset a full depth the wrong way
  (v01 first render: 66 overlaps on the L side only).
- **Numeric overlap check instead of eyeballing.** 102 boxes → 5 151 pairs,
  15-axis SAT each, well under a second. It caught every one of my mistakes
  (below) before a single render was inspected.
- **Struts land under the purlins** (target point = principal underside at
  `PURLIN_Y`), so the truss delivers the purlin load directly to the king
  post, as in the reference.

## 6. Detailed geometry

Levels (z, metres): post top 2.60; plate 2.60–2.80; tie beam 2.80–3.05
(y ±3.45); principal underside at post centre 3.05, at king post face 5.50;
king post 3.05–5.83; ridge 5.83–6.03 (RIDGE_TOP = commons' underside at
y = ±0.075); purlins on the principal top surface at |y| = 1.4; raising plates
3.05–3.25 at |y| = 3.184–3.384 (v03+; v01/v02 had a tilted eave purlin at
|y| = 2.8 instead); commons from y = ±4.0 (1.0 m eave overhang; 0.6 in v01,
0.8 in v02/v03) to the ridge plane, 18 per slope at x = −0.6 … 9.6 (0.6 m
gable overhang); longitudinal members run x = −0.625 … 9.625 so their ends
are flush with the outermost rafter.

Raising plate position is derived, not typed:
`RP_Y_OUT = (z_c(0) − RP_TOP) / tan θ`, with two asserts (inside the tie end;
clear of the principal foot's top corner at |y| = 3.0 + 0.2·sin 40°).

Head cuts: a principal/common head is inset against the vertical king-post
face / ridge plane so the *top* corner touches it; the bottom corner sits
0.2·sin 40° = 0.13 m (principal) or 0.10 m (common) further out — the two
commons of a pair therefore meet on the ridge plane along their top edge only,
which is exactly the plumb-cut pair of a real ridge joint without the
bevelled ridge.

Knee braces: 45°, 0.8 m legs, from post face (z = 1.8) to plate underside
(longitudinal) or tie-beam underside (bent plane, inside the plate at
|y| < 2.9). End posts have no outward longitudinal brace. Ridge braces: 45°,
0.6 m legs, king-post face → ridge underside, same end-bent rule. Struts: from
the king-post face 0.15 m above the tie beam to the principal underside at
|y| = 1.4 → 42° (v01 had 24° with the purlin at 1.7 and the strut base at
0.35, visibly flatter than the reference).

## 7. Verification

- Numeric: SAT overlap test over all member pairs, tolerance 1 mm. Touching
  faces/edges report ≤ 0 and are therefore not flagged; v02, v03, v04: 0 pairs.
- Visual: 12 fixed views, including framing-only (06/07) and three close-ups.
  Outlines on, so the 50 mm commons directly above the 150 mm principals at
  the bents stay distinguishable. For the comparison pass the reference images
  were cropped and 2× upscaled (scratch files, not archived) to read the eave
  and truss details.
- Not verified: bearing *adequacy* (knife-edge bearings are accepted as
  stand-ins for bird's-mouths), member sizing, and connection design.

Mistakes the check caught (all mine, all in `member()` usage):

1. Bearing normals for the king-post face given along X instead of Y →
   division by zero (axis ⟂ normal).
2. Principals/commons placed with their *centre line* on the underside points
   → 116 overlaps of 75–77 mm (half a depth × cos 40°). Fixed with
   `on_underside`.
3. Depth axis pointing down on the left slope → 66 overlaps, left side only.
   Fixed by the e2-up rule.
4. v02 strut upper bearing normal written as (0, S, −C), which is not normal
   to the rafter underside at all → inset exploded, struts shrank to 0.44 m
   and slid into king post and tie beam. Correct normal (0, S, C).

## 8. Iterations

| v | change | result |
|---|--------|--------|
| 01 | full frame: slab, posts, plates, braces, king-post trusses, purlins, ridge, commons | after the three fixes above: 0 overlaps; frame matches the reference; struts too flat (24°); two close-up cameras aimed at the wrong face (fixed in the renderer, views re-rendered) |
| 02 | purlins to true mid-slope (\|y\| = 1.4), strut base lowered to 0.15 m → 42°, eave overhang 0.8 m, strut normal fixed, apex close-up from below | 0 overlaps, 96 members; end of first pass |
| 03 | reference comparison: raising plates on the tie ends replace the eave purlins, ridge braces, struts 150×150 | 0 overlaps, 102 members; eave build-up now reads like the reference (plate / tie ends / raising plate / rafters) |
| 04 | eave overhang 1.0 m, slab ±4.2 m | 0 overlaps; final |

## 9. Scope and known simplifications

No roofing, fascia, sheathing or gable infill (the reference shows the bare
frame). Straight instead of curved knee braces. No joinery: arris bearings
replace bird's-mouths, end-face insets replace housings/tenons, the ridge is
square (not bevelled) with the commons bearing on its arrises, the principals
stop at the post centre-line so the tie-beam ends project bare under the
raising plate, the purlins are continuous over the principals rather than
trenched, and the raising plate sits on the tie ends without a housing. No
foundations below the slab, no post bases. Member sizes are plausible for a
6 × 9 m carport but not calculated.
