# Version notes, experiment 16, Fable run

One entry per version. The next Builder starts from the last entry.

## v01 (2026-09-14)

Script `experiment_16_fable_v01.py`, views `views_fable.py` (views 01 to 20 rendered, 21 appended for v02). First version, from the template. Everything in concept.md sections 3.3 to 3.6 is built: raft, floor, four layered walls with the door, box roof with deck, 11 ring trusses, y-bracing.

Numbers: 3248 members (3247 timber pieces plus the raft; ring trusses 1782, box 1393, bracing 72). 32 penetrating pairs, 0 floating. Render-and-check pass 37 s wall clock for 20 views, so the truss panel fallback (0.80 to 1.00 m) was not needed and was not applied.

2:1 rule, measured on the generated geometry (R-02): z_e = 11.9481 (bisection, 60 steps, on the outer-face polyline of all 11 trusses), z_h = 11.5781. W_out = 6.6206 (x extent 6.621, y extent 6.620), H_out = 13.2417, H/W = 2.0001. Asserted in the script within 0.01, plan square within 0.05 (R-03). Leg panels 15 of 0.7965 m, top halves 3 of 0.784 m.

### Pair families

Two rows in the table, one cause. All 32 pairs are RingIn x RingOut at 30 mm (28) or 28 mm (4), on trusses 1, 2, 3, 4, 6, 7, 8, 9, four pairs each: the chamfer segment of the outer chord that skips an eave corner (segment 21 at the +x corner, segment 15 at the -x corner) passes through the inner chord's corner (both slats of the leg's top piece and of the top run). The concept's rule puts outer vertices only at half-panel points and at the feet, so the outer chord cuts across each corner between the vertex 0.40 below it on the leg and the vertex 0.39 along the top. The distance from that chamfer line to the corner is about 0.74 (d - 0.325): at d = 0.63 it is 0.225 and clears; at d = 0.33 it is 0.004, straight through the corner. Anything under d = 0.49 collides, and the wave puts eight of the 22 eave corners there.

Fix for v02 (one function, `ring_nodes`): add an outer vertex at each of the three outline corners, on the corner bisector at the offset-polygon position P_c + (n1 + n2) d(s_c, i) / (1 + n1 . n2). The depth rule stays as written (d measured along the normal of both runs at the corner); the outer chord gets a mitred kink at the corner instead of the chamfer. No web to the corner vertex: the 60 gap holds two web planes, and both are taken at a corner node by the rising and falling webs. The panel-to-vertex index shift (outer[j + 1]) must then be replaced by a stored mid-vertex index per panel. The concept sentence "the corners of the outline are therefore chamfered by the outer chord, not mitred" changes; Designer question 6 below.

### Derived constants that depart from the concept's numbers

Each of these is a contradiction inside the concept resolved toward the checkable requirement; none narrows the brief. Numbered as Designer questions at the end.

1. Box roof end trusses at y = +/-1.89, not +/-1.95. A truss centred on 1.95 has slats to 2.01, 60 mm inside the end wall (inner board face 1.950, stud zone from 2.004): it would cut the end wall's inner head rail and the gable studs. At 1.89 the outer slat face is flush with the inner board face; deck spans 0.59 and 0.17 m at the ends (R-24 holds).
2. Deck eave at x = 2.249 (19 whole 120 boards from the eave to the apex), not 2.28. The ring legs' inner face is at 2.26; a deck to 2.28 runs 20 mm into every leg the deck crosses. Overhang past the wall face 0.071 instead of 0.10. Top chord tails end at 2.22 (0.096 past the head plate, R-25's 0.11 holds) so they clear the brace plane.
3. Braces and ties in x = 2.230 to 2.260, not 2.198 to 2.228. The concept says "flat against the legs' inner faces" and R-20 wants contact with every leg; 2.228 leaves 32 mm to the leg face at 2.26. Clear of the wall face by 0.052.
4. Upper tie at z 11.669 to 11.789 (derived: deck underside at the eave minus 10 mm), not 11.75 to 11.87, which would cut through the deck eave (z 11.79 to 11.83 at x 2.23 to 2.25) and the ring's corner mitre. Upper brace panel z 6.07 to 11.669 (the concept's 6.05 overlaps the lower tie's top at 6.07 by 20 mm). Angles 59.9 to 60.7 degrees, asserted at or above 45.
5. Splices. Slats over 4.80 m are split at supports, A and B slats of a pair staggered: side wall studs at rail centres 4.55 and 9.10 (A) and 2.60 and 7.15 (B), gable studs get a third cut at the sill rail (9.57) where the last piece would exceed 4.80; ring inner leg chords at nodes 6 and 12 (A) and 4 and 10 (B); braces spliced on the leg at y = -1.30 or 1.30; ties at y = 1.30. Splice sets (3, 9) for the leg B slat failed the length assertion at 4.83 because the corner mitre adds 50 mm to the top piece. Longest piece in the model 4.788 m (asserted at 4.80 plus 20 mm for bevelled ends).
6. End walls drop the +/-1.95 module stud: it would overlap the end stud at 1.944 to 2.004. End studs at +/-1.974 stand in for it.
7. Door leaf hinge stile at y = -2.004 (against the jamb lining) so the open leaf touches the wall and the contact check sees it; concept placed the leaf from -1.950.
8. Bottom plate and outer bottom rail run continuous under the door: the sill is 0.144 above the raft, so they form the single step of the threshold. The inner bottom rail stops at the opening.

