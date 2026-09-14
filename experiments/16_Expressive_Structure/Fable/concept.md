# Concept, experiment 16, Fable run

Every number the Builder needs is here. A number carries its source in brackets: (brief), (photo rule N), (manual clause, as returned by the Researcher and folded into section 4), or (mine) for my own derivation. The Builder never opens `sources.md`.

Coordinates: origin at the centre of the plan on the raft top, z up. x runs across the trusses (the direction the trusses span), y runs along the row of trusses. The door is in the wall facing -y.

## 1. Spatial concept

One room, a square shaft, 3.90 x 3.90 m clear and 11.4 m from floor to the underside of its roof trusses (mine, from the 2:1 rule and the section stack in 3.4). The proportion inside is about 2.9:1, which is the tall shaft the brief asks for; the red building's own room is 1.5:1 with the light band, and its overall silhouette with the undercroft is 2:1 (photo rule 3).

Floor at z = 0.144 on a concrete raft whose top is the ground (z = 0). One door, 1.00 x 2.10 m, centred in the -y wall, threshold one step above the raft. No stair, no terrace, no undercroft.

Light: a continuous open band under the roof on all four sides, from z = 9.63 (top of the wall boards) up to the roof deck's underside: on the side walls to about z = 11.80, the head plate a transom across the band and the 0.24 m slot above it open between the roof truss heels; on the gables to the sloped head plate. About 2.2 m tall (photo rule 4: the red building's 1.8 m translucent band sits directly under an opaque roof; photo rule 3 for the scaling; v02 decision in design_notes.md). This is the "windows close to the roof" option. The roof option loses because both red-building photos show an opaque deck and light only from the side, and because the ring trusses pass over the roof and would shade a rooflight anyway. The band is modelled as open framing (mullions and rails); no glass, per the brief.

