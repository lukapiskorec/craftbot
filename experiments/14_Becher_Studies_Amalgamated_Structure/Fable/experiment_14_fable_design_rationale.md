# Experiment 14 – Fable run: design rationale

Single record of what was built and why, written by the model at the end of
each phase (phases 1 and 2 on 2026-09-04/05, phase 3 on 2026-09-05). Claude
Code transcripts drop the model's private reasoning; only messages, tool
calls and tool results survive in the `.jsonl`, so the reasoning is written
here first and the transcript archived last.

## 0. About this document

Sections follow the template established in experiment 13, with "Brief as
understood" added as section 1 in this run (every later rationale carries
it), and 3b and 6b for the phase-2 tables. The numbering below is therefore
one higher than experiment 13's for everything after section 0.

| § | Section | Purpose |
|---|---------|---------|
| 0 | About this document | This table. |
| 1 | Brief as understood | The task in one paragraph, as the run read it, before any source is opened. |
| 2 | How to run / outputs | Render command, view legend, collection tree, counts. |
| 3 | Reading the inputs | The photo read, the manuals, the source-to-rule-to-number table, deliberate deviations. |
| 3b | Comparison round | Photo versus model, item by item, with the decision. |
| 3c | User review round | The phase-3 requests, what changed for each, and what was pushed back on. |
| 4 | Reading the reference code | What was inherited from `tools/` and what it constrains. |
| 5 | Construction logic settled before geometry | Bearing stack, levels, the stair problem, the envelope logic. |
| 6 | Core modelling decisions | With the alternatives that were rejected. |
| 6b | Independent structural improvements | The review that ignores the photo. |
| 7 | Detailed geometry | Numbers with their datum. |
| 8 | Verification | What the checks prove and what they do not. |
| 9 | Iterations | One row per version: change, members, penetrating pairs, what the renders showed. |
| 10 | Scope and known simplifications | What is absent, approximate or plausible-only. |

## 1. Brief as understood

A timber railway coaling tower, photographed in the Bechers' typological
style, becomes a single multi-storey home. The original heavy-timber
post-and-girt tower, the clapboard shed at its foot and the gabled hoist
house on top are kept, repaired and stay visible inside and out; they are
the point of the design, not a constraint on it. New floors, a stair,
glazing, infill walls and cladding are inserted into the frame. The side
trestle with the cyclone tank is machinery, not habitable structure, so one
preserved braced leg stays as a sculptural relic and the tank and chutes go.
The hopper bottom and the bin levels go with them; the frame is re-levelled
to 3.0 m storeys. Phase 3 added the owner's review: no braces on the tower
(the photo has none), the cladding inside the frame so the frame reads on the
facade, boards inside as well as outside, varied windows, stringers under the
stairs, a canopy on the outriggers and a ladder to the hoist house.

## 2. How to run / outputs

Every version `experiment_14_fable_vNN.py` was executed in background Blender
4.3 by `tools/render_views.py`, from the repo root:

```
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" --background --python tools/render_views.py -- "experiments/14_Becher_Studies_Amalgamated_Structure/Fable/experiment_14_fable_v09.py" "<abs repo>/experiments/14_Becher_Studies_Amalgamated_Structure/Fable/experiment_14_fable_v09_blender" --views "experiments/14_Becher_Studies_Amalgamated_Structure/Fable/views_fable.py" --lib "experiments/14_Becher_Studies_Amalgamated_Structure/input"
```

Views (`views_fable.py`, numbered once, appended only): 01–04 orbits, 05 top,
06 south elevation, 07 east elevation, 08 frame only, 09 from below, 10
matched to the photo (from the south-east, low), 11 long section through the
stair strip (y = 1.2), 12 L1 plan section, 13 posts through the shed roof,
14 repaired post foot, 15 stair hole in the shed roof, 16 ground floor plan
section, 17 trestle relic and tie-back, 18 shed outriggers, 19 terrace corner
frame, 20 facade bay, 21 L1 void guard and beam seats, 22 cross section at
y = 2.2 looking south (interior boards, stairs, stringers), 23 outrigger with
knee and canopy, 24 ladder, 25 ground stair with stringers and landing posts,
26 interior boards alone. Views 17–19 exist from v03, 20–21 from v06, 22–26
from v08. The hide lists of views 08, 13, 14, 15 used slash paths in v01–v03
and hid nothing; Blender collection names are global, so from v04 they use
the bare child names (`Shed_Walls`, not `Existing/Shed_Walls`).

Collections (assembly order, colour in the renders):

```
Foundation/{Plinths}                                 grey
Existing/{Tower_Posts, Tower_Girts, Shed_Walls, Shed_Ceiling, Shed_Roof,
          Shed_Roof_Boards, Shed_Outriggers, Terrace_Frame, Terrace_Deck,
          HeadHouse_Frame, HeadHouse_Floor, HeadHouse_Walls, HeadHouse_Roof,
          Trestle}                                   dark brown: preserved timber
Repairs/{Post_Feet, Splices}                         orange feet, grey plates
New/{Beams, Slabs, Stairs, Infill_Walls, Glazing, Doors, Cladding_Shed,
     Cladding_Tower, Cladding_HeadHouse, Cladding_Interior, Roofing, Guards,
     Ladder, Connections}                            pale glulam, blue glass, grey steel
```

`Existing/Tower_Braces` existed in v02–v07 and was removed in v08.