### What the renders show (Builder's look at 01, 07, 11, 13; no Inspector, over the threshold)

The ripple reads in the orbits. View 07, the side elevation from +x, does not show it at all: the depth varies toward the camera, and orthographic projection flattens it. View 21 (azim 12, elev 10) is appended for v02. The end elevation (06) shows the wave as the superimposed outlines of the 11 trusses. The node close-up (11) shows web ends flush inside the sandwich, the chord splices, and the brace halving joints. The section (13) shows the shaft, the band and the box roof trusses; there is a small dark artefact at the ring apex above the inner chord that the v02 Inspector should check on view 19 (apex webs or the top-run mitre).

Not yet judged (Inspector items for v02): closure of the eaves. Between the side wall head plate (z_h) and the deck underside (z_h + 0.24) the side walls are open between the roof truss heels, 0.24 m tall, for the full length. The concept says nothing about it; a board strip between heels would close it. Also the corner block above the side head plate at each end wall is filled with a four-slat corner post; the outer rail layer has a 30 x 30 x 120 notch at each eave corner.

### Requirements

Ticked (script assertions passed or Builder-confirmed from the geometry written): R-01, R-02, R-03, R-06, R-07, R-09, R-12, R-14, R-16, R-18, R-19, R-21, R-24, R-25, R-26, R-27, R-29, R-30, R-31. R-32 marked waived per its own text. Open: R-04, R-05, R-08, R-10 (script part passes: three sampled outer vertices per truss sit at d(s, i)), R-11 (no web crosses another: zero web pairs), R-13 (script part passes: 0.082 to the legs, 0.070 deck to chord at eave and apex; inspector part open), R-15, R-17, R-20 (script part passes), R-22 (32 pairs), R-23, R-28 (asserted on the y-braces; the door leaf braces run at 34 degrees and are not counted as structural bracing, see question 7), R-33.

### Open questions for the Designer

1. End roof trusses at +/-1.89 instead of +/-1.95 (derived 1). Alternative built if refused: five trusses and the gable plate carrying the deck edge, deck span 0.76 at the ends, which breaks R-24.
2. Deck eave at 2.249 and top chord tail at 2.22 (derived 2). Alternative: eave at 2.28 with the ring leg centreline moved out to 2.35, which moves W_out and every leg.
3. Brace plane at 2.230 to 2.260 (derived 3). Alternative: 2.198 to 2.228 as written, braces then touch no leg and R-20's contact clause is dropped.
4. Upper tie at deck underside minus 10 mm, upper panel from 6.07 (derived 4). Alternative: ties as written and the deck eave pulled back to x = 2.22.
5. Splice positions for studs and leg chords (derived 5): confirm that a splice at the sill rail and two-panel stagger on the leg slats are acceptable.
6. Outer chord corner: v02 will add a mitred corner vertex on the bisector (the chamfer as written cuts the inner corner for d under 0.49). Alternative: keep the chamfer and raise the minimum depth to 0.50 (d = 0.75 +/- 0.25), which changes the ripple rule.
7. R-28 "every diagonal brace at 45 degrees or steeper": the door leaf braces stand at 34 degrees, set by the ledge spacing of concept 3.3.8. Confirm R-28 covers the y-bracing only.
8. Eaves: should the 0.24 m slot between the side wall head plate and the deck be closed with boards between the roof truss heels, or left open as part of the band?

