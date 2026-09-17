# Version notes — Astra

## v01 — phase 1, 2026-09-16

### Implementation and evidence

First implementation from `tools/experiment_template.py`, using `craftbot_lib`, `geometry2d`, `framing`, `planes`, and `ruled`. It includes the full 54 × 114 m ring, 19 × 6 structural grid, five occupied levels, four curved stairs, four service cores, room/corridor partitions, special south inclined facade, northern courtyard insert, rooflights, terrace route, site and three plant housings. Absolute dimensions remain inferred. The image-supported five levels override the article's four-storey wording as recorded in the brief.

The approved corbel revision is incorporated: 1.00 m normal depth, 0.60 m shaft, 0.20 m shoulder projection on each side, 1.30 m width along the facade, and 0.60 m depth vertically. Shoulders and shafts are separate convex pieces with shared faces. Slabs, beams and partitions use common stair/core/column exclusion rectangles. Window half-bays have timber perimeters, broad fixed panes and narrow operable lights. South glazing derives from one ruled plane with the specified endpoints.

Core centres adopted: west (3.8, 66.2), east (50.2, 66.2), north (27.9, 110.7), south (45.3, 8.5). Four core wall sets rise to z18.0. The floor diaphragms and core walls are the intended lateral system; seated exterior beams are not described as moment frames. Foundations, wall/beam sections and fixing intent remain architectural estimates, with no reinforcement or engineering calculation.

### Checks and rendering

The standalone Blender build passed after merging overlapping partition exclusion intervals, as required by `wall_pieces`. It initially reported 18,839 meshes; the subsequent render build removes repeated landings and adds one courtyard landing. Final count: **18,828 members, 85,230 penetrating pairs, 2 floating members**. The overlap tolerance is 1 mm and the contact tolerance is 2 mm. Diagnostic run took about seven minutes including the build; the separate saved-model orbit run completed without rebuilding geometry.

Blender runs with `--factory-startup` to avoid unrelated installed add-ons. The fixed view file defines 26 views: four orbits, top, four elevations, frame-only, from below, four photo matches, longitudinal/transverse sections, stair and structural cutaways, five floor plans, south facade section and corbel close-up. Initial rendering requests views 01–04 while the first numeric check is triaged. If over the 20-pair threshold, the remaining views and all Inspector work are deferred under the workflow rule; their definitions are retained.

Glass has an actual transmission material in the `.blend`. Workbench renders are solid-color geometry diagnostics. No transparency requirement is passed until Inspectors see the matched south/courtyard/stair subset rendered with a transmission-capable renderer.

### Known items for the next builder

- **Critical observed defect:** orbit 02 shows the courtyard covered by unintended slabs, so R-03/R-12 are not satisfied. `geometry2d.tile` adds hole edge cuts without first rejecting holes outside the tiling rectangle. v01 passes the global hole list directly. In `slab_zone` and `cut_box`, prefilter holes for true rectangle intersection and clip the retained holes to the target rectangle before calling the kit. Otherwise west/east hole coordinates expand slabs and beams outside their intended domains. Fix the experiment callers; do not edit the shared kit during this run. This also explains much of the unexpectedly high mesh count.
- Resolve family-level junctions from the numerical report before visual inspection; preserve all major geometry.
- Slab fabrication module still needs the specified 1.5 m wide units spanning 6 m. v01 uses 9 × 6 m subdivision for the first floor-envelope layout; this is an unresolved implementation item, not a change to the concept.
- Inspect insert north/south enclosure and upper-side enclosure continuity; v01 explicitly models the lower east glazing and diagonal upper strip but these do not alone close all volume ends.
- Review the south stair's alternating half-circle orientation against the inclined wall. Traversing the same inward semicircle in alternating directions is a potential implementation correction that keeps the four stair locations and tread counts.
- Check ground-floor support, panel-to-beam seating, rooflight curb attachment, and stair-end bearing in close-up after the numerical fixes. Contact alone will not establish an adequate load path.

### Open Designer questions

1. The W/E stair centres (3.0/51.0) and 2.70 m radius reach x0.30/53.70, while the facade inside faces are x0.77/53.23. North stair reaches y113.40 while its facade inside face is y113.23. Should the centres move inward by 0.50 m for W/E and south by 0.20 m for N, retaining the radii and 22 risers? Actual pairs confirm the conflict: `Panel_West_20_2 × StairTread_W_2_21`, `Panel_East_20_3 × StairTread_E_3_21`, and `Window_North_10_2_Glass0 × StairTread_N_2_11`. The stair/facade subset has 153 depth-grouped family rows in `triage_v01.txt`. v01 retains the handoff coordinates pending Designer revision.

### Final version record

Rendered views: **01, 02, 03, 04**, all Workbench. The initial unquoted PowerShell comma list selected no views; the four images were then rendered from the saved `.blend` with a quoted selection and `--no-check`. Geometry and numeric checks were not repeated. Remaining 22 views and Inspector work are deferred because 85,230 pairs exceed the 20-pair gate. `inspection_v01.md` records this deferral and the builder's observed courtyard error without representing it as an independent inspection.

The checker reports 1,747 depth-grouped rows. Dominant rows are:

| Count | Pair family | Cause / next action |
|---:|---|---|
| 8,750 | Beam × EdgeBeam, 650 mm | Both callers emitted out-of-domain pieces; clip hole inputs first, then resolve the remaining actual beam crossings. |
| 2,682 each | EdgeBeam × Window_West / Window_East, 285 mm | Expanded edge beams cross enclosure; rerun after clipped domains. |
| 2,400 each | EdgeBeam × Window_CourtWest / Window_CourtEast, 285 mm | Same expanded-beam cause in the court. |
| 1,685 | EdgeBeam × Window_North, 285 mm | Same domain cause at the end facade. |
| 1,653 | FloorSlab × FloorSlab, 250 mm | The four intended ring zones expanded into one another. |
| 1,500 | Column × EdgeBeam, 600 mm | Expansion reintroduces areas outside valid exclusion cuts. |
| 1,440 | EdgeBeam × CorridorWall, 100 mm | Expanded beam overlap plus remaining partition-head junctions to resolve after domain fix. |

The complete top-40 family table and stair/facade subtable are in `triage_v01.txt`; `triage_v01.py` reproducibly summarizes the pair artifact. Do not chase the 85,230 individual pairs. Restore rectangle bounds, then triage the substantially smaller true-junction set.

Floating members: `SiteGround_North` is the isolated raised exterior site patch; provide a geometrically connected grade/subsoil construction. `CourtStairTopLanding` was unintentionally included in the whole-collection X/Y transform for the kit's straight flight; place it after the transform or exclude it explicitly. The orphan landing is visible beside the building in orbit 02.

Requirements ticked: R-02 for source-role implementation/provenance, R-04 and R-05 for the passed explicit grid/level assertions, with visual confirmation still pending. All visual, support and convergence requirements remain unticked. **Converged: no.** Runtime cost/token telemetry is unavailable. Proposed shared-tool improvement after this run: make `geometry2d.tile` reject out-of-domain holes internally; this version changes no shared modelling module.

## v02 — phase 1 implementation record (unrendered preflight)

The final rendered count and inspection record will follow this entry. Numeric builds during development are not rendered versions. v01 remains unchanged.