Final model: v09, 4576 elements, 0 penetrating pairs at 1 mm.

## 3. Reading the inputs

### 3.1 The photo

`input/becher_studies_amalgamated_structure.jpg`, a Becher-style black and
white photograph of a timber railway coaling tower. Read full frame first,
then four upscaled crops (house, bunker, head, trestle). What the photo
settles, in the role photographs have (topology, counts, proportion, never
absolute size):

1. Ground-floor house: one storey, horizontal clapboard, low gable along the
   long axis with a kicked eave, a six-pane sash window and a diagonal-boarded
   door on the gable end, a row of about nine projecting outrigger beam ends
   under the long-side eave carrying a narrow canopy. The tower's heavy posts
   pass down through its roof and walls.
2. Tower: a post-and-girt frame, about four bays long by two deep, bolted
   girts at three levels, horizontal planking set between the posts on the
   bunker, long rakers in the open zone between the house roof and the
   bunker where the hopper bottom and chutes were. No knee braces on the
   bunker faces (phase 1 read them in, phase 3 took them out).
3. Bunker cap: a low overhanging roof over a band of open framed panels, a
   frieze.
4. Head house: a small gabled, vertically boarded hoist house standing on an
   open colonnade of posts above the cap, toward one end.
5. Side trestle: a tall braced leg with a cyclone tank, chutes and an A-frame
   platform. Machinery, not habitable structure.

Calibration: the door, taken as 2.0 m, gives about 95 px/m at ground level in
the original 736 x 1115 image. The photo looks steeply upward, so heights read
off it above the shed are compressed and were not used; the tower's height
comes from the storey stack (§5) instead.

### 3.2 Manuals

Selected from `manuals/INDEX.md` by description, then chapter, then the
extracted `.md`, then the PDF pages. All five PDFs were present locally.

| Manual | Read | Fixes |
|---|---|---|
| Canadian Wood-Frame House Construction (CMHC) | ch 9, 10, 11, 17, tables 20, 25, 31, 33; PDF pp. 113–115 (beams, ledgers), 133 (balloon frame), 142–145 (roof framing), 208–211 (stairs) | shed studs, rafters, ceiling joists, collar ties, stair rise, run and stringers, guards |
| Architect's Handbook of Construction Detailing | ch 4 sections 4-9 to 4-13, PDF pp. 200–207; stair geometry 3-10 to 3-13; door sizes 6-5 | beam-to-post seats, post base on a raised bracket, glulam widths and depth steps, guard height, door leaf thickness |
| CLT Handbook, facts and planning | ch 2, ch 4 (fig 4.16, PDF pp. 77–78), ch 5 table 5.1 | slab thickness by span, slab on a beam |
| How to CLT | ch 5 rules of thumb | cross-check of slab thickness, opening piers |
| London Housing Design Guide 2010 | ch 4, ch 5 | storey height, sill height, terrace depth, stair going |

### 3.3 Source to rule to number

