# Experiment 06 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-23, two rounds: v01–v04 first build, v05–v07 comparison
against the reference images and building-performance review). Claude Code transcripts redact the model's thinking, so
the reasoning, rejected alternatives and key numbers are written out here.

## 0. About this document

Same structure as `experiments/13_.../Fable/experiment_13_fable_design_rationale.md`
(§1 run/outputs, §2 inputs, §3 reference code, §4 what had to change, §5 core
decisions, §6 detailed geometry, §7 verification, §8 iterations, §9 scope),
plus §2b "Comparison round" for the second pass.

## 1. How to run / outputs

Every iteration `experiment_06_fable_vNN.py` was executed in background Blender
4.3 by `render_fable.py` (Workbench, object colour per collection, cavity
shading and object outlines on so coplanar boards stay distinguishable),
producing 18 (19 from v05) `*_blender_view_NN.png`, a `.blend`, and a separating-axis
overlap report over every pair of members. Run from this folder:

```
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render_fable.py -- experiment_06_fable_v07.py ../input <abs_out_prefix> [01,05,...]
```

Views: 01/02 orbit SW/NE, 03 south elevation, 04 west gable (door), 05 roof
plan, 06/07 frame only, 08 portico elevation (walls hidden), 09 tray-rib plan
(decks hidden), 10 platform + portico + ridge, 11 from below, 12 door gable
close-up, 13 portico head / ridge splice, 14 eave-rail corner, 15 roof off
(lining visible), 16 portico lattice, 17 joists/bearers, 18 shuttered window, 19 lattice ridge girder (v05+).

Collections: `Foundation`, `Structure/{Floor_Framing, Portico, Ridge_Beams,
Gable_Panels, Wall_Posts, Eave_Rails}`, `Floors/Floor_Boards`,
`Facade/{Cladding, Interior_Lining, Openings}`, `Roof/{Tray_Ribs, Tray_Decks,
Covering}`, `Ceiling`, `Stairs`. Final model: v07, 1155 members.

The `ChatGPT 5.1/` folder was **not** opened (user constraint: the two runs
must be independent); only `input/` was used.

## 2. Reading the inputs

`01-042-pavillon-6x6-05-2_crop.jpg` is the MONTAGE page of Prouvé's 6×6
demountable house (1944). Its six captions became the build order and the
structural hierarchy of the script:

1. *"Sur la dalle de béton ou sur le plancher métallique, on dresse le
   portique"* → platform first, then a single central A-frame (*portique
   axial*). Timber version: footings + bearers + joists + boards instead of a
   slab / steel floor.
2. *"Les poutres faîtières auxquelles sont fixés les pignons étant brochées sur
   les gousses des portiques, on lève un côté…"* → two ridge beams, each pinned
   to gussets on the portico head and carrying a **gable panel** at its far end.
   The drawing shows the gable as a narrow full-height panel (≈ 1 m) under the
   ridge, with the door in it — so the gable is a stiff panel, not a whole
   triangular end wall.
3. *"…puis l'autre, que l'on soutient par des panneaux. Les faîtières sont alors
   boulonnées."* → the two ridge halves are bolted together over the portico
   (modelled as a butt joint at x = 3 with 18 mm ply splice plates both faces).
4. *"Entre les extrémités des pignons s'inscrivent les rives supérieures et les
   chéneaux qui les raidissent"* → eave rails span between the gable ends along
   the long sides only. (The end walls therefore have no rail; their tops follow
   the roof.)
5. *"…les bacs de toiture qui, agrafés les uns aux autres et sur les faîtières
   sont boulonnés aux rives. Ils règlent toute la construction."* → roof trays
   span ridge → rail, side by side, and square up the whole frame.
6. Ceilings, interchangeable facade panels, partitions, equipment last.

`mljeanprouve01des-copy_0_0.png` (four photos of the reassembled unit): the
portico legs are open-web **lattice** girders in the same vertical plane as the
ridge beam (bottom-left photo: the beam lies over the A, legs spreading along
the beam) → legs spread along X, the ridge axis. Facade = 1 m modules with
horizontal board cladding, slim vertical dividers, shuttered windows, white
interior lining; deep eave beams cantilevering well past the walls; trays
overhang on all sides. The floor edge shows as a dark band below the walls.