The rectangle-domain defect is fixed at the experiment call sites: hole lists are filtered and clipped before `geometry2d.tile`. Floor units use 1.5 m widths and end on the actual 6 m transverse support axes. The special first raised south beam is offset to y6.35, within the original corbel footprint, behind the recessed ground glazing; its adjoining slab joint uses the same axis. Four main wings/links, all 19×6 bays, five occupied levels, four stairs, all service cores, room partitions, courtyard insert and three plant housings remain.

Construction junctions now use explicit precedence and convex decomposition: continuous columns and core walls, transverse beams, landings and slabs, then fitted enclosure and partition pieces. Chamfered shoulders use the shared kit's actual half-space profiles. No shared geometry module was edited. Narrow facade cuts fit around real structure; rendering and independent inspection must still check that coverage, openings and appearance survive those cuts. The helper operates on member families rather than deleting individual reported pairs.

Ground grade beams seat the ground-floor panels on the pads/pedestals. The north site solid extends down to the adjoining lower ground datum. The courtyard stair landing is placed after the flight transform, its post bases meet actual tread tops, and its west guard is moved inside the usable passage away from the sloping glass. The insert has explicit end walls, foundation pads/pedestals, a shelf closing the lower-glass/slope junction, and four skylight support beams tied to the retained transverse insert beams. Plant housings are hollow shells retaining the original outer profiles; drains are displaced 0.60 m off the column axes. Service cores receive ground caps and roof caps on integral 0.20 m ledges.

The Designer's final stair correction supersedes the rejected reversing half-circle proposal. Adopted stair centres: W(3.65,61), E(50.35,61), N(32.4,110.30), S(40.2,9.20). Each flight rises 3.6 m over 180° with 22 risers; each upper landing occupies the following 50°, advancing 230° per storey. Apertures are polygonal circles of radius2.75 m; landing plates extend to that perimeter. The 0.10×0.65 m steel edge rims span radii2.75..2.85 m. W/E rims join the retained y60 transverse beam branches; the south rim joins the y6.35/y12 branches; the north rim joins y108 and an added transfer to y114. No new well posts were added. Lower and upper connections include underside thickening with at least0.20 m angular length at the inner radius. The ground slab itself supplies the bottom approach landing. Adopted core centres are W(3.8,66.30), E(50.2,66.30), N(27.85,110.7), S(45.3,8.5), within the allowed tolerance.

The reversed-flight trial exposed a real headroom failure near shared landings; it was rejected before rendering. For the corrected stairs, 3,648 upward samples returned minimum2.700 m and no result below2.10 m. The independent `check_headroom_v02.py` then intersected projected underside faces with 512 actual convex walking regions and minimized the affine height difference over intersection vertices: minimum2.700 m, no violations. The governing pair was `StairLanding_E_3_9` beneath `Beam_5_10_1_1_0`. The continuous test excludes the actual rail-edge footprint by a40 mm radial allowance and uses the model's1 mm contact tolerance; a first test correctly required debugging micrometre-wide seam intersections. The final result must be rerun against the frozen v02 geometry. These are geometric clearance checks, not a code-compliance or structural-capacity claim.

Preflight progression, before final rendering:

| Stage | Members | Pairs | Floating |
|---|---:|---:|---:|
| Clipped domains and1.5 m subdivision |19,200|14,064|0|
| Rectangular junctions and support corrections |25,691|1,908|0|
| Chamfered shoulder and sloped-facade corrections |26,680|1,111|0|
| Final angular stair topology and circular openings |30,981|305|0|

The last305-pair table was dominated by insert slope framing orientation, south corner/facade joints, roof/site contacts and ground thickening duplicated inside the ground slab. Subsequent source edits address these as families. No independent Inspector has yet been invoked; the20-pair gate still applies. View27 was appended to expose the new stair rim/landing/beam connection; views01–26 retain their numbers. View18 follows the adopted west stair centre. Glass verification still requires the Cycles south/court/stair subset.

The permitted experiment17 override in `tools/layers.py` classifies known roof drains, parapets, plant components and site surfaces. The exported v01 audit now reports zero elements in `other` (61 previously unclassified).

### Open review item

1. Confirm at least1.20 m usable landing exits and routes around the west/east perimeter-side landings and adjoining cores in the floor plans and stair cutaway. The3 m corridor jogs are implemented; a circular floor connection alone does not establish every usable route width. No circulation requirement is ticked on this basis alone.

## v02 - final frozen handoff

**31,149 members; 0 penetrating pairs above1 mm; 0 floating at2 mm; converged: no.** `render_v02.log` is the final standard check; earlier preflight reports are superseded. Standard Workbench views01-27 and supplementary frozen-model views28-31 are complete. Geometry has not changed since the first v02 render. The final24 added members before freezing were core roof ledges. Final collision families: none.

The exact saved model passed `check_headroom_v02.py`:512 usable convex tread/landing regions, minimum2.700 m, no violations below2.10 m. `headroom_v02_final.log`/`headroom_v02.txt` preserve the final result. `check_rims_v02.py` finds actual beam/header contacts for all16 raised stair rims under the standard2 mm SAT-gap predicate; `rim_contacts_v02.txt` names those joints. Neither check proves joint capacity, bearing area or complete foundation load paths.

Five independent per-storey Inspectors confirmed the courtyard repair, partial northern insert/east passage, facade rhythm and external frame, five occupied bands, open curved stair wells and sparse roof plant. Their reports are merged by reference in `inspection_v02.md`. R03,06,08,09,10,12,19,21,27,29 are newly ticked from the relevant visual and parameter evidence. R07/13/16/22/23/24 retain unverified support/clearance portions. R17 remains open: even close plan30 does not make the intended room/corridor topology legible; this observation alone does not establish absent partitions. Phase2 proportions and structural review remain pending.

**Actual circulation defect:** the read-only `check_routes_v02.py` rasterizes actual frozen floor/landing faces and obstacle sections50 mm above the floor at50 mm spacing. Its1.20 m disc cannot get from west level1 or west level4 landings to the x9 corridor. Level1 has271 valid landing-disc centres and only277 cells in their reachable component; level4 has210 centres/component210. Higher obstacles are omitted optimistically. `routes_v02.txt` and `route_v02_W1.npz`/`route_v02_W4.npz` preserve the evidence. These are sampled results, not a continuous/code-compliance claim. The outward-facing finite landings require a Designer correction in v03; R15/R18/R30 stay open despite zero collisions and adequate vertical headroom.

Cycles transmission uses explicit collection material roles in `views_astra.py`, muted palette,32 samples,1200x900, OPTIX. South12, court15 and enclosed stair28 are complete; `render_v02_cycles_muted.log` ends DONE and the presentation blend is saved. The ground Inspector confirms visible transmission with readable interior columns/stairs in12, transparent insert rooflight/east glass in15, and visible flights/rails through stair enclosure28. R20/R26 are ticked for this required representative subset, not every individual pane. The earlier default-white south image is a superseded diagnostic. The presentation process did not alter frozen geometry. View31 supports the grade route visually but does not close exact retaining continuity underR14.

### Designer questions for v03

1. Replace the rotating outward-facing landing scheme with an exit arrangement that reaches the inward corridor at every floor. Nearest alternative: a full360-degree per-storey advance with fixed inward-facing finite landings, retaining the four stair locations/radii, subject to going, risers, headroom and actual exit-envelope checks. Do not waive the1.20 m route from headroom alone.
2. Confirm each rim/header/frame support path and minimum bearing faces in the structural review; actual contacts are established, capacity is not. Keep the connected perimeter rims and avoid adding reference-inconsistent well posts.
3. Resolve R17 evidence by showing the actual office/corridor/laboratory partition topology in a legible capped plan or interior view; if the geometry itself is deficient, repair it in v03. Preserve the full room scope.
4. Complete the south/court/stair transmission review and phase2 reference proportions on the final corrected version. Retain all eight reference roles and the complete ring/insert/plant scope.

