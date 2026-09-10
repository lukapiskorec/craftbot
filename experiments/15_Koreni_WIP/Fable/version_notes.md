# Version notes, experiment 15 (Koreni), Fable run

One entry per rendered version: what changed and why, the counts (members, penetrating pairs, floating), the pair families with their causes, what the Inspector found, which requirements were ticked, what remains. Rationale section 9 is compiled from this file.

## v01 (2026-09-10)

**What it is.** The first rendered version: the script the previous Builder session left unrendered, completed and run. Three terrain strips (skin 0.30 thick on z(x), one convex prism per ground segment, holes around every element that crosses it) and the three variations of concept sections 3 to 5 in one scene, collections `A_Bridge`, `B_Cut`, `C_Steps` with children `A_Terrain`, `A_Footings`, `A_Concrete`, `A_Slabs`, `A_Steel`, `A_Glazing`, `A_Cores`, `A_Stairs`, `A_Roof` (and the same for B and C). The children carry the variation prefix because Blender collection names are global: a bare `Terrain` could exist once, and the frame-only view of one variation must hide that variation's skin only. `Slabs` is a child R-06 does not list; the floor slabs and paving needed a hiding switch of their own for the frame-only views.

**Completed before the render.** Footing runs cut at the kinks of the underside function (the footing under a cut level follows `min(z(x), paving) - 1.2`, and the stepper divided each ground segment evenly, so one step took the whole kink: 0.79 and 0.93 m steps against the 0.6 limit); runs shorter than 0.6 m merged into their neighbour at the lower level; the bridge slab thickness as a parameter (200 on beams) instead of a post-hoc rescale; the B side-wall check set to the concept's 2.75 m ledger limit; the beam-clearance check restricted to the house (no clear-height rule on a terrace).

**Counts.** 1255 members, 245 penetrating pairs in 90 families, 0 floating. 163 script checks, 1 failed (R-45, below).

**Pair families and causes** (one row per cause, not per family):

| Cause | Families, pairs | Fix in v02 |
|---|---|---|
| C storefront heads and mullions are horizontal boxes under the sloped edge beams of the folded roof (8.2 percent) | EdgeBeam x GlzHead/GlzMull/GlzGlass, 76 | head transom, mullion tops and glass follow the beam soffit (sloped prisms) |
| C posts have flat tops under the sloped edge beam | Post x EdgeBeam, 18 (6 mm) | post tops bevelled to the soffit |
| A dogleg flight guards placed inside the 1.2 m tread lanes | DoglegUp/Lo x FlightGuard, 24 | lanes inset by the guard thickness inside the void; guards beside the lanes |
| A well guard runs from the box floor through the floor beam at x = 55 and the landing; that floor beam crosses the stair void | FloorBeam x WellGuard, Landing x WellGuard, FloorBeam x FlightGuard, 3 | void framed with headers, trimmers and tails; well guard bottom on the lower flight and the landing |
| Per-piece strip footings crossing at every wall corner (pavilion front/side/rear, box S/N/W/E, plinth end walls, pier, B end-wall base against the side bases and foundation walls) | 26 families, about 40 | corner rule: x footings run through, y footings between them at the run's level, wall ends over a cross footing stand on it (`trim0/trim1`) |
| C foundation walls at a level edge start inside the step footing, side stems inside the step and ridge footings | StepFtg/RidgeFtg x FndWall/SideStem/SideBase, 10 | same corner rule |
| gravel layer under the slab on ground runs into the foundation walls | FloorGravel x FndWall, 14 | gravel between the walls |
| C closed wall pieces spanning a level edge get a sloping bottom (floor evaluated at both ends of a piece across the step) | ClosedWall x Floor/StepWall/FndWall, 4 | closed walls split at the level edges |
| C step wall tops at the upper slab underside while the post at x = 47 stands on L3; L1's trench continues 1 m past its level into the step wall's return | StepWall x Post, SideStem/SideBase x StepWall, 3 | step wall top at the upper floor, boundary post moved 75 mm uphill, trenches end at the step walls and skip stubs under 1 m |
| B: post lines 11.1 and 15 built twice (high bay and low bar), corbel through the closed wall and the edge beam, pavilion roof built twice, insulation wedge into the end parapet | Post x Post, ClosedWall x RoofBeam, Corbel x ClosedWall/EdgeBeam, PavRoof x PavRoof, RoofIns x Parapet, RoofBeam x LandingGuard, 10 | low bar starts at a first post line beside the step wall; corbel removed; duplicates removed; wedge inset |
| B entry stair passes through the transverse step wall | StepWall x FlightGuard/EntryStair, 2 | opening in the step wall over the flight (headroom 2.1 above the nosing) |
| partitions drawn to the wrong side's inner face (closed wall side taken from segment 1) and to the mullion line inside the edge beam | Core x Part, ClosedWall x Part, ClosedPanel x Part, EdgeBeam x Part, 13 | partition extents derived from the open side at its x; against a core, one half thickness off the core face |
| A terrace 65..71 glazed and closed like the house (house end taken as 71) | ClosedPanel x Balustrade, 6 | `HOUSE_END` = 65 for A; terrace open with the balustrade |
| A box partitions run through the girders; store walls overlap at their corner; guards run inside core 1 | Girder x BoxPart, Core x Core, FlightGuard/LandingGuard x Core, 7 | partition split below and between the girders; store corner; core 1 ends at the guard line |
| C pavilion front wall top evaluated at mid-thickness under the rising R1 soffit | PavFront x PavRoof, 5 (10 mm) | flat top at the low face plus a wedge |