Deliberate deviations from the source: steel → timber throughout (the task is
a timber-frame translation, as in the original experiment prompt); the
perforated steel ridge girder became a solid beam in v01–v04 and a timber lattice from v05; the A-frame head is a
plain timber block rather than a cast gusset; shutters are flat leaves.

## 2b. Comparison round (v05–v07): model vs. reference, and as a building

There is no `references/` folder in the repo, so the two input images were the
reference. Differences found by putting v04 view 01/12 next to the photos:

| # | reference | v04 | change (v05) |
|---|-----------|-----|--------------|
| 1 | walls stand *inside* the platform; a strip of floor runs round the facade | walls flush with the platform edge | platform 6.8 × 6.8 (`DECK = 0.40` margin), walls stay on the 6 × 6; footings/bearers/joists/boards/steps follow `P0..P1` |
| 2 | ridge girder is an open-web lattice (photo) / perforated plate girder (drawing) | solid 100 × 400 beam | lattice girder: 100 × 60 chords, 45 × 100 zigzag web (0.35 step, 0.10 node gap), 45 mm end posts; top chord keeps the roof-plane peak |
| 3 | roof and eave beams cantilever ≈ 1 m past the gables, less at the eaves | 0.6 m all round | `OVH_G = 1.0` (gables; 0.9 from v07 so the roof length is a whole number of trays), `OVH = 0.8` (eaves, covers the deck margin) |
| 4 | slim vertical dividers between 1 m panels | 100 mm post faces | intermediate posts 60 × 100 (`POST_W`), corner posts stay 100 × 100 |
| 5 | tall windows with full-height shutters | 700 × 1100 | 700 × 1300, sill 0.85, shutters follow |

Reviewed independently of the reference ("does it work as a building?"):

- **Portico feet** stood bare on the floor boards → 40 mm sole plates 600 long
  under each lattice leg (bolting surface for thrust and uplift), chords
  clipped at `FFL + SOLE_T`.
- **Lattice ridge through the gable wall** (found in v05 view 19/12 reasoning):
  an open web crossing the end wall would leave holes in the facade → a solid
  web block between the chords over the wall thickness (x 0…0.1 / 5.9…6.0),
  the web runs in two segments either side with their own end posts (v06).
- **Deck margin + wider overhang** keep rain off the facade base and give the
  door a landing; steps moved outside the deck edge.
- Considered and not done: wall diagonal bracing (Prouvé's system braces
  through the portico, gable shear panels and tray diaphragm — adding braces
  would misrepresent the system); gutters (*chéneaux*) — would need a
  non-convex profile; door on the long side (the drawing puts it in the gable).

## 3. Reading the reference code

`experiment_04_fable_v02.py` supplied the toolkit: nested `get_collection`,
`box()` from corner coordinates, `prism()` (convex polygon extruded along
u × v), `prism_x` (y‑z profile along X), `clip()` half-plane clipping, `strip()`
rectangles around a segment, `positions()` member spacing. Added here:
`prism_y` (x‑z profile along Y, for the portico which lives in the plane
y = 3), `split_rows()` so wall infill rows are cut at hole tops/bottoms, and
`panel_end` / `panel_side` infill generators (rows × columns, holes skipped,
top clipped by the roof plane). `craftbot_lib.place_element` is still the
primitive behind every axis-aligned box.

## 4. Why the first geometry had to change

- **Gable head rail through the skin (v01, caught on paper).** The head rail
  between the two gable posts was first drawn full wall depth (x 0…0.1), which
  the 22 mm boards and 9 mm lining would pass through. Moved inside the panel
  depth (x 0.022…0.091). The same rule was later used for the end-wall head
  plates.
- **Ridge/rail corners piercing the trays (caught on paper).** A flat-topped
  ridge beam with the roof plane tangent at its centre would have its edges
  8 mm above the tray underside; a flat eave rail leaves a 13 mm wedge gap at
  its outer edge. Both tops are bevelled to the roof plane (ridge beam = 5-gon
  profile with a peak; rail = 4-gon with a sloped top), and the roof plane is
  *defined* through the rail's inner top edge and the ridge beam's edge, so the
  trays bear flat on both. Alternative rejected: raise the plane to clear the
  corners — leaves the trays bearing on an edge only.