No shared geometry modules were changed. The experiment17 layer override remains the sole shared implementation change. Runtime token/cost telemetry is unavailable.

## v03 — source-correct semicircles and circulation (unrendered development)

v02 remains immutable. Designer rechecked input08/03 and corrected the previous full circular aperture inference: W/E/N stairs occupy north semicircles, S the south semicircle, with a straight opposite-side gallery joining each pair of flight endpoints. The final v03 source uses identical180-degree flights with22 risers per3.60m, half-disc radius2.75m slab openings,1.40m straight gallery/endpoint landings, retained full supporting rims and0.40x0.65m diameter headers on the gallery side. Both earlier230-degree progression and the unrendered310-degree/28-riser trial are superseded. Stair positions, radii,19x6 grid, five levels, building envelopes, insert and plant are preserved.

North core alone rotates90 degrees and moves to(27.10,111.35), with foundation, openings, walls and roof cap derived from the same bounds. Its outer faces are x24.725..29.475,y109.725..112.975. The conceptual north bypass above the y108 column is1.425m; actual route checks remain the deciding evidence. South east-corridor return begins at y13.95 instead of12.80 to clear the turn above the y12 column. W/E stair-side doors centre on y60.30 with1.40m openings; the ground east branch uses y61.00 through the laboratory and courtyard-gallery wall, clear of the y60 laboratory divider.

Room-door audit found a real R17 defect: west office doors coincided with transverse partitions and became two0.60m stubs. Doors now use each actual3m/6m room interval. A12m west laboratory midpoint coincides with a main column, so that room instead uses its first6m-bay midpoint. Room sizes and transverse partitions remain. Capped vector plans are to be extracted from the actual frozen mesh, with program labels outside wall geometry.

Development checks, not final version results:

| Unrendered trial | Members | Pairs | Floating | Notes |
|---|---:|---:|---:|---|
| Fullturn fixed inward exits |31,900|2|0|Superseded after source reread; two ground underside laps crossed grade beams. |
| Semicircles and straight galleries |29,812|48|0|All48 pairs were gallery slabs duplicating nonrectangular floor remnants. Caller now reserves gallery rectangles before floor subdivision. |

The semicircular trial passes all20 floor-exit raster screens with a1.30m sampled disc through2.10m actual obstacle height. Its continuous swept-envelope check passes all20 endpoint galleries and all4 upper circulation loops. The east exits expose accumulated float32 floor-seam residue (about0.0000143m2), requiring per-gap measurement rather than a repeated-area threshold. The ground east courtyard branch identified two real doorway returns; the source corrects these in the next preflight. A prematurely launched diagnostic opened the previous saved fullturn model before the semicircular job saved; `routes_v03_semicircles.log` is explicitly stale and cannot support a model conclusion. Subsequent final diagnostics must share the geometry digest written by `snapshot_v03.py`.

The support helper checks actual full-footprint column/pedestal/core-foundation faces and named rim-to-foundation contact chains. A249-seat pass on the earlier trial is development evidence only; rerun on frozen geometry. Contact paths do not establish joint capacity or complete bearing minima. The new nominal0.20x0.40m corbel-seat audit must report its exceptions honestly. Section sizes, reinforcement, diaphragm capacity and retaining design remain inferred, not engineered.

The narrow experiment17 layer override now classifies `Insert/InsertFloors/InsertEastShelf` as frame. No shared geometry module changed. Final counts, renders, independent inspections and remaining requirements follow after the same geometry passes the required checks.

## v03 - final frozen results (supersedes development counts above)

**30,003 members; 0 penetrating pairs above 1 mm; 0 floating at 2 mm; converged: no.** Standard check: `render_v03_checks.log` and `experiment_17_astra_v03_blender_pairs.txt`. All 34 Workbench views and the three muted Cycles views 12/15/28 are complete. No geometry changed after the first v03 render. Final pair families: none. Independent ground review reopens R09: visible front shafts/corbels divide the upper fascia and ribbon into six bays, inconsistent with the source reading of a continuous upper front. This is a real geometry/source-fidelity issue for v04, not a presentation failure.

### Snapshot and changes

The frozen mesh identity is **3c85bdc6c1282389ab1659f8295bba9d183fde50345fd2ae74b3dec840fd2216**, SHA256 of sorted names and world vertices rounded to one micrometre. `reproduction_v03.txt` independently rebuilds the complete script and matches this identity exactly. All final route, headroom and support reports identify the same 30,003-member snapshot. Earlier trial counts and the stale diagnostic named above do not describe this version.

In addition to the source-correct semicircular stairs, straight galleries, rotated north core and room-door corrections recorded above, the final model adds the Designer-approved enclosed two-level insert connection at y75. Its aligned doors are 1.40 x 2.40 m; its fitted west enclosure, sidewalls, lintels, decks and roof close the former missing access/enclosure. Ground west and all east decks bear on fitted steel ledgers; the raised west decks at z3.60/7.20 bear directly on the retained concrete EdgeBeam. The narrowed raised-west steel is supplemental attachment only. Two first-raised south beam ends now bear on rooted concrete core ledges. Eight upper reduced-width corbel seats remain explicitly classified below. Finally, sixteen nominal perimeter core-base strips fill the 0.25 m vertical gap between core foundations and walls; fitting the south column produces eighteen convex pieces. The exact script reproduces these pieces; the saved blend is not an unreproducible manual repair.

### Quantitative evidence

