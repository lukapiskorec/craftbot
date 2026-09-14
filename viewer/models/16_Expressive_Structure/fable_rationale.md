# Experiment 16, Expressive Structure: design rationale

## 0. About this document

Written by CraftBot, the orchestrator of the Fable run of experiment 16, in Claude Code on 2026-09-14. Judgement agents (CraftBot, Designer, Builder) ran on Fable 5.1, model id claude-fable-5-1. Mechanical agents (Researcher, Inspectors, Runner) ran on Sonnet. Compiled from `brief.md`, `concept.md`, `sources.md`, `design_notes.md`, `version_notes.md` and the inspection files in `experiments/16_Expressive_Structure/Fable/`. Section 1 is the brief as first written; nothing in it was rewritten later.

## 1. Brief as understood

Build one small room, a single-variation run. The floor plan is square and the building stands twice as tall as it is wide, the proportion measured on the outside of the finished structure. One entrance, one door. Daylight enters only from high up, either through the roof or through a band of windows just under it; the Designer picks one of the two from the red building photos and records the choice. Every member is a thin timber slat: walls, floor, roof and the outer trusses alike are built up from slats, with no sawn heavy sections, no sheet material and no glass modelled beyond the openings. The three photos of the red timber building in `input/` (01-soane-front, 02-soane-outside, 03-soaneinterior-1) set the construction method, the slat sizes and the overall dimensions. The two other images (Erne_Dachbau_778, Tchumi-02) set only the articulation of the roof and the outer structure: a series of trusses whose outlines undulate from one to the next, so that the outside reads as an expressive, rippling structure while the room inside stays a plain square box. Nothing from the red building is preserved literally; its proportions are dropped where they conflict with the 2:1 rule, and the brief wins over the photos on that point.

Ambiguities resolved before any source was opened: the 2:1 rule applies to the outer structure, ridge to ground against outer plan width, and the room inside should still read as a tall shaft; light comes from one of the two options, not both; "slats" means built-up slat trusses, not solid sawn ones; the trusses are a series along the building with an outline that changes from one to the next; flat ground, no context.

Scope decisions at the concept check, appended by CraftBot the same day: the row of eleven ring trusses is 6.62 m long while the box is 4.36 m long, so two trusses at each end stand beyond the end walls and the door is reached through two open truss bays with no roof. One concrete raft, 7.20 x 7.20 x 0.25 m with its top at ground, is the single non-timber element, accepted as the modelled ground. The room inside comes out at about 2.9:1. The Builder could apply the concept's own fallback on truss panel length (0.80 to 1.00 m) only if one render-and-check pass took longer than 15 minutes; it never did.

## 2. How to run, and outputs

Render any version from the repo root:

```
"<blender 4.3>" --background --python tools/render_views.py -- "experiments/16_Expressive_Structure/Fable/experiment_16_fable_v04.py" "<abs repo>/experiments/16_Expressive_Structure/Fable/experiment_16_fable_v04_blender" --views "experiments/16_Expressive_Structure/Fable/views_fable.py" --lib "experiments/16_Expressive_Structure/input"
```

The script asserts the 2:1 rule, the corner and depth rule of every ring truss, the web reach, the splice rule, the brace angles and the two sections, and prints W_out, H_out and the ratio, the overlap check with its pair families and the contact check.

Views (`views_fable.py`): 01 to 04 orbits; 05 top; 06 front elevation with the door; 07 side elevation; 08 frame only (cover hidden); 09 from below; 10 camera matched to photo 01; 11 ring truss node close-up; 12 roof heel; 13 cross section at y = 0; 14 long section at x = 0; 15 plan section at 1.5 m; 16 inside looking up; 17 bracing X close-up; 18 door from inside; 19 ring apex over the box roof; 20 east elevation with the ring hidden; 21 low oblique along the row (the ripple and its diagonal crests); 22 ring eave corner at the shallowest depth; 23 ring apex close-up; 24 wall board joints; 25 box eave corner; 26 door leaf; 27 to 34 gable stud splice sections and close-ups; 35 outer spacers on the +x legs; 36 roof plan with the deck hidden; 37 inside looking up with the deck and box trusses hidden; 38 frame-only box with the ring hidden; 39 one roof X crossing from above; 40 section past that crossing.