**Inspector (inspection_v01.md).** Confirmed by eye: strips and pavilion placement, the open/closed alternation, R-10, R-14, R-16, R-24, R-30, R-34, R-43, all comparison rules S-01 to S-11 in views 06 to 08. Open: B's stair bay rises to the pavilion roof (+3.65) over x = 11..15.28 (the "high bay", a Builder addition: the concept's landing at +0.15 under a roof underside at +1.03 leaves 0.9 m; the Designer must choose between this and a stair inside the pavilion), against R-40; C stair 2's guard reads on the wall side (view 22 cuts through the flight: Workbench renders back faces, and the treads' far faces at y = 8.4 are coplanar with the guard's near face, which won the draw; the wall's sloping bottom let the guard show from outside in view 26; the guard is on the open side, view 31 of v02); a full-height panel in A's stair hall (the well guard, redesigned); end walls at the house end not legible (they did not exist: added in v02 with close-ups 32 to 35); terrace guards "visible with Glazing hidden" (the collections are correct on inspection of the .blend; the far closed wall seen through the open side at 14 px/m; close-up 35 settles it); a dark patch in B's skin near the pavilion (the cut plane at -1.1 slicing the skin between x = 21 and 27: section behaviour, not geometry); the C plans cut at the wrong levels and a dark square under A's pavilion at the box-level cut (harness: the clip distance is taken along the direction to the focus centre after the framing shift, which lands a shifted plan 1.5 m high; all cut views now carry a focus, which removes the shift); a skin wedge at C's x = 29 corner (the trench end at the segment switch had no return: v02 adds `TrenchEnd` walls).

**Requirements.** None ticked at v01 (first version, 245 pairs). Conflict for the Designer: R-45 asks 3.3 m clear at the downhill end of every level, but R-44's plane R2 (+3.90 at x = 11 to -0.93 at x = 70) over R-41's L3 at -3.90 gives 3.10 m at x = 66 (L1: 3.43, L2: 3.30). Nearest alternatives: end R2 at -0.73 at x = 70 (7.85 percent; +0.20 at x = 66) or lower L3 and the terrace by 0.20 to -4.10 (stair 3 becomes 10 risers of 150 over 2.52 m). Kept as written; the assertion stays failing until decided.

**Proposal for tools/ (after the run).** `render_views.py`: derive the cut plane distance from the camera's own -Z axis instead of the direction to the focus centre, so a fitted (shifted) plan or section lands exactly on the requested plane.

## v02 (2026-09-10)

**What changed and why.** Every v01 family fixed at its cause (table in the v01 entry), plus the geometry the v01 Inspector found absent: glazed end walls at the house end (x = 65 in A, 66 in B and C) with a terrace door pane on a flush threshold; A's terrace 65..71 open (house end 65, `HOUSE_END` separate from the slab and roof ends); A's abutment wall y = 7..9 to the roof and a parapet across the bar roof's uphill edge; A's stair void framed with two headers, two trimmers and tail beams (the IPE 300 at x = 55 crossed the void); the dogleg's lanes 1.2 m inside the void with the guards beside them, the landing split for the one-tread lead, the well guard following the flights; B's low bar from a first post line beside the step wall (the corbel and the doubled posts and beams gone), the stair passing through an opening in the step wall; C's storefront heads, mullions, glass and post tops following the sloped edge beams; C's closed walls split at the level edges and the step walls rising to the upper floor; C's boundary post at x = 47 moved 75 mm uphill onto L2; C's trenches ending at the step walls with an end return where a trench stops at a segment switch; the corner rule for footings throughout (`trim0/trim1`, `run_level`); partitions derived from the open side. Views: every cut view carries a focus (exact plane), ten close-ups appended (29 to 38).