Outside the box, at 0.08 m from its faces, stands the row of 11 ring trusses that gives the building its outer figure. Two of them at each end stand beyond the end walls, so the entrance is reached through two open truss bays (a 1.3 m deep porch under the trusses' top chords; no roof over it, the box roof stops at the box). The outer structure's plan is 6.62 x 6.62 m over the outermost slat faces and its top is 13.24 m above the raft, i.e. 2:1 (brief).

```
Section across the trusses (x-z), not to scale

            ___..--''''''''''--.._     <- outer chord, rippling (d = 0.33 to 0.93)
         .-'   / \ / \ / \ / \    '-.
        /   __/___\_/___\_/___\__   \   <- inner chord, 1:6 gable, straight
       |   |   box roof trusses  |   |
       |   |  ----- band -----   |   |   z 9.63 to 11.5, open
       | / |                     | \ |
       |/  |    red board box    |  \|   <- webs between inner and outer chord
       |   |     3.90 clear      |   |
       | \ |                     | / |
       |  \|                     |/  |
     __|___|_____________________|___|__  raft, z = 0
        ^                         ^
     ring leg                  ring leg
```

```
Plan, not to scale (y along the row, door at -y)

   y = -3.25 -2.60 -1.95 -1.30 -0.65  0  0.65 1.30 1.95 2.60 3.25   <- 11 truss planes
        |     |     |     |     |    |   |    |    |    |     |
        |     |   +-------------------------------------+     |
        |     |   |                                     |     |
        |     |   |          room 3.90 x 3.90           |     |
        |     |   |                                     |     |
        |     |   +----------------+ +------------------+     |
        |     |            door 1.00 wide at x = 0           |
      porch bays                                          porch bays
```

## 2. What comes from where

| Image | Role | Taken |
|---|---|---|
| 01-soane-front | construction, proportion, calibration | box in a separate slat frame; paired posts with diagonals between; translucent band under opaque roof; box 1.5:1, overall 2:1; frame bays about 1.1 m |
| 02-soane-outside | construction detail | paired posts, single diagonals passing between the pair, box tied to the frame at rail levels |
| 03-soaneinterior-1 | interior topology | plain boarded shaft, vertical boards with staggered joints, low dado joint, light band under a dark deck carried by slat trusses, one small door |
| Erne_Dachbau_778 | truss articulation only | built-up Warren trusses: paired chords sandwiching single webs, curved chords, depth about 1 m, webs at 50 to 65 degrees |
| Tchumi-02 | surface articulation only | rippling surface from straight parallel members of varying projection, crests running diagonally across the row |

## 3. Construction concept

### 3.1 The two systems

Two separate timber systems, as in the red building (photo rule 2): a self-supporting boarded box, and an exoskeleton of 11 ring trusses standing 0.08 m outside it. The box carries its own floor, walls and roof to the raft. The trusses carry themselves and brace the box; the box is tied to the truss legs at every rail level. Keeping them separate is what lets the trusses ripple while the inside stays a plain box, and it avoids the collision a shared roof would cause (webs rising from a chord that also carries a deck).

### 3.2 Slat family (mine, to be checked by the Researcher; section 4 records the verdict)

Two sections only, both thin, no other timber in the model:

- F, framing slat, 30 x 120 mm: studs, rails, plates, joists, chords, webs, braces, deck boards of the roof, door ledges.
- B, board, 24 x 120 mm: wall boards inside and out, floor boards, door boards.

Capacity comes from repetition, never from a bigger section: paired slats face to face for studs and joists (60 x 120), paired slats with webs between them for truss chords (the sandwich of photo rule 2 and Erne). Slat length 4.80 m maximum; splices land on a support (a rail centre, the sill rail included) or a truss node; in a pair the two slats' splices are at least one module (0.65 m) apart on studs and two panels apart on chords (v02 wording; v01 said "half a length"). Nailed and bolted throughout, no carved joints.

### 3.3 Bearing stack, ground to roof

1. Raft: concrete, 7.20 x 7.20 x 0.25 m, top face at z = 0, centred (mine; the one non-timber element, it stands in for the ground). Truss legs stand on it in steel shoes with hold-down bolts (named, not modelled). Wall bottom plates lie on it.
2. Floor: joists = paired F on edge (60 wide x 120 deep), running x from x = -2.004 to +2.004 (stud face to stud face; the inner lining starts on top of the floor), at y = -1.95 + 0.65 k, k = 0..6 (7 joists, on the 0.65 module shared with the studs and the trusses). Floor boards B laid flat across the joists, running y, from y = -2.004 to +2.004 and x = -2.004 to +2.004, no gaps. Floor top z = 0.144 = 0.120 joist + 0.024 board.
3. Walls: four walls, 0.228 m thick, room clear 3.90 (inner board faces at +/-1.950). Build-up from inside, distances from the plan centre: inner boards B 24 (1.950 to 1.974), inner rails F 30 laid with the 30 through the wall (1.974 to 2.004), stud zone 120 (2.004 to 2.124, stud centreline 2.064), outer rails F 30 (2.124 to 2.154), outer boards B 24 (2.154 to 2.178). Outer face at 2.178. Studs = paired F face to face (60 x 120) on the 0.65 module: side walls (normal x) at y = 0, +/-0.65, +/-1.30, +/-1.95, plus an end stud at each end of each wall; end walls (normal y) at x = 0 (removed at the door), +/-0.65, +/-1.30, +/-1.95, plus end studs. Side walls run through in y, end walls fit between them. Bottom plate F flat, 30 x 120, on the raft under the stud zone. Rails on both faces at z centres 0.65 k for k = 1..14, a bottom rail (inner: 0.144 to 0.264 on the floor; outer: 0.000 to 0.120 on the raft), and a sill rail 9.51 to 9.63 under the top of the boards. Boards vertical, 24 x 120, from the bottom rail to z = 9.63, lengths at most 4.80, joints on rail centres, adjacent boards alternate two joint patterns (A: joints at 3.25 and 7.15; B: joints at 1.95 and 5.85) so no two neighbours share a joint (photo rule 6).
4. Band: above z = 9.63 the studs continue as bare mullions to the head; a head rail F on both faces directly under the head plate. Nothing between mullions (glass not modelled).
5. Wall heads. Side walls: level head plate F flat, top at z_h = z_e - 0.37 (11.484 as built in v03 with the mitred apex; 11.578 in v01; see 3.6 for z_e). The 0.24 m slot between the side wall head plate and the deck underside stays open between the roof truss heels, no boards, no fascia (v02 decision: it is part of the light band, section 1). End walls: gable walls, studs cut to the slope, sloped head plate F under the roof deck, top face on the deck underside plane (3.3.6); the end walls carry the deck edge directly.
6. Box roof: 7 shallow slat trusses, five at y = 0, +/-0.65, +/-1.30 over the studs (vertical alignment, one module) and the end pair at y = +/-1.89, pulled in 60 mm so the outer slat face is flush with the end wall's inner board plane at 1.95 (at 1.95 the truss would cut the end wall's inner head rail and the gable studs; v01 derived constant 1; deck spans at the ends 0.59 and 0.17). Each: bottom chord paired F sandwich (30 + 60 gap + 30 = 120 thick, 120 deep) level on the side wall head plates from x = -2.124 to +2.124 (the stud zone); two top chords, same sandwich, at 1:6 from the heel to the apex at x = 0, the top chord's underside passing through the bottom chord's top outer arris at x = +/-2.124 (arris bearing), tails ending at x = +/-2.22 (0.096 past the head plate, clear of the brace plane at 2.230); webs F single: a king post at x = 0, queen posts at x = +/-1.06, two diagonals from the bottom chord's centre node up to the top chords at x = +/-1.06. Deck: F 30 x 120 laid flat, running y across the trusses (span 0.65), from y = -2.28 to +2.28 (one piece each), on both slopes from the eave at x = +/-2.249 to the apex: 19 whole boards per slope, 19 x 0.120 along the slope = 2.249 in plan, no ripped board (the ring legs' inner face is at 2.26, so the v01 concept's 2.28 ran 20 mm into every leg; v01 derived constant 2). Overhang past the wall face 0.071. Deck underside plane (the top chords' top face, extended): z = z_h + 0.242 + (2.124 - |x|) / 6. Deck top at the eave edge (x = 2.249) z_h + 0.251, at the apex z_h + 0.626. Boards laid across the trusses and nailed at every chord act as the roof diaphragm together with the box; covering and drainage are not modelled (brief: no sheet material); the 1:6 fall to both eaves is what a membrane would need.
7. Ring trusses, the outer structure: 11 planes at y_i = -3.25 + 0.65 i, i = 0..10. See 3.6.
8. Door: opening 1.00 wide x 2.10 tall through all wall layers, centred at x = 0 in the -y wall, sill at the floor (z = 0.144), head at z = 2.244. Framing in the stud zone: king studs at x = +/-0.65 (the module studs), jacks doubled inside them (2 x 60 = 120 each side) to bring the module opening down to 1.00; header of four F on edge side by side (120 x 120) on the jacks from z = 2.244 to 2.364; cripples above at the module up to the head. Rails and boards on both faces stop at the opening. Leaf: ledged and braced, B boards vertical on three F ledges (at 0.25, 1.05 and 1.85 above the sill) and two F braces (each from the hinge side of a lower ledge to the free side of the ledge above, about 34 degrees to the horizontal as the ledge spacing sets it; the 45 degree rule for building bracing does not apply to a door leaf), 1.00 x 2.10 x 0.054, hung on the +x jamb, modelled open 90 degrees into the room (brace direction and size ranges from the external row in section 4).