### For the next Builder

Fix the corner vertex (families above), add assertions for R-24 spacing and R-31 board-to-rail contact, render the full set plus view 21, then spawn the two Inspectors (box interior and floor; ring trusses and bracing). The `bar` plus half-space pattern for webs (extend, cut flush at the far chord face) worked with zero web pairs; keep it.

Proposal for tools (not done in the run): `board_columns` with the under-40-mm remainder shared by the last two boards, and `enforce_max` (split a member at the support nearest the midpoint of any piece over the stock length) are general enough to promote into `framing.py`.

## v02 (2026-09-14)

Script `experiment_16_fable_v02.py` (v01 patched), views 01 to 26 rendered (22 to 26 appended in this version). The one geometric change is the v01 plan: `ring_nodes` adds an outer vertex at each of the three outline corners, on the corner bisector at the offset-polygon position P_c + (n1 + n2) d(s_c, i) / (1 + n1 . n2), depth rule unchanged; it now also returns `mids`, the index in `outer` of each panel's half-panel vertex, and the webs and the R-10 samples index through it instead of `outer[j + 1]`. New assertions: each corner vertex sits at d(s_c, i) from both run lines; R-24 spacing (joists and roof trusses at most 0.65); R-31 (board layers contiguous with their rail layers). The Designer's answers to the eight v01 questions landed on disk while the Inspectors ran (design_notes.md "v01 Builder questions", concept.md patched, requirements.md reworded, R-34 added); all eight confirm the v01 resolutions, and one (answer 5) changes geometry, see below.

Numbers: 3310 members (3309 timber pieces plus the raft). 0 penetrating pairs, 0 floating, 0 families. The delta from v01 is 62, not the 66 new outer chord pieces (3 corners x 2 slats x 11): the mitred apex is higher than the chamfer, so the 2:1 bisection pulled z_e from 11.9481 to 11.8540 (z_h 11.4840), and the gable studs at x = +/-0.65 got 94 mm shorter, enough for their B slats to drop the third cut at the sill rail (4 pieces). Longest piece 4.797 m. W_out = 6.6207 (x 6.621, y 6.620), H_out = 13.2426, H/W = 2.0002. Upper tie 11.575 to 11.695 (rule: deck underside at the eave minus 10 mm). Brace angles 59.4 to 60.7 degrees. Corner assertions pass on all 33 corners.

### Pair families

None. The v01 family (RingIn x RingOut at the eave corners, 32 pairs on the eight corners with d under 0.49) is gone with the mitred vertex: the outer chord now runs at d - 0.12 clear of the inner chord's outer face all the way round, 0.21 at the shallowest.

### What the Inspectors found (inspection_v02.md)

One defect, and it is older than v02. The two webs at every apex node are stubs: `RingWeb_03_17F` spans x -0.157..0.116, `RingWeb_03_18R` x -0.105..0.133 (probe on the .blend), where each should run 0.45 m from the apex node to the outer vertex at x = +/-0.39. Cause, in `inner_clips`: at a corner node the web is clipped to stay inside the other run's outer face. At the eave corners the other run's face is the leg's vertical face (for the web on the slope) or the gable line below the web (for the web on the leg), so the clip only trims the end. At the apex the other slope's outer face, extended past the ridge, passes under the web body and cuts everything except the piece inside the chord zone. Both checks are blind to it: a stub overlaps nothing and touches the chord. It is the "small dark artefact at the ring apex" the v01 Builder saw in view 13 and read as a rendering mark; the box Inspector saw it in 13 and 14, the ring Inspector in 13, and the close-up 23 plus two diagnostic renders (RingWebs hidden: gone; RingChords hidden: stands alone) pinned it. 22 stubs, the Warren zigzag broken over two panels per truss, R-11 not met.