| Source | Rule | Number in the model |
|---|---|---|
| Photo | tower about 4 x 2 bays, posts through the shed roof | `BAY` 2.4, `NX` 4, `NY` 2, `POST` 0.25; tower 9.6 x 4.8 m |
| Photo | bolted girts outside the posts, planking between the posts | `GIRT` 200 x 300 on the outer post faces; boards between posts (v06 flush with the post faces, v08 against the infill walls) |
| Photo | shed long and low, ridge along X, eave low, window and door on the gable | shed 12.0 x 6.6 m, `PLATE_TOP` 2.8, pitch 4/12, door 1.0 x 2.1, windows 1.2 x 1.2 |
| Photo | outrigger row under the long-side eave with a canopy | 50 x 150 at about 1.2 m against real studs, 0.9 m reach, sloping top, 19 x 184 canopy boards |
| Photo | frieze of open framed panels under the cap | clerestory band, sill 1.5 m above the top slab, head 2.35 |
| Photo | head house on an open colonnade, 2 x 2 bays, gable, vertical boards | posts continue to `Z_HH_GIRT`, colonnade 2.4 clear, walls 2.4, pitch 8/12 |
| CMHC table 25 | 38 x 140 at 600 for an exterior wall with roof plus one floor | `STUD_T` 0.038, `WALL_T` 0.14, `SPACING` 0.6 |
| CMHC table 31 | 38 x 184 at 600 spans 4.41 m at 1.5 kPa | shed rafters `RAF` 38 x 184, span 3.3 m run each side |
| CMHC ch 11 | 1:3 is the threshold: ceiling joists tie the feet, collar ties 38 x 89 | `PITCH` 4/12, `CJ` 38 x 184, `COLLAR` 38 x 89 at 3.35 |
| CMHC fig 83 | ceiling joist nailed to the side of each rafter | south joist west of the rafter, north joist east of it |
| CMHC fig 52, 84 | built-up beam 3 x 38, joists lapped over an interior support, lap 300 max | `MIDBEAM` 114 x 235, `CJ_LAP` 0.15 each side |
| CMHC fig 64, ch 9 | floor openings: doubled headers and trimmers; headers over 3.2 m need engineering | doubled trimmer joists and rafters, headers 5.3 m, flagged |
| CMHC ch 17 | rise 125–200, run 210–355, width 860, headroom 1.95, flight 3.7 max, landing 860; stringers 38 thick, 235 deep | ground 23 x 195.7 mm in two runs, going 230, landing 0.9; upper 15 x 200, going 250, width 0.9; stringers 50 x 235 |
| CMHC ch 26 | guard 1070 mm above 1.8 m, decking 38 mm at 600 | `GUARD_H` 1.07, `DECK_T` 0.038 |
| CMHC table 29 | roof joists 38 x 235 at 600 span 4.52 m | terrace joists `TJ` 38 x 235 at 600, spans 2.4 and a 0.9 cantilever |
| CMHC ch 11 | ridge board on a roof at or over 1:3 | `RIDGE_B` 38 x 235 (shed), 38 x 184 (head house) |
| Architect's Handbook 4-10 | beam ends on seats attached to a column that runs through the floor line | steel seats 12 mm, 150 long, 100 leg, under every new beam end |
| Architect's Handbook 4-13 | column base on a bracket, bearing raised 25–76 mm | `PLINTH_H` 0.075, plinths 0.28 square |
| Architect's Handbook 4-9 | glulam widths 79, 130, 171, 222; depth in 38 mm steps | `GLB` 222 x 342 (9 x 38) |
| Architect's Handbook 6-5 | wood door 44.4 mm thick, 2032 high | `DOOR_T` 0.045, doors 2.1 high |
| Architect's Handbook 4-5 | continuous tie-down needed in multistorey light frame | not modelled, §10 |
| CLT Handbook table 5.1 | 100 mm 3-layer spans 3.7 m simply supported at L/300 | `CLT_T` 0.10 on a 2.4 m span between beams |
| CLT Handbook fig 4.16 d | slab bearing on a beam under the panel | strips cover the perimeter beams and meet over the mid beam (v08); v05–v07 bore 50 mm |
| How to CLT | 200 mm for housing under 5 m; piers at least 300 mm at a panel edge | 100 mm kept (single dwelling, 2.4 m span); the stair void runs to the beam, recorded |
| London guide 5.4.1 | 2.5 m clear minimum, 2.6 desirable | `STOREY` 3.0; clear 2.84 under the slab, 2.56 under the beams |
| London guide 4.4.6 | living room sills 800–850 | plain windows sill 0.85; small high windows 1.5; full-height windows to the floor |
| London guide 4.10.3 | private open space at least 1.5 m deep | terrace deck 0.9 m beyond the posts plus the bays: 2.4 m and more |
| London guide 3.2.8 | easy-access stairs: risers not over 170, goings not under 250 | not met on the ground flight (195.7 / 230), met on the upper flights' going |

Defaults where the sources are silent, labelled as mine: 19 x 184 roof boards
laid closed (CMHC fig 98 rule from experiment 13), 25 x 140 exterior boards
and 19 x 140 interior boards on the tower and head house, 19 x 160 clapboard
exposure, 24 mm glazing, 60 x 90 ladder stiles with 30 mm rungs at 300, 50 x
100 outrigger knees at 45 degrees.

### 3.4 Deliberate deviations from the photo and the brief

1. The hopper bottom and chutes are removed. The brief preserves the timber
   structure, not the process plant; the girt zone that carried the hopper
   stays and is now clad down to the shed roof.
2. The cyclone tank, pipes and A-frame platform on the trestle are dropped.
   One braced leg with its girts and St Andrew's crosses stays as a
   freestanding relic, tied back to the tower at the terrace level.
3. The bunker cap's low pitched roof becomes a flat terrace deck with a guard.
   A usable terrace under the head house colonnade is the reason to convert
   the building at all.
4. The original bin levels are re-cut to 3.0 m storeys. The girts move to the
   new floor levels. This is the one place the "preserved" frame is
   re-levelled; it is recorded as repair and re-levelling, not preservation.
5. The shed's kicked eave and six-pane sash are not modelled (§3b).
6. The shed's gable studs are removed at the owner's request (§3c); the
   gable boards are nailed to the end rafters and the plate. CMHC fig 83 has
   gable end studs; 38 x 140 studs on the 0.6 grid would be the way back.

## 3b. Comparison round (photo versus model)

Done after v05 stood clean; the changes went into v06. Phase 3 revisited two
rows (marked).

| In the photo | In the model (v05) | Decision |
|---|---|---|
| Posts and girts exposed on the bunker face, planking set between them | cladding outside the girts, frame hidden except in the window reveals | changed in v06: boards between the posts flush with their faces; v08: boards against the infill walls, the whole post depth exposed |
| Bunker planking horizontal | vertical open-jointed boards | changed: horizontal; v08 gapless |
| No knee braces on the bunker faces | 45-degree knees lapped on every post | phase 1 misread the rakers of the hopper zone as knees; removed in v08 |
| Shed door on the gable beside the window | door on the west gable | changed: window and door on the east gable, window on the west |
| Outriggers carry a narrow canopy | bare beam ends | changed in v08: sloping tops, board canopy, knees |
| Head house vertically boarded | vertical boards | kept; gapless from v08 |
| Cap roof low-pitched with a wide overhang | flat deck, 0.9 m overhang | kept, §3.4 |
| Kicked eave on the shed | straight eave | kept: a 0.2 m kick needs a second rafter plane for a hidden detail |
| Six-pane sash windows | single glazed opening | kept: sash bars are fixtures |
| Tank, chutes, A-frame on the trestle | braced leg with two tie beams | kept, §3.4 |
| Hopper bottom in the open zone | open braced band (v05), clad band (v08) | plant removed, §3.4 |
| Long rakers from the trestle to the tower | none | kept: the tie beams at the terrace level do that job |
| About nine outriggers under the shed eave | nine at 1.2 m (v03), eight against real studs (v08) | kept |

