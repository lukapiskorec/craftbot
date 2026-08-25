# Experiment 04 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-22/23). Claude Code transcripts redact the model's thinking,
so decisions, rejected alternatives and key numbers are recorded here.

## 0. About this document

Same section layout as `experiments/13_.../Fable/experiment_13_fable_design_rationale.md`
(§1 how to run, §2 inputs, §3 reference code, §4 why things had to change,
§5 core decisions, §6 detailed geometry, §7 verification, §8 iterations,
§9 scope). Two sections were added for the second phase of the run:
§2b (comparison with the manual's finished house) and §5b (structural
improvements made independently of the reference).

The run had two phases. Phase 1 (v01–v02) built a plain box house from the
manual's member sizes and the brief (stilts, one door, four windows, Fink
roof, ply both sides). Phase 2 (v03–v04) compared that with the manual's
photos and drawings and re-planned the house to the manual's layout.

## 1. How to run / outputs

Every iteration `experiment_04_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, object colour per collection,
cavity shading, black object outlines so coplanar members stay
distinguishable), producing `*_blender_view_NN.png`, a `.blend`, and an
overlap report. Run from this folder:

```
blender -b --python render_fable.py -- experiment_04_fable_v04.py ../input <abs_out_prefix> [01,05,...]
```

Views: 01/02 front (SW) and back (NE) corners, 03 south elevation (door /
verandah wall), 04 east gable elevation, 05 roof plan, 06/07 frame only,
08 truss end-on (frame only), 09 roof framing plan, 10 platform only, 11
from below, 12 door and stair close-up, 13 heel/eave detail, 14 apex
detail, 15 walls with interior ply (roof off), 16 gable/eave corner with
skin on (v02+), 17 joist layout with boards hidden (v02+), 18 ceiling over
partition P1 (v03+), 19 verandah from the front with the roof off (v03+).
Azimuth 0 = camera on +X (east gable), 270 = camera on −Y (south wall).

Collections: `Structure/{Foundation, Floor_Framing, Wall_Framing,
Partition_Framing, Roof_Framing}`, `Floors/Floor_Boards`,
`Facade/{Exterior_Sheathing, Interior_Sheathing, Beading, Openings, Verandah}`,
`Roof/{Gable_Sheathing, Roof_Covering}`, `Ceiling`, `Stairs`.
Final model: v04, 1013 members, 0 penetrating pairs > 1 mm.

## 2. Reading the inputs (phase 1)

Main source: `input/construction_manual_extracted.md` (FRIM Technical
Information Handbook No. 5, 1996). Numbers taken directly:

- 610 mm planning grid, M = 1220; studs and joists @ 610, trusses @ 1220,
  all vertically aligned (fig. 8 load path).
- Platform: 12 footings 600 × 600, tops 50 above ground; posts
  120 × 120 × 499; paired bearers 60 × 194 bolted both sides of the posts;
  joists 47 × 145 @ 610; stiffeners 50 × 50 at the ends and 50 × 75 at
  mid-span "seated in notches" (modelled flush with the joist top); header
  joists 20 × 194 flush with the floor; T&G strip flooring 22 × 145.
  Resulting floor level 0.910 m ≥ the 700 mm ventilation minimum.
- Walls: base plate 47 × 112 on the floor boards; panel 2745 high with
  47 × 97 studs (Table 1 "thicker panel"), 9 mm WBP ply outside, 6 mm MR
  inside → 112 mm wall; head binder 47 × 112 on top. Lintels 97 × 145 on
  cripple (jack) studs; window 1587 high with sill at 900 above floor
  (Drg 101/94/6); main door 840 × 2100 with 8 mm floor clearance, bottom
  rail *and* base plate cut out after erection (fig. 32). Noggings at the
  sheathing edge: sheets stood upright, 2440 high, so the joint and the
  nogging row sit at 2440 above the bottom plate with a 305 strip above.
- Roof: all truss members 35 × 72, rise 1195 (manual span 5770 → 23.5°),
  plywood gussets 9 mm both faces, trusses skew-nailed to the wall plate,
  gable ends closed with 6 mm ply on the end truss, purlins 35 × 72 on top
  of the trusses, fascia 20 × 145, fibre-cement sheets, diagonal braces
  22 × 97 "from the top of the gable-end truss to the bottom of the fourth
  truss" in a diamond, horizontal braces, ceiling noggings 38 × 50 @ 610 and
  6 mm ceiling ply.
- Stairs: rise 170 / run 230 in the manual; the 910 floor height gives
  5 × 182 rises with the same 230 run. Stringers 60 × 219, treads 47 × 250 on
  ledgers 50 × 50 × 180, concrete landing.
- `references/fink_truss_01.jpg` and the marked screenshot define the Fink
  (W) web layout: bottom-chord panel points at the third points, top-chord
  points at mid-rafter, outer webs third point → mid-rafter, inner webs third
  point → apex; rafter tails with plumb cuts; purlins on the top chords;
  "BC runner" and "web runner" bracing along the building.

Phase-1 deviations: footprint 7320 × 5490 taken as the *wall* outer faces
(the manual's 7320 × 5490 is the wall line on a 7544 × 5714 platform — see
§2b); rafter overhang 520 (the manual's 520 is the kitchen-side tail; the
main eave is 860); post bays 2240/2445 chosen to clear the header joists.

## 2b. Comparison with the manual's finished house (phase 2)

The PDF was re-read page by page (cover photo of the prototype, fig. 11
perspective, appendix sheets: plan/elevations/sections, panel layout plan,
panel elevations, door/window details, platform details, connection
details, truss and roof framing). Differences between v02 and the
reference, and what was done about each:

| Aspect | Manual | v02 | v03/v04 |
|---|---|---|---|
| Platform | 7544 × 5714 joist layout; walls inset 112 on a ledge; posts on 3 × 2440 / 2 × 2700 centres *under the wall lines* (section A-A / B-B) | 7320 × 5490 platform = wall faces; posts 300 in | adopted: `PL, PW = 7.544, 5.714`, walls at `X0 = Y0 = 0.112`, posts at X0 + 2440 k, y = 157 / 2857 / 5557 |
| Plan | BR1, BR2, Living/Dining, recessed verandah (3660 × 1332) at the front-right corner with exposed columns, railings and the entrance stair; main 840 door from the verandah into L/D; kitchen wing on a ground slab behind | empty box, door in the front wall | verandah, partitions P1 (BR / L-D line, continuing the verandah side wall) and P2 (BR1 / BR2), door from the verandah, two 770 interior doors; **kitchen wing not adopted** (ground-slab concrete/cemboard construction contradicts the brief's "raised on stilts") |
| Verandah structure | "void" panels 3, 4, 7: columns with a 1830 × 305 ply strip at the top, exposed col. / double col. at the corners; base plate 2576 on the front with an 1108 gap for the stair; railing 47 × 97 at 1000, balusters 20 × 20 | – | columns 94 × 97 on the truss lines (x = 4.992, 6.212) and a 94 × 112 corner column; top rail 47 × 97 with 305 strips both faces (9 mm out / 6 mm in); base plate with the stair gap; rails and balusters @ 100 |
| Windows | 1220 opening on the stud grid, frame ex 47 × 112 full depth, central stile, 8 adjustable "Naco" louvre leaves (1143) + fixed glass louvres (376) above, sill ex 47 × 145 | one glass pane | frame ring 47 × 112, mullion, transom, 8 leaves @ 20° + 3 fixed blades @ 45° per half (glass prisms) |
| Facade finish | plywood beading 9 × 72 over every sheet joint and over the base plate / binder joints (clearly visible as battens in the cover photo); skirting 9 × 100 inside | none | `beads()` vertical at every 1220 joint, horizontal at z = 0.957 / 3.397 / 3.702, split around openings; `skirting()` inside, cut at doors and inside corners |
| Truss bearing | chord ends 28 past the bearing point; eave ≈ 860 from the wall; purlins ≈ 730 | chord ends at the wall face; eave 520; purlins 670 | chord ends at wall face + 28 (`CH0/CH1`), tails 860 from the wall face, purlins @ 730 |
| Trusses | 4 × 1220 + 1323 ends (7526 overall), i.e. end trusses at the platform ends | 7 trusses on the 1220 stud grid over the gable walls | kept on the stud grid over the gable walls (end trusses over nothing would need cantilevered binders and a soffit detail the manual does not draw) |
| Gable | 6 mm ply with a row of ventilation holes | plain ply | holes not modelled (cannot cut a convex prism; see §9) |
| Openings count | 7 + 1 windows, 3 doors | 4 windows, 1 door | brief kept: 4 windows (BR1 front, BR2 west, L/D east, L/D verandah), 1 exterior door; back wall blind where the kitchen would attach |

Dimensions read from the panel layout plan that fixed the new plan:
bottom edge 722 + 610 + 1220 + 610 + 722 | 1108 | 1220 | 1332 = 7544 → the
verandah starts at x = 3884 and the stair bay is the 1108 gap between the
verandah side wall and the first column; right edge 1332 → verandah depth;
base-plate plan (fig. 22): 3884 | gap | 2576 on the front, partitions at
3000 (BR1/BR2) and on the 3884 line.

## 3. Reading the reference code

`input/craftbot_lib.py` provides `place_element` (a 2 × 2 × 2 cube placed by
loc/rotation/scale; it deletes a same-named object first). The
`element_placement_template.py` pattern (import + reload) is kept.
From the experiment 03 Fable run I reused `get_collection` (nested paths),
`box()` from corner coordinates, `positions()`, `tile_sheets()` and the
`stud_wall`/`clad` idea, but rewrote the last two: `positions` got a `grid0`
argument so that studs fall on the 610 grid measured from the wall's outer
face, `stud_wall` builds the manual's single top plate + separate head
binder, splits the bottom plate at doors and uses the 145 lintel, and
`clad` lays 1220 × 2440 sheets upright with a 305 top strip and cuts around
holes per column only. Phase 2 wrapped these in `ext_wall()` / `partition()`
(framing + both plies + beads + skirting + door/window units from one call,
with explicit framing / exterior-ply / interior-ply / bead / skirting extents
so inside and outside corners are resolved by the caller, not by magic).

The renderer is the experiment 13 style (outlines, cavity, per-view
bounding-box camera fit) with the experiment 02/03 overlap check
generalised from boxes to arbitrary convex meshes (§7).

## 4. Why sloped members could not be scaled cubes

`place_element` makes boxes; a rotated box cannot have a plumb or mitred end.
With rotated boxes every truss joint (rafter–chord heel, rafter–rafter apex,
web–chord nodes), the ridge of the roof sheets, the louvre blades in their
frames and the stringer ends would either interpenetrate or leave wedge
gaps. So every sloped member is a convex prism built with `bpy.data.meshes`
from a 2D profile: `prism_x` (profile in Y–Z, extruded along X) for trusses,
gussets, purlins, sheets, ridge cap, barge boards, gable ply, stringers and
louvres in the long walls, `prism_y` for louvres in the gable walls, and the
general `prism(origin, u, v)` for the diagonal roof braces that lie in the
roof plane. Axis-aligned members stay `place_element` boxes.

## 5. Core modelling decisions

### 5.1 Truss members as clipped strips

Each web is a 72 mm wide strip around its node-to-node centreline, extended
0.4 m past both nodes and then cut by half-planes (`clip`): above the bottom
chord top, below both rafter undersides, and — where two webs share a node —
by the vertical line through the node (outer web keeps the heel side, inner
web the apex side; the two inner webs are split at the ridge line). This
gives exactly the cuts a carpenter makes and guarantees no web overlaps a
chord or its neighbour. Rejected: overlapping boxes at the nodes (fails the
overlap check) and shortening webs to miss the nodes (gaps, no bearing).

Rafters are parallelograms from the plumb tail cut to the plumb ridge cut at
mid-span; the underside passes through the chord's top outer corner (the
heel), so rafter and chord touch along that line and the tail drops past the
wall. From v04 the heel is 28 mm outside the wall face (manual truss detail),
so the chord bears on the full 112 binder; in v03 the chord ran to the
platform edge and the rafter met it 112 mm outside the binder — a detail the
frame-only view 13 showed to be wrong.

Gussets are rectangles clipped to the truss outline (above chord bottom,
below both rafter tops) so nothing protrudes above the rafters where the
purlins run. Mid-rafter gussets are rafter-aligned (450 along the rafter,
72 + 110 deep) from v02. Gable trusses get gussets on the inner face only;
the outer face carries the 6 mm gable ply.

### 5.2 Roof-plane coordinates

All roof covering geometry is expressed in (v, t): distance up the slope from
the heel and height normal to the roof. A plumb line at a given y maps to
`v = (y − CH0 + t·sinθ)/cosθ`, so sheet, ridge-cap and barge-board profiles
get true plumb cuts at the ridge and eave at both their bottom and top
surfaces; the two slopes then share the ridge plane without overlapping.
Purlins are 72 × 35 flat on the rafters at six slope positions (first 80 mm
from the tail, 730 spacing); sheets are 8 columns over the 7.92 m roof width
(300 mm purlin cantilever at each gable), one 2440 sheet plus a cut sheet per
slope, overhanging the fascia by 50 mm.

### 5.3 Bracing that clears the nodes

The diagonal braces run under the rafters (t = −22…0) from the gable-truss
apex (inner gusset face) to the heel of truss 4. Their y position at trusses 2
and 3 clears the mid-rafter gussets and heel gussets; they stop 150 mm short
of the apex and heel so they do not run into the opposite rafter or the
chord, and the two braces on one slope butt against the truss-4 gusset faces
instead of overlapping each other. Bottom-chord runners sit 250 mm off the
chord nodes so they miss the web bases; web runners sit on the heel-side edge
of the outer webs at mid-length.

### 5.4 Corner and layer logic for the walls

Wall zone = 9 ply + 97 stud + 6 ply = 112 = base plate / binder width.
"Through" walls (front wall up to the verandah side wall, verandah back wall,
back wall) own their corner blocks; "butting" walls (west, east, verandah
side wall) sit between them. Each `ext_wall()` call states the framing
extent (inside both plies), the exterior-ply extent (through the corner),
the interior-ply extent (between the neighbours' interior faces), the bead
extent (stopped where the neighbour's bead column or a verandah member sits)
and the skirting extent / cuts (stopped 9 mm short of inside corners, cut at
partitions). Openings: king studs coincide with grid studs, jacks inside
them, so the 1220 module is preserved across windows (`window_at(c)`); the
door's right king is the grid stud at 4.992 (`door_right_of_stud`).

Partitions are 47 × 72 studs + 6 mm ply both sides = 84, centred in the
112 line of the verandah side wall (P1) or on the 3000 line (P2), base plate
47 × 84, head binder 22 × 84 → top at 3.724, 25 mm below the chords and
19 mm below the ceiling ply (manual fig. 9: non-load-bearing walls shorter
than the load-bearing ones).

### 5b. Structural improvements independent of the reference

- **Joist under the partition line** (x = 3.940): P1 runs parallel to the
  joists between the 3.772 and 4.382 grid joists; a joist was added under
  it so the partition and its doors do not load the floor boards alone.
- **Posts under the wall lines** (manual section A-A) instead of 300 in
  from the edge: the exterior walls now bear over bearers, the 112 ledge is
  the only cantilever.
- **Verandah columns on the truss lines** (x = 4.992, 6.212 = trusses 4 and
  5): the head binder over the open front is loaded only at the columns and
  spans 1220 between them; the 305 ply strips on both faces of the top rail
  make the "void panel" a 352 mm deep boxed edge beam, which is what the
  manual's void panels are.
- **Truss heel over the binder** (v04): the chord bears over the whole
  112 mm binder width with the 28 mm projection, not on a 112 cantilever.
- **Partition clearance**: 25 mm under the chords so roof deflection does
  not load the partitions.
- Kept from phase 1: all trusses over king or grid studs, three stiffener
  rows in the joists, noggings at every sheet edge, diagonal roof bracing
  diamond + runners, ply both sides of every wall (racking).

## 6. Detailed geometry

- Coordinates (v03+): platform 0…7.544 × 0…5.714; wall outer faces
  X0 = Y0 = 0.112, X1 = 7.432, Y1 = 5.602; verandah corner XV = 3.884,
  YV = 1.444; P2 at y = 3.000; chord ends CH0/CH1 = Y0 − 0.028 / Y1 + 0.028.
- Truss x: gable trusses at X0 + 0.006 and X1 − 0.041 (behind the 6 mm
  gable ply, flush with the wall ply face), intermediate at X0 + 1.22 k −
  17.5 mm, i.e. over the studs at 1.332 / 2.552 / 3.772 (grid) and the
  verandah columns at 4.992 / 6.212.
- Openings: windows `window_at(c)` = (c + 70.5, + 1079) between the grid
  studs at c and c + 1220: BR1 front c = 1.332, BR2 west c = 3.772, L/D
  east c = 3.162, L/D verandah c = 5.602. Main door 3.988…4.922 (right king =
  stud 4.992), i.e. centred on the 1108 stair bay 3.996…4.922 so stair,
  verandah and door line up. Interior doors 770 + 2 × 47 at y = 1.844…2.708
  (BR1) and 3.600…4.464 (BR2) in P1.
- Louvres: adjustable zone z = sill + 47 … head − 47 − 376 (≈ 1117 → 8 leaves
  @ 139.6, blade 140 at 20° → 131.6 vertical, 8 mm overlap-free); fixed zone
  376 → 3 blades of 110 at 45°. All blades centred in the 112 frame depth.
- Beads: horizontal at z = 0.957 (covers base plate / ply joint), 3.397
  (sheet joint), 3.702 (binder joint); vertical between them at every
  1220 from the exterior-ply start; all split around openings so a bead
  never crosses a frame. 9 × 72 on the face.
- Stair: bay 3.996…4.922, stair 800 between stringers (the 934 door-width
  stair of v02 did not fit the 926 bay), 5 × 182 / 230, landing 1300 × 600.
- Fascia top = roof-sheet underside over the fascia's *outer* face (v01 used
  the rafter face → 8 mm clash).

## 7. Verification

- Visual: 19 fixed views (15 in v01), including frame-only, end-on truss,
  roof framing plan, from-below, platform, verandah and four close-ups.
  Object outlines make coplanar ply sheets, beads and chord/gusset faces
  readable. Renders were compared with the cover photo, fig. 11 and the
  appendix elevations (verandah recess, railing, battens, louvres, eaves).
- Numeric: `render_fable.py` runs a separating-axis overlap test on every
  pair of members using each mesh's world-space face normals and edge cross
  products (AABB broad phase, 1 mm tolerance). It works for boxes and prisms
  alike; touching faces report 0. v01: 16 pairs (sheet × fascia 8 mm);
  v02 first run: 24 (T2 gusset normal flipped → 38 mm into a purlin), then 0;
  v03 first run: 16 (corner column in the strip plane 9 mm, verandah-back
  beads into the side wall 9 mm, N/S skirting into the gable base plates
  6 mm), then 0; v04: 0.
- Not verified: bearing of every member (e.g. the first joist cantilevers
  past the bearer ends), nail patterns, the 1–3 mm expansion gaps between
  sheets (sheets are modelled edge to edge), louvre blade clearances to the
  frame depth other than by the overlap test.

## 8. Iterations

| v | change | result |
|---|--------|--------|
| 01 | full box house: platform, walls, openings, Fink trusses with clipped webs and gussets, bracing, purlins, sheets, gable ply, ceiling, stair | reads correctly; 16 overlaps = roof sheets 8 mm into the fascia; mid-rafter gussets awkward rectangles |
| 02 | fascia top at its outer face; rafter-aligned mid-rafter gussets; views 16/17 | 24 overlaps from a flipped gusset normal, fixed → 0; 677 members; end of phase 1 |
| 03 | re-planned to the manual: 7544 × 5714 platform with inset walls and posts under the wall lines; verandah with columns, void-panel strips, railings, stair bay; partitions P1/P2 with interior doors; louvre windows; beading and skirting; eaves 860, purlins @ 730; joist under P1; `ext_wall()` / `partition()` with explicit extents | 16 corner overlaps (9 mm beads/strip, 6 mm skirting), fixed by extents/cuts → 0; 1013 members; heel detail wrong (chord to the platform edge) |
| 04 | chord ends 28 past the wall face; heel, eaves, gable, braces and roof covering measured from the heel point | 0 overlaps, 1013 members, final |

## 9. Scope and known simplifications

Not modelled: kitchen / bath / WC wing on the ground slab (concrete curbs,
cemboard panels, extended rafters, water tank) — deliberately, because the
brief asks for a house raised on stilts; gable ventilation holes (a convex
prism cannot carry holes; they would need a boolean or a polygon-with-holes
mesh); plywood beading on the gable ply and the verandah strips; nail plates,
bolts, U-straps, bearer splices; joist notches (stiffeners sit flush instead
of in notches); security bars on the louvres; corrugation and laps of the
roof sheets (flat 6 mm sheets butted); services. The manual's 21 numbered
panels are not represented: framing is continuous per wall, which differs
only where panel joints would double up studs (and where the manual's stud
spacings are off-grid, e.g. 713 / 1108 / 1332 bays next to the verandah).