- `routes_v03.txt`: all twenty stair/floor raster screens pass a 1.30 m sampled disc on a 50 mm grid through 2.10 m obstacle height.
- `route_envelopes_v03.txt`: all 47 continuous supported swept envelopes pass. Twenty stair exits, twenty endpoint galleries, four upper circulation loops and the ground east courtyard branch use **1.20 m** width. The two insert-access cases at z0/3.60 use **1.40 m** width. Every case uses 2.10 m headroom. Actual floor-face unions and obstacle sections are tested; the float32 seam allowance is a maximum 20 micrometre inscribed diameter, with 1e-7 m2 obstacle intersection tolerance. These are geometric checks, not statutory compliance.
- `headroom_v03.txt`: 368 usable convex tread/landing regions, minimum 2.700 m, zero violations below 2.10 m. The governing region is the east first-raised gallery under `Beam_3_10_1_1_12`.
- `supports_v03.txt`: 250 column/pedestal/core-foundation footprint seats pass (the earlier note's 249 was a transcription error; corrected against the saved report during v04). Of 876 nominal corbel cases, 866 have ordinary 0.20 x 0.40 m seats; eight have 0.20 x 0.325 m seats (0.065 m2, an 18.75% width/area reduction); two first-raised cases instead use actual 0.080 m2 core-ledger seats. The eight reduced cases have no capacity-equivalence claim.
- All 22 local connection-face checks pass: two alternate core seats, twelve insert deck-seat/attachment cases and eight lintel ends. Raised-west deck contact is 0.15 x 2.00 m = 0.30 m2 on the retained beam; it is not attributed to the shortened steel. All eight core wall-to-base/base-to-foundation horizontal union checks pass. This explicitly checks vertical bearing rather than relying on side contacts.
- `rim_contacts_v03.txt` and the support report name actual beam/header contacts and footing-connected structural chains for all sixteen raised stair rims. An undirected contact chain alone does not prove gravity or lateral capacity. Reinforcement, anchors, diaphragm forces, soil, retaining restraint and section capacities remain inferred and require engineering design; broad R22-R24 closure remains subject to independent structural review.

### Views and inspection record

Workbench `experiment_17_astra_v03_blender_view_01.png` through `_34.png` are complete. Appended view32 is the north gallery/core plan crop at level1, view33 the south gallery/core plan crop at level1, and view34 the insert-link section at y75. Cycles filenames are `experiment_17_astra_v03_cycles_view_12_muted_none_no_foundation.png`, `_15_muted_none_no_foundation.png` and `_28_muted_none_no_foundation.png`; explicit material roles, muted palette, 32 samples, 1200 x 900, OPTIX.

Separate mesh-derived capped plans `plan_v03_32.png` (west offices/corridor/labs, level1), `plan_v03_33.png` (east asymmetric rooms and ground court gallery) and `plan_v03_34.png` (insert connection, level1) make the actual walls and door openings readable. They are separate evidence drawings, not substitutes for the numbered Workbench views. Twenty `plan_v03_route_<W/E/N/S><0..4>.png` crops show the tested stair exits. The existing SVG polygons, clipping, line styles and text were rasterized with installed Windows GDI+ via `rasterize_plans_v03.py`, without changing the model. Chrome capture failed inside the sandbox; two escalation calls were aborted while awaiting approval and never ran. The native renderer required no browser, installation or security-policy change.

Fresh Inspector threads were unavailable at the runtime thread limit. Coordinator authorized the existing independent `/root/stair_exits` reviewer to inspect five storey subsets sequentially; the reviewer did not read geometry scripts. Reports are `inspection_v03_ground.md` and `inspection_v03_level1.md` through `_level4.md`, merged by reference in `inspection_v03.md`. The same-reviewer runtime exception is explicit. R09's inherited pass is cleared. Plan verdicts and final requirement ticks are recorded in the merged report and requirements table.

### Open Designer questions

1. Correct the exposed upper south-front shafts/corbels without changing the source-supported seven porch column stations, inclined glazing or major volumes. Nearest alternative is the Designer's bounded upper-front support/concealment revision in v04; v03 remains immutable.
2. Complete the independent structural and source-proportion review, especially every load-bearing family, retaining restraint and diaphragm connections. Preserve the named bearing/contact evidence and the eight reduced-seat limitation; do not convert geometric contact into a capacity assertion.

Shared geometry modules remain unchanged. Only the experiment17 layer override is modified. Runner owns export/viewer/close-out. Runtime token/cost telemetry is unavailable.

Final inspection/requirement update: all five storey reports and capped-plan addenda are merged in `inspection_v03.md`. R01/R07/R13/R15/R16/R17/R18/R25 are newly ticked from the stated model, face/route and visual evidence. R09's inherited tick is removed. R11/R14 retain their unverified complete entrance/grade-route portions; R22-R24 require the formal structural review; R28/R32 require formal reference/phase2 review; R30 remains open because the south facade defect is real. R31 awaits Runner close-out. The independent reviewer also records Cycles28's dark, distant interior as a presentation limitation for a later perspective evidence view. A read-only actual collection inventory is `collection_tree_v03.txt`; south-front coordinates requested for the next Designer decision are `south_faces_v03.txt`. A second narrow experiment17 layer override maps only `Insert/InsertFloors/InsertLinkDeck` to FRAME after the Runner found three unclassified deck members. No new model version has been started by this Builder.

## v04 — unrendered development, 2026-09-17

Fresh Builder implements the Designer's source-based south enclosure correction. The entire metal field moves to y-1.00..-0.78, with seams to-1.03 and lip to-1.20. The genuine ribbon glass is centred at y-0.72; steel posts and timber sill/head lie y-0.78..-0.68. Nineteen shared ribbon/secondary-post stations avoid coincident steel and timber jambs; 57 steel brackets meet retained beams or shafts. Thirty-millimetre top/end/head/sill returns close the cavity. Exact dimensions/fixings remain architectural inference. All seven front shafts and their original concrete support members remain in place.

Initial south-only preflight:29,870 members,0 pairs,0 floating;368 walking regions with minimum2.700m headroom. Actual member signatures for14,056 named column/corbel/beam/floor/core/stair/insert members exactly match v03. The57 bracket checks exposed six end brackets with only50mm of their post face engaged; shifting their X interval inside the unchanged assembly endpoints gives the full contact. Actual rail-to-corbel clearance is30.00003mm. These are development figures, not final-version totals.

The R11 access audit found a real inherited doorway defect: existing glazing/sills closed the entrance markers, and the retained x27/y6 column occupied the nominal central portal. Designer approved an inferred entrance centred at22.50, clear x21.30..23.70 and z0..2.40, with jambs/head outside and movable leaves omitted in an explicitly open state. A3m-wide concrete approach closes the1.20m lawn-to-porch paving gap; its top0 has one150mm lawn riser. The second preflight found one150mm base/grade-beam overlap (29,875 members,1 pair,0 floating). Designer approved retaining the existing grade beam and fitting the compacted base around it:1.20m2 direct beam seat plus2.40m2 prepared base beneath the3.60m2 paving slab. Prepared soil and structural capacities remain inferred. No geometry has been rendered during these corrections.

Views35/36 append south support section/corner projection; view37 appends the entrance plan. A separate35mm perspective at level1 eye height1.60m, exposure+1.5EV, uses the existing Cycles kit and honest transmission. Actual-mesh tests cover the complete entrance-to-foyer route, stepped court route, exact doorway, slab support union, the established48 circulation cases, headroom, seats, and unchanged-member signatures before the first render.

## v04 — final frozen evidence

**29,876 members; 0 penetrating pairs above 1 mm; 0 floating at 2 mm. Phase 1 geometry converged.** The standard result is in `render_v04.log`; the final pair file is `experiment_17_astra_v04_blender_pairs.txt`, and pair families are empty. No geometry changed after the first v04 render. Final identity: **8a02c4b9865c497bbd2d1af58a76140a978e0863a98ebd97a32ff63a26951657**. `reproduction_v04.txt` rebuilds the final generator and matches that exact identity and count. The unrendered base completion and collection correction are therefore reproduced by the complete script, not just by a patched saved file.

### Final quantitative evidence

- `south_v04.txt`: all 57 secondary-bracket rail/concrete connections pass; the fascia is a continuous unnotched backing; actual minimum post-to-corbel clearance is **30.00003 mm**. Exact signatures match v03 for **14,056 members in the explicitly named column/corbel/beam/edge-beam/floor/core/stair/insert families**. This statement has that defined scope rather than claiming an unspecified all-member comparison.
- `route_envelopes_v04.txt`: **48 continuous route envelopes pass**. Twenty stair exits, twenty endpoint galleries, four upper loops, the east courtyard-gallery branch and the entrance/foyer route use 1.20 m width; two insert approaches use 1.40 m. All use 2.10 m height. `routes_v04.txt` supplies the twenty sampled stair-route corroborations. The same documented 20 micrometre seam allowance remains.
- `public_routes_v04.txt`: **28 exact walking-strip/aperture cases pass**, covering the lawn/paving/porch, courtyard garden/path, nineteen tread tops and final landing (twenty 150 mm rises), retaining top, terrace and exact **2.40 x 2.40 m** open entrance. Actual paving support is **2.40 m2 fitted base plus 1.20 m2 retained grade beam**, a full 3.60 m2 union. The beam has a named direct contact path to `FootingPad_120`. The lawn step is 150 mm and the garden/path step 100 mm. Tested terrain and occupied-interior volumes do not intersect. These are stepped pedestrian routes, not step-free access or code certification.
- `headroom_v04.txt`: **368 walking regions**, minimum **2.700 m**, zero violations below 2.10 m. The governing face remains the east first-raised gallery beneath `Beam_3_10_1_1_12`.
- `supports_v04.txt`: **250 full-footprint seats**, zero failures; **866 ordinary / 8 reduced-width / 2 alternate-core-ledger** corbel cases; **22 local connection faces** and **8 core-base interface unions**, zero failures. The eight reduced seats remain 0.065 m2, 18.75% below nominal area, without a capacity-equivalence claim. All sixteen raised stair rims retain named beam/header contacts and foundation-connected structural paths in this report and `rim_contacts_v04.txt`.
- Bearing geometry and contact paths do not establish reinforcement, anchor, diaphragm, retaining, soil or member capacity. Those limitations remain explicit for the independent structural review.

### Renders and independent review

All **37 Workbench views** are saved. Added views 35/36 show the projected south enclosure/support section and corner; view 37 shows the corrected entrance plan. Standard muted Cycles views **12/15/28** use the existing material roles, 32 samples, 1200 x 900 and OPTIX. Twenty-four labelled actual-mesh plans are saved as SVG/HTML/PNG: room/insert/entrance plans 32–35 and twenty stair-route crops. Native Windows GDI+ rasterization is recorded by `rasterize_plans_v04.py`; no browser capture is needed for these plans.

Perspective **40** is the selected interior evidence: camera **(33,10.1,5.2)**, target **(40.2,7.5,5.5)**, **35 mm**, eye height **1.60 m above level 1**, exposure **+2 EV**, world strength **0.35**, neutral fill **0.75**, **48 samples**, **1400 x 1100**. It shows the model's south stair from the wider common-space gallery, with its floor, curved flight, guards, open well, frame and inclined glazing legible. It applies source 03's interior relationships at this model location; the inclined south glazing is supported by sources 02/05, and the exact source-03 camera position is not claimed. Earlier views 38/39 are retained detail trials: 38 had a dominant foreground soffit, and 39 remained too close to the west stair. Only presentation settings changed between them; each has its own settings JSON. The final pose is in `interior_v04_40_settings.json`.

A fresh independent **gpt-5.6-luna** Inspector reviewed the ground subset. A second fresh storey spawn failed with `agent thread limit reached`; the Coordinator authorized sequential reuse of that same reviewer for all five subsets. No geometry scripts were read by the reviewer. Reports `inspection_v04_ground.md`, `_level1.md` through `_level4.md`, and `_interior.md` are merged by reference in `inspection_v04.md`. Stale pending-view wording and incorrect view attributions were sent back and corrected. The final independent reports find **no actual visual defect**. Ground details confirm the retained full-height supports, enclosure projection/returns and new entrance. Perspective 40's exact doorway detail is not legible from that camera; actual openings and route checks are separate evidence.

R09, R11 and R14 are newly ticked from the combined numerical and visual evidence. R20/R26/R27 now cite the final v04 presentation set. R30 is ticked for phase 1 after the standard 0/0 result and independent review with no actual defects. R22–R24 and R28/R32 remain assigned to the formal phase-2 structural/reference review; R31 remains Runner close-out work. Those final run gates are not waived by the Builder's phase-1 handoff.

### Designer question

1. Accept the narrow doorway-detail limitation of perspective 40 using the existing actual-mesh plans and route/opening evidence, or request a dedicated doorway view. The final image already resolves the former dark/distant stair presentation. No geometry defect is identified, and no doorway dimension or capacity is inferred from the perspective.

### Harness proposal after this run

Investigate repeated visibility/matrix preparation for large models: the 37-view Workbench batch took about 21 minutes before its numeric checks, while individual image rendering generally took 3–8 seconds. Shared harness optimization is a separate task; the model and checks use the existing tools.

## v05 — Phase 2 structural support completion, 2026-09-17

**Status:** Builder geometry, numeric checks, full renders and independent visual review complete. No actual visual or implementation defect remains. Formal structural acceptance and Runner close-out are separate Coordinator gates.

The generated model has **30,167 meshes**, geometry SHA256 **6cd07366762f8213cb58508c746d180142bf48f2534813f8f0bb0b64dc922f4c** (sorted names/world vertices at one micrometre). `reproduction_v05.txt` records an independent full generator rebuild with the same identity. The final master rendered file has **9968993522e362026e472282a4226d99961ec4017ae27497458e024213082417** because Blender decomposes reassigned render matrices with float32 roundoff; the explicit bridge is recorded below. V01–v04 artifacts remain unchanged. The version starts from v04 and invokes the versioned local `support_geometry_v05.py` after inherited joinery.

### Changes and exact retention

Designer concept 8 supplies three structural corrections: north/south perimeter slab ledgers, a supported exterior court-stair waist and landing, and contained fill/base beneath the north terrace. Main grid, occupied floors, internal stairs, facade, reference envelope, terrace/stair walking tops, routes and camera 40 remain as v04.

`retained_v05.json` proves **29,870 of 29,876 original members are bit-identical**. The only six altered originals are buried portions of `SouthClosure_East_Fit5/Fit7/Fit9` and `SouthClosure_West_Fit7/Fit10/Fit14`. These 30 mm weather returns initially crossed six new south slab seats; treating metal closure as concrete bearing was rejected. The Designer authorized removing only their actual intersections at y0.30–0.50 and zF−0.45…F−0.25 for F10.8/14.4/18. Each removed volume is approximately 0.0012 m³ and is completely replaced by ledger concrete. Exact bounds/volumes and closure-to-concrete face continuity are recorded. Each original closure becomes two fitted pieces; its exposed geometry is retained. All primary member signatures remain unchanged.

There are **291 added objects**: 128 perimeter ledger pieces (83 north, 45 south); 20 exterior waist pieces; 3 landing support pieces; 1 landing ledge; 2 stair footing pieces and 1 prepared-soil pad; 3 terrace walls; 13 terrace footing pieces; 6 fill and 6 granular-base pieces; 102 prepared-subsoil pieces fitted around retained foundations; and 6 additional weather-return fragments. The six modified closure originals remain in the total. Existing top-level collections are retained; `Site` gains `TerraceFill` and `TerraceBase` children. New concrete uses existing Beams, SiteStairs, Retaining and Foundation collections.

### Actual support evidence

`completion_v05.txt` has **zero failures**. Its tests use actual mesh face unions with explicit float32 seam allowances; no micrometre edge contact is credited as a structural joint.

- All **4,534 ordinary physical slab-end cases** pass the 120 mm minimum, including **all 261 previously failed ends** with the intended **200 mm seat**. The 1,960 excluded small/notched/decomposition faces remain separately classified, rather than becoming fictitious independent panels. North ledgers bridge y113.70–113.80 at levels 1–5; south ledgers bridge y0.20–0.30 at levels 3–5. Root concrete remains part of the unchanged beam/shaft. The six 30 mm corner filler pieces each have two full **200 × 200 mm vertical concrete interfaces**, approximately **0.04 m² each**, leading through adjacent monolithic ledger pieces to named retained beams. These are not freestanding strips or unanchored metal seats. Joint reinforcement and capacity remain inferred.
- All **19 exterior treads and the top landing** have full underside support. Twenty convex pieces make one stepped-top waist; every piece has positive-area interfaces greater than 0.01 m² along paths to both the bottom footing and the retaining-wall-supported landing. The bottom seat is **0.49 m²** and the top plate/ledge seat is **0.459992676 m²** against nominal 0.46 m². The retaining wall/base and explicit prepared soil complete the modelled path. Walking surfaces and 20 × 150 mm rises are unchanged.
- The terrace has **184.089966431 m² requiring support**, with **184.089914856 m² actual union coverage**; the approximately 0.000051575 m² residual lies within the stated 20-micrometre float32 seam allowance. The separate **0.507056778 m² north edge strip** is the Designer's intended **30 mm slab cantilever** over the glazing clearance. It is not claimed as ground-supported. The actual north-wall gap is **30.003052 mm**. Walls, footings, fill, base and prepared subsoil have verified horizontal support unions; soil is contained independently of glazing. Retaining stability, ties, reinforcement and soil capacities are not calculated.

The local new-member SAT initially found 16 north-ledger/stair-header penetrations. Fitting the new ledger solids to the actual convex header planes resolved that one geometry cause. The six later weather-return bearing conflicts were found by face coverage, not collision diagnostics, and were resolved by the narrowly approved buried trims. The final local support SAT has **0 penetrating pairs**. The final unmodified standard gate in `render_v05.log` reports **30,167 members, 0 penetrating pairs at 1 mm tolerance and 0 floating members at 2 mm contact tolerance**. There are zero final overlap families.

### Retained and current regressions

`carried_evidence_v05.txt` binds unchanged v04 structural measurements to exact v05 member retention: **250 footprint seats; 866 ordinary + 8 reduced-width + 2 alternate beam cases; 22 local connection faces; 8 core-base unions; and foundation paths**. These are honestly identified as retained measurements, not newly rerun tests. The eight 0.065 m² seats remain 18.75% below nominal area, without a capacity-equivalence claim.

The insert's **67 horizontally seated cases and 45 internal integral interfaces** remain separate. The latter are 36 level-1 and 9 roof cases, with **13.8749976158 m² required and covered concrete end-face area** and a full **0.40 m beam-supported band** beyond every joint. This unchanged continuous cast-RC system needs reinforcement continuity; it is not 112 independently precast seated ends. No insert geometry was added or removed.

Current v05 reports rerun **57 south bracket contacts**, the **14,056-member primary signature comparison**, **16 rim/header groups**, actual core/diaphragm face interfaces, **48 circulation envelopes**, **28 public strip/aperture cases**, and **368 internal stair walking regions**. These pass with **minimum headroom 2.700 m** and no occupied-volume/terrain intersection. Reports are `south_v05.txt`, `rim_contacts_v05.txt`, `structural_followup_v05.txt`, `route_envelopes_v05.txt`, `public_routes_v05.txt` and `headroom_v05.txt`.

### Render and inspection scope

The full Workbench set is **41 images: 01–37 plus 41–44**, not 44 images. Added 41 shows the exterior stair support, 42 the terrace containment, 43 the north ledger and 44 the south ledger. Twenty-four retained actual-mesh plans plus four new capped support sections produce **28 SVG/PNG drawings** using native GDI+. The capped sections explicitly show the waist, footing, landing ledge, terrace fill/containment and beam-edge seats.

The three standard Cycles views remain 12/15/28. Final interior perspective 40 retains v04 camera (33,10.1,5.2), target (40.2,7.5,5.5), 35 mm lens, 1.60 m eye height above level 1, +2 EV, world 0.35, fill 0.75, 48 samples and 1400 × 1100 output. Standard whole-model SAT/contact ran once on the master rendered geometry, after the harness reset/save; subsequent renders use `--no-check`. Two disjoint Workbench batches have separate output prefixes to avoid file races; their PNGs are consolidated into canonical version filenames. `render_evidence_v05.json` inventories all five saved-model identities and **73 PNGs:41 Workbench,4 Cycles,28 capped drawings**, with image SHA256 values and unchanged interior40 settings.

A fresh independent `gpt-5.6-luna` Inspector completed the ground subset. A second storey spawn returned `agent thread limit reached`; the Coordinator authorized sequential reuse of that reviewer. Five storey reports and a separate four-image presentation report now pass with **no actual visual defect** and are merged by reference in `inspection_v05.md`. This is one independent reviewer across six reports, not six separately spawned reviewers. Ground includes whole-frame/from-below WB10/11 and new support41–44; all41 Workbench images are covered by the union. Local x12 support sections do not prove the buried corner trims; those use numeric evidence. Cycles transmission is representative, not every-pane certification. Camera40 does not claim a visible doorway or exact historical pose.

The final identity audit detected render-harness float32 matrix decomposition, not a design edit. `render_identity_difference_v05.json` proves all local meshes unchanged. Master rendered world coordinates differ from preflight only on19 court treads (maximum0.238419 micrometre) and10 inclined-glazing rails (maximum3.814698 micrometres). Secondary Workbench and Cycles batches have hash **927586e39708935f92af4fad3e359e617db733e09cde56b39918195250bd6975**: they differ from master on two court handrails by less than0.5 micrometre and two insert glazing rails by at most3.814698 micrometres. All other world vertices remain exact, including every primary bearing interface and new support. `render_support_bridge_v05.txt` repeats the19 actual master-rendered tread underside unions, all passing within the existing20-micrometre seam allowance. The exact29,870-original retention claim above applies to generated/preflight geometry; render-time roundoff is separately qualified. Exact hash equality across batches is **not** claimed, and the standard SAT/contact is not falsely attributed to the generated hash. No repeated whole-model check or render is needed for these explicitly bounded presentation roundoff differences.

The only shared-code change is the sanctioned experiment-17 `tools/layers.py` override assigning the 12 `Site/TerraceFill` and `Site/TerraceBase` elements to the existing foundations/site layer. It does not alter geometry; Runner performs the final bake and audit.

R20/R21/R26/R27 are reconfirmed by the final presentation set and independent review. R30's geometric and visual conditions pass; its phase completion follows Coordinator structural acceptance. R22/R24/R32 await that formal acceptance of the supplied support/identity evidence, and R31 awaits Runner close-out. No gate is silently waived by this Builder record.

**Open Designer questions:** none. All implementation conflicts received explicit concept amendments. Builder checks, renders and independent visual review are complete; final structural acceptance and Runner close-out remain Coordinator responsibilities.

## v06 — User review corrections, 2026-09-17

**Status: not converged.** The requested geometry and display changes are built and the complete image set is recorded. One actual facade attachment issue remains open: 30 CourtSouth spandrel pieces lack a modeled primary connection. The unmodified stock gate passes 29,976 members, zero penetrating pairs and zero floating members, but the missing attachment remains a distinct structural defect. Appearance or a zero-pair result cannot close the missing connection.

### Geometry and changes

The generated/preflight model has **29,976 meshes**, SHA256 `523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416` for sorted names/world vertices rounded to one micrometre. `reproduction_v06.txt` records an exact fresh factory-startup rebuild. V01–v05 geometry and scripts are preserved. The generator uses the new `support_geometry_v06.py` copy, not edits to the previous helper.

Concept 9.1–9.7 implements the user's corrections:

- All 1,250 corbel wings and 1,250 corbel seats rotate 90° in plan. Wings project along global X, aligned with genuine transverse Beam spans, while shafts and support heights remain unchanged. Ten integral 50 mm rear nibs restore complete bearing under the shifted first-raised y6 beams; the two core-ledger exceptions do not receive invented nibs.
- All 760 invented longitudinal EdgeBeam solids are removed before fitting. Real transverse beams, slabs and facade spandrels remain. Twenty north ledger dependencies are regenerated against actual primary concrete, and the two raised west insert-link ledgers recover their full 200 mm attachment and 150 mm seat.
- The specified opaque east/west panel fragments below the south incline are removed. Twenty-three fitted pieces are clipped or removed; the newly cleared region is open, with no invented triangular glass. Real upper/later spandrels and existing glazing remain.
- All 122 landscape/soil/base objects are omitted. Actual floors, paving, terrace, stairs, retaining walls and foundations remain. Their external ground-bearing interfaces terminate at declared unmodeled earth.
- The complete facade timber/steel frame and insert skylight-frame collections, plus every StairRim, map to fixtures. All 6,959 explicitly requested objects pass. True Beam, Column, Corbel and RooflightSeatBeam remain frame. A later independent layer review found the existing generic `entrance` rule also caught the concrete EntranceApproachSlab; an exact experiment-17 override now classifies that single object as floors. No geometry was changed for classification.

`changes_v06.json` measures **23,710 unchanged members, 2,703 changed shared names, 3,754 deleted names and 3,563 added names** relative to v05. Primary shafts, real beams, main slabs, foundation pads/pedestals and stair walking geometry remain unchanged. Reclassified fixtures include 6,145 unchanged pieces and 814 separately inventoried refitted pieces; reclassification is not falsely described as the only operation on those 814.

### Actual structural and route checks

All ordinary seats were measured anew: **866 ordinary 350 × 400 mm seats (0.140 m²), eight 350 × 325 mm core-reduced seats (0.11375 m²), and two independent core-ledger seats (approximately 0.080 m²)**. The eight reduced seats retain an 18.75% width/area limitation without capacity equivalence. The obsolete 0.065 m² area is not reused. All 2,500 seat/wing shaft roots have finite opposed faces, with minimum area **0.359998741151 m²**. Each of the ten nib roots has approximately 0.070 m².

Current reports verify all **250 foundation footprint seats, 22 local connections, eight core-base unions, 16 stair rim/header paths, 4,534 ordinary slab-end cases and all 261 specified 200 mm perimeter seats**. The insert's **45 integral vertical interfaces** have complete **13.874997615814 m²** coverage and adjoining 400 mm support bands; **67 horizontal cases** remain a separate classification. The 57 south enclosure brackets pass and the actual ribbon-to-corbel clearance is approximately 180 mm. No deleted EdgeBeam is credited in these paths.

The first rotated-corbel fit exposed real defects in the landing and terrace walls because a horizontal footprint subtraction removed concrete outside the actual chamfer volume. The independent Designer fallback approved concept 9.7/R39. Exact XZ subtraction over actual Y intervals now retains a full landing cap, with separate **0.439992676 m² lower ledge** and **0.050000000 m² upper corbel** seats. The landing underside is fully covered over **1.379996033 m²**; 12 plate pieces have finite paths to the retaining wall or corbel/shaft. The wall-plus-primary-concrete union covers all 24 section boundaries/midpoints and every actual wall bottom has a real concrete seat. Twelve former void probes pass. `fit_delta_v06.json` confines the repair to the approved three support families, records recovered volumes of 0.007971446, 0.001921495 and 0.560853322 m³, and reports zero local SAT pairs. R39 is independently accepted.

The terrace's **184.089966431 m²** required underside is separated into **11.399926567 m² actual concrete** and **172.690039864 m² explicitly unmodeled earth**. Its separate **0.507056778 m² northern strip** is the declared 30 mm cantilever. No soil/base support claim is retained from v05.

All **48 continuous route envelopes** pass. Sixteen CorbelSeat ceilings intersect four route envelopes, with actual minimum **2.0999996185302727 m**, within the existing 20 µm float32 coordinate allowance at the 2.10 m boundary. No positive-volume intrusion beyond that tolerance is accepted. The **368 stair regions separately have minimum 2.700 m**; the gallery minimum is not reported as 2.700 m. Public route and doorway checks retain constructed approaches while explicitly excluding omitted ground.

### Open facade attachment issue

The all-plane panel graph excludes glass from support paths. It roots **3,630 of 3,660 panels**, including all changed corner fragments, through actual finite concrete/panel/frame interfaces. The axis-only preliminary screen in `connections_v06.txt` flagged 68 pieces; 38 were resolved through actual sloped interfaces or an existing terrace footing and are not defects.

The remaining **30 CourtSouth pieces** occupy five bays and six bands. Their inward face at y12.55000019 lies **250 mm beyond the slab edge** at y12.30000019; the true beam face is approximately 350 mm away. A glass-excluded v05 comparison proves **24 inherited gaps** in bays 1, 2, 4 and 5. Bay 3's six pieces formerly contacted an old Y-projecting corbel through timber heads/jambs and lose that path under the required rotation. Thus the issue cannot all be dismissed as historical, nor can window glass be credited as gravity support. Evidence is in `panel_roots_v06.json`, `panel_baseline_v05_for_v06.json` and `panel_root_gaps_v06.txt`.

The Designer's nearest coherent repair is discrete slab-rooted facade brackets, retaining the corrected corbels and zero EdgeBeam scope. `facade_connector_candidates_v06.txt` is a read-only probe of 60 locations: two per panel, with complete 100 × 100 mm upper side interfaces, 100 × 150 mm ground interfaces, and a 100 × 200 mm actual Beam/GradeBeam band under each root slab. A possible thin-plate/web connector was supplied for design consideration; **no connector geometry has been added or approved by the Builder**. Because v06 is rendered, a geometry repair belongs in a subsequent version.

### Renders, independent review and identity

The final inventory contains **51 Workbench images (01–37, 41–54), four selected Cycles images (muted 12/15/28 and interior40), and 30 capped drawings: 85 images**. One preliminary white Cycles12 is explicitly excluded. The full initial 49-view set was rendered once; only presentation corrections 53/54 were added after independent findings. View52 is occluded by an unrelated insert slab, so isolated saved-geometry detail53 supplies the landing judgment. Original fixtures view50 retains the historical approach-slab classification; view54 shows the corrected layer map. Plan35's stale lawn label was corrected to “150mm STEP TO UNMODELED GROUND.” All originals remain preserved and identified honestly.

Fresh Luna Inspector and prior Luna reuse attempts both failed with the runtime thread limit. The Coordinator assigned the former v05 Builder as one independent v06 Designer/reviewer, who did not author or read v06 geometry code. Five storey reports plus source, layer and presentation reports record that exception. Sources 01/02/06/07 were freshly read by that reviewer; the Builder did not read the source images. The requested corbel/beam hierarchy, open south corner, omitted ground and fixture distinction pass the reviewed images, while the CourtSouth attachment issue remains explicit. The independent reviewer confirmed corrected views53/54 and all85 inventoried images; both presentation findings are closed.

The saved Workbench/Cycles masters share geometry hash **25c4743bc414e69436a7b18e84e6fc5535ae58651dd41d9913a78b3ee06e6f1a**. `render_identity_difference_v06.json` proves every local mesh unchanged, with 93 matrix differences and only 29 world-coordinate changes: 19 court treads and ten inclined-glazing rails, maximum **3.814697265625 µm**. All primary support world vertices are exact. The saved detail master has hash **eb8c41148a212fc5e40a778760eb1142a3e661c1ba7963af4f7dcc1ea6bc20a9**, with only the documented additional handrail/rail roundoff, 31 changed objects relative to preflight. All 19 actual master-rendered tread underside unions pass in `render_support_bridge_v06.txt`. No duplicate whole-model gate was run for Cycles or detail renders. `render_evidence_v06.json` records all identities and image hashes.

Runner rebaked the single approach classification without re-exporting geometry: current viewer JSON SHA256 **3418977bac8e7bb2913c6d7eef4ee381396477601414db8d4cffdc6956d23a80**, 29,976 elements, zero unclassified objects and six taxonomy checks passed. This is not final structural close-out.

### Standard gate and remaining Designer question

**Standard diagnostic result: 29,976 members, zero penetrating pairs at1mm, zero overlap families, zero floating members at2mm.** The unmodified stock checks completed on saved master hash25c4743bc414e69436a7b18e84e6fc5535ae58651dd41d9913a78b3ee06e6f1a; render_v06.log lines200–202 and the canonical pairs file record the result. The initial 29,961-mesh 0/0 preflight is historical and not substituted for this result.

1. Approve the bounded discrete CourtSouth facade-connector concept and subsequent version scope, using the measured 60 candidate root/receiver locations, then verify actual roots, panel paths, local collisions, routes and final diagnostics. No geometry repair or capacity waiver is implied by the current candidate. R22/R30/R32/R34/R38 remain open where they require complete structural convergence; R39 is closed only for its independently accepted local landing/wall repair.


## v07 — discrete CourtSouth attachments; 2026-09-17

### Change and scope

Implemented approved concept10 only: **60 discrete welded/anchored steel assemblies,180 convex meshes**, two for each of30 CourtSouth panels across five bays and six bands. Each assembly has100 mm-wide,10 mm-thick end plates and a10 mm web across the250 mm slab/panel gap. Upper hardware is100 mm high; ground end plates are150 mm high at staggered levels with one continuous300 mm-high web. Outer plates snap to the actual retained concrete planes. Anchors, weld details and capacities are inferred/unmodeled.

`delta_v07.json` proves all **29,976 v06 objects exactly retained**, including names, local/world vertices, transforms, polygons and collections. No removal or modification exists. Added hardware belongs to existing `Facade/SteelFrames` fixtures; no shared toolkit or layer changes were needed. The corrected corbels/Beam hierarchy, zero EdgeBeam, open under-incline side, omitted earth, walking surfaces, building outline and R39 landing/wall repair remain exact. The generator is a minimal v06 copy plus `facade_brackets_v07.py`; immutable `support_geometry_v06.py` remains its inherited support helper.

### Actual checks

All120 concrete/end-plate interfaces and120 web/end-plate interfaces pass full actual face unions; actual dimensions match the concept within2.136230469 micrometres. All60 continuous root-to-beam slab strips and60 actual100×200 mm Beam/GradeBeam seats pass. Upper concrete interfaces are nominal0.010 m2 and ground0.015 m2; weld interfaces0.001/0.0015 m2. These are anchorage interfaces, not horizontal gravity-bearing claims or capacity calculations.

The glass-excluded all-plane graph now roots **3,660/3,660 panels**; all30 prior CourtSouth failures are closed, and the former3,630 paths remain available on exact geometry. Both new connections for each panel reach its real slab without glass or timber gravity credit. Full48 continuous circulation envelopes and constructed public routes pass, including the150 mm-high ground hardware. The retained gallery tangent remains2.0999996185 m within the recorded20 micrometre coordinate allowance;368 unchanged stair regions separately retain the2.700 m minimum. `evidence_reuse_v07.md` maps every inherited concrete/slab/core/rim/insert/R39/ground-boundary check to exact retained inputs.

Local SAT reports0. **Final unmodified stock result:30,156 members,0 penetrating pairs at1 mm,0 overlap families,0 floating at2 mm.** `render_v07.log` ends DONE with exit0, and the canonical pairs file contains0. This whole-model gate ran once, on the final saved canonical render master.

### Renders, independent review and identity

Full final set: **55 Workbench01–37/41–58; four Cycles12/15/28/interior40;32 capped drawings;91 images**. New55/56 show upper/ground bracket sections,57 the thin stepped assembly,58 all60 assemblies; capped55/56 show actual mesh sections. Existing view numbers are preserved. WB52 remains occluded;53 is the usable isolated landing view. Section55's corrected “capacity unverified” caption closes the sole presentation wording comment; initial caption artifacts remain excluded. No geometry repair was needed after first rendering.

The shell's initial unquoted numeric filter removed leading zeroes. A quoted no-check batch supplies01–09. Final exact-name inventory verifies every required view;51 batch images are copied byte-identically to canonical names, with all source/copy hashes recorded. All rendering is from the frozen generated blend; no duplicate full gate was run for supplemental batches or Cycles.

Fresh Luna Inspector creation failed at the runtime thread limit. Coordinator retained the independent Designer/former v05 Builder, separate from the fresh v07 author. That one reviewer inspected all91 images, independently checked all91 hashes and51 batch copies, and accepted the new attachments, allfive storeys, source preservation, materials and display layers. Nine part reports merge into `inspection_v07.md`; `structural_review_v07.md` records independent geometry acceptance. No visual or geometric issue remains.

Generated hash: `6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed`. Allfive saved masters share `1efe2518e65ac7d515c5fb795a9778603de1f95f6e026191dc32975ebde93ad0`. Every local mesh and every primary-support/new-hardware world vertex is exact. Each saved master has29 pre-existing tread/inclined-rail coordinate changes, maximum3.814697265625 micrometres; all19 actual rendered tread underside unions pass. The distinct hashes and measured bridge are explicit in `render_identity_difference_v07.json` and `render_evidence_v07.json`.

Runner export:30,156 elements, other0,11/11 taxonomy checks; all180 new pieces are fixtures. JSON SHA256 `2a074a8867df408bdd16b5c3a24f0d7d5177bbb9f7a2a1e126a8ce07c2cf26b3`. Final mechanical/viewer close-out and run documents remain Coordinator/Runner responsibilities; no archive or commit was made by Builder. A preliminary local-check launch loaded user add-ons and hung on shutdown; the owned process was stopped after its checks completed. Clean factory-startup attachment/route checks and every final render/gate completed successfully; no geometry exception followed.

### Requirements and open questions

R40 closes on actual interfaces/roots, route tests, final0/0 stock gate, independent91-image review and exported fixture checks. R27 records the complete final view inventory. Designer/Coordinator own broader final acceptance wording and Runner owns R31 close-out. All model geometry and inspection issues are closed. Engineering limits and the explicitly unmodeled ground boundary remain unchanged.

1. **No open Designer geometry question.** The sole inherited CourtSouth attachment issue is resolved by the approved discrete hardware; no substitute longitudinal beam or ground support was introduced.