## 3c. User review round (phase 3)

The owner's list after v07, with what changed and where.

| Request | Change | Where |
|---|---|---|
| Remove the knee elements on the tower | `Existing/Tower_Braces` gone; the trestle crosses stay | v08, §6.1, §6b |
| Exterior cladding between the posts and the infill | gapless 25 x 140 boards against the infill wall's outer face, between the posts, in bands split by the slabs | v08, §6.5 |
| Interior cladding throughout, mirroring the exterior | 19 mm horizontal boards inside the shed and tower walls, vertical inside the head house, gable rows cut to the rafter undersides and holed at the ridge boards | v08, §6.8 |
| No gaps in any cladding | gap parameters removed; the deck and the head house floor keep their drainage gaps (they are floors) | v08 |
| Vary the tower windows, six at most on the south face | storeys 1 and 2 get explicit lists: full-height, small high and plain windows; south face 3 + 3; the clerestory is untouched | v08, §6.6 |
| Stringers on both sides of every flight, posts under the ground landing | 50 x 235 stringers whose top line runs through the tread back corners, feet cut level; four 90 mm posts under the landing | v08, §6.7 |
| Floors have gaps | the strips bore 50 mm on the beams and stopped 122 mm apart over the mid beam; they now run from the beam's outer edge to the mid-beam centreline | v08, §6.2 |
| Ladders from the roof to the small house | one ladder at the head house door, 75 degrees, stiles leaning on the floor girt with inset ends, seven rungs; the door is the only entry, so one ladder | v08, §6.9 |
| Outriggers thinner, on studs, with knees and a roof | 50 x 150 against the face of the nearest stud or king stud (away from the window side), a 50 x 100 knee at 45 degrees from the outrigger underside through a cut in the clapboard to a foot lapped on the same stud, 19 x 184 canopy on the sloping tops | v08, §6.10 |
| Remove the thin shed gable elements | removed; they were 38 x 38 by a bug (the wall thickness was passed as the stud thickness); the head house had the same bug and its studs were corrected to 38 x 140 instead, since nothing was said about them | v08, §3.4 |
| Close the gap between the shed roof and the tower floor | the lowest cladding band runs down to the shed roof boards; on the gable faces its rows are cut to the roof slope | v08, §6.5 |
| Window and door fixtures everywhere | glass in every shed and head house window, 45 mm leaves in the two doors, glass to the floor in the full-height windows | v08 |
| Update every document, add "Brief as understood", update the skill | this document §1, callouts, viewer models, the two skills | close-out |

Pushed back on, then done as asked: the gable studs. The correct fix is the
section, not the removal; recorded in §3.4 so the next run can reinstate them.

## 4. Reading the reference code

No inherited model. Everything comes from `tools/`: `craftbot_lib.box`,
`prism`, `prism_x` and `prism_y` for every solid, `planes.sloped_member` for
rafters (build long, clip by half-spaces: plate top, ridge face, header face),
`planes.member` for the ladder stiles and the outrigger knees (end inset
against a bearing plane), `framing.stud_wall` for every stud wall,
`framing.clad` for the clapboard rows, `framing.boards` for the deck and the
head house floor, `framing.flight` for the stair treads,
`framing.halved_brace` for the trestle crosses, `geometry2d.positions` for
every repeated member, `geometry2d.rect` and `clip` for the slab pieces and
the roof-cut board rows.

Constraints these impose: every solid convex (a slab with a hole becomes
pieces, a rafter with a bird's mouth becomes body and tail sharing the heel
face, a gable board row cut by two roof slopes becomes two pieces split at the
ridge), `place_element` replaces a same-named object silently (every name
carries all its loop indices), collection names are global (bare child names
in the hide lists), and a heredoc with an apostrophe breaks the shell on this
machine (patch scripts are written to files).

## 5. Construction logic settled before geometry

**Bearing stack, ground to roof.** Plinth, post (continuous, 250 square, 20 m
to the head house girts on the east three columns, 13.3 m on the west two),
perimeter girts on the outer post faces (preserved, carry the original
planking line), new glulam beams between the posts on the three X rows (carry
the CLT strips), CLT strips spanning Y 2.4 m, terrace joists spanning Y on the
terrace girts and beams, deck boards; head house girts and a mid beam, floor
joists, boards, stud walls, rafters, ridge, roof boards.

**Levels.** The shed roof passes under the tower. Its rafter tops reach 4.047
at the ridge (y = 1.8) and 3.894 at the mid post row (y = 2.4). The L1 beams
must clear that: with the slab top at 4.5, the beams' underside is 4.058, 145
mm over the boards at the mid row. So `Z_L1` is 4.5, not 3.0, and the ground
floor keeps its 2.8 m ceiling with an attic band above it. The storeys above
are 3.0 m (7.5, 10.5), the terrace girts top at 13.3, deck at 13.573, head
house girts at 15.973, floor 16.189, plate 18.589, ridge 20.347. Total height
20.3 m, in the range of small timber coaling stations.

**The ridge.** With equal pitches the ridge sits on the shed's centreline, so
the shed is placed asymmetrically about the tower (y from -1.5 to 5.1,
centre 1.8) to keep the ridge 0.6 m off the mid post row. Nothing hits the
ridge board.