- **Portico legs clipped away (v01 render).** The half-plane that keeps each
  leg on its own side of the axis had the sign inverted (`(-side, 0)` instead
  of `(side, 0)`), so both legs were clipped to almost nothing. Only the head
  block was visible in view 06. Fixed in v02.
- **Lattice diagonals overlapping each other (v02 overlap check, 10 pairs at
  23.6 mm).** A 45 mm diagonal meeting the chord at ≈ 32° leaves an 85 mm
  footprint on the chord face; consecutive diagonals were offset only 40 mm at
  the node. Offset set to 100 mm (each diagonal bolted to the chord separately;
  the zigzag is open at the nodes). Alternative rejected: mitre consecutive
  diagonals against each other — more code for a detail the SAT check already
  accepts as face contact.
- **End walls without a head member (v03 render, view 14).** Posts with
  sloped tops carried the trays directly. Added a sloped 80 mm head plate
  (inside the panel depth) from the rail inner face to the ridge beam on both
  slopes, posts shortened by 80 mm.

## 5. Core modelling decisions

1. **Prouvé's hierarchy, not a stud-wall house.** The structure is
   portico → ridge beams → gable panels → eave rails → trays; the facade posts
   are only the module dividers of interchangeable panels. This is why there is
   no bottom plate, no diagonal wall bracing and no end-wall rail: stability
   comes from the A-frame (longitudinal), the gable shear panels (transverse)
   and the tray diaphragm, exactly as caption 5 says.
2. **Portico legs spread along the ridge axis** (plane y = 3). Supported by the
   photo and by statics: the A-frame then braces the ridge line and the two
   ridge halves can be pinned to its head from either side.
3. **Legs as lattice girders** (two 60 × 100 chords 300 mm apart + 45 × 100
   diagonals) built with `strip` + `clip`: chords are cut horizontally at the
   floor, horizontally at the head underside and vertically at the axis, so
   the two inner chords meet face to face under the head and no rotated box is
   needed anywhere.
4. **Roof plane as a single function `z_u(y)`**, mirrored about y = 3, used by
   the trays, the rail and ridge bevels, the ceiling, the end-wall post tops,
   head plates, cladding and lining (`below_roof` clipping). One definition →
   no coplanarity errors between the members that meet the roof.
5. **Wall infill as row × column pieces with holes**, the same generator for
   cladding boards (100 mm pitch, 90 mm face) and ply lining (one row), for
   side walls (boxes) and end walls (prisms clipped by the roof). Openings are
   holes in the generator; frames, glass, leaves and shutters are separate
   boxes inside the hole.

## 6. Detailed geometry (key numbers)

- Platform 6.8 × 6.8 (walls on the 6 × 6 inside it): 20 footings 400² on a
  4 × 5 grid, bearers 90 × 200 along X at y = −0.35 / 1.5 / 3.0 / 4.5 / 6.35
  (centre line under the portico feet), joists 47 × 145 @ 600 along Y, rim
  joists, 22 × 120 boards along X. FFL = 0.417. (v01–v04: 6 × 6 platform.)
- Posts: corners 100 × 100, intermediates 60 × 100 on the 1 m module; side
  posts FFL → FFL + 2.30; end posts up to `z_u − 0.08` under the head plates.
- Eave rail 80 × 250, y 0.01…0.09, x −0.9…6.9, top bevelled; rail top (inner
  edge) FFL + 2.55.
- Ridge girder 100 wide × 400 deep lattice: bottom chord 100 × 60 box, top
  chord 100 × 60 prism with the roof-plane peak, web 45 × 100 zigzag (0.35 m
  step, 0.10 m node gap; footprint 0.045/sin 39° = 72 mm < 100 mm gap), 45 mm
  end posts, solid web block through the gable wall; underside FFL + 2.65,
  edges FFL + 3.05; halves x −0.9…3 and 3…6.9; splice plates 18 × 300 × 1000
  both faces (z ≤ FFL + 2.95 to clear the ceiling ply at y = 2.93).
- Roof slope = 0.5 / 2.86 = 0.175 (≈ 1:5.7), roof 7.8 × 7.6 overall
  (0.9 m past the gables, 0.8 m past the eaves).
