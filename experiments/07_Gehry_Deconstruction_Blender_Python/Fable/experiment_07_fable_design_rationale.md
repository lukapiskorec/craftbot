# Experiment 07 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-23). Claude Code transcripts redact the model's thinking, so
the reasoning is written out here; the archived `.jsonl` holds the messages,
tool calls and tool results only.

## 0. About this document

Same section structure as `experiment_13_fable_design_rationale.md` (§1 how
to run, §2 inputs, §3 reference code, §4 why the model had to change, §5 core
decisions, §6 geometry, §7 verification, §8 iterations, §9 scope). §2 here is
"reading the photographs" rather than a manual, and §4 is "what deconstruction
meant for the box" rather than a bug list.

## 1. How to run / outputs

Every iteration `experiment_07_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, object colour per collection,
object outlines on so coplanar members stay distinguishable), which then runs a
separating-axis overlap check on every pair of members. Run from this folder:

```
blender -b --python render_fable.py -- experiment_07_fable_v06.py ../input <abs_out_prefix> [01,05,...]
```

Views: 01 SW (both wings), 02 SE (cube, east end wall), 03 NW, 04 NE (old
facades), 05 plan, 06 south elevation, 07 west elevation, 08 framing only,
09 roofs off, 10 cube close-up, 11 fractured south window, 12 west door +
wedge window, 13 wrap alone, 14 corner post / valley detail, 15 wrap from
inside (old house hidden), 16 cube framing, 17 from below, 18 east end wall
framing. v02 was rendered as view 01 only (an overlap-check build); v01, v03
and v04 have all 18 views.

Collections: `Old_House/{Foundation, Floor_Framing, Floor_Boards,
Wall_Framing, Roof_Framing, Exterior_Sheathing, Windows, Gable_Sheathing,
Roof_Covering}`, `Wrap/{Deck_Foundation, Deck_Framing, Deck_Boards,
Wrap_Wall_Framing, Wall_Cladding, Wrap_Roof_Framing, Roof_Boards,
Wrap_Openings, Wrap_Doors, Steps}`, `Cube/{Frame, Glass}`. Blender
collection names are global, so the wrap sub-collections carry a `Wrap_`
prefix where a name would otherwise collide with an old-house one.

Phase 1 ended at v04 (1278 members, 0 penetrating pairs). Phase 2 (reference
comparison + independent improvements, sections 10-12) ended at v06:
**1328 members, 0 penetrating pairs (> 1 mm)**, views 19 (cube trimmers, cage
legs) and 20 (braces, eave blocking) added from v05.

## 2. Reading the inputs (the Gehry Residence photographs)

Only the photographs were available (no manual). What I took from each:

- `frank_gehry_home_06.jpg`, `references/frank_gehry_home_04.jpg` (street
  side, and the model): the 1920s gabled house is kept whole and *wrapped* on
  two street sides by a new skin standing a few metres off the old walls.
  The skin is a set of **tilted planar walls of different heights with
  sloping tops**, clad in corrugated metal with vertical ribs; a **tilted
  glazed cube** crashes through the roof of the wrap over the kitchen.
- `frank_gehry_home_05.jpg` (kitchen): the cube is a timber-framed glass box
  rotated about all three axes, sitting in the roof of the low wrap; the
  kitchen lives in the wedge between the old wall and the new skin, on a lower
  floor.
- `frank_gehry_home_01.jpg`, `02.jpg`, `references/03.jpeg` (the later house and
  interiors): exposed heavy timber, plain straight sticks, bolted plates, glass
  framed by ordinary rafters, roofs and canopies as tilted planes.

Design rules derived from this (the "deconstruction" of the experiment-04 box):

1. The FRIM box is a *found object*: keep its platform, stud walls, Fink
   trusses and gable roof. Strip all interior ply and the ceiling (exposed
   studs and trusses, as Gehry stripped his house to the lath), remove the
   exterior ply on the two wrapped sides, cut lintel-framed openings in them.
2. Build an L-shaped wrap on the south and west on a deck **360 mm lower** than
   the old floor (the level change is the "dynamic layout": the old rooms step
   down into the new kitchen / entry wedge).
3. The wrap walls tilt: plumb at the shared corner, leaning out 0.7 m at the
   far ends, tops sloping. A wall whose bottom and top edges are skew straight
   lines is a hyperbolic paraboloid – **a ruled surface built entirely from
   straight sticks**. This is the constructive reading of "ruled surfaces in
   architecture": studs along one family of rulings, cladding boards along the
   same rulings (like the vertical corrugation ribs), no member is bent.
4. The wrap roofs are a second pair of hypars between ledgers on the old walls
   and the leaning wall tops; rafters fan along rulings, boards run along the
   cross rulings; the west roof rises to 4.36 m at the street corner (the
   tilted canopy of photo 02).
5. Openings are "fractured": a skew trapezoid on the south wall (sill and head
   planes tilted in opposite senses), a wedge on the west wall, the door, and
   the tilted cube through the south roof.

Deliberate deviation from the photos: corrugated metal and chain-link are not
in the timber/plywood palette of the experiment, so the skin is 22 × 145 mm
vertical boards with 4 mm open joints – same visual grain, buildable with the
same stock as the rest.

## 3. Reading the reference code

`input/experiment_04_fable_v02.py` (my own exp-04 run) supplied the old house
verbatim: 7.32 × 5.49 m, 610 grid, 47 × 97 studs, panel 2745 high, FFL 0.910,
eaves 3.749, Fink trusses @1220, 520 mm rafter tails, 300 mm gable overhang.
The helpers it brought – `box`, `prism`, 2D `clip`, `strip`, `positions`,
`stud_wall`, `clad` – were kept; `prism`/`prism_x` were re-expressed on top of
the new `Frame` class. `craftbot_lib.place_element` is still used for every
axis-aligned box. The ChatGPT 5.1 scripts were not opened (only the prompt
file in `input/`, which told me the earlier run had struggled with corner
studs of twisted walls – I designed the corner around a single vertical post
from the start).

## 4. What "deconstructing the box" meant concretely

| Old house part | Change | Why |
|---|---|---|
| Interior 6 mm ply, ceiling ply + noggings | removed | exposed studs / trusses (photo 01) |
| Exterior ply S and W | removed below the wrap roof, kept above 3.15 m | those walls now face the wrap interior; the strip above the wrap roof is still outdoors (missed in v01–v03, see §8) |
| South wall | 2.3 m wide lintel-framed opening, 4 bays, head 3.005 | connects living room to the kitchen wedge; head sits just under the wrap ledger |
| West wall | 1.7 m opening, 3 bays | entry wedge |
| Front door + stair | removed | entry is now through the west wrap |
| Roof, N/E walls + windows | unchanged | the found object stays readable |

New parts: deck on 400 footings / 120 posts / 60 × 194 bearers / 47 × 145 joists
@610 / 22 × 145 boards at 0.55; corner post 120 × 120; two hypar walls; two
hypar roofs with a shared dropped valley rafter; planar end walls at x = L and
y = W; ledgers 47 × 145 on the old walls; the cube; steps.

## 5. Core modelling decisions

### 5.1 Every member is a convex prism in its own plane (`Frame` + `frame_prism`)

A `Frame` is a point and two unit axes; a member is a 2D polygon in that plane
extruded along the normal from t0 to t1. Every cut is a 3D half-space
`(p, n)` converted into a 2D line in the member's frame. This one abstraction
builds the old trusses, the ruled studs, the tapered boards, the cube bars and
the planar end walls, and – because everything is convex – the generic SAT
overlap check works on all of it.

### 5.2 Slab-exact clipping

v01 clipped the polygon in the member's mid-plane; a 47 mm stud cut by a plane
that is not parallel to its thickness then pokes through by
`thickness/2 · sin(angle)` (1–2 mm at the rails, 6 mm at the last rafters).
`slab_coeffs` shifts every clip plane by the worst-case thickness term
`min(t0·(n·fr.n), t1·(n·fr.n))`, so the whole slab satisfies the half-space.
Cuts become slightly conservative bevels – which is what a carpenter would do.

### 5.3 Convex subtraction for holes (`subtract`)

Polygon minus convex hole = union of `rest ∩ outside_i`, peeling one hole
plane at a time. Used for the cube cut-out in boards and rafters and for the
fractured windows in boards and intermediate studs. v02 computed `rest` with
the un-shifted plane while `outside` used the shifted one, leaving 1.5–2.8 mm
overlaps between pieces of the same board; v03 takes the exact complement.

### 5.4 Ruled surfaces as bilinear patches (`Ruled`)

`P(t,u) = (1-u)·A(t) + u·B(t)` between two straight segments. Rulings `t =
const` carry studs / rafters (`ruling_member`: section d0..d1 along the local
normal, w0..w1 along the surface); cross rulings `u = const` are also straight,
so roof boards run across the rafters. Any patch `[t0,t1]×[u0,u1]` gets a
best-fit plane (`quad_frame`); its out-of-plane residual is recorded and
printed for the five worst members.

### 5.5 Straight rails on a twisted wall

A rail following the wall top is straight (the top edge is a line) but its
section cannot rotate with the local normal. Options: segmented blocking
between studs (follows the twist, no continuous member), or a straight rail
narrower than the studs. Chose the second: rails/plates are 47 × 75 centred on
the 97 mm stud depth, leaving 11 mm each side for the ±6° normal rotation; stud
ends are cut to the rail planes (slab-exact).

### 5.6 Boards follow rulings and are tapered

On a hypar the distance between two rulings varies linearly, so a board between
them is a trapezoid; `surface_quad` makes it from the patch outline with a
2 mm inset per edge (4 mm open joints). Wall boards are one ruling long (2.3–
3.7 m). Roof boards were first made full length (7–10 m) and failed: a long
board along a twisting ruling has ±4 mm edge error and touched the rafters.
v02 cuts roof boards to two-bay stock with joints on rafter centre lines,
rows staggered – the same rule as closed-method sheathing in exp 13.

### 5.7 Corner and ends

Both wrap walls are plumb at the corner and share one 120 × 120 vertical post;
their first studs, plates and rails butt against its faces. Each wing ends in a
planar wall in the plane of the old house's end wall (x = L, y = W) so the wrap
and the old gable read as one flush facade; its vertical studs are cut under
the last (in-plane) rafter and its boards under the roof boards and against
the leaning end stud's cladding face. Members with slanted end faces (cut
square to a tilted axis) are additionally clipped by the post face and the end
plane (`END_S`, `END_W`) – v03.

### 5.8 The cube

1.6 m cube, Euler (35°, 20°, 30°), centre (4.9, −1.8, 3.35): twelve 70 × 70
edge bars (axis-0 bars full length, the others shortened by one bar width at
each end so the three bars at a corner butt), 6 mm glass inset inside the bars
on every face whose normal has z > −0.3. Its six faces are the hole planes
for the south roof: boards cut with 30 mm, rafters with 50 mm clearance
(flashing / trimmer zone not modelled). It rests on nothing explicit – in the
real house it sits on the kitchen roof framing; here the two cut rafters are
its supports by implication (documented simplification).

## 6. Detailed geometry

Wrap surfaces (stud inner faces), metres:

- South wall: A (−2.40, −2.80, 0.55)→(7.32, −2.80, 0.55); B (−2.40, −2.80,
  2.88)→(7.32, −3.50, 3.45).
- West wall: A (−2.40, −2.80, 0.55)→(−2.40, 5.49, 0.55); B (−2.40, −2.80,
  2.88)→(−3.10, 5.49, 4.20).
- Roofs: ledger line at y or x = −0.038, z = 3.31 (ledger top 3.15 + 0.16);
  wall-top line raised by 0.16 (0.23 at the corner for the deeper valley) so a
  145 mm rafter clears the rail top everywhere (slopes ≤ 12°, worst 148 mm).
  The t = 0 ruling of both roofs is the diagonal from the old corner to the
  post top: one shared valley rafter 70 × 190, dropped 10 mm so its top corners
  stay under both board layers (same logic as "dropping the hip" in exp 13).
- Rafters fan from 610 at the ledger to ~800 at the rail; the last rafter
  lies in the end plane and carries the end wall.
- Fractured south window (studs 5–8): sill plane through (0.9, ·, 1.35) normal
  (−0.30, 0, 1), head plane through (0.9, ·, 2.45) normal (0.20, 0, −1). Wedge
  west window (studs 4–6): sill falls north at 0.45, head rises north at 0.75
  (0.50 in v01–v03; widened because it read as a slit). Door (studs 7–9), head
  2.10 above the deck, leaf 40 mm with 10 mm clearance, 10 mm above the plate.
- Opening framing: intermediate studs end at the cut planes; per-bay trimmers
  97 − 4 mm deep sit behind the boards between the stud side faces, one stud
  depth beyond the cut plane. v01 had one header across all bays in a single
  fitted plane; on a 3-bay patch the 21 mm residual made it collide with the
  studs.

## 7. Verification

- SAT overlap check (renderer): v01 242 pairs → v02 53 → v03/v04 0.
- Out-of-plane residual report: worst remaining members are the door leaf
  (19 mm) and single-bay glass / trimmers on the west wall (11 mm). They are
  clipped so nothing penetrates, but they record a real property of the
  design: a planar door or pane hung in a twisted bay needs 10–20 mm of play
  at the corners. Boards and studs stay below 3 mm.
- Visual: the check cannot see *missing* geometry – the stripped strip of old
  wall above the wrap roof (v03 view 03) was only found by looking. Views 08/09
  (skin / roofs hidden) confirmed rafter fans, valley and cube framing.
- Not verified: structure (the cube's bearing, the 160 mm open eave gap over
  the rails without blocking), weathering details (valley and cube flashing),
  and the old truss tails crossing above the wrap roof (clearance computed,
  ≥ 120 mm, but no member models the junction).

## 8. Iterations

| v | change | result |
|---|--------|--------|
| 01 | full concept: stripped old house, deck, two hypar walls + roofs, valley, end walls, cube, three openings, steps | 1002 members, 242 overlaps, all < 36 mm: deck × tilted boards, studs × single-plane header, rafters × 10 m roof boards, thickness-ignorant clips, door leaf into plate, steps into footing |
| 02 | slab-exact clipping; per-bay trimmers, studs end at opening planes; roof boards two-bay stock, staggered; boards clipped at deck + post; leaf above plate; steps moved; lean 0.5 → 0.7, west top 3.74 → 4.20 | 1265 members, 53 overlaps ≤ 9 mm: ledger into north ply, slanted end faces past x = L / y = W / post, subtract pieces overlapping, trimmer × board 1.3 mm |
| 03 | exact complement in `subtract`; end/post clips on plates, rails, first/last studs, last rafters; ledger stops at the ply; trimmers 4 mm shallower; residual report by name | 1267 members, 0 overlaps. Visual review found the old S/W walls open above the wrap roof |
| 04 | ply strip on old S/W walls above the ledger; wedge window head slope 0.75; door leaf in `Wrap_Doors` | 1278 members, 0 overlaps, end of phase 1 |
| 05 | phase 2: trimmers each side of the cube hole between the nearest uncut rafters, rafters cut back to the trimmer faces; eave blocking between rafters on the rails; 47 x 97 diagonal braces in corner and end bays; cube 1.7 m moved west; rooftop lattice cage on legs | first run: cage into the cube (moved), rafters into trimmers by 47 mm (cut extended to the trimmer outer faces), then 1-8 mm (cut planes made to contain the trimmer edge line, not perpendicular to the ruling); cube moved off the old eave. 1324 members, 0 overlaps |
| 06 | cage enlarged to 1.4 x 1.3 x 1.3 and tilted (12, -8, 15 deg) like the cube; legs cut between the roof top plane and the frame underside plane | 1328 members, 0 overlaps, final |

## 9. Scope and known simplifications

- No flashings, trimmers or curbs around the cube; its support is implied.
- Rails and plates are straight 47 × 75 members; on a real twisted wall they
  would be blocked between studs or laminated.
- Open rafter eaves without blocking; no fascia on the wrap.
- Glass panes and door leaf are planar in twisted bays (residuals in §7).
- Corrugated metal / chain-link replaced by timber boards (§2).
- The old house keeps its full gable roof; the wrap roof passes under the
  south and west overhangs (≥ 120 mm clearance) – the "old roof sticking out
  of the new skin" image of photo 06.
- Interior fit-out, mezzanine box (photo 01) and the wedge floor finish are
  out of scope; no ceiling in the old house by design.

## 10. Phase 2 – comparison with the reference photographs

| Reference (photos 04/05/06, 01-03) | v04 model | Change made |
|---|---|---|
| Wrap silhouette: several tilted planes plus chain-link volumes rising above the kitchen roof | two continuous hypar walls, one low roof, nothing above it | rooftop lattice cage (timber analogue of the chain-link form): 70 x 70 bar box 1.4 x 1.3 x 1.3, tilted about all three axes, slats @150, on four legs |
| Glazed cube ~2 m, hard against the old house over the kitchen | 1.6 m cube mid-roof | 1.7 m cube (1.8 m collided with the old fascia / truss tails at 60-80 mm), moved west so it sits over the kitchen end of the wedge |
| Openings framed into the roof with trimmers; heavy visible timber | cut rafters hanging free next to the cube with 50 mm clearance | two trimmers across the hole between the nearest uncut rafters; cut rafters end on the trimmer faces (+3 mm) |
| Diagonals and bolted braces everywhere (photo 01) | no racking resistance in the leaning walls except boards | 47 x 97 flat braces in bays 0, 1 and the last two of both wrap walls, alternating direction |
| Old clapboard kept above the wrap | restored in v04 | - |
| Corrugated metal, chain-link | timber boards | kept (palette of the experiment) |
| Kitchen on a lower floor in the wedge, entry through the wrap | deck 360 lower, door in the west wrap | - |

Not changed, deliberately: plan proportions (the FRIM box is smaller than the
Santa Monica house, so the wrap is 2.4-2.8 m deep instead of ~4 m), and the
old house's roof is left untouched (Gehry also kept it).

## 11. Phase 2 – independent structural improvements

- **Trimmers** (`surf_extent` + `Trimmer_0/1`): the cube's hole extent in
  (t, u) is found by sampling the roof surface (and a second layer 145 mm
  below it) against the six cube planes with the rafter clearance; the
  trimmers are cross-ruling strips one rafter thick just outside that range,
  between the last uncut rafters on either side (the dormer rule from the
  CMHC chapter: opening framed by headers between doubled rafters – doubling
  not modelled). Rafters in between are cut by planes that *contain the
  trimmer edge line*: on a hypar a plane perpendicular to the ruling is not
  the same thing (the parametric directions are not orthogonal) and left
  1-8 mm penetrations until corrected.
- **Eave blocking** (`Block_NN`): 70 mm wide pieces between rafters standing
  on the rail top plane and reaching the roof surface, closing the 160-230 mm
  gap that the constant-offset roof line had left over the rails.
- **Braces**: in-plane diagonals in the stud layer, cut to the stud faces,
  plate top and rail underside with the same slab-exact clips as studs.
- **Cube bearing**: still implied (bolted to the trimmers); the cube's lower
  corner hangs 1.3 m into the kitchen.
- **Cage legs**: vertical 70 x 70, each cut by the roof top plane at its own
  (t, u) (nearest-point search on the surface) and by the tilted frame's
  underside plane, so a tilted object stands on a warped roof without either
  being modelled as anything but convex prisms.

## 12. Phase 2 – what the checks caught

Every phase-2 element first collided with something: the cage with the
enlarged cube (235 mm), the 1.8 m cube with the old fascia and truss tail
(50-80 mm), the cut rafters with the trimmers (47 mm, then 1-8 mm). All were
found by the SAT check, none by the renders; the visual review found only the
design issue (the first cage read as a crib rather than a Gehry volume).
