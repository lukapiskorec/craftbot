# Experiment 03 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-22, two rounds: build v01–v02, then reference comparison and
structural revision v03–v04). Kept because Claude Code transcripts redact the
model's thinking; only messages, tool calls and tool results survive in the
`.jsonl`.

## 0. About this document

Same structure as `experiments/13_.../Fable/experiment_13_fable_design_rationale.md`
(§0 there lists the sections). §3 ("reading the reference code") is short here:
the ChatGPT 5.1 scripts were deliberately **not** read, so the two runs stay
independent; only `craftbot_lib.py` / `element_placement_template.py` were used.
§4 is the reference-comparison / structural-review round that the second
prompt asked for.

## 1. How to run / outputs

Every iteration `experiment_03_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, object-colour per collection,
cavity + black object outlines so coplanar sheets stay distinguishable),
producing `*_blender_view_NN.png`, a `.blend`, and a separating-axis overlap
report of every member pair. Run from this folder:

```
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render_fable.py -- experiment_03_fable_v04.py ../input <abs_out_prefix> [01,05,...]
```

Views: 01 front/glazed-end corner, 02 back/bathroom-end corner, 03 front
elevation, 04 top, 05/06 frame only (sheathing + glazing hidden), 07 top with
roof deck hidden (roof + box framing), 08 ground floor only, 09 plan of
partitions on the subfloor, 10 hatch / box 1 close-up, 11 light well / box 2
close-up, 12 glazed corner with ring beam; from v03: 13 light-well rim and
blocking, 14 bathroom shear panels, 15 floor blocking over a girder.

Collections: `Structure/{Foundation, Floor_Framing, Ground_Walls,
Interior_Walls, Shear_Panels, Roof_Framing, Loft_Boxes}`,
`Floors/{Ground_Subfloor, Roof_Deck}`, `Facade/{Sheathing, Glazing}`.
Final model: v04, 555 elements, 0 penetrating pairs > 1 mm.

## 2. Reading the inputs

- `vipp_shelter_ground_floor.jpg`: 5.2 × 11.5 m plan; bathroom module at one
  end (≈ 2.3 × 2.9 m), storage/fireplace wall beside it (magenta marks in the
  `references/` copy), kitchen island and table in the open part, walk bridge
  entering through the long side next to the bathroom, "gutter: lower front
  edge" on the long side → the flat roof of the ground floor drains to the
  front.
- `vipp_shelter_upper_floor.jpg`: two equal boxes 5.0 × 2.5 m, aligned to one
  long edge, a hatched flat-roof strip with "upper front edge with integrated
  gutter" on the other. Box over the bathroom end = loft bed (bed, ladder to
  lower level, storage); the other = "sky light" only. Their tops are glazed.
- Photos (`Vipp_View01`, `Vipp_outside_photo_01`, `r_hjortshoj…158`): ground
  floor on slender round steel stilts ≈ 0.6 m high; both long sides full-height
  glass in four bays (two fixed, two sliding); thin dark fascia band at roof
  and floor; bathroom end solid with louvred fins; the boxes are set back to
  the rear edge, box 2 has a pair of small windows on its front face; box 1
  carries an exterior ladder. Interior photo (`av_16122`) shows the light well
  as a deep, open shaft above the kitchen with a skylight on top; bed photo
  (`ignant…015`) shows the loft with a three-pane glazed roof and a small side
  window.
- Construction figures (`Screenshot …`): balloon frame (full-height studs,
  ribbon-supported joists), joists on bearers with header joist, floor boards
  on joists, door-opening framing with top/bottom rails and a header. Used as
  the vocabulary for the stud walls, joist platforms and openings; no text
  manual was available for this experiment, so member sizes are standard
  Scandinavian/N-American sections (50 × 150 studs @ 600, 50 × 200 floor
  joists, 50 × 250 roof joists, 18 mm plywood in 1.22 × 2.44 sheets).

Deviation from a strict balloon frame: the loft boxes are **platform-framed**
on the roof deck (own sole plate) instead of running ground-floor studs
through. Reason: the long sides have no studs at all (glass), so there is
nothing to continue; the box walls are carried by built-up trimmer joists and
a header on the ring beam instead. The solid end wall keeps single full-height
studs from sill plate to ring beam (balloon style, no intermediate plate).

## 3. Reading the reference code

`craftbot_lib.place_element` creates a 2 × 2 × 2 cube and applies T·R·S, so a
box from corner coordinates is `loc = centre, scale = half-size`; the thin
`box()` wrapper in the script does that and re-links the object into a nested
collection (`place_element` links to the scene root). Everything is
axis-aligned, which is what makes the SAT overlap check in `render_fable.py`
exact.

## 4. Reference comparison and structural review (round 2, v02 → v04)

Comparison of the v02 renders with the photos/plans, then a review of the
frame on its own terms. Each finding, what was done, and what was rejected:

| # | finding | action |
|---|---------|--------|
| 1 | **Geometric defect**: the deck strip under box 2's back wall (x 6.1–10.9, y 5.1–5.2) sat 250 mm above the ring beam with no joist under it — the light-well joists had been cut at y = 2.7 and nothing replaced them at the back. | Doubled rim joist on the back ring beam between the box-2 trimmers (`Well_Rim_N`). |
| 2 | Light-well header: a 2-ply 50 × 250 spanning 4.8 m carrying the box-2 front wall, half the box roof and the tail-joist reactions — undersized. A post under it was rejected (it would stand in the kitchen island); a dropped beam was rejected (nothing for it to bear on along X). | 3-ply header (150 wide, y 2.70–2.85) directly under the wall; box-2 trimmers also 3-ply. Box-1 trimmers stay 2-ply (continuous joists, lighter). |
| 3 | Loft floor: 50 × 250 @ 600 over 5.2 m is at the floor-span limit. | 400 c/c joists between the box-1 trimmers (only the 400 grid there — mixing 600 and 400 members produced a joist through the hatch in v03). |
| 4 | Hatch: a single 0.55 m bay is narrow for a ladder. | Two 400 bays (x 3.025–3.775): the middle joist is cut into two tail joists bearing on the 50 × 250 headers — proper trimmed-opening carpentry. |
| 5 | Connection details: joists simply sat on beams with nothing between them. | Solid blocking between joist ends over both ring beams (acts as rim blocking behind the fascia) and between floor joists over each girder — stops rollover and gives the sheathing a nailing edge. |
| 6 | Lateral stability along X: both long sides are glass, the only X-shear elements were unsheathed partitions. Knee braces on the mullions were considered and **rejected** — a 45° brace cuts straight through the glass pane in the same plane. | Plywood shear panels on the bathroom walls (door cut out) and the storage wall; with the roof deck as diaphragm this is the conventional timber answer. Y-shear is taken by the sheathed end wall and the Y-partitions. |
| 7 | Box-2 window is a pair of panes in the photo. | Split by a 50 mm mullion stud, two glass panels. |
| 8 | Proportions: box/ground ratio ≈ 0.58 in both; four glass bays; boxes flush with the rear edge; stilts — already matching. The 0.57 m roof band is heavier than the real (steel-framed) unit's thin edge. | Kept: 150 × 300 ring beam is the honest timber answer to the 2.875 m glass bays; a thinner band would need steel. |

Not done (scope): exterior ladder, louvred fins, walk bridge, gutters, sliding
door hardware, the box-1 side window (it would face the 0.5 m gap between the
boxes in this layout).

## 5. Structural concept

1. **Stilts + girders + joist platform.** Ten 150 mm stilts at 2.5 m centres
   in two rows (y = 0.6 / 4.6) under two doubled 50 × 250 girders running the
   full length; 50 × 200 joists @ 600 span the 5.2 m width across them
   (4.0 m span + 0.6 m cantilevers), header joists close the long edges,
   blocking over the girders, 18 mm subfloor on top (FFL = +1.068).
2. **Ring beam instead of a top plate.** A 150 × 300 beam runs around the
   whole perimeter at z 3.568–3.868. It spans the 2.875 m glass bays between
   150 × 150 mullion posts and collects the roof joists *and* the box walls.
   The box side walls fall 0.25–0.35 m from a post (x = 0.5/11.0 near the
   corners, 5.5/6.0 beside the middle mullion), so the beam is lightly loaded
   at mid-span. Alternative rejected: double 50 × 150 top plate (fine on the
   studded end wall, no capacity over the glazed bays).
3. **Roof / loft floor joists 50 × 250** across the width, bearing on the long
   ring beams with solid blocking between their ends; 600 c/c generally,
   400 c/c under box 1. Built-up trimmers exactly under each box side wall.
   Box 2 is an open light well: the joists inside it stop on a 3-ply header
   under the box front wall; a doubled rim joist on the back ring beam carries
   the box back wall. Box 1 keeps continuous joists (it has a floor) with the
   two-bay ladder hatch.
4. **Loft boxes.** 50 × 100 studs @ 600 with noggins on a sole plate on the
   roof deck, double top plate, 50 × 150 rim on top with two cross bearers →
   three skylight panes (bed photo). Box height 2.05 m above the deck.
   Cladding 18 mm plywood on four sides; side sheets overlap the front/back
   sheets at the corners. Box 2: paired window in the front wall.
5. **Glazing.** 20 mm panels centred in the 150 mm post depth, sitting on the
   sill plate, stopping under the ring beam; four bays per long side, two on
   the far end.
6. **Partitions / shear walls.** 50 × 100 stud walls from the subfloor up to
   the underside of the roof joists: bathroom L (x = 2.45, y = 2.85) with a
   0.85 m door (header at +2.10 m, cripples above), storage wall at x = 3.6,
   fireplace stub at y = 1.6; 18 mm plywood on one face of the bathroom walls
   and the storage wall.

## 6. Core modelling decisions

- **One generic `stud_wall(along, a0, a1, b0, b1, …)`** handles every wall in
  both orientations: sole plate, studs from `positions()` (first and last
  flush, grid in between, a grid stud closer than half a spacing to the end
  is dropped), double top plate, noggins between the actual vertical members,
  and openings (jack + king studs, 150 mm header, cripples; optional sill and
  sill cripples for windows). Openings are framed *after* the regular studs
  are filtered out of the opening zone, so no stud ever lands inside a
  header. Noggins are generated from the sorted list of placed verticals, so
  they never cross an opening.
- **Plywood as real sheets**, not one slab per surface: `tile_sheets` lays
  1.22 × 2.44 sheets with half-sheet stagger and clips the last sheet of each
  row; decks with holes (hatch, light well) are given as a list of rectangles
  that leave the hole out. Walls use upright sheets; `clad_x` splits a wall
  around an opening into left / right / below / above pieces (zero-height
  pieces skipped, so a door hole reaching the floor works).
- **Corner rule for overlaps**: long members run full length (S/N sill, ring
  beam, headers), cross members run *between* them (W/E sill, ring beam). The
  same rule is used for box plates (side walls full depth, front/back between)
  and for the cladding (end-wall sheet covers the band ends). Blocking is
  derived from the list of placed joists (`roof_joists`, `floor_joists`), not
  from the grid, so it always fits the real bays including built-up members.
- **Every member is a box** → the SAT overlap check is exact; the two clashes
  it reported in v03 (joist through the hatch, stub wall into the new shear
  panel) were both real and fixed in v04.

## 7. Detailed geometry (key numbers, v04)

| item | value |
|---|---|
| stilts | 0.15 × 0.15, z 0–0.60, x = 0.75 + 2.5k, y = 0.6 / 4.6 |
| girders | 0.10 × 0.25, z 0.60–0.85; blocking 50 × 200 over each girder |
| floor joists | 50 × 200 @ 600, z 0.85–1.05; subfloor 18 mm → FFL 1.068 |
| sill plates | 50 × 150 all round, z 1.068–1.118 |
| studs / posts | z 1.118–3.568 (2.45 m); end wall 50 × 150 @ 600 + mid-height noggins |
| mullions | 150 × 150 at x = 2.875, 5.75, 8.625 (both sides) and y = 2.6 (far end) |
| ring beam | 150 × 300, z 3.568–3.868 |
| roof joists | 50 × 250, z 3.868–4.118; 600 c/c, 400 c/c in x 0.6–5.4; rim blocking y 0–0.05 and 5.15–5.2 |
| trimmers | box 1: 2-ply at x 0.50–0.60 and 5.40–5.50; box 2: 3-ply at 5.95–6.10 and 10.90–11.05 |
| light-well header | 3-ply 50 × 250, x 6.1–10.9, y 2.70–2.85; rim N 2-ply y 5.10–5.20 |
| hatch | x 3.025–3.775, y 3.40–4.60; headers 50 × 250; tail joists at x = 3.4 |
| roof deck | 18 mm → loft floor 4.136 |
| boxes | y 2.70–5.20; x 0.5–5.5 and 6.0–11.0; studs 50 × 100 z 4.186–5.936; plates to 6.036; rim 50 × 150 to 6.186 |
| skylight glass | 20 mm, 40 mm below rim top, three panes per box |
| box-2 window | x 9.05–10.45, z 5.186–5.786, 50 mm centre mullion |
| glass | 20 mm, z 1.118–3.568, centred in the post |
| sheathing | 18 mm: end wall (z 0.6–4.136), floor band (0.6–1.068), roof band (3.568–4.136), box walls (4.136–6.186) |
| shear panels | 18 mm on bathroom X wall (y 2.95–2.968, door cut), bathroom Y wall (x 2.55–2.568), storage wall (x 3.70–3.718); fireplace stub starts at x 3.718 |

## 8. Verification

- Visual: 12 (v01–v02) / 15 (v03–v04) fixed views per version, including
  frame-only, plan and close-ups of every revised detail; outlines on so sheet
  joints and plate layers read.
- Numeric: SAT box-box overlap check on all member pairs (tolerance 1 mm) —
  v01 391/0, v02 458/0, v03 567/6 (see §9), v04 555/0.
- Not verified: bearing/continuity (e.g. that each stud actually has a plate
  under it) is by construction only — the v02 missing-rim defect (§4 #1) was
  found by reasoning through load paths, not by the overlap test, which only
  sees penetrations, not voids. Structural sizing is by rule of thumb.

## 9. Iterations

| v | change | result |
|---|--------|--------|
| 01 | full model: stilts, joist floor, ring beam on mullions, solid end wall, glass, partitions, roof joists with trimmers/header/hatch, two boxes with three-pane skylights, cladding bands | 391 elements, 0 overlaps; massing matches photos; missing box-2 window and blocking |
| 02 | generic opening framing (door/window with sill), box-2 front window with glass and cut cladding, noggins in all stud walls | 458 elements, 0 overlaps |
| 03 | review round: rim joist under box-2 back wall, 3-ply header + trimmers, 400 c/c under box 1, blocking over ring beams and girders, shear panels, paired window | 567 elements, **6 overlaps**: mixed 600/400 grid put a joist through the hatch (2 × 250 mm), fireplace stub ran into the new storage shear panel (4 × 18 mm) |
| 04 | box-1 zone uses the 400 grid only; hatch widened to two bays with tail joists; stub wall starts after the panel | 555 elements, 0 overlaps — final |

## 10. Scope and known simplifications

Round stilts modelled square; sliding doors, louvred fins on the bathroom end,
exterior ladder, walk bridge, gutters, roof membrane, interior linings,
ceiling panels and all furniture omitted (furniture excluded by the brief).
The 150 × 300 ring beam makes the roof band ≈ 0.57 m deep, visibly heavier
than the real unit's thin steel edge — accepted as the honest timber answer
to the 2.875 m glass bays. Hatch trimming joists and headers are single
members (0.75 m opening). No hold-downs, straps or hangers are modelled —
the tail joists and light-well joists would need hangers at the headers.
