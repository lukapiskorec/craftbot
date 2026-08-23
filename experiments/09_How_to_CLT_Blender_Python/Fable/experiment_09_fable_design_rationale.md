# Experiment 09 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model (Claude
Fable 5, Claude Code) at the end of the run on 2026-08-23 (phase 1: v01-v05; phase 2 after comparing with the handbook figures: v06-v07). Claude Code
transcripts redact the model's thinking, so the reasoning is written out
here; the archived `.jsonl` only holds messages, tool calls and results.

## 0. About this document

Follows the template of `experiments/13_.../Fable/experiment_13_fable_design_rationale.md`:

| § | Section | Purpose |
|---|---------|---------|
| 1 | How to run / outputs | Exact command, view legend, file naming, collections. |
| 2 | Reading the inputs | Which handbook rules became numbers; deliberate deviations. |
| 3 | Reading the reference code | What was inherited from `craftbot_lib.py` and earlier Fable runs. |
| 4 | Design of the building | Typology, plan, core, roof – the decisions and rejected options. |
| 4b | Comparison with the handbook figures | Phase 2: what the PDF figures show that the extraction did not, and what was changed. |
| 5 | Core modelling decisions | Representation and algorithms (convex pieces, balloon strips, section cuts). |
| 6 | Detailed geometry | Derivations: storey stack, stair, roof planes, attic walls, podium, phase-2 elements. |
| 7 | Verification | Visual and numeric checks, what they caught, what they cannot catch. |
| 8 | Iterations | One row per saved version. |
| 9 | Scope and known simplifications | What was left out or approximated. |

## 1. How to run / outputs