**The stair.** A straight flight along X in the strip y 0.75–1.65 between the
y = 0 and y = 2.4 post rows, alternating direction per storey (a scissor
stack). The ground flight has to climb 4.5 m: two runs of 12 and 11 risers
with a 0.9 landing (CMHC: no flight over 3.7 m), run 5.73 m. It passes through
the shed ceiling and roof, which means one hole in the preserved roof:
between doubled trimmers at x = 3.3 and 8.7, from a sloped header at y = 0.6
up to the ridge board, on the south slope only (the north slope stays whole
and carries the ridge board). Alternatives rejected on paper: a switchback in
one 2.4 m bay does not fit (7 goings of 230 plus a 0.9 landing exceed the
2.15 m clear between post faces); a stair in the 1.5 m south strip of the
shed cuts a 5.7 m hole along the eave; a stair in the trestle needs three
flights in a 2.4 m square, which fails the same arithmetic; an external stair
is not a home stair.

**Envelope logic (v08).** Infill stud walls stand on the slabs inside the post
line (y 0.136–0.276 from the post row), so no post interrupts a wall. The
exterior boards sit against the wall's outer face (y 0.111–0.136), between
the posts, so the full post depth, the girts and the beam edges read on the
facade. The interior boards sit against the wall's inner face (y 0.276–
0.295). The cladding bands are split by the slabs, whose edges show outside as
floor bands. Below the L1 slab the lowest band runs down to the shed roof, so
the former open zone is closed and the L1 soffit is inside.

## 6. Core modelling decisions

### 6.1 Knee braces: added, patterned, removed

Phase 1 read 45-degree knees on the bunker faces and spent three versions on
their geometry: v01 put them on the post row plane, where they ran into the
new beams; v02 lapped them outside the post faces and every post got two that
crossed; v03 gave each post one; v06 patterned them from the interior posts on
the long faces and the corner posts on the short faces. Phase 3's re-read of
the photo agreed with the owner: the bunker faces show posts, girts and
planking, the diagonals belong to the hopper zone and the trestle. v08 removed
them. What that costs structurally is in §6b.

### 6.2 CLT strips over the beams, notched around the posts

The beams are 222 wide between 250 posts, so any slab that bears on a beam
enters the post's footprint. v04 ran the slab edge 14 mm into every interior
post. v05 bore 50 mm on each beam and notched the strip around every interior
post with 25 mm clearance (a CNC cut, How to CLT). That left the strips 122 mm
apart over the mid beam and the perimeter beams 172 mm exposed inside, which
the owner saw as gaps; v08 runs each strip from the outer edge of the
perimeter beam to the centreline of the mid beam, so the two strips meet
there. Decomposition: peel each rectangular hole's four sides off every piece
in turn (`rect_minus`), which keeps every piece convex and the check exact.
Rejected: `wall_pieces`, whose column grouping asserts when a post notch
column and the stair void overlap in x.

### 6.3 The shed roof as preserved structure with one hole

Rafters at 0.3 + 0.6k miss the 2.4k posts by 156 mm, ceiling joists and
collar ties sit on the same grid, and the roof boards are split around each
post with 12 mm clearance. The stair hole follows CMHC's opening grammar: on
each edge grid line the stack from the line outward is rafter, north joist,
trimmer rafter, trimmer joist (each 38 mm), so the doubled trimmers sit beside
the joists rather than through them; a 235 deep sloped header between the
trimmer rafters; doubled joist headers at y = 0.6 and at the ridge; the joists
in the hole become tails and stubs. The header spans 5.3 m, past CMHC's 3.2 m
limit for a prescriptive header; flagged, not solved.

### 6.4 Ceiling joists beside the rafters

v01 put joist and rafter on the same grid line, so they shared the plate.
CMHC fig 83 nails the joist to the rafter's side: south joist on the west of
the rafter, north joist on the east, lapping 0.3 m over the mid beam with the
rafter thickness between them. A real lap has the two joists touching; here
they are 38 mm apart, the spacer is not modelled.

### 6.5 Boards inside the frame, in bands, down to the roof

v02–v05 skinned the tower outside the girts and hid the frame. v06 set the
boards between the posts flush with their faces, which exposed the girts but
still put the boards in the post plane. v08 moves them against the infill
walls (§5), gapless, in bands: from the shed roof to the L1 slab underside,
then slab top to next slab underside, then slab top to the terrace joists.
The bands stop at the slab undersides because the strips cross the board
plane (v06's bands reached the girt underside, 42 mm above the beam underside,
which produced 104 pairs). On the gable faces the lowest band's rows are cut
to the roof slope, split at the ridge so each piece stays convex; on the long
faces the roof is level along the band, so the rows start at its height. At
the corners the side bays start past the front boards (v08 overlapped them by
11 mm); inside, the front boards run between the side walls and the side
boards start past the front boards (v08 overlapped by 19 mm).

### 6.6 Windows as lists, not a rule

Phase 1 generated one window per bay per storey from a rule, which the owner
read as uniform and repetitive (12 on the south). v08 keeps the clerestory
rule on the top storey and writes storeys 1 and 2 by hand per face: on the
south, a plain window, a full-height window and a wide window on L1, a small
high window, a full-height window and a narrow window on L2 (six in all);
fewer on the north and one per storey on the gables. A full-height window is
a `None` sill, which `stud_wall` treats as a door (bottom plate cut), and the
glass and both cladding holes run from the slab top. Every opening is
asserted to leave two stud thicknesses inside its wall segment.