- Trays 600 wide, 13 per slope, ribs 45 × 120 at both edges
  (adjacent trays' ribs touch), deck 18 mm, plumb cut at y = −0.8 and at the
  ridge; ridge cap 2 × 250 × 20; fascia 20 × 160 outside the tray ends, barge
  boards along the gable edges.
- Portico: feet at x = 3 ± 1.1 on 600 × 100 × 40 sole plates, leg centreline
  aimed 0.45 above the head underside so the chords' vertical cut lands under
  the 800 mm head block; head 100 × 150 × 800, diagonals every 0.38 + 0.10 m
  along the leg.
- Gable panels: posts at y = 2.45…2.55 and 3.45…3.55 up to the ridge underside,
  head rail 100 × 100 between them (inside the panel depth); west = door
  800 × 2050 (45 mm frame, 40 mm leaf), east = window.
- Windows 700 × 1300, sill FFL + 0.85, 45 mm frame between cladding and lining,
  6 mm glass, two 22 mm shutters open 90° (boxes perpendicular to the wall);
  side-wall bays 1 & 4 (south), 2 & 5 (north).
- Ceiling: 9 mm ply under the tray ribs from the rail inner face to the ridge
  beam face, 1 m panels between the end walls.
- Steps: two blocks outside the deck edge at the west door (FFL/2 risers).

## 7. Verification

- Numeric: SAT overlap check (face normals + edge cross products) on all
  ~1150 convex members, threshold 1 mm. v01 0 pairs (but legs missing), v02 10
  pairs (diagonals), v03–v07 0 pairs. Face-to-face contact is accepted by
  design (it is how every joint in the model is expressed).
- Visual: 18/19 views per version including frame-only, hidden-deck plan,
  from-below and five close-ups; outlines on. v05 view 19 confirmed the
  lattice; the gable-wall hole problem was found by reasoning about that view,
  not by the check (a see-through web is not an overlap). The v06 roof gap was
found in the roof plan (view 05): `int(round(8.0 / 0.6))` silently dropped a
third of a tray - missing coverage is another failure class the SAT check is
blind to, so plan views of every layer stay in the view list. The v01 render immediately
  showed the missing portico (a case the overlap check cannot catch — absence
  of geometry).
- Not verified: structural sizing (members are plausible, not calculated);
  bolting/connection hardware; that the trays and ceiling are *supported* at
  every edge (they rest on rail, ridge, head plates by construction).

## 8. Iterations

| v | change | result |
|---|--------|--------|
| 01 | full model from the montage sequence | 1095 members, 0 overlaps, but portico legs clipped away by a sign error |
| 02 | leg clip sign fixed | legs appear; 10 diagonal/diagonal overlaps (23.6 mm) at lattice nodes |
| 03 | node offset 40 → 100 mm | 0 overlaps; end walls lack a head member |
| 04 | sloped end-wall head plates, posts shortened; decks in own collection, view 09 shows ribs | 1113 members, 0 overlaps, end of round 1 |
| 05 | comparison round: 0.4 m deck margin, lattice ridge girder, 1.0/0.8 m overhangs, 60 mm dividers, 1.3 m windows, leg sole plates, view 19 | 1151 members, 0 overlaps; open web would pierce the gable wall |
| 06 | solid web block where the girder crosses the gable wall, web in two segments with end posts | 1157 members, 0 overlaps; roof plan shows 8.0 m / 0.6 m = 13.3 trays → 0.2 m uncovered at the east gable |
| 07 | gable overhang 1.0 → 0.9 m so the roof is exactly 13 trays | 1155 members, 0 overlaps, final |

## 9. Scope and known simplifications

No bottom plates under the wall panels (they bolt to the floor in Prouvé's
system); gutters (*chéneaux*) not modelled; ridge
girder solid instead of perforated; roof trays without bottom skin or
insulation; partitions and equipment (caption 6) omitted; shutters shown open
and flat; no door hardware; interior lining omitted on the side-wall area
above the posts (the rail is exposed inside, as in the photos). Stairs are two
solid blocks. Bearers end flush with the platform edge (outer footings 0.3 m
in from it). The lattice girder's web is not modelled inside the 18 mm splice
plates at the portico (plates simply cover it).