Collections: Foundation (Raft); Floor (Joists, FloorBoards); Walls (Studs, Rails, Plates, BoardsIn, BoardsOut, DoorFrame); Door; BoxRoof (RoofTrusses, RoofDeck); Ring (RingChords, RingWebs, RingSpacers, RoofBracing); Bracing. Hide lists use bare collection names.

Counts: v04, the final version, has 3545 members (3544 timber pieces plus the raft), 0 penetrating pairs, 0 floating. The render-and-check pass takes 67 s for 40 views.

## 3. Reading the inputs

The Designer measured the red building on photo 01 with the external stair as the only object of known size (14 risers, about 2.4 m, about 105 px/m) and cross-checked with the board count on the far wall in photo 03 (31 boards at 130 to 140 mm give a 4.1 to 4.3 m room). The Erne and Tschumi images were read for type and behaviour only, never measured.

| Source | Rule taken | Number in the model |
|---|---|---|
| Brief | outer structure twice as tall as wide, square plan | W_out 6.62 m, H_out 13.24 m, ratio 2.0002 asserted within 0.01 |
| Photo 01, stair calibration | room width from the board count | 3.90 m clear (six 0.65 modules) |
| Photo 01, 03 (rule 4) | translucent band under an opaque roof, not a rooflight | open band from z 9.63 to the deck underside, about 2.2 m, all four walls |
| Photo 01, 02 (rule 2) | box in a separate frame, paired posts with single diagonals between | box and ring trusses separate, 0.082 m clear; chords paired, webs single |
| Photo 03 (rule 5, 6) | slat trusses under the deck; vertical boards with staggered joints | 7 box roof trusses; boards 120 wide, joints on alternate rails per column |
| Erne (rule 9) | built-up Warren trusses, paired chords sandwiching webs, about 1 m deep | ring trusses 120 mm thick, depth 0.33 to 0.93 m, webs 40 to 67 degrees |
| Tschumi (rule 10) | straight members whose projection varies smoothly, crests diagonal across the row | depth d(s, i) = 0.63 + 0.30 sin(2 pi s / 8.0 + 2 pi i / 11) |
| CMHC Table 22 p.287, FRIM Table 1 A7 | lumber subfloor 19 mm at 600 mm | floor boards B 24 x 120 on joists at 0.65 m, conservative |
| CMHC Table 35 p.305 | lumber roof sheathing 19 mm at 600 mm | roof deck F 30 x 120 flat on trusses at 0.65 m, conservative |
| CMHC Fig. 86 p.125, Table 36 p.306; FRIM Sheet 9 | heel bears over the wall plate; 1:6 is the low-slope threshold | bottom chord on the head plate, top chord on its arris; both roofs at 1:6, covering not modelled |
| CMHC p.94; FRIM Sheet 7 p.56 | built-up members nailed from each side at most 450 mm apart; splices staggered and plated | pairing rule for studs, joists and chords; splices on a support or node, staggered (named nailing) |
| CMHC p.109, APA p.15-16 | a 1.0 m opening needs one jack per side | kings at +/-0.65, doubled jacks for the module, header of four slats |
| CMHC Fig. 86; FRIM Ch. 6 Fig. 30 | braces at 45 degrees or steeper | y-bracing panels halved to 3.25 m so the X's stand at 59 to 61 degrees |
| FRIM Table 1 E2 | horizontal tie between trussed frames | ties at z 5.95 to 6.07 and 10 mm under the deck eave |
| FRIM Sheet 7 p.56 | post in a steel U-strap with two 12.7 mm bolts on a footing | named at 44 truss feet, not modelled |
| CMHC Fig. 47B p.79 | sleeper on the slab over polyethylene | joists as sleepers on the raft, polyethylene named |
| TRADA WIS 0-3 p.5 | cladding battens at most 600 mm | rails at 0.65 m, 50 mm over, kept for the one-module argument |
| external, marked (ledged-and-braced door) | braces from hinge-bottom to latch-top; board and ledge size ranges | leaf of B boards, three F ledges, two F braces at 34 degrees |