### 6.7 Stringers and the landing

`framing.flight` makes solid tread blocks with nothing under them. v08 adds a
stringer on each side of every flight: a 50 x 235 parallelogram in the x-z
plane whose top edge passes through the back-bottom corner of every tread (so
the blocks bear on it at their back edge and touch it nowhere else), depth
measured perpendicular to the pitch line, foot clipped level at the floor it
starts from, head plumb at the landing riser. The stringers sit at y
0.70–0.75 and 1.65–1.70, inside the void strip, so they pass the slabs and
the roof hole without touching them. The ground landing gets four 90 mm posts
inside its corners; the run-2 stringers bear on the landing top beside the
box.

### 6.8 Interior boards

Same rows and widths as the exterior they mirror (19 mm thick): horizontal
19 x 160 on the shed's inner faces up to the plate, then gable rows above it
cut to the rafter undersides and holed at the ridge board; horizontal 19 x
140 on the inner faces of every tower wall segment; vertical 19 x 140 on the
head house's inner faces, the gables cut to the rafter undersides and holed at
the ridge board. Holes for every opening, for the outriggers where they pass
into the shed, and for the shed's mid beam where it bears on the gable walls.
The shed's gable rows above the plate are nailed to nothing now that the
gable studs are gone (§3.4).

### 6.9 The ladder

Two 60 x 90 stiles at 75 degrees from the deck to 50 mm under the head house
floor girt's top, leaning on the girt's outer face: `planes.member` with the
foot inset against the deck plane and the head inset against the girt face,
so both ends touch on one edge and nothing penetrates. Seven 30 mm rungs at
300 between the stiles. The stiles stand at y 2.0 and 2.6, inside the 1.2 m
door and north of the deck void guard at y 1.94; the floor is one step above
the girt. Rejected: leaning on the floor edge above the girt (nothing there
to bear on) and a second ladder (the door is the only entry).

### 6.10 Outriggers against studs, with knees and a canopy

The v03 outriggers were 100 x 200 on a ledger, between studs. v08's are 50 x
150, each placed against the face of the stud nearest to a 1.2 m target: a
regular stud on the grid, or a king stud beside a window on the side away
from the window. The candidate list is rebuilt with the same skip rule
`stud_wall` uses, and every outrigger is asserted clear of every opening
zone. The top slopes from 2.60 at the inner end to 2.52 at the tip; five rows
of 19 x 184 boards lie on that slope from the tip to the clapboard face, in
three lengths split at outriggers. A 50 x 100 knee rises at 45 degrees from a
foot inside the wall cavity (lapped on the same stud, 50 mm short of the
interior boards so its square end clears them) to the outrigger underside
0.55 m out, its head inset against the underside plane; where it crosses the
19 mm clapboard the rows are cut around it, the cut sized from the knee's
section rotated 45 degrees plus the board thickness. Rejected: a knee
bearing on a cleat outside the siding (a weak, invented detail) and a knee
in the plane of the stud (the outrigger is beside the stud, not on it).

### 6.11 Repairs as geometry