Everything else the Inspectors raised was zoom, and the four appended views closed it. 24: the board joints alternate column by column (1.95 on the B columns, 3.25 on the A columns), the elevations 06 and 20 had merged them into seams. 25: the four-slat corner post from the side head plate to the gable plate, the gable plate on the deck underside, the truss tails on the head plate and the open slot between them read as construction. 26: the leaf has vertical boards, three ledges and two braces low at the hinge side, high at the latch side. 22: the mitred eave corner at truss 3 (d = 0.33) is a clean join with nothing cut. The ring Inspector's plan question (braces stopping short of the end trusses) is construction: braces and ties end at y = +/-3.25, the end trusses' centreline, covering 60 of the 120 mm of the end leg face.

### Designer's answers, and what they change

Answers 1 to 4 and 6 to 8 confirm what v01 built (end roof trusses at +/-1.89, deck eave 2.249, brace plane 2.230..2.260, upper tie rule, mitred corners, R-28 for the y-bracing only, eave slot open as part of the band, new R-34). Answer 5 changes the splice rule to a number (pair splices at least one module apart on studs, two panels on chords, every splice on a rail centre or node) and gives the gable studs and the door cripples the set B = 3.25/7.80 with no third cut. v02 was already rendered with B = 2.60/7.15 plus `enforce_max`, so the x = 0 gable stud (N wall) and the door cripple still carry a third cut at the sill rail 9.57, 0.47 from the A splice at 9.10. R-21 stays open for v03.

The concept's z_e-dependent numbers (z_h 11.578, upper tie 11.669 to 11.789) are v01 values; the rules behind them hold in v02 at z_e = 11.854. Remark 9 below.

### Requirements

Ticked this version: R-04, R-05, R-08, R-10, R-13, R-15, R-17, R-20, R-22, R-23, R-28, R-33, R-34. Still ticked from v01: R-01, R-02, R-03, R-06, R-07, R-09, R-12, R-14, R-16, R-18, R-19, R-24, R-25, R-26, R-27, R-29, R-30, R-31; R-32 waived. Open: R-11 (apex web stubs), R-21 (gable stud and cripple splices per answer 5).

### Open questions for the Designer

The eight v01 questions are answered. One remark, no decision needed:

9. Concept 3.3.5, 3.5 and R-20 quote z_h = 11.578 and the upper tie at 11.669 to 11.789; with the mitred apex the tuned values are z_e = 11.854, z_h = 11.484, tie 11.575 to 11.695. The rules (z_h = z_e - 0.37, tie top 10 mm under the deck underside at the eave) are what the script implements; the numbers in the concept could be marked "v01" or replaced by the rules alone.

### For the next Builder (v03)