Deliberate deviations from the photos, each with its cause and the rejected alternative:

| From | In the model | Why, and what lost |
|---|---|---|
| Undercroft on heavy sawn posts, external stair | dropped; floor 0.144 above a raft flush with the ground, one step at the door | brief: thin slats only, flat ground, one entrance; a slat undercroft would add a storey and a stair |
| Box 1.5:1, overall 2:1 with the undercroft | outer structure 2:1, room 2.9:1 | brief overrides the photos on proportion |
| Scaffold with walkways, ladders and a corrugated band | 11 ring trusses, open band, no walkways | the trusses are the brief's own instruction from the other two images |
| Squat 0.8 x 0.75 m hatch with a sawn frame | 1.00 x 2.10 door with slat kings, doubled jacks, slat header | a usable door; no sawn sections |
| Frame bays about 1.1 m | trusses at 0.65 m | one module for studs, joists, roof trusses and ring trusses; 11 samples keep the ripple continuous (9 at 0.80 read as steps) |
| Shallow arched corrugated roof | 1:6 board gable, covering not modelled | no sheet material; the 1:6 fall is what a membrane would need |
| Erne's laminated curved chords | straight 0.8 m sandwich segments, mitred | box-and-prism vocabulary |
| Dado joint about 1 m up | none | the photo's joint is the head rail of its hatch; with a 2.10 door the line is the header at 2.24 |
| Red paint | not modelled | colour is not geometry |