Four posts (the two south corners, the north-east corner and the mid-row post
at x = 4.8) get a new 0.9 m foot in its own collection and colour, with a
12 x 160 x 600 steel splice plate on each X face centred on the joint. The
plinths raise every post 75 mm (Architect's Handbook 4-13). Nothing else
about the repair (bolts, scarf, moisture barrier) is modelled.

## 6b. Independent structural improvements

Reviewed with the photo set aside, after v05; revisited after v09.

| Finding | Load path argument | Action |
|---|---|---|
| Beam ends bore on nothing at the posts | the CLT strips deliver into the beams, the beams into the posts | steel seats under every beam end, 12 mm plate 150 long, 100 leg, per Handbook 4-10 (v06) |
| Stair voids unguarded | 4.5 m and 3.0 m drops on the slabs, 2.4 m on the deck | 1.07 m guards on the three open edges of every void (v06) |
| Upper flight feet inside the void below, 12 cm landing | a foot on a void is a fall, a 12 cm landing is a wall in the face | voids end at the landing riser, flights start 5.0 m from the far wall (v06) |
| Treads on nothing | the tread blocks had no support | stringers both sides, landing posts (v08) |
| Lateral stability after the braces went | wind on the long faces reaches the ground through the short faces; the infill walls are boarded, not sheathed | not modelled: 19 mm boards nailed to studs are not a rated shear panel; ply sheathing on the infill walls or the CLT strips screwed to the beams as a diaphragm is the fix. The trestle crosses brace only the trestle |
| Roof hole headers span 5.3 m between trimmers | past CMHC's 3.2 m limit | not changed; needs engineering, or a post under the header at the y = 0 row |
| No hold-downs, no diaphragm connection between the CLT strips | Handbook 4-4/4-5 wants a continuous tie-down; the strips act as a diaphragm only if screwed together and to the beams | not modelled, §10 |
| Shed gable triangle unframed | the gable boards span from the plate to the end rafter with no studs | not changed at the owner's request; §3.4 |
| Outrigger knee foot inside the cavity | the knee delivers the canopy load into the stud by the lap bolts, not by bearing | recorded; the lap is the connection, the bolts are not modelled |
| Trestle top bay 0.3 m tall | a cross in it is meaningless | no cross in the stub bay (v04) |
| Terrace deck boards cantilever 0.2 m past the last whole joist at the void | 38 mm decking, 0.2 m, fine | kept |

Considered and not changed: a second mid-row beam line in Y (the strips span
2.4 m in Y and need none), a ridge beam in the shed (the roof is exactly 1:3,
joist ties suffice), a ledger under the outriggers (they are bolted to the
studs, the ledger would cross every stud inside the cavity).

## 7. Detailed geometry

Datum: ground slab top z = 0, tower post rows x = 0, 2.4, 4.8, 7.2, 9.6 and
y = 0, 2.4, 4.8 on the post centres.

- Shed: x -1.2 to 10.8, y -1.5 to 5.1. Plates top 2.8. Rafter top line at the
  wall outer face 2.947 (= 2.8 + 0.194 - 0.14/3); ridge 4.047 at y = 1.8;
  ridge board dropped 6.3 mm (19/2 x 1/3) so the last board row clears it.
  Overhang 0.45. Boards 19 x 184, 0.1745 m wide in plan. Mid beam 114 x 235
  under the joist laps at y = 2.4, between the posts, bearing on the gable
  walls.
- Outriggers: x = 0.799, 2.201, 3.256, 4.544, 5.599, 7.001, 7.999, 9.401
  (against the king studs of the three windows and the regular studs at 3.3
  and 4.5), section 50 x 150, underside 2.45, top 2.60 inside to 2.52 at the
  tip, from 0.9 outside the wall to 0.3 inside. Knees 50 x 100 from (y -1.41,
  z 1.81) to (y -2.05, z 2.45). Canopy 19 x 184 from y -2.4 to -1.519, five
  rows, three lengths.
- Tower: girt tops 4.4, 7.4, 10.4, 13.3; beams 222 x 342 with undersides
  4.058, 7.058, 10.058, 12.958. Exterior boards 25 x 140 at y 0.111–0.136
  (and the mirror positions), bands roof–4.4, 4.5–7.4, 7.5–10.4, 10.5–13.3.
  Interior boards 19 x 140 at y 0.276–0.295.
- Slabs: 100 mm, tops 4.5, 7.5, 10.5; strips y -0.111–2.4 and 2.4–4.911;
  post notches 0.30 wide; voids L1 (6.0, 8.4), L2 (1.1, 3.7), L3 (5.5, 8.1),
  deck (1.1, 4.2), all y 0.6–1.8.
- Stairs: ground flight x 2.67 to 8.40 (11 x 0.23, landing 0.9, 10 x 0.23),
  23 risers of 195.7 mm, landing top 2.348 on four 90 mm posts; upper flights
  15 x 0.2, 14 x 0.25, from 4.6 westward (L1, L3) and from 4.6 eastward (L2),
  tread blocks 60 mm; stringers 50 x 235 at y 0.70–0.75 and 1.65–1.70.
- Windows, storey 1 (a0, a1, sill, head above the slab): south (0.6, 1.8,
  0.85, 2.25), (2.85, 4.35, floor, 2.6), (7.7, 9.1, 0.85, 2.25); north (2.85,
  4.35, floor, 2.6), (7.7, 8.9, 0.85, 2.25); west (2.95, 4.15, floor, 2.6);
  east (0.7, 1.9, 0.85, 2.25). Storey 2: south (1.0, 1.9, 1.5, 2.3), (5.25,
  6.75, floor, 2.6), (7.9, 8.9, 0.85, 2.25); north (0.6, 1.8, 0.85, 2.25),
  (5.5, 6.4, 1.5, 2.3); west (0.7, 1.9, 0.85, 2.25); east (3.2, 4.0, 1.5,
  2.3). Storey 3: clerestory in every bay, sill 1.5, head 2.35.
- Terrace: joists 38 x 235 at 0.6 from x -1.025 to 10.625, y -1.025 to 5.825;
  deck 38 mm, boards 0.14 at a 6 mm gap; guard posts 90 square at 1.2 m, top
  rail at 1.07, mid rail at 0.5.
- Head house: x 4.675–9.725, y -0.125–4.925; colonnade 2.4 clear; girts
  200 x 300 at 15.973; joists 38 x 184; boards 32 mm; walls 2.4; gable studs
  38 x 140; rafters 38 x 140 at 8/12, ridge 20.347, ridge board dropped 12.7
  mm; roof boards 19 x 184; exterior boards 25 x 140 vertical, interior 19 x
  140 vertical.
- Ladder: stiles 60 x 90 from (x 3.85, z 13.573) to (x 4.475, z 15.923) at y
  2.0 and 2.6; rungs 30 x 30 at 0.3.
- Trestle: posts at (12.3, 1.2) and (12.3, 3.6) to 13.9; girts at the tower
  girt levels plus the top; crosses 150 square halved at the crossing, lap
  d(1 + cos φ)/sin φ + 0.05; ties 100 x 200 at 13.1–13.3 from the tower's
  east girt face to the trestle girt face.
- Seats: 12 mm plates 150 long under each beam end, 100 mm leg on the post
  face, 30 mm narrower than the beam each side.
- Fixtures: glass 24 mm in the wall centre of every window; door leaves 45 mm
  in the shed's east door (y 3.0–4.0) and the head house's west door (y 1.5–
  2.7).

## 8. Verification

- Numeric: `tools/check_overlaps.py` after every render, separating-axis test
  over every pair at 1 mm. v09: 4576 members, 0 pairs. Touching faces (slab on
  beam, joist on girt, board on rafter, tread on stringer, stile on girt, seat
  under beam) report zero by design. The harness prints 80 pairs; for v08's
  589 the full list was dumped from the saved blend and grouped by name family.
- Assertions in the script: the L1 beams clear the shed roof at the mid post
  row, the ground flight lands short of the east beam, the riser counts close
  the storey heights exactly, every upper flight's foot lies outside its
  slab's void, every window leaves two stud thicknesses inside its wall
  segment, every outrigger is clear of every opening zone, the shed ridge sits
  on the shed centreline.
- Visual: 26 fixed views per version, all opened. The frame-only and
  close-up views were blind in v01–v03 (hide lists never matched) and were
  re-read from v04.
- Not verified: structural adequacy of any member (sections are plausible for
  the spans, not calculated); bearing lengths and seat capacities; the 5.3 m
  roof-hole headers; the lateral system without braces; the CLT-to-beam
  fastening; the post splice; the outrigger and knee bolting; the stringer
  fixings; the ladder's bearing; wind uplift and hold-downs; the deck fall;
  fire and acoustics of the floor build-up.

## 9. Iterations

| v | change | members | pairs | what the renders and the check showed |
|---|--------|---------|-------|---|
| 01 | preserved frame, shed with its roof hole, terrace, head house, repairs, beams, slabs, stairs | 972 | 127 | braces on the post row ran into the beams (42 mm), joists shared the plate with the rafters (38 mm), trimmer stacks collided |
| 02 | braces lapped on the post faces, joists beside the rafters, trimmer stack, whole envelope (clapboards, infill walls, glazing, tower and head house cladding, roof boards, guards) | 2502 | 342 | brace pairs crossed on the post faces (150 mm), W/E infill walls ran through the mid-row beam, plinths hit the shed's north plate, L1 braces at the short faces sat inside the shed roof |
| 03 | one brace per post, W/E walls split at the mid beam, window king studs inside the corners, plinths 0.30, outriggers on a ledger, trestle relic with ties | 2556 | 247 | head house cladding inside the floor girts (25 mm), ties into the trestle girts, a cross in the 0.3 m stub bay, short-face L1 braces still in the roof |
| 04 | cladding above the girts, ties to the girt face, no stub cross, no short-face braces at L1, bare collection names in the views | 2540 | 105 | first honest frame-only and close-up renders; slab edges 14 mm into the posts, ridge boards 6–10 mm into the last board row, rafter tails 10 mm into the cladding, tower cladding foot 9 mm into the shed ridge boards |
| 05 | slab strips notched at the posts with 50 mm bearing, ridge boards dropped, cladding tops under the tails at the cladding face, cladding foot over the ridge | 2586 | 0 | phase 1 converged |
| 06 | phase 2: boards between the posts, brace pattern from the interior and corner posts, void guards, steel seats, stair layout and voids, roof hole moved, door on the east gable | 3209 | 104 | bands reached the girt underside, 42 mm above the beam underside; seats as wide as the beams |
| 07 | bands to the beam underside, seats 30 mm narrower | 3197 | 0 | phase 2 converged |
| 08 | phase 3: braces removed, boards against the infill walls in slab-split bands down to the shed roof, interior boards everywhere, varied windows, stringers and landing posts, strips over the beams, ladder, outriggers on studs with knees and canopy, gable sticks removed, fixtures | 4576 | 589 | interior front boards ran 19 mm into the side walls, exterior front and side boards overlapped 11 mm at the post corners, plinths 9 mm into the shed's north interior boards; everything else read correctly, including the knee cut in the clapboard and the ladder on the girt |
| 09 | front boards between the side walls inside, side bays past the front boards outside, plinths 0.28 | 4576 | 0 | phase 3 converged |

## 10. Scope and known simplifications

Absent: interior partitions, bathrooms, kitchen, interior doors, window
frames and sash bars, the guard infill (the 100 mm sphere rule is not met by
two rails), fascias, soffits, gutters, flashing, membranes, insulation, the
deck fall, the tie-down system, hold-downs, shear sheathing, the joist lap
spacer, bolts and nails everywhere, the hopper, tank and chutes, the site.

Present only as texture: the boards (flat rows, no lap, no tongue), the
glazing and door leaves (slabs in the wall centre), the steel splice plates
and seats, the ladder rungs.

Plausible, not calculated: every section; the 5.3 m roof-hole headers are past
the prescriptive limit; the ground flight's 195.7 mm risers are within CMHC's
200 but above the London guide's 170 easy-access limit; the CLT strips are
100 mm 3-layer where How to CLT's housing table would say 200 mm for
acoustics; the terrace joists' 0.9 m cantilever with 38 x 235 at 600 is
inside the deck tables by inspection only; the tower has no rated lateral
system since the braces went.

Residual geometric approximations, in millimetres: ridge boards dropped 6.3
(shed) and 12.7 (head house); north joist and south joist 38 apart at the
lap; clapboard and cladding stop 5 under the rafter tails; slab notches 25
off the posts; exterior boards 25 inside the post face plane; interior gable
rows 2 under the rafters; the knee's clapboard cut 10 wider than the knee
each way; the shed gable boards unbacked above the plate.