1. Apex webs: in `inner_clips`, apply the other-run clip only when the web's far end (the outer vertex Q) satisfies it; at the apex Q violates it and the clip must be skipped. The own-run inner-face clip then bounds the end: past the apex node the web stays above the other slope's inner face (the own run's inner face line rises past the ridge) and below its outer face (checked for the 60 degree web, 0.12 depth). Add a no-stub assertion over all 792 webs: vertex span at least |Q - node| - 0.15.
2. Splices: gable studs and the door cripple get B = 3.25/7.80 (answer 5); `SPLICE` becomes per wall kind. Check the longest piece stays under 4.80 at the new z_e (top piece to the apex 12.049 - 7.80 = 4.25).
3. Views: `--only` the orbits plus 08, 11, 13, 14, 19, 23 (webs and studs); the full set only if v03 is the last version of the phase. Consider a v03 view of a leg node at the shallowest depth if the Inspector asks.
4. Not converged until R-11 and R-21 close; nothing else is open.

Proposals for tools stand from v01 (`board_columns`, `enforce_max`). One more: a `min_span` check in `check_contacts.py` or a small `check_stubs.py` that flags any member whose vertex span is under a fraction of its intended length would have caught the apex stubs in v01; both channels missed them for two versions.

## v03 (2026-09-14)

Script `experiment_16_fable_v03.py` (v02 patched), views 01 to 34 rendered (27 to 34 appended in this version). A restart: the first v03 Builder ran out of usage after patching the script and before rendering. I diffed the patch against v02 and kept it. It was complete: `SPLICE` per wall kind with two assertions, `inner_clips(idx, k_own, far)` with both call sites passing the outer vertex `Q[m]`, `WEB_ENDS` filled per web and the reach assertion run after the rings with a count check (792). Nothing was missing, so I did not go back to v02.

Two geometric changes, both from the v02 list. Apex webs (R-11): the corner-node clip in `inner_clips` (stay inside the other run's outer face) now applies only when the web's far end satisfies it, tested as `(far - p_o) . n_in >= 0`. At the eaves the far end lies inside and the clip stays; at the apex the far end lies outside (the other slope's outer face, extended past the ridge, passes under the web body) and the clip is skipped, so the own chord's inner-face clip bounds the end. The reach assertion measures, for every web, the distance from each intended end to the nearest vertex; the worst is 0.072 against a limit of 0.15, where the v02 stubs sat at more than 0.2. Splices (R-21): `SPLICE` is now `{"side": A 4.55/9.10, B 2.60/7.15; "end": A 4.55/9.10, B 3.25/7.80}` (answer 5), `stud_pair` indexes it by wall kind so every N and S wall stud and the door cripple get the end set, and `stud_slat` asserts that `enforce_max` has nothing to add (no third cut). A probe on the .blend lists all 14 gable stud pairs and the cripple: A slats cut at 4.55 and 9.10, B slats at 3.25 and 7.80, three pieces each, the longest 4.55, nothing at the sill rail 9.57.

Numbers: 3309 members (3308 timber pieces plus the raft), one under v02: the N wall x = 0 stud's B slat lost its third cut at 9.57, the door cripple's B slat traded one cut for another. 0 penetrating pairs, 0 floating, 0 families. z_e = 11.854, z_h = 11.484, W_out = 6.6207 (x 6.621, y 6.620), H_out = 13.2426, H/W = 2.0002. Upper tie 11.575 to 11.695. Brace angles 59.4 to 60.7 degrees. Longest piece 4.743 m (v02 4.797). The 2:1 assertion and the corner and depth assertions pass unchanged.

### Pair families

None.

### Views

First pass with `--only`: the orbits 01 to 04 plus 08, 11, 13, 14, 19, 23 (the v02 list) and the new 27 and 28. Views 27 and 28 are vertical sections 5 mm into the x = 0 stud pair of both end walls, the A slat from +x and the B slat from -x, because the splices sit on rail centres and no face-on view can show them. Their focus radius took two corrections (4.5 framed the whole wall, 3.0 cut the sill rail off; 3.3 frames z 2.9 to 9.9). The frame in `render_views.py` is about 2.1 x the focus radius tall, worth knowing before the next close-up. The box Inspector still could not read a 20 px stud band, so 29 to 34 followed at the radius of view 24, one splice per frame with the sill rail in the upper frames, on the N stud (both slats) and the door cripple (B slat). Since the phase converged, the rest of the set (05 to 07, 09, 10, 12, 15 to 18, 20 to 22, 24 to 26) was rendered too; all 34 views are on the same geometry.

### What the Inspectors found (inspection_v03.md)

Nothing open. The ring Inspector confirms the apex fix on view 23 and on all 11 trusses in 08 and the orbits: zigzag continuous through the ridge, nothing above the outer chord, no crossing. The box Inspector confirms R-04, R-05, R-08, R-15, R-17, R-18 and R-34, and could not judge R-21 from 27 and 28 (resolution) or R-19 from 08 (the frame-only view hides the boards but not the ring bracing behind; R-19 is a script check, unchanged since v01). The splices Inspector reads one cut per frame at the right rail in all six close-ups and the sill rail clean in 30, 32 and 34. It queried a faint line at about 8.70 on the B slat in 32 and 34; the probe shows no piece boundary there and I see no line in 34. Not geometry.

### Requirements

Ticked this version: R-11, R-21. Everything else stands from v01 and v02; R-32 waived. Every line of phase 1 is ticked or waived. Converged.

### Open questions for the Designer

None new. Remark 9 from v02 stands: the concept's z_h 11.578 and upper tie 11.669 to 11.789 are v01 numbers; the built values are z_e 11.854, z_h 11.484, tie 11.575 to 11.695, from the rules z_h = z_e - 0.37 and tie top 10 mm under the deck underside at the eave. The rules govern; the concept's numbers could be marked v01.

### For the next Builder

1. Phase 1 is closed at v03. A v04 exists only if the Designer's phase-2 round asks for one.
2. View 08 hides the cover but not the ring, so the box framing (door kings, jacks, header, cripple) is hard to read against the bracing. A frame-only box view with `RING` hidden as well would give a future Inspector R-19 by eye; not added now because R-19 is a script check and the version was converging.
3. Close-up framing: about 2.1 x the focus radius in height. A 120 mm member needs a radius under about 1.2 to read as more than 40 px.

Proposals for tools stand from v01 and v02 (`board_columns`, `enforce_max`, a stub check). One more from this version: the `far` guard on a corner clip (apply a neighbour's face clip only when the member's far end satisfies it) is the general fix for any clip that is right at one kind of corner and wrong at another; it belongs next to `mitre_clip` in `planes.py` if a second experiment needs it.

## v04 (2026-09-14), phase 2

Script `experiment_16_fable_v04.py` (v03 patched, sections 7 and 8 added), views 01 to 40 rendered (35 to 40 appended). First and, as it stands, only version of the structural review. Two families added, both from the Designer's phase-2 entry in design_notes.md.

Chord spacers (P2-01), collection `Ring/RingSpacers`, names `ChordSpacerO_<bay>_<vertex>` and `ChordSpacerI_<bay>_<node>`. One `spacer()` constructor for both: a true 30 x 120 `bar` from the vertex on truss i's +y chord face (y_i + 0.06) to the same vertex on truss i + 1's -y face (y_i+1 - 0.06), depth along the vertex's bisector normal, width along its tangent, built long and cut flush by the two face planes. Outer chord: 13 per bay at outer vertices 20 +/- 3k, every third vertex counted from the apex both ways (indices 2, 5, ..., 38 of 0..40), so five per leg from z 1.19 to 10.67, one at each end half-panel of the top run and one at the apex vertex; counted from the feet instead it would be 14 including a spacer sitting on the raft, and asymmetric. Inner top chords: all seven nodes of the two slopes, both eave corners included (indices 15 to 21 of the inner node list). Where the depth differs between the two trusses the bar is inclined (at most 0.17 over 0.53, 18 degrees) and its bevelled end measures 120 / cos(beta) on the chord face; the axis is shifted inward by 60 (1 / cos(beta) - 1) plus 15 tan(kink / 2) for the chord's mitre at the vertex, so the outer edge never leaves the chord's outer face and the inner edge is proud inside the truss depth by at most about 12 mm. Measured: outer ends 0.03 mm inside the chord face at worst; the whole Ring collection's bounds equal the chord-only bounds to 0.000 mm, asserted at 0.1 mm. At the eave corner nodes the 30 x 120 rectangle on the bisector fits inside the mitred chord section (every corner within 55 mm of one run's centreline, 78 available); at the apex node the block is 1.7 mm proud on the truss-interior side and its underside corners 3.3 mm above the diagonals' plane.

Roof-plane X's (P2-02), collection `Ring/RoofBracing`, names `RoofBrace<E|W>_<ia><ib><R|F>_<piece>`. `roof_diag()` copies the y-brace pattern: per slope, panels of three bays 0-3, 3-6, 6-9, a rising diagonal (eave line at truss ia to apex line at truss ib) and a falling one, laid flat in the 30 mm layer directly under the inner top chord's underside plane (top face on the plane, 120 in the plane), three boxes each with the halving joint at the crossing (lap 0.185, the lower half to R, the upper to F), clipped to the panel's truss planes in y (a mitre against the next diagonal of the zigzag, or the end plane at truss 0 and 9), plumb at the apex line x = 0 and at the leg inner face x = +/-2.26. Plan angle to the row 50.0 degrees (asserted 45 or steeper), each diagonal 3.06 m, underside 0.039 above the deck top (asserted 0.035). Bay 9-10 unbraced as the review says. Contact with every chord passed under, the apex webs' end faces and the inner spacers' undersides is coplanar on the chord underside plane: face contact, zero penetration.

Numbers: 3545 members (3544 timber pieces plus the raft; v03 3309 + 200 spacers + 36 roof pieces). 0 penetrating pairs, 0 floating, 0 families, at the first render. z_e = 11.854, z_h = 11.484, W_out = 6.6207 (x 6.621, y 6.620), H_out = 13.2426, H/W = 2.0002, unchanged from v03 and now measured on `RingChords` alone (R-02's definition) with the whole ring asserted equal. Brace angles 59.4 to 60.7; longest piece 4.743. Render and checks 67 s wall clock for 40 views.

### Pair families

None.

### Views

Full set, 40, as the likely last version of the phase. New: 35 outer spacers on the +x legs from azim 30 (the stepped bar between the legs), 36 roof plan with the deck hidden (X's and the inner spacers lined up at the nodes), 37 inside looking up with the deck and box trusses hidden, 38 frame-only box with the ring hidden too (the v03 suggestion; R-19 by eye), 39 one X crossing from above (halving joint, spacers at x 0.77 and 1.55), 40 section 15 mm past that crossing (diagonal layer under the chord, gap to the deck). `RING` in views_fable.py now hides the two new collections as well, so every "ring hidden" view stays that. Two view comments corrected after the Inspectors: 40 (the inner spacer sits exactly in front of truss 5's chord and cannot be separated) and 14 (the door opening is closed in projection by its jamb).

### What the Inspectors found (inspection_v04.md)

Nothing open. Ring: both families as specified, none above the outer chord, none in the box or band; R-20 closed with view 17. Box: no regression; R-19 judged on 38; view 26 reads the leaf detail for P2-04. Four "cannot judge" lines resolved as view limits or colour readings (the view 40 spacer, the X count from above, the open door leaf in 15 and 16 read as an unidentified segment, the view 14 legend). The ring Inspector returned its tables inline instead of writing its file; I wrote `inspection_v04_ring.md` from the return.

### Requirements

Ticked this version: P2-01, P2-02. P2-03 and P2-04 waived by the Designer. Everything from phase 1 stands. Every line ticked or waived, 0 pairs, 0 floating, nothing open in the inspection: phase 2 converged, subject to the two count questions below.

### Open questions for the Designer

10. P2-01's check clause says 6 inner spacers per bay ("count = 10 bays x (outer positions + 6)"); the text says "every inner node of both slopes". The two slopes have seven nodes between them once both eave corners count, and the six of the clause is the two runs times three nodes of the node list, which leaves out one eave and is asymmetric. Built: 7 per bay, 200 spacers in all. Alternatives if refused: 5 per bay (no eave corners; the corner is 0.16 above the upper tie that already holds the leg there), or the asymmetric 6 as literally counted.
11. P2-02 and the review say "16 pieces of about 3.05 m". Three-bay diagonals from truss 0 to 9 give three per zigzag, two zigzags per slope, 12 diagonals; with the halving joints each is three boxes, 36 pieces. Built: 12 diagonals. If 16 was meant as four per zigzag, the panels would have to be 2.25 bays or the row 12 bays; neither fits the concept.
12. Remark 9 (v02, v03) stands: the concept's z_h 11.578 and upper tie 11.669 to 11.789 are v01 numbers; the rules govern.

### For the next Builder

1. A v05 exists only if the Designer changes the counts in 10 or 11. Both are one-line changes: `SPACER_IN_IDX` and `ROOF_PANELS`.
2. The `spacer()` shift formula is what keeps W_out and H_out exact with inclined bars; do not drop it if spacers move.
3. Inspector spawns: say in the prompt that `inspection_vXX_<part>.md` is a hand-off file the workflow requires, or the mechanical model may refuse to write it and return the tables inline as the ring Inspector did here.

Proposals for tools stand from v01 to v03. One more: the flat-layer X with halving joints (`roof_diag`, a twin of `brace`) and the between-planes spacer (`spacer`, inclined bar cut flush by two parallel planes with the outer-face-preserving shift) are both general enough for `framing.py` once a second experiment needs bracing between parallel trusses.