Departures from the manuals, by instruction of the brief and recorded under the waived requirement R-32: sections 30 x 120 and 24 x 120 sit below any manual member (FRIM's thinnest structural member is 35 x 72); studs of 11.5 m against CMHC Table 25's 4.2 m ceiling; paired 60 x 120 posts below CMHC's 140 x 140 column minimum; the sandwich truss node and the clerestory band are extensions by analogy. Compensation is by pairing, rails every 0.65 m on both faces, ties to the ring legs at every rail, and the trusses rather than the studs taking the wind.

## 3b. Comparison round

The Designer's Inspector read v03 on the matched view 10, the orbits, the front elevation, the section, the look-up, the door view and the low oblique against all five images. No row called for a change; the one "fix" (the door leaf reading as a white slab in view 18) was over-exposure, since the v02 Inspector had confirmed boards, ledges and braces on view 26 and the geometry had not changed. The full table is in `inspection_v03_comparison.md` and `design_notes.md`.

| In the reference | In the model | Kept, with reason |
|---|---|---|
| Board box inside a separate scaffold, tied at rail levels | box inside 11 ring portals, gap visible all round | topology swap is the recorded deviation |
| Overall 2:1 with the undercroft | gate-shaped 2:1 silhouette | matches |
| Box 1.5:1 | room 2.9:1 | brief overrides |
| Band about 1.8 m | about 2.2 m | scaled with the shaft; 0.19 of the wall height against the photo's 0.30 |
| Dark opaque deck against a light band | deck opaque and closed, same tone as the walls | colour is out of vocabulary |
| Slat roof trusses visible from inside | chords and posts read against the deck | matches |
| Dado joint about 1 m up | board joints at 1.95 and 3.25 | the photo's joint belongs to its hatch |
| Ledged-and-braced door leaf | confirmed on view 26 | view 18 over-exposed, not geometry |
| Erne webs at 50 to 65 degrees, curved chords | 40 to 67 degrees, straight mitred segments | the 0.33 m minimum depth keeps the ripple's amplitude; straight segments are the vocabulary |
| Diagonal crests across the row | crest shifts truss to truss in view 21 | matches; a true side elevation cannot show a depth that varies toward the camera |

Matched view 10 against photo 01: the silhouette's proportion is close; what differs is what fills it, many thin members instead of a few bold ones, no undercroft, low colour contrast, all three decided.

## 4. Reading the reference code

No inherited script. The run started from `tools/experiment_template.py` and `tools/views_template.py` and used the `craftbot_lib`, `planes` and `framing` kits. Two helpers the Builders wrote inside the script are proposed for promotion after the run: `board_columns` (the under-40 mm remainder shared by the last two boards) and `enforce_max` (split a member at the support nearest the midpoint of any piece over stock length); also the `far` guard on a corner clip (apply a neighbour's face clip only when the member's far end satisfies it), which belongs next to `mitre_clip` in `planes.py`.

## 5. What had to change: construction logic settled before geometry

Two systems, not one. The Designer first tried the ring trusses carrying the box roof on their inner top chords, and it fails geometrically: the webs rise from the inner chord through any deck laid on it, in every sandwich arrangement drawn. Only a deck hung under the inner chord avoids the collision, and then the roof is a ceiling with no bearing for a covering. So the box carries itself with its own seven shallow slat trusses, and the ring trusses stand 0.08 m outside it and brace it. The red building has the same two-system logic, so the separation is also the more faithful reading.

The module. The outer structure has to be square in plan, otherwise "twice as tall as wide" has two answers. Ring trusses wrap the box in one direction only, so the row's length has to match the trusses' width, about 6.6 m. Ten bays of 0.65 give 6.5 m between end planes, six bays give the 3.90 m room, so studs, floor joists, roof trusses and ring trusses share one module and one origin. Consequence: two trusses at each end stand past the end walls, which is the entrance porch.

The truss plane. With one web plane the two webs meeting at a node collide. A 60 mm gap between the chord slats gives the rising webs and the falling webs their own 30 mm plane, each nailed to the chord slat on its side; gusseted nodes lost because there is no sheet material.

Bracing along the row. The braces between ring legs cannot lie on the outer chord (it ripples) or inside the truss depth (webs). They lie flat on the legs' inner faces in the gap, as X's with halving joints and horizontal ties. The Researcher's 45-degree rule forced the panels to half the row's length so the X's stand at 61 degrees.

## 6. Core modelling decisions

Light from the band, not the roof. Both red-building photos show an opaque deck and light only from the side, and a rooflight would sit under the ring trusses' top chords and be shaded by them. Rejected: a rooflight; band plus rooflight (the brief says one of the two).

The ripple rule. The inner chord stays straight (it is what the box ties to and what stands on the shoe); only the depth varies, d = 0.63 + 0.30 sin(2 pi s / 8.0 + 2 pi i / 11) along the arc length s of the inner outline. Depth 0.33 to 0.93 m: the minimum keeps the webs steeper than 40 degrees on a 0.8 m panel, the maximum is what fits a 6.62 m outer width. Wavelength 8 m: 1.5 waves per leg and half a wave over the top, an arc like Erne's rather than a serration. Phase 1/11 of a turn per truss: adjacent trusses differ by at most 0.17 m and the crest crosses the side elevation diagonally, which is the Tschumi effect. Rejected: a ripple in the inner chord too; a wave symmetric about the apex (kills the diagonal travel); amplitude 0.20 (a 0.4 m ripple on a 6.6 m elevation is hard to see).

Mitred corners, not chamfered. The concept's first node rule put outer vertices only at half-panel points, so the outer chord cut across each corner, and at eight of the 22 eave corners (depth under 0.49 m) it passed through the inner chord. v02 added an outer vertex on each corner's bisector at the offset-polygon position, a mitred kink with no web to it. Rejected: a minimum depth of 0.50 (halves the ripple, moves every tuned number, and still leaves a chamfered shoulder); a web to the corner vertex (no free web plane at a corner node).

Apex webs. At a corner node each web is clipped to stay inside the other run's outer face. Right at the eaves, wrong at the apex, where the other slope's face extended passes under the web body and left 22 webs as 0.27 m stubs through v01 and v02. Both checks were blind to it: a stub overlaps nothing and touches its chord. The v02 Inspectors caught it as the "dark artefact" the v01 Builder had written off. v03 applies the clip only when the web's far end satisfies it and asserts the reach of every web.

Door 1.00 x 2.10 with doubled jacks. The module gives 1.12 clear between single jacks on the +/-0.65 kings; doubled jacks bring it to 1.00. Header of four slats on edge. The leaf is ledged and braced, hung on the +x jamb, modelled open into the room and touching the wall so the contact check sees it.

Eave slot open. The 0.24 m gap between the side wall head plate and the deck underside stays open between the roof truss heels. Photo rule 4 has the band directly under the roof, and inside the trusses stand in the band. The diaphragm reaches the side wall through the heels, not through any board in the slot. Rejected: a board fascia between heels (about 60 pieces unlike the photos).

Splices. Slats over 4.80 m split on a rail centre or a truss node, the two slats of a pair at least one module apart on studs and two panels apart on chords. Gable studs got two cuts at 3.25 and 7.80 on the B slat after the first rule's third cut at the sill rail landed 0.47 m from the A splice.

The raft. One concrete element, the modelled ground. Rejected: 22 pads plus a slab; no foundation.

## 6b. Independent structural improvements

The Designer's review of v03 with the structural-logic checklist, reference set aside. Vertical load paths close to the raft for every family; across the trusses the eleven rings are trussed-corner portals (the mitred corner vertex and the webs to both neighbouring outer vertices make the corner a truss); along the row the two braced planes reach the eave. Bearings and discontinuities walked: door header on jacks, the deck reaching the side wall through seven heels on the head plate, four-slat corner posts at the gables.

Two findings, both actioned in v04:

1. Weak-axis restraint of the ring chords. The outer chords, 28 m of paired 30 mm slats per ring, were restrained out of their plane by nothing between the raft and the raft; the inner top chords over the roof likewise. In a built Erne roof the purlins do this job; here the ripple forbids a straight purlin, but short spacers between adjacent trusses need not be straight across the row. P2-01: F 30 x 120 spacers between the facing chord slats of adjacent rings at every third outer vertex and at every inner node of the top runs. Rejected: purlins over the outer chords (cannot lie on a rippling surface); nothing.
2. Stability along the row above the upper tie. With the spacers the eleven tops become a grid, and a grid without diagonals holds only by chord bending. P2-02: one zigzag of F diagonals per roof slope, laid flat under the inner top chords in the 0.07 m gap, eave line to apex line over three bays, plus its mirror. Rejected: diagonals on the outer chords (the ripple); diagonals under the deck inside the box (the inside stays plain).

Recorded, not modelled (P2-03): steel shoes and hold-downs at 44 feet, FRIM's 50 mm footing upstand, polyethylene under the joists, a gutter at the 1:6 eaves, all nailing. Considered and not changed: the box roof trusses' 0.12 m heel depth on a 4.25 m span; the open eave slot; the porch bays' free trusses; the 60 x 120 studs at 11.3 m, restrained every 0.65 m and not asked to take the wind.

## 7. Detailed geometry numbers

Coordinates: origin at the plan centre on the raft top, z up; x across the trusses, y along the row; door in the -y wall.

| Item | Value | Source |
|---|---|---|
| Raft | 7.20 x 7.20 x 0.25, top at z = 0 | Designer |
| Module | 0.65 m | Designer (6 x 0.65 = 3.90; 10 bays = 6.50) |
| Room clear | 3.90 x 3.90 | brief, photo 03 board count |
| Wall build-up, from the plan centre | boards 1.950 to 1.974, inner rails to 2.004, stud zone to 2.124, outer rails to 2.154, outer boards to 2.178 | Designer |
| Studs | paired F 60 x 120 at 0, +/-0.65, +/-1.30, +/-1.95 plus end studs; end walls drop the +/-1.95 stud into the end stud | Designer, v01 |
| Rails | both faces at 0.65 k, k = 1..14, plus bottom, sill (9.51 to 9.63) and head rails | Designer |
| Boards | vertical B 24 x 120 from the bottom rail to 9.63, joints at 1.95 and 5.85 (B columns) or 3.25 and 7.15 (A columns) | photo rule 6 |
| Floor | 7 paired joists running x on the module, boards running y, top at 0.144 | Designer |
| Door | opening 1.00 x 2.10 at x = 0, sill 0.144, header 2.244 to 2.364 of four F on edge, kings at +/-0.65, doubled jacks | Designer, CMHC |
| Box roof trusses | 7 at y = 0, +/-0.65, +/-1.30, +/-1.89; bottom chord level on the side head plates; 1:6 top chords with tails to x = +/-2.22; king, queens at +/-1.06, two diagonals | Designer, v01 derived |
| Deck | F 30 x 120 flat running y, 19 whole boards per slope from x = +/-2.249 to the apex, one piece from y = -2.28 to 2.28 | v01 derived |
| Side wall head plate | z_h = z_e - 0.37 = 11.484 | rule, tuned |
| Ring trusses | 11 planes at y = -3.25 + 0.65 i; inner chord centreline (-2.32, 0) to (-2.32, z_e) to (0, z_e + 0.387) to (2.32, z_e) to (2.32, 0); plane 120 thick, chords at +/-(0.03 to 0.06), webs in +/-(0 to 0.03) | Designer |
| Ring depth | d(s, i) = 0.63 + 0.30 sin(2 pi s / 8.0 + 2 pi i / 11), 0.33 to 0.93 | Designer |
| Panels | legs 15 of 0.7965, each top half 3 of 0.784; outer vertices at half panels, feet and corners | Designer, v02 |
| z_e | 11.854 (bisection on the outer-face polyline of all 11 trusses) | tuned to the 2:1 rule |
| W_out, H_out | 6.6207 (x 6.621, y 6.620), 13.2426, ratio 2.0002 | asserted |
| Y-bracing | X's in x = +/-(2.230 to 2.260), panels y -3.25..0 and 0..3.25, z 0.15..5.95 and 6.07..11.575; angles 59.4 to 60.7; ties 5.95 to 6.07 and 11.575 to 11.695 | Designer, CMHC and FRIM 45-degree rule, v01 derived |
| Splices | side wall studs A 4.55/9.10, B 2.60/7.15; gable studs and cripples A 4.55/9.10, B 3.25/7.80; leg chords A nodes 6/12, B nodes 4/10 | Designer answer 5 |
| Longest piece | 4.743 m | script |
| Chord spacers | F 30 x 120 bars between the facing chord faces of adjacent rings (y_i + 0.06 to y_i+1 - 0.06), 10 bays; outer chord at every third vertex counted from the apex both ways, 13 per bay from z 1.19 up; inner top chords at all seven nodes including both eave corners; 200 in all; inclined by at most 18 degrees where the depth differs; axis shifted inward so the outer edge never leaves the chord's outer face | Designer phase 2, v04 |
| Roof-plane X's | per slope three panels of three bays (trusses 0-3, 3-6, 6-9), a rising and a falling diagonal each, laid flat in the 30 mm layer under the inner top chord underside, halving joint at the crossing (three boxes per diagonal), 12 diagonals of 3.06 m, plan angle 50 degrees, underside 0.039 above the deck top; bay 9-10 unbraced | Designer phase 2, v04 |

## 8. Verification

What the checks prove: no two timber pieces penetrate each other by more than 1 mm (overlap check, 0 pairs from v02 on); every piece touches another piece or the raft (contact check, 0 floating in every version); the 2:1 rule, the square plan, the ring depth at sampled nodes, the corner vertex positions, the web reach, the splice rule, the brace angles, the joist and truss spacing and the two sections hold as script assertions. The Inspectors confirmed by eye what the checks cannot: the Warren zigzag continuous through every apex on all eleven trusses, the staggered board joints, the door leaf detail, the mitred eave corner at the shallowest depth, the open eave slot and the porch bays.

Not verified: structural adequacy of any member (every section is "plausible for its span, not calculated", and all of them sit below manual sizes by the brief's instruction); the nailed and bolted connections, named throughout and modelled nowhere; the steel shoes and hold-downs at the 44 truss feet; overturning of a 13.2 m tall frame; the roof covering, its drainage and the footing upstand; the ties between the box and the ring legs at rail levels, named and not modelled. The stub check the v02 Inspectors performed by eye is a gap in the tools: a member whose vertex span is far short of its intended length passes both checks. Residual approximations: the outer chord is faceted at 0.8 m against Erne's continuous curve; the corner vertex is an unbraced kink about 0.4 m from its neighbours each way; the end roof trusses sit 60 mm inside their stud line, spread by the head plate.

Cost, from the task notifications (context at return, tool calls): Designer concept stage 179k, 46 calls; Researcher (Sonnet) about 240k, 78; Runner 15k standing by, then 18k, 21k, 24k per version close-out at 2 calls each; Builder v01 234k, 58; fresh Designer for the eight v01 questions 81k, 10; Builder v02 207k, 51 (including two Inspectors); Builder v03 first attempt cut off by a usage limit after patching the script, restart 162k, 54; Designer phase 2 (resumed) 229k, 61, with its comparison Inspector about 89k, 25; Builder v04 256k, 59, with Inspectors of 98k (23 calls) and 109k (27); fresh Designer for the v04 count questions 38k, 8 (it confirmed 7 inner spacers per bay and 12 roof diagonals as built and corrected the two requirement lines, so no v05). One usage-limit cut-off in the run. Summed over the run: three Builder returns plus the cut-off at about 860k of context, the Designer at 490k over three returns, four Researcher and Inspector spawns on Sonnet at about 640k, the Runner under 30k per call.

## 9. Iterations table

| Version | Change | Members | Pairs | Floating | What the renders or checks showed |
|---|---|---|---|---|---|
| v01 | everything in the concept from the template; full set of 20 views | 3248 | 32 | 0 | all 32 pairs one cause: the outer chord's chamfer cut the inner chord's eave corner on the eight corners under 0.49 m depth; over the threshold, no Inspector; a "dark artefact" at the apex noted and written off |
| v02 | mitred corner vertex on every outline corner; z_e re-tuned 11.948 to 11.854; views 22 to 26 | 3310 | 0 | 0 | first inspected version: the apex artefact is 22 web stubs from a clip wrong at the ridge; everything else zoom, closed by the close-ups; Designer's eight answers landed mid-version |
| v03 | far-end guard on the corner clip, reach assertion over 792 webs; gable stud splices at 3.25/7.80; restart after a usage cut-off; views 27 to 34 | 3309 | 0 | 0 | zigzag continuous through every apex; splices read one per frame; phase 1 converged |
| v04 | P2-01 chord spacers between adjacent rings (200), P2-02 roof-plane X's (36 pieces); views 35 to 40 | 3545 | 0 | 0 | clean at the first render; spacers and X's as specified, none above the outer chord, none in the box; W_out and H_out unchanged to 0.1 mm; the Builder found the requirement lines' counts (6 inner spacers per bay, 16 diagonals) wrong against their own rules and built the rules (7 and 12) |

## 10. Scope and known simplifications

Modelled: the raft, the floor, four layered walls with the door and its leaf, the box roof with seven slat trusses and a board deck, eleven ring trusses with the ripple rule, the bracing along the row, and from v04 the chord spacers and roof-plane diagonals. Not modelled by the brief's rule against sheet material and glass: the roof covering, glazing in the band, any lining. Not modelled by vocabulary: nails, bolts, plates, shoes, hold-downs, polyethylene, gutters, paint. Simplifications: the concrete raft stands in for ground and foundation; the curved chords of the Erne trusses are 0.8 m straight segments; the roof drains over an open eave slot into the gap with no gutter; the box-to-ring ties at rail levels are named connections, not pieces. The sections are the brief's thin slats and no manual validates them; the compensations are pairing and close restraint, argued in section 3 and never calculated.