### 3.4 Section stack (z, mine unless noted)

| z | what |
|---|---|
| 0.000 | raft top, ground, truss feet, wall plates |
| 0.144 | floor top, door sill |
| 0.65 k | wall rails, k = 1..14 |
| 2.244 to 2.364 | door header |
| 9.51 to 9.63 | sill rail; 9.63 = top of wall boards (photo rule 4: band about 1.8 to 1.9 m) |
| z_h = z_e - 0.37 (11.484 built, v03) | side wall head plate top, bottom chord of box roof trusses on it |
| z_h + 0.12 | bottom chord top |
| z_h + 0.25 to z_h + 0.63 | deck top, eave edge to apex |
| z_e (11.854 built, v03) | ring truss inner chord eave node (centreline) |
| z_e + 0.387 | ring truss inner chord apex node (centreline) |
| 2 x W_out (expected 13.24) | highest slat face of the outer chords |

### 3.5 Lateral system, per direction

- Across the trusses (x): each ring truss is a portal whose corners are trussed (chords continuous around the eave, webs continue), so the 11 rings are 11 moment frames. The box's side walls are tied to the legs at every rail (bolts through the outer boards into the leg's inner chord, named, not modelled). Load path: wind on a side wall -> studs -> rails -> ties -> ring legs -> trussed corners and feet -> raft.
- Along the row (y): the rings are thin planes and need bracing between them. Diagonal braces F 30 x 120 in the gap between the box and the legs, lying flat against the legs' inner faces, in the plane x = +/-(2.230 to 2.260), 0.052 clear of the wall face (v01 derived constant 3; the v01 concept's 2.198 to 2.228 left 32 mm to the leg face). Per side four X's in four panels: y from -3.25 to 0 and from 0 to 3.25, z from 0.15 to 5.95 (lower tie underside) and from 6.07 (lower tie top) to the upper tie underside; each X is the two diagonals of its panel (corner to corner), so 8 diagonals per side, 16 in all, each about 6.5 m long at about 60 degrees to the horizontal (CMHC Fig. 86 and FRIM Fig. 30 both want braces at 45 degrees or steeper; one X across the whole row would sit at 42 degrees, which is why the panels are half the row). Halving joint where the two diagonals of an X cross (three boxes, as in the timber-framing skill); each diagonal spliced once at a leg crossing (4.80 + rest), the splice landing on a leg. Horizontal ties F in the same plane from y = -3.25 to 3.25: the lower at z = 5.95 to 6.07, the upper with its top face 10 mm under the deck underside at the eave edge, z = 11.575 to 11.695 with z_h = 11.484 in v03 (11.669 to 11.789 at the v01 z_h of 11.578; v01 derived constant 4; the v01 concept's 11.75 to 11.87 cut the deck eave and the ring's corner mitre) (FRIM Table 1 item E2, horizontal brace tying trussed frames). Every diagonal and tie is nailed to every leg it crosses (named, not modelled). Load path: wind on an end wall -> end wall studs -> box roof deck (boards nailed at every chord act as the diaphragm) and the rails -> side walls -> ties to the legs -> braced planes -> feet -> raft. The braced planes reach the eave, so they serve the whole height.
- The box itself: boards nailed to rails and studs on both faces make each wall a shear panel; the floor is on the raft.