**Counts.** 1294 members, 9 penetrating pairs in 9 families (four causes), 0 floating. 161 checks, 1 failed (R-45, the concept conflict).

**Pair families and causes.**

| Cause | Pairs | Fix in v03 |
|---|---|---|
| glazed end wall drawn to the long run's mullion line, 4 mm inside the edge beam whose level its head shares | 6 (4 mm), A, B, C | end wall between the closed wall's inner face and the edge beam's inner face |
| box partition's upper piece (between the girders) runs into the void trimmer | 1 (150 mm) | upper piece stops at the trimmer |
| B partition at the x = 60 switch straddles two closed-side conventions | 1 (20 mm) | placed wholly in segment 4 |
| well guard's landing part meets the landing's end guard at one corner | 1 (19 mm) | ends at the end guard |

**Requirements ticked at v02** (script, render, builder checks, and inspector lines confirmed in v01 that v02 did not change): R-01 to R-06, R-09 to R-11, R-13 to R-18, R-21 to R-26, R-28, R-30 to R-34, R-36 to R-38, R-41 to R-44, R-47, R-48. Open: R-07, R-08, R-12, R-19, R-20, R-27, R-29, R-35, R-39, R-46 (await the v02 inspection); R-40 (B high bay, Designer); R-45 (concept conflict, Designer); R-49 (9 pairs, v03).

**Views note.** Workbench renders back faces, so a cut plane inside a solid shows that solid's far face as a fill: views 22, 30 and 38 cut inside a wall or a flight and show the wall, not the stair. v03 appends 39 and 40 with the plane just past the wall and the coplanar guard hidden. Views are never renumbered.

## v03 (2026-09-10)

**What changed and why.** The nine v02 pairs at their four causes: the glazed end wall now spans between the closed wall's inner face and the edge beam's inner face (it was drawn to the mullion line, 4 mm inside the beam whose level its head shares); the box partition's upper piece stops at the void trimmer; B's partition at the x = 60 switch sits wholly in segment 4; the well guard's landing part ends at the landing's end guard. Views 39 and 40 appended (C stair 2 and B entry stair as sections just past the closed wall with the coplanar guard hidden, since Workbench renders the far face of a cut solid as a fill). Two Runner items from the v02 close-out: an `OVERRIDES` entry for 15 in `tools/layers.py` (the only sanctioned tools edit), because the variation names hit the generic rules ("A_Bridge" contains "ridge", so all of A was "frame"; "C_Steps" contains "step", so all of C was "fixtures"; B fell through to "other"), so the child collection now decides the layer for all three (footings, terrain, plinth and foundation walls to foundations; slabs to floors; roof; glazing and stairs to fixtures; cores to interior; concrete and steel to frame); the audit reads 0 in "other". And the frame-only views 16 to 18 spelled out as literal hide lists, since `closeout.py` looks for a literal `hide=["`; same views, same numbers, same renders.

