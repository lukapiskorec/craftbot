# Experiment 15, Koreni: design rationale (Fable run)

## 0. About this document

Written by CraftBot, the orchestrator of the six-agent team, running as Fable 5.1 (model id `claude-fable-5-1`) in Claude Code, from the hand-off files of the run folder `experiments/15_Koreni_WIP/Fable/`. Every agent of this run (Designer, Researcher, Builder, Inspectors, Runner) ran on the same model; the mechanical tier on Sonnet was introduced after this run's cost audit and applies from the next run. The run started on 2026-09-09, built v01 to v04 on 2026-09-10 and was paused by the user after v04 with phase 2 half done; this document was compiled on 2026-09-11 at the pause, so that the run can be continued from disk. The agents' files: `brief.md`, `concept.md`, `sources.md`, `requirements.md`, `design_notes.md`, `version_notes.md`, `inspection_v01.md`, `inspection_v03.md`, `inspection_v04.md`, `inspection_v04_comparison.md`, `closeout_v01.md` to `closeout_v04.md`.

## 1. Brief as understood

Experiment 15 is a new design, not a reconstruction: a long, modern, open house in concrete, steel and glass on the sloped site at Koreni, with the terrain itself modelled so that the way the house meets the slope is visible in every view. Because it is an early-stage study, three variations of the house are developed side by side, and they must differ in how the building takes the slope (for example bridging over it, cutting into it, or stepping down it), not only in dimensions or finishes. Each variation is a complete model with its interior spaces (rooms, level changes, stairs, the fixed elements that define the plan) and its construction details (slab and wall thicknesses, columns, beams, glazing frames, footings and retaining walls where the house meets the ground). The site images and sketch diagrams in `input/` fix the slope, the orientation and whatever parti the sketches carry; the 43 reference images in `references/` are inspiration only, since the brief says to match them less and to develop a strong concept instead. Dropped: timber construction as the primary system (the manuals in `manuals/` are timber manuals and serve only for secondary timber elements and for general rules such as bearing and spans), furniture, landscaping beyond the terrain surface, and services.

Ambiguities resolved by CraftBot before any source was opened: the three variations differ in section and slope strategy, a scope decision so that they are alternatives and not one design at three sizes; one script and one model per version holds all three, side by side on three copies of the terrain strip, so the checks, the viewer and the iteration slider cover all three at once; the terrain is a surface built from the contours in the site plan with the fall stated as a number; construction details are modelled members and layers with derived, labelled dimensions, while rebar, connections and waterproofing are not modelled; concrete for slabs, cores, retaining walls and footings, steel for columns, beams and glazing frames, glass for the long facades; the version limit is the default 10 per phase.

## 2. How to run, outputs

Render any version from the repo root:

```
"<blender>" --background --python tools/render_views.py -- "experiments/15_Koreni_WIP/Fable/experiment_15_fable_v04.py" "<abs repo>/experiments/15_Koreni_WIP/Fable/experiment_15_fable_v04_blender" --views "experiments/15_Koreni_WIP/Fable/views_fable.py" --lib "experiments/15_Koreni_WIP/input"
```

Views (`views_fable.py`, 49 views, numbered once and appended only): 01 to 04 the orbits of the whole strip set; 05 top; 06, 07, 08 the long sections on the strip axes of A, B, C; 09 from below A; 10 to 15 interior plans and sections per level; 16, 17, 18 frame-only per variation (terrain, glazing and slabs hidden); 19 to 23 and 27, 28 close-ups of the girder seats, the retaining wall base, the step wall with its stair; 24, 25, 26 the ESE elevations of A, B, C; 29 to 38 close-ups added in v02 (end walls, stair void, guards); 39, 40 the sections just past the closed wall added in v03; 41 to 49 the five risers, the pavilion doors, the four closed-wall doors, the store, the guard and the beam in its pocket, added in v04.

