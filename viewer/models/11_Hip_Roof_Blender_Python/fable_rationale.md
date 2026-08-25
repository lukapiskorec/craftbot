# Experiment 11 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model (Claude
Fable 5) at the end of the run on 2026-08-23. Claude Code transcripts redact
the model's thinking, so the reasoning is written out here; the archived
`experiment_11_fable_conversation.jsonl` holds messages, tool calls and
results only.

## 0. About this document

Same section structure as `experiments/13_.../experiment_13_fable_design_rationale.md`
(§1 how to run, §2 reading the inputs, §3 reference code, §4 what had to
change, §5 core decisions, §6 detailed geometry, §7 verification, §8
iterations, §9 scope). Two sections were added for the phase-2 request
(compare with the PDF figures, independent structural review): §2b (model
vs. the PDF figures) and §5b (structural improvements).

## 1. How to run / outputs

Every iteration `experiment_11_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, studio light, cavity shading,
object outlines on so coplanar boards and doubled members stay
distinguishable), producing `*_blender_view_NN.png` and a `.blend`, followed
by a separating-axis overlap check of every member pair (all members are
convex prisms or boxes). Run from this folder:

```
blender -b --python render_fable.py -- experiment_11_fable_v06.py ../input <abs_out_prefix> [01,05,...]
```

`../input` must contain `craftbot_lib.py` (copied there from experiment 01;
`element_placement_template.py` was copied too for completeness). Views:
01–03 orbit, 04 roof plan, 05–07 framing (sheathing + facade hidden), 08
ceiling/walls plan, 09 south elevation, 10 east elevation, 11–15 framing
close-ups (N dormer, E dormer, valley/ridge junction, NE hip foot, wing-S
dormer), 16–17 dormer / valley with boards, 18 from below (joists, struts,
strongbacks), 19–21 one dormer isolated (main framing hidden). v01 was
rendered with framing views only; views 19–21 exist from v02.

Collections: `Walls`, `Ceiling`, `Roof_Framing/{RF_Main,RF_Wing,RF_Dormers}`,
`Sheathing/{SH_Main,SH_Wing,SH_Dormers}`, `Facade/{FA_Cladding,FA_Windows,FA_Fascia}`
(child names are prefixed because `get_collection` reuses bare names).
Final model: **v06, 1841 members (770 sheathing boards), 0 penetrating pairs
> 1 mm.**

## 2. Reading the inputs

Everything comes from `input/canadian_wood_frame_roof_extracted.md` (CMHC
ch. 11–12), the PDF figures read directly in phase 2, and the three
reference images. The ChatGPT 5.1 scripts were not opened (rule of the
experiment); only the folder listing was used to copy the file naming.

| Source | Rule taken | Number in the model |
|---|---|---|
| Fig. 82/83B hip roof | commons to a ridge board, four hips at 45°, jacks to hips and plates | ridge x = ±3.0 (= 7.2 − 4.2), hips from the four corners |
| Fig. 83B, 85, 87 | hips/valleys ≥ 50 mm deeper than jacks | commons 38 × 235, hips/valleys/ridges 38 × 286 |
| p. 132 example (4.7 m span, 1:3, Ottawa) | 38 × 235 @ 600 | spacing 0.6 m everywhere |
| Roof slope conventions | slope ≥ 1:3 → collar ties, no ridge beam | 9:12 (S = 0.75, 36.9°) |
| "heel bears directly over the exterior wall", bird's mouth | seat = plate width, plumb heel at the outer face | HAP = 235/cos θ − 0.75·140 = 189 mm |
| Ceiling joists (p. 123) | beside each rafter pair, lapped at the centre bearing wall | 38 × 184 at x = 0.6k ± 38, lap 0.2 m over the centre wall |
| Fig. 85 | doubled joist + stub joists where the hip leaves no room | v05: doubled joist at x = ±6.6, stubs beside every hip jack (stubs at y = ±3.9 dropped: 126 mm into the hip) |
| Fig. 87 | valley rises from the inside corner, jacks from both plates/ridges | valleys (±4.2, −4.2) → (0, 0), jacks from the main ridge and from the wing ridge |
| Fig. 88 | doubled rafters, double header, valley rafters in hangers, side studs on a bottom plate **on the sheathing**, sheathing first | one dormer module (§6.2) used five times |
| Fig. 90 | projection < 300 mm: rake rafter, 19 mm nailing strip, blocking | 0.3 m rake overhang, fly rafter pair, strip (v06) + 4 blocks |
| Fig. 98 closed method | 19 mm boards ≤ 286 wide, edge to edge, joints staggered on supports | 19 × 184 (widest two-nail board), 3.6 m stock |
| Fig. 99 | fit tightly at hips and valleys | mitred board ends on the plane intersections |
| `hip_roof_naming_convention.jpg` | member vocabulary (hip jack, valley jack, king) | object names |
| `dormer_window_example_01.jpeg` | gable dormer with rake/eave fascia and horizontal siding | FA_Fascia / FA_Cladding |

Deliberate deviations: dormer wall plates sit directly on the boards (no
separate sheathing cut-out band); no soffits, nailing, flashing, roofing.

## 2b. Model vs. the PDF figures (phase 2)

| Figure | In the figure | In v04 | Change in v05 / v06 |
|---|---|---|---|
| 83B | ceiling joists beside each jack, hips to a short ridge | same | – |
| 85 | double ceiling joist set inboard + stub joists to the end plate | stub joists only, last joist single | doubled joist at x = ±6.6 (N and S halves), stubs start from its outer face |
| 86 / p. 126 | intermediate struts ≥ 45° on a bearing partition; strongback of two 38 × 89 under hip-end jacks, struts radiating from the bearing wall | none on the main roof (collar ties impossible, §5.1) | struts at 50.5° on every uninterrupted main common (N: x = 0, ±0.6, ±1.2, ±3.0; S: ±1.8…±3.0), standing on the lapped joists over the centre wall; strongbacks at x = ±5.1 with two 54° struts each; v06: wing-S strongback on the new partition |
| 87 | valley bearing on the corner studs | same | – |
| 88 | front studs on the sheathing, collar ties on every dormer pair | ties on pairs 2–3 only | unchanged (pairs 0–1 carry the gable, 4–5 are valley jacks) |
| 83A | collar ties on every pair | wing pairs only | unchanged; main roof uses struts instead (see §5.1) |
| 90 (v06) | rake rafter on a 19 mm nailing strip fixed to the rafter over the gable wall, blocking @ 600 toenailed to the strip, rough fascia supports the rake heel | fly rafter + blocking, no strip | 19 × 89 nailing strip on the outer face of the front rafter pair (notched over the top plate like the rafter), blocks shortened to bear on it; the dormer eave fascia already carries the rake heel |
| p. 126 "hip and valley ≥ 50 mm deeper" applied to dormers | – | dormer valleys 184 vs 140 jacks (+44) | v06: dormer valleys 38 × 235 (+95; 184 + 50 is not a dressed size) |
| 89 | lookouts when the projection > 300 mm | 300 mm rake | kept as a narrow projection (Fig. 90) – at the limit |
| 97/98 | boards closed, joints on supports, ends supported | same | – |
| p. 124 rafter pairs opposite or offset ≤ one thickness when joists are lapped | – | pairs opposite, N joist on +x, S joist on −x side of the same rafter line | – (consistent with the text) |

## 3. Reading the reference code

Only `craftbot_lib.place_element` (scaled unit cube → `box()`) and the
template's call pattern were inherited. All sloped members reuse the prism
toolkit developed in my experiments 07/08/13: `Frame` + `frame_prism`
(polygon in a plane, extruded, cut by 3D half-spaces), `member()` (straight
sloped member defined by a plan line, a slope and a top height), and the
facet/scan-line board layout of experiment 13. New here: `frame_prism`
clips the outline **separately at both faces** of the member (t0 and t1), so
oblique planes give true cheek cuts (jack rafters against hips and valleys,
hip tips against each other) instead of the square worst-case cut used in
experiment 07. If the two outlines end up with different vertex counts it
falls back to the square cut.

## 4. Why the design is what it is

* **True T with equal ridges.** A first layout with a 6 m / 7.2 m wing gave a
  lower wing ridge whose valleys stop on the main south slope; the south
  hip-end facet of such a wing is too small for any dormer of the module
  (apex would land past the wing ridge). Making the wing as wide as the main
  block (8.4 m) puts both ridges at one height, the valleys run at exactly
  45° from the inside corners to the ridge junction (x = −y), and all three
  hip ends (E, W, wing S) become identical 4.2 m-run triangles that carry
  one dormer each.
* **Slope 9:12 rather than 8:12.** Dormer depth = (board + wall height +
  dormer HAP + dormer rise)/S. At 8:12 a 1.1 m dormer wall put the apex at
  0.56 m from the main ridge (trimmed commons of 0.5 m); at 9:12 the apex is
  3.16 m up the 4.2 m run, leaving 1.0 m of untrimmed commons above the
  header. 10:12 would have been steeper than the manual's usual range.
* **Dormer module 1.8 m (doubles at ±0.9).** Chosen so that a 0.6 m grid
  offset by 0.3 m puts the doubled rafters *and* the trimmed rafters (±0.3)
  on grid lines on every facet; the N facet keeps the 0.6k grid (doubles at
  1.2 and 3.0 for centre 2.1), the hip-end facets use 0.3 + 0.6k. The
  0.3 offset also removes the E/W king common, which made the hip tips
  simpler (they mitre against each other on y = 0 and butt on the ridge end
  face x = ±3.019).
* **Rafter = body + tail.** A bird's mouth makes the profile non-convex; the
  overlap check needs convex solids. Splitting on the plumb heel face keeps
  both parts convex and the two share one face (0 mm penetration). Seat width
  is set by choosing HAP so the underside emerges exactly at the inner plate
  face; for the 286 mm hips the seat runs 40 mm past the plate – accepted.
* **Dropping the hip** by S·19/√2 = 10 mm so the hip's top corners lie on
  the two roof planes; valleys start on the plane intersection (their corners
  fall 9 mm below both planes). Dormer valleys are also dropped 10 mm (§6.3).
* **Sheathing first.** Following Fig. 88 literally: the main boards run
  under the dormer overhangs, the dormer plates sit on the boards
  (h = 19…57 mm above the rafter plane), the cut-out is the inside of the
  dormer walls, and the dormer ridge / rafter tails / side top plates are all
  clipped by the plane "main board top" – this one plane handles every
  dormer-to-roof contact.

## 5. Core modelling decisions

### 5.1 Half-space clipping instead of coordinates

No member end is typed in. Each facet carries a fixed list of half-spaces
(ridge face, hip cheeks, valley cheeks, plate top); every rafter of the
facet is a long prism cut by all of them, so the same call makes a common, a
hip jack, a valley jack or a hip–valley cripple (e.g. S slope at x = 3.6:
cut by the SE hip cheek at y = −0.6 and the E valley cheek at y = −3.6). The
tail is added only when the clipped body still reaches the wall line. Dormer
members add their own planes (header faces perpendicular to the slope,
dormer ridge face, dormer valley cheeks, main board top).

Rejected: computing member endpoints analytically per case (the ChatGPT-era
approach) – every special case (king, cripple, trimmed, doubled) would be a
separate formula.

Consequence: collar ties on the main roof are impossible – every N/S pair is
interrupted by a dormer (N: x = ±1.8, ±2.4 trimmed) or by the valleys (S:
valley jacks end above tie height for |x| < 1.8), and the king pair at ±3.0
clashes with the dormer valley feet (found by the SAT check). The manual's
alternative – struts ≥ 45° on the bearing partition – was used in v05.

### 5.2 Cheek cuts as two-level outlines

`frame_prism` clips the profile polygon on the near and far face of the
member separately. A vertical hip cheek plane (offset ±19 mm from the hip
centre line) intersects a jack at a different plumb position on each face →
the jack gets a real compound cheek. The same trick yields the mitred hip
tips, the V-cut of the dormer valleys at the apex and the bevel on the
dormer valley feet against the inner doubled rafter.

### 5.3 Boards: scan-line rows with exact edge mapping

Board layout is the experiment-13 algorithm (rows from the eave, joints on
rafters, half-board stagger, rip at the ridge), but the way the underside
outline is derived changed. Exp. 13 scanned both outlines and fell back to a
square end whenever vertex counts differed – which happens at every ridge
row, eave row, facet apex and dormer cut-out apex, and produced 18 mm
overlaps here. v03 instead scans only the **top** outline and maps every
corner to the *same outline edge* on the underside plane (`under_corner`):
side edges by intersecting the underside edge line with the row edge,
constant-v edges (eaves, ridges, dormer fronts) by the edge's underside v.
Two guards were needed: corners whose extrapolated underside edges cross
(facet apexes) are collapsed onto the apex (`uncross`), and trapezoids are
cut at the ends of constant-v edges so a board running past a dormer front
never gets a slanted row edge (`split_quad_u`; decided by the piece's
centre u, not the corner u, after a corner on the hedge end was mis-mapped).

### 5.4 Dormer/main board junction

Three planes define it: main underside M0, main top Mt, dormer underside D0.
Main boards inside the dormer walls end on D0 (hole edge = M(h) ∩ D0); the
dormer boards end on Mt (edge = D(h) ∩ Mt). The main board's top and the
dormer board's underside then share the line Mt ∩ D0 — no overlap, no gap
along the visible line. With the symmetric choice of exp. 13 (both on the
same offset level) the two layers overlapped by the board thickness.

## 5b. Independent structural review (phase 2)

Implemented in v05 / v06:

1. **Rafter span.** 4.2 m run at 9:12 is 5.25 m along the slope, beyond the
   manual's 4.7 m / 38 × 235 @ 600 example. Struts (38 × 89) from the centre
   bearing wall to the rafter underside at y = ±1.5 halve the span; the
   attachment point was chosen so the angle is 50.5° (≥ 45°, p. 126). They
   stand on the lapped joists directly over the wall, so the load path is
   strut → joist → partition.
2. **Hip ends.** Strongbacks of two 38 × 89 on edge under the E/W jacks at
   x = ±5.1 (between grid lines, clear of joists), each on two struts at 54°
   from the centre wall.
3. **Wing ceiling.** The wing joists spanned 7.2 m from the flush header to
   the south wall – far beyond 38 × 184. A bearing partition at y = −7.8
   (under the wing ridge end) splits it into 2 × 3.6 m and the joists lap
   over it like the main ones.
4. **Doubled end joists** (Fig. 85) so the stub joists have a proper
   back-span member.
5. (v06) **Wing-S hip end**: with the new partition available, a strongback
   at y = −9.0 under the wing-S jacks on three 54.6° struts (x = 0, ±1.2,
   standing between the lapped joists on the partition plate). First attempt
   sized the strongback with the wrong hip line (half-width 2.4 instead of
   1.8 m) and ran 64 mm into the hips and boards – the SAT check caught it.
6. (v06) **Dormer valleys 38 × 235**, ≥ 50 mm deeper than the 140 dormer
   jacks, flush with the main rafters and the headers.

Checked and rejected: struts under the hips and valleys. At 9:12 a strut
from any bearing line below a member that itself rises at 0.75 can never
reach 45° (the limit is atan(0.75) = 36.9°, less the heel offset); the
manual's answer for these members is a beam with a roof strut or a post,
which would need a partition that the open T-plan does not have. The 38 × 286
hips (7.7 m) and valleys (5.9 m) are therefore recorded as members to be
engineered (LVL or a post at the valley foot).

Noted but not modelled: the flush header across the 8.4 m wing opening
carries a full bay of joists from both sides and needs an engineered
section (LVL/flitch) or a post; ceiling joists adjacent to the dormer
doubled rafters sit one member further out (§6.1) and should be nailed
through the double.

## 6. Detailed geometry

### 6.1 Main frame numbers

Plate top 2.70; Z_T0 (rafter top at the wall line) 2.889; ridge surface
6.039; ridge board top 6.024 (under the rafter top corners at y = ±19);
hip slope 0.530 (27.9°), hip drop 10 mm; eaves 0.5 m, tails plumb-cut on
the eave planes, hip/valley tails cut by both eave planes. Valley tails at
the inside corner are split at plate level: above it a normal tail, below it
a piece clipped to x ≥ 4.2 and y ≤ −4.2 so it stays outside both wall
footprints (the 19 mm half-width otherwise entered the top plates by 13 mm).
Joists beside a doubled rafter move one member outward (`beside()`), found
by the SAT check in v02 (38 mm clashes). Strongbacks are boxes whose top is
taken at their *lower* edge on the sloping underside (the first attempt at
the centre line was 23 mm into the jacks).

### 6.2 Dormer module (local a across, s up-slope from the wall line)

Walls 89 thick, outer faces a = ±0.919, front s = 0.6…0.689; wall height
1.1 m from board top at the front to top of the level top plates; dormer
rafters 38 × 140 with their own bird's mouth (HAP 108 mm), ridge 38 × 184,
ridge surface z_dpt + 0.797, apex at s = 3.162. Rafters at s = 0.319 (fly),
0.645 (over the front wall), 1.2, 1.8 (full, with 0.2 m tails), 2.4, 3.0
(valley jacks). Dormer valleys from the apex to the inner double's inner
face (a = 0.843), top 11 mm below the main plane. Headers 2 × 38 × 235
perpendicular to the slope: lower one under the front wall (l = 0.75 −
0.076…0.75), upper one at the apex; trimmed commons at a = ±0.3 split into
ridge→upper header and plate→lower header, plus 0.3 m jacks between header
and valley. Side walls: sloped bottom plate on the boards (plumb-cut at the
front wall), studs at 0.6 from the front, level top plate cut by the board
top plane (ends at s ≈ 2.0). Front wall: corner/king/jack studs, 0.8 × 0.62
rough opening, 2 × 38 × 140 header, sill, gable studs at a = 0, ±0.45 cut
under the rafters and the ridge. Rake: fly rafter pair at s = 0.319, 19 × 89
nailing strip on the front rafters, four 38 × 140 blocks. Facade: 19 × 184
horizontal cladding on all three faces cut around the opening, under the
rafters and under the ridge, 19 × 184 fascia on eaves and rakes mitred at
the corners, window with 38 mm frame, mullion and 6 mm glass.

### 6.3 Things the renders showed that the check could not

v01: all dormer rafters missing (inverted ridge-face normal – the SAT only
reported the p/m pairs overlapping each other). v02: dormer valleys reduced
to stubs (inverted centre-plane normal). v05: gable cladding stopped at
z_dT0 + 0.2, half the gable open in the elevation view. Each of these is a
"missing geometry" case: the frame-only and isolated-dormer views (19–21)
were added for exactly this reason.

## 7. Verification

* Numeric: SAT overlap check over all member pairs after every render
  (~1 min for 1841 members). It drove fixes in every version (§8); final
  0 pairs > 1 mm. Touching faces (rafter body/tail, joists beside rafters,
  boards in adjacent rows, hip tips on the ridge end) register as 0.
* Visual: 21 views including frame-only, dormer-only, plan, elevations and
  from below; checked after each version for missing members.
* Not verified: structural sizes (no span tables in the excerpt), nailing,
  bearing lengths, whether the ripped ridge row width (< 40 mm merged) is
  practical, board joints inside the 3.6 m stock on the hip facets.

## 8. Iterations

| v | change | result |
|---|--------|--------|
| 01 | full frame (walls, joists, ridges, hips, valleys, all rafters, 5 dormers) | 124 overlaps: dormer rafters clipped away (normal sign), valley tails in the wall plates, dormer valleys in the doubles, outer stub joists in the hips |
| 02 | signs fixed, valley tails split at plate level, valleys bevelled on the doubles, joists moved past doubled rafters, main collar ties removed (clash with dormer valley feet) | 0 overlaps, framing visually complete |
| 03 | closed-method sheathing; edge-mapped underside outlines, hole/dormer junction planes, tightened split rule, dormer valleys dropped, rake blocks dropped | 770 boards, 0 overlaps |
| 04 | fascia, dormer cladding, windows; found front studs straddling the wall line and sloped plates 34 mm off their wall faces (plumb end clips) | 0 overlaps |
| 05 | phase 2: doubled end joists, struts, strongbacks, wing partition, gable cladding to the apex | 1826 members, 0 overlaps |
| 06 | second pass through the figures: dormer valleys 38 × 235, Fig. 90 nailing strip, wing-S strongback + struts (first try 64 mm into hips/boards, strip 10 mm into the top plate → notched) | 1841 members, 0 overlaps, final |

## 9. Scope and known simplifications

No soffits, eave protection, roofing, flashing, insulation, ventilation or
nailing; wall openings not modelled (walls are context only); the wing
opening header is a placeholder section; dormer windows sized by the wall
height (0.8 × 0.62 RO) rather than by daylighting; hip seats 40 mm wider
than the plate; the 4 mm wedge where the sloped dormer plates meet the
vertical front wall faces is cut plumb; boards on the hip facets are not
checked for stock length where no rafter joint is reachable; hips and
valleys have no intermediate support (see §5b).