**Counts.** 1294 members, 0 penetrating pairs, 0 floating. 161 checks, 1 failed (R-45 at 3.30; the Designer has since relaxed the line to 3.0 m clear, carried by v04's assertion).

**Inspector (inspection_v03.md, covering what the v02 inspection would have).** All nine v01 findings and all six Builder-known items read fixed (end walls with the door pane in 32 to 34, terrace open, guards beside the lanes in 37, the void framed in 36, the plans at the right levels, the skin patches gone). Confirmed: R-07, R-12, R-20, R-27, R-29, R-35, R-39, R-46 (ticked). Open: a door-height opening in segment 4's closed wall near the house end in all three variations (views 24 to 26, 35, 36): the closed-wall door rule put a door in the last bay wherever the ground was not above the floor, which in segment 4 means a door at +0.90 over a 5.5 m drop in A, 2.4 m in B, 1.1 m in C, and into core 4's back wall; a dark slot at the top of C's segment-1 closed wall at x = 27 (views 22, 39): identified from the export as `C_RoofBeam_003` in its pocket (26.92..27.08, z 2.054..2.384), cut by the section plane so its far faces render dark, the designed bearing of R-13, settled by eye in v04's view 49; view 29 misses A's five risers (the sight line at 20 degrees passes under the slab edge); R-08 and R-19 in part (B's and C's door from the pavilion into the bar in no view, since a y-section cannot show a wall along y; study, utility and store not distinguishable); R-40 reported: the high bay's ESE face is glass to the roof beam, no 200 mm spandrel above +1.03 as the rewritten line says.

**Requirements.** Ticked at v03: R-07, R-12, R-20, R-27, R-29, R-35, R-39, R-46. Open: R-08, R-19 (views 41 to 43, 47 in v04), R-40 (Designer's wording: the built high bay has no spandrel; question to CraftBot), R-45 (relaxed to 3.0, v04 assertion), R-49 (final version).

**v04 plan.** Closed-wall doors by one rule: a door where the outside surface at both jambs is between one riser (0.165) below and 0.02 above the floor, in the downhill-most bay that is not the window bay, 0.3 clear of the beams and 0.1 clear of the cores and stairs against the wall (`keep_out`, the core positions now one list per variation); B's outside surface is the courtyard paving at -2.75 over x = 11..46. Result: A none (the bridge floor is never within a riser of the ground; R-10's "door openings" are then the strip windows only on A, reported), B two doors onto the courtyard (segment 1 y_max at x = 25.72, segment 2 y_min at 37.72), C two doors onto the grade (L2 y_max at 44.5, L3 y_max at 56.5). R-45 assertion at CLEAR_MIN = 3.0. Views 41 to 49 appended.

## v04 (2026-09-10)

**What changed and why.** R-45 as rewritten (3.0 m clear, floor to slab underside: `CLEAR_MIN`; the assertion passes with L1 3.42, L2 3.30, L3 3.10). Closed-wall doors by one rule instead of "last bay unless the ground is above the floor": a door where the outside surface at both jambs is between one riser (0.165) below and 0.02 above the floor, in the downhill-most bay that is not the window bay, 0.3 clear of the beams and 0.1 clear of the cores and stairs against the wall (`keep_out`; the core x ranges are now one list per variation, used by the core calls too); B's outside surface is the courtyard paving at -2.75 over x = 11..46. Result, as the script prints: A none (the bridge floor is never within a riser of the ground); B two onto the courtyard, segment 1 y_max wall at x = 25.72..26.62 and segment 2 y_min wall at 37.72..38.62; C two onto the grade on the y_max wall, L2 at 44.50..45.40 (outside -2.53..-2.60) and L3 at 56.50..57.40 (outside -3.88..-4.01). The Designer confirmed the rule and wrote the positions into R-10, dropped the R-40 spandrel (high bay as built), and split R-19 into a script zone list and the Inspector's check of the bounding elements. Views 41 to 49 appended (A's five risers steep, B and C pavilion doors as x-sections, the four closed-wall doors, A's core 1 store, C stair 1's guard, the x = 27 beam in its pocket).

**Counts.** 1296 members (+2: the door piers), 0 penetrating pairs, 0 floating. 161 checks, 0 failed.

**Inspector (inspection_v04.md).** Fixed: the segment 4 opening in all three; the "dark slot" at C's x = 27 is the roof beam seated in its pocket (49); the five risers countable (41); the pavilion door into the bar seen for B (42, onto the landing) and C (43, onto the top of stair 1); the four doors at the stated positions, at floor level, onto paving or grade, none into a core, none cutting a window or a beam pocket (44 to 46); C stair 1's guard on the open side (48); no regressions in 01 to 40; S-01 to S-11 unchanged. Confirmed: R-08, R-10, R-16, R-20, R-23, R-40 as rewritten. Open: A's lower box, where the partition at x = 56.9 runs only beside the void (y = 7.25..9.4) and the lower flight and landing occupy 53.68..58.24 across y = 9.4..12.0, so "bedroom 2" (56.9..60) is the stair arrival with a 3.0 x 2.15 alcove, not an enclosed room (views 06, 11); A's segment 1 strip window not seen straight on (a view gap; from the script it is at 11.28..14.72, which is behind core 1 at 11.2..15.2, a placement mistake of the same kind as the v03 doors; the window bay is the longest bay of the segment with no regard to what stands against the wall, so C's segment 1 window sits over stair 1 and segment 3's over stair 3, harmless, and A's segment 3 window at 47.28..50.72 is crossed by the partition at 48.33); whether C's L2 trench return stands in the L2 doorway (from the script: the return is at 43.7..44.0, the door jamb at 44.5, clear).

**Zone list (R-19, script half; computed from the v04 numbers, the same block goes into the v05 script).** Net areas are the zone rectangle at the clear width (5.7 between the closed wall face and the glass line; 5.5 in A's box; 6.0 on the terraces) minus the cores and stair footprints inside it; the LHDG minima are 29 m2 for kitchen and dining, 12 m2 and 2.75 m for a double bedroom, 8 m2 for the terrace.

| Var | Zone | x | net m2 |
|---|---|---|---|
| A | entry hall, core 1 (utility, WC, store 1.2 x 2.5) | 11.0..15.2 | 15.1 |
| A | living | 15.2..28.0 | 73.0 |
| A | kitchen and dining, core 2 (pantry, WC) | 28.0..44.0 | 84.0 |
| A | study, core 3 (bathroom) | 44.0..48.28 | 17.2 |
| A | guest room | 48.38..53.38 | 28.5 |
| A | stair hall (void 53.4..58.24) | 53.4..58.45 | 28.8 |
| A | master bedroom, core 4 (ensuite) | 58.55..65.0 | 29.6 |
| A | covered terrace | 65.0..71.0 | 36.0 |
| A | box: stair arrival and hall | 53.25..56.85 | 11.6 |
| A | box: "bedroom 2", enclosed part 3.0 x 2.15 beside the landing | 56.95..59.95 | 6.5, FAIL |
| A | box: bedroom 3, core 5 (bathroom) | 60.05..64.75 | 18.7 |
| B | entry and stair hall, core 1 (utility, WC, store) | 11.0..15.08 | 8.8 |
| B | living | 15.28..30.0 | 82.2 |
| B | kitchen and dining, core 2 | 30.0..42.0 | 61.2 |
| B | study, core 3 (family bathroom) | 42.0..48.0 | 27.0 |
| B | bedroom 2 | 48.1..53.95 | 33.3 |
| B | bedroom 3 | 54.05..60.0 | 33.9 |
| B | master bedroom, core 4 (ensuite) | 60.1..66.0 | 26.9 |
| B | covered terrace | 66.0..70.0 | 24.0 |
| C | L1 living hall, core 1 (utility, WC, store), stair 1 inside | 11.0..28.7 | 91.1 |
| C | L2 kitchen and dining, core 2 (bathroom), stair 2 inside | 29.0..43.65 | 73.6 |
| C | L2 study | 43.75..46.7 | 16.8 |
| C | L3 master bedroom, core 3 (ensuite), stair 3 arrives inside it | 47.0..54.0 | 30.0 |
| C | L3 bedroom 2 | 54.1..59.45 | 30.5 |
| C | L3 bedroom 3, core 4 (family bathroom) | 59.55..66.0 | 29.6 |
| C | covered terrace | 66.0..70.0 | 24.0 |

**Conflict for the Designer (R-19 against R-27 and R-28).** The dogleg's footprint (void 53.4..58.24, R-28) leaves 58.24..64.75 = 6.5 m of the box for two bedrooms and the bathroom, and R-27 fixes the windows at 57..58.2 and 61..62.2. Nearest alternative I can build: a full-width partition at x = 58.3 (past the landing), bedroom 2 at 58.35..61.15 (2.8 x 5.5 = 15.4 m2), bedroom 3 at 61.25..64.75 (3.5 x 5.5 = 19.3 m2) with core 5 reduced to the concept's 6 m2 bathroom (2.5 x 2.4) against the y_max wall at 62.25..64.75 (bedroom 3 net 13.3, 3.1 clear beside the core), windows moved to 59.2..60.4 and 62.4..63.6 (sills 0.9 above the floor as in R-27), the x = 65 door kept at y = 9.5..10.45. Needs R-27 rewritten. Second note, no change proposed: on C's L3 stair 3 arrives inside the master bedroom (concept 5.1 places the master at 47..54 and the stair at 47..49.3).

**Requirements.** Ticked at v04: R-08, R-10 (with the window caveat, fixed in v05), R-40, R-45. Open: R-19 (box bedroom 2, Designer), R-49 (final version).

**v05 plan (when the Designer answers).** Strip window per segment in the longest stretch of a bay free of what stands against that wall (cores, stairs, partitions, each with its side), at least 1.0 m long; the zone list printed by the script; the box layout per the Designer's decision.
