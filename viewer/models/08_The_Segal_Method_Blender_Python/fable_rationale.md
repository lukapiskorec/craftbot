# Experiment 08 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-23, one session, two rounds: v01–v04 first build, v05–v06 comparison against the cover photo and structural review). Claude Code transcripts redact the
model's thinking, so the reasoning, rejected alternatives and key numbers are
written out here.

## 0. About this document

Same structure as `experiments/13_.../Fable/experiment_13_fable_design_rationale.md`
(§1 run/outputs, §2 inputs, §3 reference code, §4 what had to change, §5 core
decisions, §6 detailed geometry, §7 verification, §8 iterations, §9 scope), plus §2b (comparison round) and §5b (independent structural improvements).

## 1. How to run / outputs

Every iteration `experiment_08_fable_vNN.py` was executed in background Blender
4.3 by `render_fable.py` (Workbench, object colour per collection, cavity
shading and object outlines on so coplanar boards stay distinguishable),
producing 19 `*_blender_view_NN.png`, a `.blend`, and a separating-axis
overlap report over every pair of members. Run from this folder:

```
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render_fable.py -- experiment_08_fable_v06.py ../input <abs_out_prefix> [01,05,...]
```

Views: 01 SW orbit, 02 SE orbit (patio), 03 NE orbit, 04 south elevation,
05 east elevation (patio frame in front), 06 west gable, 07 roof plan, 08 frame
only, 09 frame + floors + stair, 10 roof framing plan (deck hidden), 11 floor
framing plan, 12 undercroft from below (foundation hidden), 13 section (south
wall + roof hidden), 14 skylights, 15 frame joint at the south post of frame 2
(double beams sandwiching the post), 16 stair, 17 patio steps, 18 glazed bay
and cladding, 19 frame east elevation (portal).

Collections: `Foundation` (pads, slabs, gravel), `Structure/{Posts, Beams,
Floor_Joists, Roof_Joists, Bracing}`, `Floors/{Floor_Boards, Patio_Deck}`,
`Facade/<South|North|West|East>/<wall>_{Cladding_Ext, Core, Cladding_Int,
Battens, Windows}`, `Roof/{Deck, Skylights, Fascia}`, `Stairs`, `Balustrade`.
Final model: v06, 2537 members, 0 penetrating pairs.

The `ChatGPT 5.1/` folder was **not** opened (user constraint: the two runs
must be independent); only `input/` and `references/` were used.

## 2. Reading the inputs

`segal_method_extracted.md` (AJ special issue "The Segal Method", J. Broome,
1986) gave the rules; the two reference screenshots (fig. 18 general
arrangement cutaway; the cover photo of a two-storey house) gave the image:
exposed dark post-and-beam frame, white infill panels with batten joints,
raised deck, big overhang. How the text became numbers:

| Manual | Model |
|---|---|
| Tartan grid 600 panel + 50 structural band (§2) | module `M = 0.65`, bands `[k·0.65, k·0.65 + 0.05]`; every joist, batten, mullion and balustrade post sits on a band |
| Columns ≤ 6 modules apart, bay ≤ 3.85 m (§4) | frames 3.9 m apart = 3.85 m clear between 50 mm posts; post lines across at 0 / 3.9 / 7.8 |
| ~200 structural depth, beams and joists same depth, joists on bearers on the side of beams so undersides align (§11, fig. 50/51) | beams and joists 50 × 200; 50 × 50 bearer on each beam face; joist ends notched over the bearer (body + tongue pieces) |
| Centre frames double beams, edge frames single (fig. 49) | `beam_xs()`: inner frames a beam on each post face, end frames one beam inside — except at roof level (see §5.3) |
| Rigid bolted cross-frames + floor-level tie beam = portal (fig. 44); other direction braced; one braced bay per floor near centre; knee/cross braces below floor for single storey (fig. 43, 45) | frames rigid along Y; undercroft X-braces (two lapped layers) on both eave lines in bays 2–3; one diagonal per storey in the north-east wall cavity (bay N3, core omitted) |
| Pads ~600 sq, ~900 deep, paving-slab cap, gravel oversite, no slab, posts on lead, unanchored (§10, fig. 33) | 600 × 600 × 800 concrete base + 50 slab per post, 40 mm gravel field tiled around the pads; posts start at z = 0.05 |
| ~12 bases for a two-storey house | 15 (the extra frame is the patio) |
| Roof immediately after frame; flat roof preferred but pitched roofs built (cover); generous overhang (§12) | user brief asked for slanted roof surfaces with skylights → 15° pitched roof, ridge over the middle post line, 0.6 m overhang on all sides |
| Floors: t&g softwood boarding on joists (§13) | 22 × 150 boards along Y over joists and beams, cut around the middle posts and the void |
| External walls: non-structural sandwich clamped into the frame with bolted battens; 600 panels; sole plate at bottom, joist at top; blocks set the grid (§14, fig. 62–64) | 12 ply / 50 core / 12 ply per 600 slot, 50 × 25 battens outside and inside on every band, 50 × 50 sole plate in the band on the floor framing, panels stop at the joist/roof slab underside; exterior ply also covers the floor zones |
| Windows site-made: panes ≤ ~1 m² sliding in a timber lining; storey-height glazing possible (§15, fig. 67–69) | lining 50 × 74 (ply face to ply face), mullions on the bands, transoms so no pane exceeds 0.6 × 1.25 m; full-height glazed bays S1-G, S2-G, S2-U, E1-G |
| Stairs: treads on hangers / posts / cantilevers, members lap at right angles; keruing outside (§18, fig. 76–78) | internal stair: two sloped carriages + cleats + lapped treads; patio steps: treads on posts (fig. 77) |
| Veranda, balustrade, porch (fig. 79–81) | covered patio bay under the main roof, balustrades, steps |