Collections: `A_Bridge`, `B_Cut`, `C_Steps`, each with children `<V>_Terrain`, `<V>_Footings`, `<V>_Concrete`, `<V>_Slabs`, `<V>_Steel`, `<V>_Glazing`, `<V>_Cores`, `<V>_Stairs`, `<V>_Roof`. The variation prefix on every child is deliberate: Blender collection names are global, and a frame-only view must hide one variation's skin only.

Counts at v04: 1296 members, 0 penetrating pairs (> 1 mm), 0 floating members, 161 script checks passing. Viewer models `viewer/models/15_Koreni_WIP/fable_v01.json` to `fable_v04.json`, layer audit 0 in `other` after the `OVERRIDES` entry for 15 in `tools/layers.py`.

## 3. Reading the inputs

`site_02.png` is the cadastral and contour plan (10.3 px/m from the printed 96.42 m boundary), `site_01.png` the same plot rotated with the sketched house and section lines, sketches 01 to 06 plan diagrams at 15.2 px/m, 07 to 09 long sections at 16.6 to 17.1 px/m. The 43 reference photos were skimmed for material language only and no requirement was derived from them.

The contours were counted by sampling pixels along the plot axis: 19 index and 74 intermediate crossings over 96 m. Read as 0.5 m index lines with 0.1 m intermediates this gives 9.4 m of fall; the other reading (0.5 m intermediates) gives 46 m, which the section sketches' own scale (8.4 to 10.8 m) rules out. Simplified to three straight segments, the profile is concave: 5 percent to x = 26, 8 percent to x = 50, 14 percent to x = 100, with z = 0 on the axis at x = 5, the building line.