### 3.6 The ring trusses and the ripple rule

Plane thickness 120 mm: chord slats at y_i - 0.060 to -0.030 and +0.030 to +0.060; webs in two planes, rising webs at y_i - 0.030 to 0.000, falling webs at 0.000 to +0.030, so the two webs meeting at a node never share a plane. Chord slats F 30 x 120 with the 120 in the truss plane; webs F 30 x 120 likewise.

Inner outline (chord centreline), the same for every truss: (-2.32, 0) -> (-2.32, z_e) -> (0, z_e + 0.387) -> (2.32, z_e) -> (2.32, 0). The 1:6 gable matches the box roof. Inner chord inner face at 2.26, i.e. 0.082 outside the wall face (2.178), room for the y-braces. The inner chord's underside clears the box deck top by about 0.06 at the eave and the apex when z_h = z_e - 0.37.

Arc length s along the inner outline from the left foot (s = 0) to the right foot (s = 2 z_e + 4.704). Truss depth, centreline to centreline, measured along the outward normal:

    d(s, i) = 0.63 + 0.30 * sin(2 * pi * s / 8.0 + 2 * pi * i / 11)      i = 0..10

so d runs from 0.33 to 0.93 m (mine: Erne's trusses are about a metre deep; 0.33 is the least depth that keeps the webs steeper than 40 degrees at a 0.8 m panel). Wavelength 8.0 m along the outline: about 1.5 waves per leg and a little over half a wave across the top, an arc rather than a crenellation. Phase advance 1/11 of a turn per truss: the crest travels one full wavelength across the row, adjacent trusses differ by at most 0.17 m, and the crests run diagonally across the side elevations as in the Tschumi image.

Nodes: inner nodes at the four corners of the outline plus equal subdivisions of every straight run into panels of at most 0.80 m (legs: 15 panels; each half of the top: 3 panels). Outer vertices at every half-panel position and at both feet: Q(s) = P(s) + n(s) d(s, i), n the outward unit normal of the run the point lies on. Outer vertices also at the three outline corners (both eaves and the apex), on the corner bisector at the offset-polygon position Q_c = P_c + (n1 + n2) d(s_c, i) / (1 + n1 . n2), n1 and n2 the outward normals of the two runs; no web reaches a corner vertex, both web planes are taken at the corner node. The outer chord is the polyline through the outer vertices, one straight sandwich pair per segment, consecutive segments mitred on the bisector plane at their shared vertex, so the outline's corners are mitred by the outer chord (v02; the v01 chamfer cut the inner corner wherever d < 0.49, see design_notes.md). Webs: a Warren zigzag, inner node -> next outer vertex -> next inner node, alternating planes, ends inset so no corner crosses the far face of the chord it lands in. Both chords reach z = 0 at each foot.

Overall size rule (brief): W_out = the larger of the plan extents of the outer structure over slat faces (x: outer chord faces at the deepest point, expected 2 x 3.31 = 6.62; y: end truss faces, 2 x 3.31 = 6.62); H_out = highest slat face of the outer chords; H_out = 2.00 x W_out within 1 percent. The Builder measures both on the generated geometry and tunes z_e (11.854 built in v03; 11.948 in v01 before the mitred apex) until the ratio holds; z_h follows as z_e - 0.37. Nothing else moves.

### 3.7 Estimated piece count (mine)

Ring trusses about 11 x 162 = 1780; box about 1400 (studs and splices 170, rails 140, boards 660, floor 50, roof trusses 100, deck 80, door 20, plates and heads 20); braces and ties 20. About 3200 pieces. If the render or check loop cannot carry it, the first reduction is the panel length 0.80 -> 1.00 (about 1450 truss pieces); the count of trusses and the module stay.

## 4. Rules from the Researcher

Verdict table and rows in `Fable/sources.md`; snippets in `references/` (named `manual_<manual>_p<page>_<what>.png`, captions in `references/captions.md`). What the Builder needs from them is here.

Confirmed (the concept stands):

- Floor board B 24 at 0.65 m joist spacing: CMHC Table 22 (p. 287) minimum lumber subfloor 19 mm at 600 mm; FRIM Table 1 A7 floor board 22 x 145 at 610 mm centres. Conservative.
- Roof deck F 30 flat at 0.65 m truss spacing: CMHC Table 35 (p. 305) minimum lumber roof sheathing 19 mm at 600 mm. Conservative. Boards up to 184 wide get 2 nails per support (CMHC Table 23), named.
- Roof heel: the bottom chord bears directly over the wall on the head plate, the top chord seated on the bottom chord's arris (CMHC Fig. 86, p. 125, heel bearing over the exterior wall plate; FRIM Sheet 9 shallow gable truss on a wall plate).
- 1:6 pitch: exactly CMHC's threshold for low-slope covering (Table 36, p. 306); at or below it a full membrane is required. Covering not modelled (brief); the note stands in the deviation table.
- Door opening: CMHC p. 109 and APA p. 15-16 both need only a single jack per side at 1.0 m; the doubled jacks are for opening size (module 1.12 -> 1.00), not for load. Kept.
- Diagonal braces at 45 degrees or steeper (CMHC Fig. 86; FRIM Ch. 6 p. 41, Fig. 30): the y-bracing panels were halved to 3.25 m wide so the X's stand at 61 degrees (section 3.5). Horizontal ties between trussed frames: FRIM Table 1 E2.
- Built-up members: nail from each side, rows at most 450 mm apart, end nails 100 to 150 mm from the ends (CMHC p. 94); splices in a pair staggered and plated (FRIM Sheet 7 bearer splice 2/30 x 194 x 440 bolted at 110). Named, not modelled; the geometry rule (splices staggered, on a support or node) is in 3.2.
- Truss feet: post in a steel U-strap (6 x 100) with 2 bolts 12.7 mm on a concrete footing (FRIM Sheet 7, PDF p. 56). Named, not modelled. FRIM wants the footing top 50 mm above ground; the raft top here is the modelled ground, so the upstand is not modelled and is recorded.
- Floor on the slab: CMHC Fig. 47 B, sleeper directly on the slab over polyethylene. The floor joists are that sleeper; the polyethylene is named, not modelled.

Outside the manuals (recorded as departures, the load-path argument stands in for the table):

- Sections F 30 x 120 and B 24 x 120: no manual states them; FRIM's thinnest structural members are 35 x 72 (truss) and 47 x 72 (studs). The brief demands thin slats; the pairing rule in 3.2 is the compensating device. The line "plausible for the span, not calculated" applies to every member.
- Stud height 11.5 m: CMHC Table 25 stops at 4.2 m. The studs carry a light roof only, are restrained in the weak direction every 0.65 m by the rails on both faces, and in the strong direction by the ties to the ring legs at every rail; the ring trusses, not the studs, take the wind. Recorded as beyond the tables.
- CMHC minimum column 140 x 140 (p. 94): the paired 60 x 120 studs sit below it; roof load per stud is a few hundred newtons.
- Rail spacing 0.65 m against TRADA WIS 0-3 (p. 5) maximum batten spacing 600 mm for board-on-batten cladding: 50 mm over, with boards 24 thick instead of TRADA's 19 to 22. Kept for the one-module argument; recorded.
- The sandwich truss node (paired chords, single web between): no manual draws it. Nailing by analogy to CMHC's built-up beam rule and FRIM's gusset nail spacing (46 along, 23 across grain, 16 edge). Named, not modelled.
- Clerestory band framing: no manual draws a continuous band; the studs continuing as mullions is the extension of CMHC Fig. 68 (cripples continue at regular spacing above a header). Mine by analogy.
- Ledged-and-braced board door: not in the manuals; one external source, approved and marked external in `sources.md` (`references/external_ledged_braced_door.md`). It confirms the leaf as specified: braces run from the bottom corner on the hinge side to the top corner on the latch side (compression), boards 20 to 30 x 100 to 150, ledges and braces 25 to 30 x 100 to 200; B 24 x 120 and F 30 x 120 sit inside those ranges. Leaf: B boards vertical, three F ledges at 0.25, 1.05 and 1.85 above the sill, two F braces each from the hinge side of a lower ledge to the latch side of the ledge above.

## 5. Photo rule set

1. Calibration: photo 01, the external stair, 14 risers read as 2.4 m over 255 px -> 105 px/m, +/-10 percent. Cross-check: 31 boards across the far wall in photo 03 at 130 to 140 mm gives a 4.1 to 4.3 m room, consistent with the 4.4 m outer box width read in photo 01.
2. Topology: a closed boarded box inside a separate slat frame that stands clear of it; frame posts are paired slats with single diagonals passing between the pair; the box is tied to the frame at rail levels (photos 01, 02).
3. Proportions: box 4.4 m wide outside, 6.6 m from floor to roof (1.5:1); 9.0 m overall with the 2.4 m undercroft (2:1). The frame has 5 posts across the front, bays about 1.1 m.
4. Light: a translucent band about 1.8 m tall directly under an opaque roof, on the front and the sides; inside, a white band at the top of the side walls under a dark deck (photos 01, 03). Roof opaque.
5. Roof: thin slat trusses visible from inside under the deck (photo 03).
6. Wall: vertical boards about 130 mm wide inside, joints staggered, a horizontal dado joint about 1 m up, boards continuous to the band (photo 03).
7. Door: one, small (about 0.8 m wide, squat), in the middle of an end wall, sawn frame (photo 03).
8. Undercroft: heavy sawn posts about 2.4 m tall on a plinth, external stair (photo 01).
9. Erne: built-up Warren trusses, paired chords sandwiching single webs, curved chords, depth about 1 m, webs 50 to 65 degrees; trusses parallel, one direction.
10. Tschumi: straight parallel members whose projection varies smoothly; crests run diagonally across the row; the members themselves stay straight.

## 6. Deliberate deviations from the photos

| From | In the model | Why |
|---|---|---|
| Undercroft on heavy sawn posts, external stair (rule 8) | dropped; floor 0.144 above a raft flush with the ground, one step at the door | brief: thin slats only, flat ground, one entrance |
| Box 1.5:1, overall 2:1 with undercroft (rule 3) | outer structure 2:1 (6.62 x 13.24), room 2.9:1 | brief overrides the photos on proportion |
| Scaffold frame with walkways, ladders, corrugated translucent band (rules 2, 4) | 11 ring trusses, open band, no walkways | brief: trusses from Erne and Tschumi set the outer articulation; glass and sheet not modelled |
| Small squat door with sawn frame (rule 7) | 1.00 x 2.10 door with slat kings, doubled jacks and a slat header | a usable door; no sawn sections |
| Frame bays about 1.1 m (rule 3) | trusses at 0.65 | one module for studs, joists, roof trusses and ring trusses; 11 samples of the wave keep the ripple continuous |
| Shallow arched corrugated roof (photo 01) | 1:6 gable of slat deck, covering not modelled | brief: no sheet material; a fall the covering would need |
| Erne's laminated curved chords (rule 9) | straight 0.8 m sandwich segments, mitred | box-and-prism vocabulary; recorded, not hidden |
| Red paint | not modelled | colour is not geometry |

Departures from the manuals are listed at the end of section 4.