Deliberate deviations from the manual:

* **Pitched roof with a plywood deck** instead of the loose woodwool / felt /
  shingle flat roof — the brief asked for slanted surfaces and skylights. The
  Segal "tablecloth" membrane and ballast are not modelled (they would be a
  single thin layer hiding the deck seams).
* **Plywood skins** instead of Glasal outside / plasterboard inside (brief).
* **Cut panels next to the middle posts of the gable walls.** The manual says
  columns must never stand longways within the grid. In a two-bay-deep house
  the end frames' middle post (150 deep along Y, in the gable wall line)
  cannot avoid it: it eats 100 mm out of the 3.85 m clear, so one 550 mm panel
  is needed on each side of it (`slots()` handles this automatically). The
  alternative — turning the end-frame middle posts 50 × 150 the other way —
  would make the end frames non-rigid in Y; rejected.
* No ceilings, partitions, services, membrane, lead pads or bolts.

## 2b. Comparison round: the cover photo vs v04

The cover photo (PDF p. 1, a two-storey Segal house) was read directly from the
PDF. Differences found and what was changed (v05/v06):

| Photo | v04 | Change |
|---|---|---|
| Storey-height glazing wraps the **corner** of the tall wing over two floors (double-height living room behind it) | void in the middle bay, solid gable | void moved to the south-west corner bay; S1 and W1 glazed on both storeys, stair and the four south skylights moved with it |
| White panels ~600 x 1200 with a dark **horizontal rail at sill height**; verticals on every band | full-storey panels, verticals only | 50 x 25 exterior rail on every solid slot at sole + 0.9 m; exterior ply split at the rail; all window sills set to that line (1.9 / 4.5) |
| **Dark band at floor level** (exposed beam / joist edge) | white ply strip over the floor zone | end frames double-beamed (see 5b) so the beam is the floor edge on the gables; eave-wall strip stained dark (moved to the batten collection) |
| Upper gable walls **tile-hung** (dark small tiles) | ply panels | staggered 300 x 300 tile courses on W2-U, E1-U, E2-U, last course following the roof |
| Steeper roof, beam ends exposed under the verge | 15 deg, 25 mm verge board | 20 deg, 50 mm verge beam (5b) |
| Light glazed **canopy** over the deck door | none | 6 mm sheet on two raking 50 x 100 arms with struts over the south door |
| Transoms level across the elevation | transoms at each column's mid-height (stepped under the sloping head) | transoms on fixed levels sill rail + 1.2 k, aligned with window sills and heads; top pane follows the slope |
| Spiral external stair, slender steel balustrade | straight steps on posts, timber balustrade | not changed (Segal's own "treads on posts", fig. 77, kept as the more self-buildable option) |
| L-shaped massing (tall wing + lower wing) | single rectangle + patio bay | not changed: the brief asked for one house with a covered patio; the patio bay under the main roof is the model's version of the photo's deck corner |

## 3. Reading the reference code

`craftbot_lib.place_element` (scaled 2 × 2 × 2 cube) is used for every
axis-aligned member via `box(x0, x1, y0, y1, z0, z1)`. Sloped members (roof
beams, roof joists, deck sheets, kerbs, braces, stair carriages, wall pieces
with sloped tops) are convex prisms from a 2D profile — the helper set from
experiments 03–06 (`prism`, `prism_x`, `prism_y`, `clip`, `strip`). Two
additions this run:

* `prism()` now re-orients the profile counter-clockwise about the extrusion
  normal: `prism_y` swaps (x, z) → (z, x), which reversed the winding and made
  every south/north wall piece render with inverted normals (dark) in v02/v03.
* `tile()` — a generic sheet tiler in a 2D plane with staggered rows and
  rectangular holes, used for the roof deck (around skylight kerbs) and for the
  gravel oversite (around the pads).

## 4. What had to change during the run

* **v01 → v02 (314 → 0 penetrations):** the straddle test in `roof_profile`
  used `y0 < Y_RIDGE - 1e-6 < y1`, which is also true for pieces that merely
  *end* at the ridge (`y1 == Y_RIDGE`). Every rafter beam and every ridge-row
  deck sheet got a flat bottom at the height of its *low* end — the rafter
  beams were 0.3 m too deep and cut through walls and posts. Fixed by dropping
  the pentagon profile altogether: a piece straddling the ridge is split plumb
  at the ridge into two parallelograms (the ridge joist becomes a pair). Also
  in v02: glazed bays and doors start on the floor boards (the sill at
  z = 1.00 intersected the boards, 12 mm), interior ply of the eave walls
  trimmed 12 mm at the house corners where it met the gable walls' interior
  ply (Segal's "offset at corners" rule, fig. 73), balustrade mid rails
  segmented between posts, north-slope skylight holes mapped from the eave
  instead of the ridge, upper-floor bearers only where joists exist (the void
  bay bearer ran through the stair carriages), first stair baluster clamped to
  floor level.
* **v02 → v03:** `get_collection` reused collections by bare name, so all four
  walls shared one `Cladding_Ext` collection linked under four parents; hiding
  `Facade/South` did nothing. Child collections are now wall-prefixed. Gravel
  oversite added so the 800 mm deep pads read as buried.
* **v03 → v04:** door leaf full height (doors skip the transom rule), ridge
  capping boards, glass coloured separately from linings/kerbs, stair view
  angle.

## 5. Core modelling decisions

### 5.1 Geometry from grid functions, not from coordinates

Everything derives from `M`, `BAND`, `FRAMES_X`, `POST_Y` and the roof
functions `zu(y)` (slab underside), `zj(y) = zu + 0.2071` (joist top / deck
underside) and `zd(y) = zj + 0.0186` (deck top). `bands(a0, a1)` returns the
tartan bands strictly inside a clear range and `slots()` the panels between
them, so eave bays (6 × 600 + 5 × 50 = 3.85) and gable halves (3.80 → one
550 panel) are generated by the same code. All roof members are plumb-cut
parallelograms in the (y, z) plane extruded along X (`roof_piece`), so joists,
beams, trimmers, kerbs, glass and deck sheets share one representation and
their horizontal footprints stay exactly on the 50 mm bands.

### 5.2 Walls as (along, z) profiles extruded across

`Wall` objects know their band coordinate `c`, which side is outside, and
whether they are gable walls. Every layer is placed by offsets from the core's
exterior face (`across()`), so the same `wall_bay()` builds all 20 bay-storeys.
Gable pieces follow `zu(a)` along the wall; eave pieces are cut flat at
`min(zu(c0), zu(c1))` so they never rise into the roof slab that slopes across
their thickness. Holes are given in slot indices, so windows always occupy
whole 600 panels and the bands inside a hole become mullions.

### 5.3 Frame rules and the gable overhang

End frames carry single beams at floor level (manual) but double beams at roof
level: the outer beam face is what the 600 mm gable outrigger joists bear on
(bearer + notched end, like every other joist). Rejected: running the bay
joists continuously past the end frame (they would cut the beam), or hanging
outriggers from the posts (only three bearing points).

### 5.4 Posts partly outside the grid

Posts are 50 mm in the band direction and 150 mm deep: south/north posts
project 100 mm outside the wall face (manual: "placed outside the building
where possible"), middle posts straddle their band (3.85–4.00). Floor beams run
from post outer face to post outer face (−0.10 … 7.95) and therefore pass
through the wall cladding zone; the exterior ply floor-zone strip is trimmed to
the beam faces so the beam ends read outside, as in the cover photo.

### 5.5 Skylights between joists

A skylight is the 600 mm clear between two joists × 1200 mm between two
sloped trimmers; the kerb (50 × 150) sits on the joist/trimmer tops and the
deck is tiled around the kerb's outer outline; a 6 mm glass lid covers the
kerb. Four over the double-height void (south slope), two over the upper floor
of bay 3 (north slope).

### 5b. Independent structural improvements (v05)

* **Double beams at every frame.** Single inside beams on the end frames
  loaded the end posts eccentrically and left the gable outriggers with no
  floor-level bearing; now every post is sandwiched symmetrically and the
  floor edge of the gables is a proper beam. The west-wall rim pieces stay as
  blocking between the beam pair.
* **Verge beam** 50 x slab depth at both gables ties the 13 outrigger ends
  per slope into a ladder (before: 13 independent 600 mm cantilevers on a
  bolted tongue each).
* **Canopy arms on the posts and bands**, struts clipped to the arm underside
  - loads go to the frame, not the panels.
* Considered and rejected: a ridge purlin (the middle posts already carry
  the ridge, and rafter beams meet at the post), roof-plane diagonal bracing
  (the 18 mm deck is a diaphragm), knee braces under the patio tie beam
  (the tie stays - it is the portal tie of the patio frame).

## 6. Detailed geometry (key numbers)

* Plan: frames x = 0, 3.9, 7.8, 11.7 (house east wall), 14.3 (patio frame);
  post lines y = 0, 3.9, 7.8; wall cores y ∈ [0, 0.05] and [7.80, 7.85];
  13 joist bands y = 0.65k.
* Levels: pad slab 0–0.05; GF framing 0.80–1.00, FFL 1.022; UF framing
  3.40–3.60, FFL 3.622; storey clear 2.378; roof slab underside 6.00 at y = 0,
  ridge underside 7.05 at y = 3.925 (15°, S = 0.268); post tops =
  `min(zu)` over the post's y-range.
* Roof extents: y −0.70 … 8.55, x −0.675 … 14.975; 18 mm deck in 2400 ×
  1200 sheets, rows staggered half a sheet, 3 + 1 partial rows per slope.
* Void (v05+): x 0.075 … 3.825 (beam faces), y 0.05 … 3.90; no UF joists in
  bands 0–5 of bay 1, boards cut around it, balustrades on its north and east
  edges (the other two are the glazed walls).
* Stair: 14 risers × 185.7 mm, going 250, width 0.9 along y 2.95–3.85,
  bottom riser at x = 0.575, landing on the beam face at x = 3.825 (v05+);
  carriages 250 deep strips clipped to the floor plane and the beam face;
  handrail 900 above nosings on 4 balusters bolted to the carriage face.
* Patio: deck 100 × 22 keruing boards with 10 mm gaps over the GF joists of
  bay 3–4; balustrade posts on the bands; 5 risers of 204 mm on posts.
* Braces 50 × 150: undercroft X in y ∈ [−0.20, −0.10] and [7.95, 8.05]
  (two lapped layers so the diagonals do not intersect); wall braces in the
  core band of N3.

## 7. Verification

* Numeric: SAT overlap check over all convex members after every iteration
  (tolerance 1 mm). v01 314 pairs, v02–v04 0, v05 3 (canopy), v06 0. Touching faces
  (sill on boards, kerb on joists, deck on joist tops) report 0 and are
  intended.
* Visual (the SAT check cannot see *missing* geometry): frame-only views 08
  and 19 confirmed all 15 posts, both floor-beam levels, the roof beam pairs,
  joists, outriggers and trimmers; view 10 the roof framing and skylight
  trimmers; view 11 the floor framing and the void; view 12 the undercroft
  (bearers, braces, beam ends); view 13 the double-height space, stair and
  balustrades; 14–18 close-ups of skylights, frame joint, stair, steps,
  glazed bay.
* Not verified: structural adequacy (50 × 200 joists at 650 cc over 3.85 m
  and doubled 50 × 200 beams over 3.9 m are at the manual's limits; the
  manual's fig. 27 calculation was not repeated), weathering details, bolt
  spacing.

## 8. Iterations

| Version | Change | Result |
|---|---|---|
| v01 | full model from the design brief | 1961 members, 314 penetrations, mostly from the `roof_profile` straddle bug; renders not inspected beyond the overlap list |
| v02 | ridge split, glazing on boards, corner trims, balustrade rails, N-slope holes, void bearers | 2045 members, 0 penetrations; renders showed the collection-hiding bug and dark (inverted) wall faces |
| v03 | unique facade collections, gravel oversite, prism winding fix | 2126 members, 0 penetrations; section and interior views usable |
| v04 | door leaf, ridge caps, glass colours, stair view | 2124 members, 0 penetrations; end of round 1 |
| v05 | comparison round: corner void + glazed corner, sill rails, dark floor band, tile-hung gables, 20 deg roof, verge beams, canopy, all frames double-beamed | 2417 members; 3 canopy penetrations (normal sign) fixed in place -> 0; tiles below the rail overwritten by a name collision, transoms stepped |
| v06 | unique tile names, transoms on fixed sill-aligned levels | 2537 members, 0 penetrations; final |

## 9. Scope and known simplifications

* No ceilings, partitions, insulation panels, services, roof membrane /
  ballast, flashing, gutters, bolts, lead pads, window tracks or sliding
  hardware.
* Tiles are flush courses (no lap, no battens behind) - the texture of
  tile-hanging, not its build-up.
* Posts are cut flat at the roof slab underside; real Segal frames would bolt
  the rafter beams over a longer post length.
* The gable-wall 550 panels (§2) are an accepted deviation.
* The patio frame keeps its upper-level tie beam (portal action) although no
  upper floor exists there; it reads as an open pergola beam across the patio.
* Floor boards run continuously over beams (beam tops flush with joist tops);
  no t&g profile, no liftable insulation panels.