Source to rule to number (the full table with page citations is `sources.md`; 95 rules from the *Architect's Handbook of Construction Detailing* (AHCD), *Canadian Wood-Frame House Construction* (CMHC) and the *London Housing Design Guide* (LHDG); no external material, four online searches refused):

| Source | Rule | Number in the model |
|---|---|---|
| AHCD 1-1 | slab on ground at least 100 mm | 200 mm floor slabs, 150 mm gravel under |
| CMHC ch. 7 | slab top at least 150 above finished grade | courtyard and strip paving 150 below the floor; pavilion floor +0.15 |
| CMHC Table 5 | 300 mm wall retains 1.50 free, 2.30 braced | C's step and side walls within the table; B's walls exceed it |
| CMHC Table 4, Fig. 32 | strip footing at least 450 wide, thickness at least the projection | strips 0.8 x 0.4; pads 1.8 x 1.8 x 0.6 under columns with 300 x 300 x 30 base plates |
| CMHC Table 3 | footing underside 1.2 m below grade | 1.2 m everywhere, no local frost depth known |
| CMHC Fig. 35 | stepped footings, steps at most 0.6 m, runs at least 0.6 m | A's box footings step three times, C's every 0.6 m of fall |
| CMHC Table 18 | W200 to W250 spans 5.8 m at 4.2 m tributary | IPE 330 roof beams, IPE 300 floor beams, one size up for the concrete deck |
| AHCD 6-6, 6-11 | storefront in a one-storey opening, 25 mm IGU | 51 x 152 mullions at 1.333 m, 25 mm glass, 6 mm slip joint at the head |
| AHCD 1-21, 5-15 | parapet at least 305 above the roof surface, 2 percent drainage | tapered insulation 150 to 270 mm, parapet 600 above the slab |
| AHCD 3-10, 3-15, CMHC ch. 17 | riser at most 178, going at least 279, guard 1.07 | risers 150 to 165, going 280, guards 1.07, glass balustrades 1.10 |
| LHDG 4.1, 4.5 | 3b5p at least 86 m2, double bedroom 12 m2 and 2.75 m wide | about 215 m2 net, bedrooms at 12 m2 or more |
| CMHC crawl space | 300 mm clearance under framing | bridge floor raised from +0.60 to +0.90 |

Deliberate deviations (the ledger is concept section 8): the plot taper (16.8 to 20.1 m) is dropped for a 20 m rectangle the house never reaches; the ground steepens from x = 50 as surveyed, not from x = 66 as the sections draw it, because the brief says to model the actual terrain; the bar is widened from the sketches' 3.5 to 4 m to 6 m so that an open plan has 5.7 m clear; the fork, bend and hook plans of sketches 03 to 05 are rejected for the straight bar of sketch 06 so that the section stays the only variable; variation C gets a pavilion plus three levels and three stairs instead of sketch 07's three rooms and two stairs, because the surveyed slope is steeper; B's retaining walls at 2.3 to 2.75 m are outside the manual tables and are recorded as engineered L-walls with a base of 0.6 H; the grade falling away from walls, drains, membranes, rebar, bolts and joints are not modelled.

## 3b. Comparison round

The phase-2 Inspector compared v04's matched views (05 top, 06 to 08 sections, 24 to 26 elevations, 02 orbit, 18 frame-only) against `input/` under the rule set S-01 to S-11 of concept section 6, with calibrations cross-checked (sketches 08 and 09 are 17.1 px/m, not 16.6; `site_01` positions carry about 1 m of uncertainty). Verdicts: 13 rows within tolerance or matching, 5 fixes proposed, 15 kept with reason or out of scope. The Designer had not yet ruled on the five proposals when the run was paused, so they are recorded here as proposals and are the first item of the continuation. Condensed table:

| Rule | In the reference | In the model | Verdict |
|---|---|---|---|
| S-01 plot | 96.4 m long, 16.8 to 20.1 m wide | strip 106 x 20 m, house inside 5..71 | within tolerance; taper kept dropped |
| S-02 fall | 8.2 to 9.9 m by the sections' own scale, concave | 9.5 m from x = 5 to 96.4, knees at 26 and 50 | within tolerance; the sections steepen at 67, the survey at 50, survey kept |
| S-03 road uphill | road at the SSW end, ground falls from the first box | pavilion at the road end, ground falls to the far end | matches |
| S-04 pavilion | 4.9 to 5.4 m long, 6.2 m across, at the 5 m building line, its ESE face flush with the bar | 6.0 x 6.2 m at 5.0 m, shifted 2 m WNW leaving a 2 m step on the ESE side | fix proposed: pavilion y = 7..15, ESE face flush, 2 m WNW projection |
| S-05 bar | straight, 3.7 m wide, on the axis, ends at 66 to 70 (sketch 06 runs to 94) | 6.0 m wide on the axis, house end 65 to 66, terraces to 70 or 71 | within tolerance on start, end and axis; width kept with reason |
| S-06 one storey | boxes 5 m tall, never stacked | 3.8 to 4.4 m to the parapet, one storey everywhere | kept with reason (S-06 states 3.3 clear) |
| S-07 open sides | green edges overlap 2 to 8 m at every switch; WNW open from 21, ESE open to 66 and along the pavilion | clean glass-to-glass corners at 28, 44, 60; ESE closed at 60..66 and along the pavilion | fix proposed: WNW open from 21, ESE open to 66 (both-sides-open zones at the switches); pavilion ESE face to be ruled |
| S-08 C's levels | three boxes with 10 m gaps, one long stair, ridge at 21 (sketch 09) or 36 (sketch 08) | pavilion plus three continuous levels, three short stairs, ridge at 11, R2 at 8.3 percent | kept with reason: one decision, the gaps removed; floor levels within 0.55 m of sketch 09 |
| S-09 A past the bank | level bar past the bank top | floor +0.90 from 11 to 71, terrace end 6.8 m clear | matches |
| S-10 far-end terrace | ellipse centred at 69 m | terraces centred at 68 on the axis | matches |
| S-11 ticks | 5.4 m rhythm, ticks near 27, 43, 59, 65 | posts at 4.0 m, switches at 28, 44, 60, 66 | note only, each switch within 1 m of a tick |

What the sketches show that the model does not: the 8 to 10 m gap between the pavilion and the bar of sketches 01 and 03 to 05, sketch 07's three separate boxes, the steeper roof fold, sketch 08's ground terraces, `site_01`'s offset far-end volume, the four trees at the road end. What the model has that no sketch shows: the three variations as such, the closed-side windows and doors, the balustrades, end walls, parapets and insulation wedge, the cores, partitions and stairs.

## 3c. User review round

None during the run. The user's second message (2026-09-10) paused the run after v04 and asked for a report and a commit; it is in the prompt file and changes no requirement.

## 4. Reading the reference code

Nothing inherited: the run is a new design. The scripts build on the kits in `tools/` (`craftbot_lib`, `geometry2d`, `planes`, `framing`) through the template; `prism_y` for the terrain and roof prisms, `planes.Frame` with `subtract` for the holes in the terrain skin, `framing.flight` for the stairs.

## 5. What had to change, construction logic settled before geometry

- **Terrain as a 0.3 m skin on the surveyed profile, 9.4 m of fall,** one convex prism per segment, with a hole cut around every element that crosses it. A terrain solid would flag every footing in the overlap check; the skin passes it and still draws the ground line in every section. Three strips at y = 0, 30 and 60 with 10 m gaps, one per variation.
- **One plan, three sections.** All three share the 6 x 6 pavilion at the building line and a straight 6 m bar to x = 66 with the open side alternating per sketch 02; only the section changes. Mixing plan and section variants would make the three incomparable, and the fork and bend wings run 20 degrees off the axis, which every kit function is not built for.
- **Bearing stacks, ground up.** A: pads, base plates, HEB 240 columns, cap plates, two 700 plate girders continuous from the pavilion's rear wall to the cantilever tip, IPE 300 floor beams at 4 m, 200 slab, posts and IPE 330 roof beams, 200 roof slab. B: L-wall bases, 300 stems to the ground line, slab on ground to x = 46 and a 300 suspended slab on 250 plinth walls beyond, posts and the 200 closed wall carrying the roof. C: stepped strips, step walls at 11, 29 and 47, side stems where a level is cut, plinth walls where it stands, slabs on ground or suspended, posts and closed walls that follow the folded roof plane.
- **What the research round changed** before v01: the bridge floor from +0.60 to +0.90 (300 mm clearance under the girders at the pavilion), the pavilion floor to +0.15 and the paving 150 below the floors, a storefront system with 51 x 152 mullions and 25 mm glass instead of a curtain wall, the parapet from 400 to 600 above the slab, suspended slabs 300 at L/20, pads 1.8 m with base plates, footing undersides 1.2 m below grade with 0.6 m steps, guards 1.07, a 3 m2 store, egress windows in A's lower bedrooms.

## 6. Core modelling decisions

- **A, the bridge.** Two plate girders 700 deep span 12 m between the abutments: the pavilion's rear wall and a concrete bedroom box at x = 53..65, with three column pairs between and a 6 m cantilevered terrace beyond. The concrete bedroom box is the far abutment of the bridge and gives the house its second level and its stair. Rejected: more steel columns instead of the box (no second level, no honest end to the span diagram); raking columns from the reference photos (a second structural idea the bridge does not need); columns at 4 m (the undercroft would not read as open).
- **B, the cut.** One level at -2.60, the ground level at x = 45.4, chosen so the cut at x = 11 (2.30 m) and the plinth at x = 66 (2.61 m) are the same height: half cut, half fill. Sunken courtyards 2 m wide paved 150 below the floor along both sides of the cut half, so the glass looks at a wall 2 m away and gets light from above. Rejected: the retaining walls as the facade (a buried box with glass only at the end, which loses the alternation rule); lowering the cut to 1.5 m to stay inside the manual tables (the floor would rise to -1.80 and the plinth to 3.4 m, a raised house, not a cut one).
- **C, the steps.** A pavilion plus three levels at 1.35 m steps, each about 18 m long, half cut and half on a plinth. One folded roof plane falling 8.2 percent from the ridge at x = 11 over the tall living hall, following sketch 09 (sketch 08 puts the ridge at 36; 09 is the later drawing and its ridge over the hall's uphill end makes the hall the tallest room). Rejected: levels graded to sit fully on cut ground (2.5 m steps and 17 risers per flight on the 14 percent segment); sketch 09's 13.9 percent fall (from a ridge at 11 it would put the roof below L3's floor at 66).
- **B's high bay (after v02).** The concept's landing at +0.15 sat under a roof underside at +1.03; the Builder raised the stair bay over x = 11..15.28 to the pavilion roof, and the Designer kept it, so the road view shows the pavilion, its stair bay and the low parapet. Rejected: a stair inside the pavilion (5.7 of its 6 m, and the cut moves to x = 5); an external courtyard stair (a 2.9 m open descent as the only entrance). A spandrel the Designer had written into the rewritten line was dropped after v03: the built full-height storefront needs none.
- **C's clear height (after v02).** The concept's 3.3 m was roof top minus floor without the 0.20 slab; as built L1 3.42, L2 3.30, L3 3.10. The rule was relaxed to 3.0 m rather than flattening the roof or lowering L3 for 0.2 m of air.
- **Closed-wall doors (v04).** A door in a closed wall only where the outside surface is within one riser of the floor: A has none (its closed walls stand over the undercroft), B two onto the courtyard at x = 25.7 and 37.7, C two onto grade at 44.5 and 56.5. The earlier "last bay" rule had put a door over a 5.5 m drop in A.
- **A's lower box and C's L3 (after v04, for v05).** The dogleg's void leaves 6.5 m2 for A's bedroom 2; the layout moves to a full-width partition at 58.3 with bedroom 2 at 58.35..61.15 (15.4 m2) and the bathroom core reduced to 2.5 x 2.4. On C's L3 stair 3 arrived inside the master bedroom; L3 becomes a stair hall with the family bathroom beside the flight, then bedrooms 2 and 3, then the master at 60.1..66.
- **Considered and not changed.** Cross fall (the middle contours are within 15 degrees of perpendicular to the axis; a ruled sheet per segment is the fallback); the plot taper; the reference photos' corrugated steel deck (the roof is concrete in all three so the folded roof and the parapets are one family); a centre spine beam under the suspended slabs (a member family for one slab).

## 6b. Independent structural improvements

Reviewed by the Designer from the v04 script with the sketches set aside. Vertical load paths are sound in all three: A's roof on beams on posts and the closed panel, its deck on IPE 300 floor beams between the girders, the girders in the pavilion wall's pockets, on 300 cap plates over HEB 240 columns at 23, 35 and 47, and continuously on the box walls over 53..65 with a 12 m back span for the 6 m cantilever; about 580 kN per column on a 1.8 m pad, 180 kPa, plausible and not calculated. B's end wall is one 300 element from the L-base to the pavilion roof; its side stems stand on 1.95 m bases at 0.6 H. C's step walls run from 0.5 below the lower floor to the upper floor on cross footings. Bearings: roof beams 200 mm in the closed-wall pockets, girders full width on the cap plates and along 12 m of box wall, suspended slabs on the full 250 walls, A's transverse beams butting the girder webs as undrawn shear connections (R-55).

The finding: across y no variation had a shear element above the floor except at the uphill end. Cores stop under the roof: the phase-2 finding, full height from v05. The cores stood 2.7 m plus a lid under a beam underside at 3.3, so the roof diaphragm leaned on nothing for 50 to 60 m, and the "portal frames" the concept had written for A's columns do not exist as built: HEB 240 columns on 300 mm cap plates, pinned both ways, with the transverse beam meeting the girder web at the top flange and no moment path. Decisions, as requirement lines for v05: R-51, cores full height to the roof slab underside with beam pockets, concrete in B and C, sheathed steel-stud panels in A (a concrete wall on the 200 deck mid-span between floor beams is the wrong load path on a bridge); R-52, A's columns declared pinned and the 6 m deep deck read as a diaphragm spanning 42 m between the two concrete boxes, depth to span 1:7, ticked as built; R-53, access openings 0.6 x 0.9 in the downhill end wall of every hollow undercroft (B's plinth and C's L3 plinth); R-54, the pavilion roof slab 300 mm for its 5.5 m span at L/20; R-55, the bearings as built, ticked. Rejected: cross walls at the segment switches (they would close the glass-to-glass corners), moment-connected post frames (a 150 SHS at 3.3 m could carry wind, but the model cannot show it as different from pinned), K-bracing in the glazed bays. Recorded as not modelled: movement joints in C's 59 m roof and B's 55 m parapets, drainage behind the retaining walls, anchor bolts and end plates, rebar, the 5 percent grade away from walls.

## 7. Detailed geometry numbers

Datum: x along the plot axis from the road boundary, downhill; y across the strip, strip axis at y = 10; z = 0 on the ground at x = 5. Sources per number are in concept sections 1 to 5; "mine" marks the Designer's derivations.

| Item | Number |
|---|---|
| Ground profile | z = +0.25 at x = 0, -1.05 at 26, -2.97 at 50, -9.97 at 100; 5, 8, 14 percent |
| Strips | 106 x 20 m at y = 0, 30, 60; terrain skin 0.30 thick |
| Pavilion | 6.0 x 6.0 m at x = 5..11, y = 9..15; floor +0.15; roof slab top +3.65; parapet +4.25; walls 250 |
| Bar | 6.0 m wide, y = 7..13, x = 11..66 (A: 71); glazed side alternating ESE 11..28, WNW 28..44, ESE 44..60, WNW 60..end |
| Facade | SHS 150 posts at 4.0 m; storefront mullions 51 x 152 at 1.333 m, glass 25 mm; IPE 330 (160 x 330) roof beams; 200 roof slab |
| Roof | tapered insulation 150 to 270 mm at 2 percent; parapet 200 thick, 600 above the slab (A, B); C: 150 fascia, no parapet |
| A | floor +0.90; girders 700 x 300 at y = 7.3 and 12.7, top +0.70, x = 11..71; HEB 240 columns at x = 23, 35, 47; pads 1.8 x 1.8 x 0.6 m, undersides 1.2 m below grade; box x = 53..65, floor -3.30, walls 250; IPE 300 floor beams at 4 m; roof slab top +4.73, parapet +5.33 |
| B | floor -2.60; L-walls at y = 5 and 15, stems 300, bases 1.7 x 0.4 (end wall 2.1 x 0.4), undersides -3.55; courtyard slabs 150 at -2.75; plinth walls 250 from x = 46; suspended slab 300; high bay x = 11..15.28 to +3.65; roof slab top +1.23, parapet +1.83 |
| C | L1 -1.20 (11..29), L2 -2.55 (29..47), L3 -3.90 (47..66), terrace -3.90 to 70; step walls at x = 29 and 47 retain 1.35 m, braced by the upper slab, 300 thick; side stems 300 on 1.5 x 0.4 bases; roof plane R1 +3.40 at x = 5 to +3.90 at 11, R2 +3.90 at 11 to -0.93 at 70 |
| Stairs | risers 150 (C, A's five in the pavilion) to 161.8 (B, 17 risers), going 280, width 1.2; three straight flights of nine risers at the level changes in C; a dogleg in A through a 2.6 x 4.6 void |
| Guards | 1.07 at every flight and void; glass balustrades 19 mm, 1.10 high, on every edge more than 0.6 m above the ground |
| Footings | strips 0.8 x 0.4 under every concrete wall, undersides 1.2 m below grade, stepped at most 0.6 m per 0.6 m run with 0.15 risers |

## 8. Verification

The overlap check (every pair of members penetrating by more than 1 mm) and the contact check (members touching nothing) ran on every version; v03 and v04 read 0 pairs and 0 floating on 1294 and 1296 members. 161 script assertions (levels clearing members, stairs closing storeys, openings inside their walls, the clear height, the door rule) pass at v04. Inspectors looked at every view of v01, v03 and v04 (v02 was inspected through v03's set): 47 of 50 phase-1 lines are ticked by the checks and by eye, and the comparison Inspector confirmed rules S-01 to S-11 as tabulated in 3b. Every version was closed out: exported to the viewer, layers audited, index rebuilt, view set checked, viewer screenshot clean.

Not verified: structural adequacy of any member (sections are plausible for their spans, not calculated); the plate girders at L/17 and the 12 m spans; B's retaining walls, which are outside the manual tables; bearing pressures; connections, anchors, rebar, waterproofing, drainage; movement joints; the pavilion roof at 200 mm (R-54 says 300, not yet built); the cores as shear walls (R-51, not yet built); the access openings (R-53, not yet built); A's bedroom 2 and C's L3 layouts (R-27 and R-46 rewritten, not yet built); the five comparison proposals of 3b; the strip windows placed behind a core and across a partition in A (a placement fix for v05). Residual approximations: the terrain has no cross fall and no taper; the ground line in a section is the skin's top face, not a solid.

Cost of the run, from the task notifications (context at return, tool calls): Builder 270k tokens over 73 calls across three forced restarts; Designer 230k over 48 calls plus four resumes for two-line questions; Runner 31k over 15 calls; each Inspector an estimated 100 to 150k after reading all 49 views; the Researcher an estimated 150k. Every agent ran on Fable. Four usage-limit cut-offs, each relaunch a cold cache and a 60 to 80k re-read. These numbers are the baseline of the cost rules in the workflow skill.

## 9. Iterations table

| Version | Change | Members | Pairs | Floating | What the renders and checks showed |
|---|---|---|---|---|---|
| v01 | first build: three terrain strips, A bridge, B cut, C steps; 28 views | 1255 | 245 | 0 | 90 families in 12 causes (C's storefront under the sloped beams, per-piece footings crossing at corners, A's stair guards in the tread lanes, B's doubled posts and corbel); the Inspector confirmed S-01 to S-11 and found the end walls absent and B's stair without headroom |
| v02 | every v01 family fixed at its cause; glazed end walls; A's stair void framed; B's low bar from a post line beside the step wall; C's storefront following the roof; ten close-ups | 1294 | 9 | 0 | four causes left (end walls 4 mm into the edge beams, a box partition into a trimmer, a partition at the x = 60 switch, a guard corner) |
| v03 | the nine pairs; views 39 and 40; `OVERRIDES` entry for 15; literal hide lists for the frame-only views | 1294 | 0 | 0 | 44 of 50 lines ticked; a door in segment 4's closed wall over a drop; the "dark slot" at C's x = 27 traced to a roof beam in its pocket |
| v04 | closed-wall doors by the one-riser rule; clear height at 3.0 m; views 41 to 49 | 1296 | 0 | 0 | 47 of 50 ticked; A's bedroom 2 at 6.5 m2 behind the dogleg; strip windows behind a core and across a partition; phase 2 started on this version |

## 10. Scope and known simplifications

In scope and built: the terrain surface, three complete houses with their rooms, cores, stairs, guards, glazing grid, roofs, footings, retaining and plinth walls. Not modelled by the brief: furniture, landscaping beyond the terrain skin (sketch 08's ground terraces, the four trees, the road), services, rebar, connections, membranes, drains. Simplifications recorded: no cross fall, no plot taper, terrain as a skin, the grade not falling away from walls, one material per element (a 200 concrete wall stands for wall plus lining), captured storefront glazing as one solid mullion box.

Open at the pause, in the order the continuation takes them: the Designer rules on the five comparison proposals of 3b and ticks R-50; v05 carries R-27 and R-46 (A's box and C's L3), R-51, R-53 and R-54 from the structural review, the strip-window placement fix and the zone-list printout for R-19; R-49 is ticked at the last version. Then the phase-2 loop to convergence, this document updated, the callouts re-checked, the run close-out repeated.