Every iteration `experiment_09_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, object colour per collection,
cavity shading and black object outlines so coplanar panels stay
distinguishable). Run from this folder (the output prefix must be absolute –
Blender resolves relative paths against its own cwd):

```
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render_fable.py -- experiment_09_fable_v07.py ../input <abs_path>/experiment_09_fable_v07_blender [01,07,...]
```

Outputs: `*_blender_view_NN.png`, `*_blender.blend`, and on stdout the
overlap report (`OVERLAP CHECK: N members, M penetrating pairs`).

| View | Content |
|------|---------|
| 01 / 02 | Full model from south-west / north-east |
| 03 / 04 | South elevation / west gable elevation |
| 05 | Bare CLT structure (facade, roof build-up and glazing hidden) – panel joints visible |
| 06 | Walls, slabs and core only (roof hidden) |
| 07 | Plan section through storey 3 (camera clip plane at floor + 1.3 m) |
| 08 | Plan section through attic 2 |
| 09 | Cross section through the stair well, looking north |
| 10 | Long section through lift A / corridor / stair, looking east |
| 11 | Core only |
| 12 | Stair close-up, core walls and core slabs hidden |
| 13 | Attic close-up: knee walls, attic-2 slab, corridor walls to the roof, core top |
| 14 | From below (eaves, podium) |
| 15 | Plan section through the podium |
| 16 | East gable attic window close-up (diagnostic, v04–05) |
| 17 | Core ledgers from below (v06+) |
| 18 | Section y = 2.9 looking north: corridor wall, partitions, ledgers, ribbed attic floor (v06+) |
| 19 | Worm's-eye plan section 0.55 m under the attic-1 slab: ribs, ledgers (v06+) |

Section views use the ortho camera's near clip plane as a cutting plane
(`cut=("z", value)` etc. in `VIEWS`); no per-storey collections are needed.
Cut solids are hollow (no cap faces), which is acceptable for inspection.
The clip plane is perpendicular to the view direction, so a cut is a true
section only at elevation 0 or ±89.9° (a tilted camera tilts the plane –
found in v07 when view 18 at 12° showed the facade instead of the interior).

Collections (Blender outliner), 2787 objects in v07 (2404 in v05):

```
Podium/   Podium_Walls 84 · Podium_Frame 16 · Podium_Slabs 8 · Podium_Stairs 21
Structure/ Exterior_Walls 518 · Interior_Walls 182 · Partitions 144 · Gable_Walls 44 · Knee_Walls 8
Core/     Core_Walls 104 · Core_Slabs 14 · Landings 14 · Stairs 112 · Ledgers 111
Floors/   Slabs 315 · Ribs 64
Roof/     Roof_Panels 78 · Roof_Covering 78
Facade/   Cladding 528
Openings/ Glazing 198 · Doors 146
```

Object counts are high because every wall *with openings* is decomposed
into convex pier / sill / lintel pieces (see §5.1).

## 2. Reading the inputs

Main source `input/how_to_clt_extracted.md` (Arkemi, *How to CLT*, 2nd ed.).
In phase 1 the PDF itself was not opened; the extraction carries the
dimension tables. In phase 2 the PDF spreads with the structural figures
(book pp. 35–61) were read directly – see §4b.
Reference images `references/U-shaped_staircase_01/02.png` fixed the stair
typology (double flight with half landing, 18 cm riser / 28 cm going,
flights ≥ 91 cm wide). The ChatGPT 5.1 folder was not opened at all (neither
scripts nor screenshots) so that the two runs stay independent.

Rules taken from the handbook and how they became numbers:

| Handbook rule | Value used | Where |
|---|---|---|
| Scope 3–8 floors, pure CLT | 8 CLT storeys on a concrete podium (6 regular + 2 in the roof) | `N_REG`, `z_floor` |
| Concrete podium raising timber off the ground, transfers loads for a different ground-floor layout (p. 41) | Ground floor: 250 concrete walls with shop windows, 400 × 400 columns + 400 × 600 transfer beams under the CLT bearing lines, 400 transfer slab | §1 of script |
| Wall panel height = master panel width ≈ 3 m, platform framing for multi-storey (p. 55) | Wall 3.00 m, slab 240 → storey pitch 3.24 m | `H_WALL`, `H_ST` |
| Exterior wall, floors VII–VIII, light floor: 140–200 → **180** (p. 60) | `T_EXT = 0.18` | |
| Partition wall VII–VIII light: single **160**, double **100 + 100** + 170 insulation (p. 61) | corridor walls `T_INT = 0.16`; parting wall two 100 mm leaves (v06+) | |
| Core / shafts: longitudinal panels up to 16 m ("longitudinal in core") | core walls 180, balloon panels in two lifts: 12.96 m and ≤ 15.1 m | `CORE_LIFTS` |
| Slab 5–7 m span, light superstructure: **240** (p. 59) | spans 5.34 m (facade → corridor wall), `T_SLAB = 0.24` | |
| Roof < 5 m / 5–7 m: 140 / 160 (p. 62) | **160**, longest roof span 6.05 m on the slope | `T_ROOF` |
| Transport ≤ 13.6 × 2.45 × 3.0 m | slab strips 2.40 m wide, wall panels ≤ 11.2 m long, roof panels 2.29 m wide × 9.4 m long, balloon strips ≤ 3.0 m wide | `SLAB_W`, `PANEL_LMAX`, `strips()` |
| Exterior wall build-up 442–482 total (200 insulation + cladding) | one 250 mm "facade" layer outside the CLT (simplified) | `T_FAC` |
| Roof build-up: 200 insulation + ventilation + metal | one 300 mm covering layer | `T_COV` |
| Openings: piers ≥ 300, opening ≤ 1500–2000 | windows 1.2 × 1.4, doors 1.0, corridor opening 1.8; all piers ≥ 0.6 m | `windows_on`, `CORR_OPEN` |
| Parting walls must line up between storeys; honeycomb = same layout every floor | identical plan on all 8 storeys, parting wall on a slab joint | `X_PW = 24.0` |
| Pitched roof: panels tilted against each other for limited spans; "pitched roof with supporting wall and beam" for larger (p. 47) | 45° double pitch; panels bear on eave wall, attic knee wall, corridor walls extended to the roof and lean on each other at the ridge | §4 of script |
| CLT stairs cut from thick panels / offcuts (p. 49) | stepped solid flights, 240 landings | `flight()` |

Deliberate deviations:

- The handbook tables stop at 8 floors; the two attic storeys are counted
  as floors VII–VIII, so a uniform 180/160/240 set is used everywhere
  instead of stepping thickness per band ("thicker lower-floor walls
  possible but not necessarily economical").
- The stair riser/going is 180/290 (2R + G = 650) instead of the reference
  image's 180/280 so that 8 treads × 290 + two 2.12 m landings fill the
  6.56 m clear core length exactly.
- Windows are not CNC-routed single panels but pier/sill/lintel pieces
  (§5.1). Structurally it corresponds to the handbook's "opening formed
  with lintel support".

## 3. Reading the reference code

- `craftbot_lib.place_element` creates a 2 × 2 × 2 cube and a T·R·S
  matrix; the `box()` helper converts corner coordinates to that call, as in
  earlier Fable runs. Axis-aligned boxes are used for everything that is
  rectangular (slabs, straight walls without sloped tops, stair blocks).
- From `experiments/06_.../Fable/experiment_06_fable_v07.py` the helpers
  `get_collection` (nested paths), `prism` / `prism_x` / `prism_y`, `clip`
  (Sutherland–Hodgman against a half-plane) were reused verbatim; they are
  what make sloped tops (gable walls, roof panels, corridor walls under the
  roof) possible as convex solids.
- `render_fable.py` is the experiment-06 renderer plus a section-cut option
  and the convex-hull SAT overlap check (unchanged).

## 4. Design of the building

**Typology.** A double-loaded-corridor slab block: 33.6 × 13.2 m outer CLT
faces, corridor 1.8 m clear between two load-bearing walls (y 5.54–5.70 and
7.50–7.66). The reason is structural: with the corridor walls carrying the
slabs, every slab spans 5.34 m across the building, inside the handbook's
plain-CLT range. A point-block plan with slabs spanning 9–14 m between
parting walls was rejected because it would need ribbed or composite slabs.

**Apartments.** Six per floor: two corner apartments on each side of the
parting wall at x = 24.0 (on a slab joint), and two L-shaped apartments
wrapping the core on the west. Entrance doors (1.0 × 2.1) in the corridor
walls at x ≈ 4.9, 20.1, 28.7 on both sides. Non-load-bearing partitions
inside apartments are not modelled (handbook: "any material").

**Core.** One 6.92 × 7.12 m core (outer) straddling the corridor at
mid-length so the corridor passes *through* it (1.8 × 2.1 openings in the
core's west and east walls every storey, with fire doors). South of the
corridor: two lifts 1.80 × 2.10 behind the corridor wall (doors 0.9 wide
facing the corridor) and a 2.6 × 2.1 service/refuse room. North: the stair
well, 6.56 × 2.50 m, flights along X. The core is centred under the ridge
(y 3.24–10.36 around 6.6) – see §6.3 for why this was the deciding factor.

**Vertical load path.** Platform framing everywhere except the core:
exterior, corridor, parting and knee walls are one-storey panels, the slab
runs over them and stops at the core faces, the core's balloon panels run
continuously and carry the core's own slab pieces (corridor piece, service
room floor, stair floor landing) on their inner faces. This is the
wall-vs-slab priority: **slab over platform walls, slab against balloon
walls.**

**Roof.** 45° double pitch with a 2.0 m eave knee wall on the attic-1
floor, ridge 8.6 m above it → two attic storeys (3.24 + ≥ 2.5 m headroom
under most of attic 2). Bearing lines per slope: eave wall (y 0.18), attic
knee wall/attic-2 slab edge (y 1.24), corridor wall extended to the roof
(y 5.54–5.70), ridge (the two slopes are plumb-cut and butt over the
corridor). Slope spans 1.5 / 6.05 / 1.27 m – all ≤ 7 m, so 160 mm panels
without ribs. The 45° pitch with a 2 m knee was chosen over a flatter roof
because a lower pitch (≤ 40°) leaves < 1.8 m headroom at the core faces in
attic 2, and over a steeper one because the attic-1 gable/knee geometry
already gives two full storeys.

**Podium.** 3.96 m (= 22 risers × 0.18, so the ground stair uses the same
riser), concrete perimeter with 2.4 × 2.4 shop windows, entrances on the
corridor axis at both gables (the corridor leads straight into the lift
lobby), columns and transfer beams under the corridor and parting wall
lines, concrete core walls under the CLT core.

## 4b. Comparison with the handbook figures (phase 2)

Read directly from the PDF (spreads 19–32 = book pp. 35–61): structural
systems table (p. 39), podium figure (p. 41), linear→planar (p. 42), opening
types (p. 44), envelope section (p. 45), floor types (p. 46), roof types
(p. 47), CLT stair photo (p. 49), master panel / trailer (p. 52), panel
applications (p. 55), ribbed panel (p. 56), build-ups and tables (pp. 59–61).

**Already consistent with the figures (v05):**

| Figure | v05 |
|---|---|
| p. 41 podium: CLT block on a concrete ground floor, glazed between piers | concrete podium, shop windows, CLT walls start on the transfer slab |
| p. 55 "transverse in platform": storey-high panels, slab sandwiched and running to the outer face | exterior/corridor/parting walls 3.0 m, slab over the wall to y = 0 / 13.2 |
| p. 55 "longitudinal in core": one tall tube, stair inside, slabs butt | balloon core in two lifts, slabs stop at the core faces |
| p. 45 envelope: roof CLT on top of the wall, build-up continues over the overhang, insulation outside the wall CLT | eave wall + sloped wedge under the roof panel, 300 mm covering to the eave, 250 mm facade layer |
| p. 44 openings: piers ≥ 300/600 mm, openings ≤ 1500/2000 mm, lintel-supported openings | windows 1.2 m, doors 1.0, corridor openings 1.8 m, piers ≥ 0.6 m, lintel pieces |
| p. 47 "pitched roof with supporting wall" / panels leaning on each other | corridor walls to the roof, plumb-cut ridge |
| p. 49 stair cut from a thick panel | stepped solid flights |
| p. 52–53 master panel 16 × 3 m, trailer 13.6 × 2.45 × 3.0 | all panels within limits (§2) |

**Differences found and resolved in v06–v07:**

1. *Parting wall build-up (p. 61).* The figure shows the apartment-separating
   wall as either a single CLT with a separate stud lining or **double CLT
   with 170 mm insulation between** (100 + 100 for floors VII–VIII, light
   floors). v05 used a single 160 leaf. Changed to two 100 mm leaves 170 mm
   apart (`PW_LEAVES`); corridor walls and slab strips stop at the outer
   leaf faces, the podium transfer beam stays centred on x = 24.
2. *Ribbed panel (pp. 46, 56).* The handbook's way to make a slab span or
   carry more without thickening it is LVL/glulam ribs glued under the panel.
   The attic knee walls (y = 1.24 / 11.96) load the attic-1 slab at
   mid-span; v06 makes that slab a ribbed panel: two 100 × 240 glulam ribs
   per 2.4 m strip in the span direction, broken at the parting wall and at
   the core ledgers (§6.7).
3. *Slab bearing on the core.* In the "longitudinal in core" figure the
   slabs simply meet the tube; the connection is not drawn. v05 had slabs
   butting the balloon walls with nothing under their edge. v06 adds
   120 × 160 timber ledgers on every core face under every slab edge, outside
   (segmented at the corridor walls so they do not run into the platform
   wall tops) and inside (corridor piece on both corridor walls, service
   room on three walls, stair floor landing on three walls).
4. *Plan layout.* The parting-wall system figure (p. 39) shows load-bearing
   CLT plus "non-load-bearing elements from any material". v05 apartments
   were empty boxes; v06 adds one 100 mm stud partition with a 0.9 m door
   per apartment (x = 7.0, 21.6, 30.0 on both sides, all 8 storeys, clipped
   to the roof in the attics) so the plan reads as rooms. Positions were
   chosen clear of apartment doors, window junctions and the attic ribs.

**Considered and not changed:**

- Floor build-up (p. 59: +283 mm light superstructure on the CLT). Modelling
  it would shift every finished floor, door sill and stair by 0.28 m for no
  structural information; the model stays at structural level (§9).
- A glulam ridge beam (p. 47 "ridge beam support"): the slopes bear on the
  corridor walls 0.9 m either side of the ridge, which the handbook's
  "panels tilted against and fixed to one another" covers for such spans.
- Thicker walls in the lower floors (p. 54): allowed but "not necessarily
  economical"; a uniform 180/160 set keeps the panel system optimised
  (p. 54 "optimized" vs "non-systematized").
- Moving the core to make the plan symmetrical: every symmetric variant
  either puts the core against an eave (roof collision, §6.3) or produces
  U-shaped middle apartments.

## 5. Core modelling decisions

### 5.1 Everything is a convex solid; openings are pieces

The overlap checker (SAT) needs convex hulls. A wall with a hole is not
convex, so `wall_pieces(poly, openings)` decomposes a convex (u, z) polygon
with rectangular openings into: full-height piers between opening columns,
and for each column the sill/spandrel pieces below and the lintel above
(openings with the same u-range form a column – this is what the balloon
strips need, one corridor opening per storey). Any convex polygon works, so
the same function cuts windows into the triangular gable walls and the
gable cladding. Cost: ~2400 objects instead of ~600; benefit: a numeric
zero-penetration proof and a pier/lintel reading close to how a panel with
a lintel-supported opening is actually produced.

v01's first implementation dropped the pier left of the first opening and
assumed openings never share a u-range; both showed up immediately (1049
overlapping pairs, exposed CLT at the south-west corner) and were fixed in
v02.

### 5.2 Balloon core walls as ≤ 3 m strips in two lifts

Each core wall is split into strips ≤ 3.0 m wide (master panel width) at
sensible lines – the corridor opening band (1.8 m) is its own strip, so its
pieces are the per-storey lintels; the lift/service door strips likewise.
Each strip is cut at z = 16.92 (4 storeys, 12.96 m) into two lifts; the
upper lift runs to the roof underside (max 15.1 m at the ridge apex). The
wall top follows the roof plane: pentagon profile for walls along Y
(`prism_x`), flat top + separate wedge for walls along X (their profile
plane cannot express a slope across the thickness).

### 5.3 Section cuts in the renderer

Instead of per-storey collections, a view can carry `cut=(axis, value)`;
the renderer sets the camera's near clip distance to that plane. This gave
plan sections (storeys 3, attic 2, podium) and two building sections
through the core for free, which is how the stair and core layout were
verified.

### 5.4 Seeded irregular windows

`windows_on()` places windows on a 3.2 m pitch with ±0.4 m jitter from
`random.Random(9)`, skipping any position that would come within 0.6 m of a
panel joint (x = 11.2, 22.4), the parting wall (x = 24) or, on the gables,
the corridor walls. Same list is used for the CLT pieces, the cladding
pieces and the glazing so the three always agree (v01 called the generator
twice and got two different sets; v05 fixed a second variant of the same
mistake on the attic-1 gables).

### 5.5 Independent structural review (phase 2)

Looking at v05 as a timber structure rather than against the book:

- *Vertical load path* – clean: facade and corridor walls carry the slabs
  on every storey, parting walls line up, the podium columns/beams sit under
  the same lines. Weak point was the attic knee wall on the attic-1 slab →
  ribbed panel (v06). Second weak point, not changed: the attic-2 slab edge
  also acts as the roof's intermediate bearing, i.e. the roof thrust enters
  the slab edge; a real detail would add a bevelled bearing plate there.
- *Lateral stability* – along X: corridor walls (33 m), core; across Y:
  gables, parting wall, core walls (6 m), and now the double leaves. Enough
  for an early-stage model; a stability check would be the first engineering
  task.
- *Slab-to-core transfer* – slabs cannot hang in the air on a balloon wall;
  ledgers (v06) make the bearing explicit. Stair landings likewise.
- *Acoustics / fire between apartments* – double CLT parting wall (v06) is
  the handbook's preferred separating wall; corridor walls keep the single
  160 leaf with lining as the table allows.
- *Roof* – 45° with spans 1.5 / 6.05 / 1.27 m on 160 mm panels; the long
  span is within the 5–7 m row. Roof windows removed some panel width but
  every panel keeps ≥ 0.65 m of continuous strip on each side of a window.

## 6. Detailed geometry

### 6.1 Storey stack

`z_floor(k) = 3.96 + 3.24 (k − 1)`; wall k spans `z..z+3.0`, slab k+1
spans `z+3.0..z+3.24`. Attic 1 = k 7 (floor 23.40), attic 2 = k 8 (26.64).
Eave (roof underside at the outer CLT face) `Z7 + 2.0 = 25.40`, ridge
`Z7 + 8.6 = 32.00`, covering top 32.65.

### 6.2 Stair

Clear well 6.56 (X) × 2.50 (Y): floor landing 2.12 (west), flights 8 × 0.29
= 2.32, half landing 2.12 (east). Flight A in the south band (1.2 wide)
rises east from the floor landing, the half landing top is at z + 1.62,
flight B in the north band rises west to the next floor landing, 0.10 m
well between the bands. Each flight is 8 tread blocks (the 9th riser lands
on the landing) 0.36 m deep under the tread – a stepped soffit like a stair
sawn from a thick panel; the first block is clamped so it never goes below
the slab it starts from (podium: ground level). Landings are 240 CLT; the
floor landing doubles as the core slab piece at each level. The stair door
is in the core's north corridor wall above the floor landing (x 10.42–11.42).
Podium stair: 2 × 11 risers, 10 blocks per flight, landings 1.83.

### 6.3 Why the core sits under the ridge

First plan: core north of the corridor, reaching the north facade. With the
attic floors inside the roof this fails: at y = 12.84 the roof underside is
only 0.86 m above the attic-1 floor, so the half landing of the last flight
(1.62 m up) would cut through the roof. Second plan: core south of the
corridor – same problem mirrored, plus lifts with no overrun. Solution:
centre the core on y = 6.6 so the roof is 5.2–8.6 m above the attic-1 floor
over the whole core footprint; the corridor then passes through the core,
which also gives a proper lift lobby. Lifts are on the south side of the
corridor, the stair on the north, and both are reachable from the corridor
at every storey including the attics.

### 6.4 Attic walls under the roof

- Eave knee walls: 2.0 m panels (0.9 × 0.9 windows) plus a sloped wedge up
  to the roof underside across the 0.18 thickness.
- Attic knee walls at y = 1.24 / 11.78: exactly where the roof underside
  equals the attic-2 floor level, so the attic-2 slab (y 1.24–11.96) ends
  in the roof plane and the knee wall top at 3.0 carries it; the roof panel
  touches the slab's top edge along a line (0 mm gap, passes the check).
- Gables: attic 1 = south/north quadrilaterals up to the roof + middle
  box under the attic-2 slab (windows); attic 2 = triangle (corridor-end
  window under the ridge + one per apartment at y = 4.4 / 8.8, where the
  roof is ≥ 2.5 m above the floor – the first choice y = 3.6 pierced the
  roof line).
- Corridor and parting walls in attic 2 run to the roof (flat top at the
  lower face + wedge, per segment – v02's continuous wedge crossed the core).

### 6.5 Roof panels and roof windows

Profile per slope: parallelogram between the underside line
`z = Z_E + tan45·y` and its normal offset (thickness × √2 vertically),
plumb-cut at the eave overhang (y = −0.5) and the ridge (y = 6.6). 15
panels of 2.293 m between x −0.4 and 34.0. Covering = same profile between
offsets 0.16 and 0.46, tiled like the panels. Roof windows (0.9 wide, y-band
0.45–1.15 on attic 1, 2.35–3.20 on attic 2) are cut by splitting a panel
into two side strips and an eave/ridge piece; panels over the core, the
parting wall and the gable overhangs are skipped, and attic-1 / attic-2
windows alternate panels. A glass pane sits mid-way in the covering layer.

### 6.6 Slabs

Regions tiled with strips of width ≤ 2.4 m: south zone (y 0–5.62), corridor
(5.62–7.58), north zone (7.58–13.2), each split at the core's x-range and
cut back to the core faces; joints lie on wall centre lines so the slab
runs over every platform wall. Attic-2 slab only between the knee lines.

### 6.7 Phase-2 elements

- *Double parting wall:* leaves at x 23.815–23.915 and 24.085–24.185
  (`PW_LEAVES`), same polygons as the former single wall on every storey
  (including the roof-clipped attic polygons).
- *Ledgers:* 120 wide × 160 deep boxes directly under each slab
  (`z_top − 0.16 .. z_top`). Outside the core on the W/E faces in three
  segments (y 3.24–5.54, 5.70–7.50, 7.66–10.36) so they clear the corridor
  walls, on the S face full length and on the N face only up to attic 1 (the
  attic-2 slab does not reach the core's north face).
- *Ribs:* under the attic-1 slab only, in the south and north zones, two per
  strip at 1/4 and 3/4 of the strip width, from the facade inner face to the
  corridor wall (or to the core ledger in the core strips); ribs within
  0.285 m of the parting wall centre are skipped. v06 had them hitting the
  core ledgers and the x = 7.2 partition – fixed in v07 by stopping the ribs
  at the ledger and moving that partition to x = 7.0.
- *Partitions:* 100 mm walls along Y with a 0.9 × 2.1 door 0.25 m from the
  corridor wall; attic-1 partitions start at the knee wall, attic-2 ones at
  the knee line and are clipped by the roof.

## 7. Verification

- **Numeric:** the SAT check over all convex members, AABB pre-filtered,
  tolerance 1 mm. v01: 1049 pairs (decomposition bug), v02: 11 (ground
  stair block below the slab, attic corridor wedge through the core),
  v03–v05: **0**; v06: 18 (ribs into core ledgers, rib over a partition),
  v07: **0** with 2787 members. Touching faces (slab on wall, roof on slab edge) give a
  0 gap and are not reported – intended.
- **Visual:** 15 views per iteration. The plan sections confirmed the
  corridor-through-core layout and door positions; the two building
  sections confirmed flights, landings and the core reaching the roof; the
  skin-off views confirmed continuous knee walls, attic-2 slab, and
  corridor walls up to the roof; close-ups found the cladding/CLT mismatch
  on the attic-1 gable.
- **Not verified:** structural adequacy (handbook dimensions are
  preliminary); lift overrun/pit; fire compartmentation; headroom under the
  roof at the attic-2 stair landing (≈ 1.7 m at its north edge); the
  stepped stair soffit against the flight below (checked only for
  penetration, not for headroom). The SAT check cannot detect *missing*
  geometry – that is what views 05/06/13 are for.

## 8. Iterations

| Version | Change | What the renders / check showed |
|---|---|---|
| v01 | Full model: podium, platform walls, balloon core, stair, slabs, attic walls, roof, cladding, openings | Massing and roof correct. 1049 overlaps: `wall_pieces` duplicated pieces for stacked openings and dropped the first pier (exposed CLT strip at the SW corner). Parting walls crossed the knee walls. |
| v02 | Column-based `wall_pieces`; knee walls split at the parting wall | 11 overlaps: first podium step below ground; attic-2 corridor wedge continuous through the core. Sections and plan confirmed the layout. |
| v03 | Soffit clamp; wedges per wall segment; better stair view | 0 overlaps. Stair reads exactly like the reference image. Attic-2 middle apartments had no windows. |
| v04 | Roof windows (panels and covering cut per panel, glass in the build-up); full-size windows on attic-1 gables | 0 overlaps. One attic-1 gable window had cladding cut but solid CLT behind. |
| v05 | Attic-1 gable windows filtered to the middle gable piece at the source | 0 overlaps, 2404 members; all views clean. **End of phase 1.** |
| v06 | Phase 2 after reading the PDF figures: double-CLT parting wall, ledgers under slab edges at the core, ribbed attic-1 floor, one partition per apartment; new views 17–19 | 18 overlaps: ribs ran into the core ledgers (S/N faces) and the x = 7.2 partition sat under a rib. |
| v07 | Ribs stop at the ledgers; partition moved to x = 7.0; section views fixed to elevation 0 / −89.9 | 0 overlaps, 2787 members. Plan, section and worm's-eye views confirm leaves, ledgers, ribs and partitions. **Final.** |

## 9. Scope and known simplifications

- Facade and roof build-ups are single solid layers (250 / 300 mm) instead
  of insulation + battens + cladding; podium left as exposed concrete.
- Openings are pier/sill/lintel pieces, not routed single panels; no
  window frames, only a glass pane; doors are a 40 mm leaf in the opening.
- No balconies, no dormers, no ridge cap or flashings, no lift pit, no
  lift machinery or overrun box (the shaft simply ends under the roof).
- The knee walls at y = 1.24 bear on the attic-1 slab at mid-span; a real
  design would check that line load or move the knee line to a wall below.
- The balloon strips of the core are cut into pier/lintel pieces per
  storey; a producer would likely route the openings into the 13–15 m
  strips instead.
- Apartment interiors have one partition each (no bathrooms/kitchens); the
  attic-2 middle apartments rely on roof windows.
- Ledgers are modelled as solid timber strips; in practice they would be
  steel angles or screwed-on LVL strips, and the slab would bear on them with
  acoustic bearing strips.
- The insulation between the two parting-wall leaves is not modelled (void).
- Swedish snow-zone and fire-class choices are not explicit; roof 160 mm
  covers snow zones up to 3.5 kN/m² for the 6.05 m slope span.
