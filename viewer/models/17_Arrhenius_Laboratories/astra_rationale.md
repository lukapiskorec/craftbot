# Experiment 17: Arrhenius Laboratories

## 0. About this document

Architectural reconstruction by Astra (`gpt-6-astra`) in Codex, started 2026-09-15 and continued through 2026-09-17. Research, initial visual inspection, and version 1–3 close-out use `gpt-5.6-luna`. The runtime thread limit prevented fresh v03 Inspectors and resuming the original Designer; an available independent Astra Designer reviewed separate storey subsets sequentially and performs the final design review. Versions 4 and 5 each received a fresh independent `gpt-5.6-luna` Inspector, reused sequentially for the five storeys when another spawn hit the same limit. The v05 Inspector also wrote a separate presentation report: six reports by one reviewer. Builders remain separate from visual review, with a fresh Builder for each version. After a fresh v04 Builder started, the runtime also prevented resuming the original Runner; the available former v03 Builder handles the remaining mechanical close-out duties as an explicit fallback. This document is compiled from the design and verification hand-offs.

For the user's correction round, v06 and v07 each have a fresh Astra Builder. Fresh/reused Inspector attempts and normal Designer access hit the runtime thread limit. The available former v05 Builder therefore acts as independent Designer and visual reviewer for those new versions, without reading their geometry code. This is one independent Astra reviewer across the reported subsets, not multiple Luna Inspectors. The former v03 Builder retains Runner duties. These role fallbacks do not waive geometry, interface, source or diagnostic acceptance criteria.

## 1. Brief as understood

Build a single-variation, faithful architectural model of the Arrhenius Laboratories building shown in the eight experiment input images, using the user-supplied HIC article to clarify the building's organization and construction. Preserve the visible forms, proportions, facade rhythm, material contrasts, exterior concrete structure, courtyard, and characteristic inclined entrance glazing. Represent the complete building to the extent established by the references; record inferred dimensions and unseen details as estimates. Detailed laboratory equipment and hidden construction assemblies are omitted where the references provide no evidence, so the model remains an architectural reconstruction rather than a claim of surveyed or engineered accuracy.

## 2. How to run and outputs

Use Blender 4.3.2 with factory startup from the repository root. Normal `python` shims were inaccessible; the bundled interpreter at `C:/Program Files/Blender Foundation/Blender 4.3/4.3/python/bin/python.exe` works for repository tools.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 4.3/blender.exe' --background --factory-startup --python tools/render_views.py -- 'experiments/17_Arrhenius_Laboratories/Astra/experiment_17_astra_v07.py' 'C:/Users/lukap/Documents/GitHub/craftbot/experiments/17_Arrhenius_Laboratories/Astra/experiment_17_astra_v07_blender' --views 'experiments/17_Arrhenius_Laboratories/Astra/views_astra.py' --lib 'experiments/17_Arrhenius_Laboratories/input'
```

The final model is v07, with **30,156 elements, zero penetrating pairs and zero floating elements**. Independent structural and image review passes. Earlier rendered versions remain immutable. The final view set comprises 55 Workbench images numbered 01–37 and 41–58, four Cycles images and 32 capped mesh drawings: 91 images, independently reviewed and hash-verified. Numeric failures above 20 pairs restrict that version to four orbits and defer independent inspection. Workbench images diagnose geometry; Cycles separately tests transmission and material appearance.

The base views include four orbits, top, four elevations, frame-only and underside views, photographic counterparts, longitudinal/transverse sections, five floor plans, stairs, rooms, entrance and enclosure details. Views 41–44 show courtyard-stair, terrace and perimeter-seat supports; 45–48 show the corrected corbel/beam hierarchy, local bearing nib, open inclined corner and restored insert ledger. Views 49/50 isolate frame/fixtures, 51/52 address wall/landing support, and 53/54 resolve the landing-camera and approach-slab taxonomy findings. Views 55–58 show upper and ground facade attachments, a stepped assembly and the complete discrete connection array. Capped drawing numbers are separate from Workbench camera numbers. Cycles12/15/28 show the south facade, courtyard and stair transmission; interior40 is the retained stair/gallery relationship study, not a recovered historic camera.

Top-level collections are Foundation, Site, Structure, Floors, Roof, Facade, Entrance, Interior, Stairs, Insert and SiteStairs. Primary shafts/corbels/beams/cores remain distinct from facade panels and fixture assemblies. The viewer assigns TimberFrames, SteelFrames, SkylightFrames, all StairRim pieces and the new CourtFacadeBracket family to fixtures. Actual concrete rooflight seat beams remain frame, and EntranceApproachSlab is floors. Landscape, soil, fill and granular-base meshes are absent; actual constructed paving, terrace, retaining and foundation components remain. The final exported model supplies the current hierarchy.

## 3. Reading the inputs

Eight supplied images are the primary visual evidence. [HIC: Carl Nyrén, Arrhenius Laboratories](https://hicarquitectura.com/2026/09/carl-nyren-arhenius-laboratories/) supplies architectural context. The Designer read all eight images and the Researcher independently checked the plan and level counts.

| Source | Rule | Number or consequence |
|---|---|---|
| Images 01 and 07 | Express separate concrete supports, beams, slabs and corbels | Repeated seated frame; no temporary construction gear |
| Images 02 and 05 | South front has a distinct section and material sequence | Seven front columns, metal fascia, recessed ribbon, inclined glass above porch |
| Images 03 and 08 | Open curved stairs and visible internal concrete frame | Four stair locations, with actual slab openings |
| Image 04 | Keep the courtyard partially open | Low two-storey insert, rooflights, east passage and grade transition |
| Image 06 and section 08 | Count the visible occupied bands | Five occupied levels; plant is additional |
| Plan 08 | Preserve the complete elongated courtyard ring | 19 longitudinal bays and 6 transverse bays |
| Drawing proportions | Set a coherent estimated grid | 6 m longitudinal and 9 m transverse modules, 54 x 114 m between outer axes |
| HIC article | Clarify materials, structural system and spatial relationships | External concrete supports, wood window frames, wings and links, courtyard insert and inclined entrance glazing |
| Concrete detailing reference, catalogued in sources.md | Assess whether a manual supplies applicable sizes | Precast detailing topics only; no Arrhenius sizes or span tables; timber rules were not transferred |

### Deliberate deviations and evidence limits

The article's four-storey description conflicts with five occupied window bands read in image 06 and section 08. Primary images govern the model; whether the article excludes a ground level is unknown. The assumed grid regularizes the scanned plan proportions by about 2%, and the assumed roof height differs from the section ratio by about 4%. No scale bar or independently reliable object calibrates the absolute dimensions. Concealed foundations and cores are inferred completions. Historical colours, fine window divisions, unseen room layouts and partly obscured plant are not documented precisely.

## 3b. Comparison round

The first independent comparison reviewed v04 against all eight supplied images. The user's later review exposed missed corbel orientation, beam hierarchy and south-corner details; the earlier visual pass did not establish those relationships correctly. The v06 independent reviewer reread images 01, 02, 06 and 07 and checked the corrected diagnostic and transmission views. The table below incorporates those corrections; unchanged images 03/04/05/08 retain the earlier bounded comparison. See section 3c for the user review and the separate CourtSouth attachment finding.

| Source | Reference feature | Built comparison and decision |
|---|---|---|
| 01 | Separate concrete frame, beams and floor members | v06 view 45 exposes slab above true transverse Beam above the aligned corbel and shaft. Invented continuous longitudinal EdgeBeam pieces are removed. Temporary construction gear remains omitted. |
| 02 | Inclined entrance glass, end frame and continuous upper face | v04 fixes fascia/ribbon continuity; v06 views 13/47 show the cleared side region beneath the incline, with regular spandrels beyond it and no invented triangular glass return. Cycles12 confirms transmission. Exact depth and entrance position remain inferred. |
| 03 | Curved flights beside a straight daylight gallery and exposed frame | Semicircular stair/gallery relationship retained. Perspective 40 is a south-stair relationship study; the original camera/location is unknown. Fine mesh/diagonal guard infill and ribbed soffit are simplified. |
| 04 | Open court, low two-level skylit insert and east passage | Major volumes and relationships retained. The model's elevated overview differs from the source's eye-level camera; exact skylight count and insert dimensions are unverified. |
| 05 | Broad lawn/porch and continuous metal/ribbon front | Corrected front sequence and seven porch stations pass. No pixel-scale measurement is claimed from the oblique photograph. |
| 06 | Five occupied bands and recessed windows behind exterior frame | v06 views 14/26 retain five bands and show the corrected chamfered shoulders ahead of the finer window/spandrel face. Historical finishes and fine fittings are simplified. |
| 07 | Enlarged precast bearing shoulders and member hierarchy | v06 rotates the principal wings into the true Beam direction; views 19/45 distinguish beams, spanning slabs and discrete column shoulders without the extra longitudinal beam line. Reinforcement pockets, lifting inserts and capacities are not reconstructed. |
| 08 | Elongated ring, unequal links, four semicircular stairs and differentiated rooms | Counts and major topology match: 19 longitudinal bays, six transverse bays, two wings/two links, four stair locations and straight galleries. Room organization is an architectural reconstruction, not an exact traced program on every floor. |

The recorded outer-axis drawing ratio is 1242/577 = 2.152513; the model's 114/54 = 2.111111 differs by **-1.923%**. The drawing's roof-height/width ratio is 185/577 = 0.320624; the model's 18/54 = 0.333333 differs by **+3.964%**. Both satisfy the adopted 5% criterion for these two gross ratios only. This does not verify every proportion, exact metre scale, camera pose or historical detail.

Retained simplifications include vertical guard infill in place of the source's mesh/diagonals, smooth soffits instead of ribbed finishes, and omitted clocks, signs, curtains, weathering and small fittings. They preserve the model's architectural level of detail; they are not claims of exact interior replication. A dedicated extra doorway perspective is unnecessary: labelled mesh plans and exact aperture/route checks provide that evidence, while perspective 40 establishes stair, gallery, frame and daylight relationships.

## 3c. User review round 1

The user's 2026-09-17 review identifies missed source details in the previously accepted v05: column/corbel orientation, invented EdgeBeam members, extra panels below the inclined facade, distracting ground geometry and incorrect viewer layer assignments. These findings reopen the relevant fidelity and support claims; v05's numerical passes do not settle whether its construction arrangement matches the photographs.

| Request | Correction and evidence |
|---|---|
| Check the apparent 90-degree column/corbel error | Images 02/06 and construction images 01/07 confirm the principal wings must align with global-X Beam spans. Rotate the shoulder profiles about each square shaft; corrected envelope is 1.30 m in X by 1.00 m in Y. Ordinary available longitudinal bearing grows from 0.20 to 0.35 m. A local inferred 50 mm rear nib completes the offset first-raised y=6 beam seats. Actual post-fit areas must be recomputed. |
| Remove EdgeBeam; retain real beams and facade parapets | Remove 760 historical longitudinal EdgeBeam pieces before fitting other families. Slabs span in Y onto genuine X-running beams. Restore the full raised west insert ledger with 0.20 m attachment and 0.15 m deck bearing; regenerate 20 perimeter seats formerly credited to EdgeBeam. Recheck opening supports and all other former dependencies. |
| Clear the space below inclined south glazing | Clip east/west opaque panels in y=0.30..6.00 below z=8-(y-0.75)*5/5.25. Retain regular side facade beyond that region. The new corner opening stays open; no replacement triangular glazing is inferred from image 02. |
| Remove ground planes | Omit landscape, soil and granular-base geometry. Actual building floors, foundations, paving and constructed stair/terrace concrete remain; founding is an explicitly unmodeled boundary rather than a mesh-verified soil contact. |
| Window frames and StairRim in fixtures | Correct all relevant families in experiment-17 viewer overrides and verify the named examples plus family coverage. StairRim's display layer does not change its physical support role. |

The ground inventory removes 122 historical pieces: four SiteGround, one CourtyardGarden, one CourtSubsoil, 102 TerraceSubsoil, six TerraceFill, six TerraceBase and two EntranceApproachBase. Tests on removed lawn/garden surfaces are explicitly excluded; constructed public routes remain tested. The previous terrace/base full-support mesh result is historical, and the entrance's 2.40 m² earth-bearing portion is now an unmodeled boundary while its 1.20 m² concrete grade-beam seat remains measurable.

Concept sections 9–10 and requirements R33–R40 record the approved rules and resulting support repairs. A fresh Builder implemented the source corrections in v06; another fresh Builder closes the discovered CourtSouth attachment gaps in v07. Final v07 geometry and independent review pass. Earlier versions retain their historical evidence and failure dispositions.

The first candidate exposed a secondary fitting defect at the courtyard landing and terrace walls. The rotated corbel at (36,96) m intersects the landing support; the old full-depth footprint cut removed a 0.050001 m² strip beneath the unchanged landing. Concept 9.7/R39 therefore requires subtraction of the actual vertical corbel profile, preserving the full support cap at z=2.70..2.85 m. Its intended support combines a 0.05 m² corbel-top seat at z=2.70 and approximately 0.44 m² on the retained ledge at z=2.50; these are separate contact planes, not a claimed equivalent capacity. The same exact-profile fitting restores terrace-wall concrete outside actual shoulder intersections. Wall-plus-structure coverage and footing seats must be measured. No walking outline or level changes, replacement frame or soil proxy is authorized by this correction.

## 4. Reading the reference code

The Builder starts from the repository experiment and view templates, using the existing geometry toolkit. No other model's experiment run is consulted.

## 5. Construction logic settled before geometry

The intended bearing stack runs from pads and pedestals through concrete shafts and corbels to beams, slabs and enclosure. Floors and roof connect to inferred concrete service cores beside the stairs. Seated exterior joints are not assumed to be moment-resisting frames. Stairs require floor openings and supported landings; rooflights and inclined glazing require framing without supporting the main building floors. These are design requirements, not proof that the generated geometry has implemented them; verification follows in section 8.

The south glazing rises outward above a recessed ground wall. Main floor geometry must respect this porch section rather than crossing the glass plane. The courtyard insert occupies only part of the open court and mediates an estimated grade change through a terrace and stepped route.

## 6. Core modelling decisions

### 6.1 Complete building

The complete courtyard ring is required. A representative facade bay was rejected because the plan and photographs establish a whole building, including four stairs, two unequal end links and a courtyard insert. Interiors retain architectural organization without invented laboratory equipment.

### 6.2 Distinct south elevation

The south front combines a tall metal fascia, recessed ribbon, fine horizontal strip and broad inclined glazing over the porch. Applying the typical concrete-and-window side elevation across this front would erase its defining section and was rejected.

The independent v03 review found that five intermediate front column/corbel stacks still crossed the ribbon at z=9.6..12.6 m and metal fascia at z=12.6..18 m. Photographs 02 and 05 show a continuous upper front bounded by its ends, with the intermediate porch supports below. Presence of all facade components was therefore insufficient: their visible overlap was wrong. Version 4 corrects that relationship, with structural support retained behind the continuous face rather than removed without a load path.

The version 4 design retains every primary shaft, corbel, beam and slab. The continuous fascia moves to y=-1.00..-0.78 m, with seams to -1.03 m and lip to -1.20 m. The recessed ribbon frame occupies y=-0.78..-0.68 m; glass is centred at -0.72 m, leaving at least 30 mm before the corbels. Heights and horizontal extent remain fixed. Fitted top, end, head and sill returns close the enclosure; secondary rails and outriggers connect it to the existing frame. This exact offset is inferred and needs a matched corner-view check. Deleting upper supports, cutting the new skin around each column or making glass opaque were rejected because they would respectively remove the load path or retain/conceal the fidelity error.

The v04 entrance-route audit also exposed an inherited defect outside the 47 v03 route cases: the nominal central door was closed by ground glazing/sill geometry, and its axis crossed a retained column at x=27 m,y=6 m. A doorway symbol therefore did not establish a usable entrance. The Designer moves a genuine 2.40 x 2.40 m opening to the adjacent bay centre x=22.50 m and removes the old overlay-only portal. All shafts and the structural grid remain; exact door position is inferred. Verification must follow the complete porch-to-foyer-to-circulation route and its site transition.

A 3 m-wide paving strip at x=21..24 m,y=-0.9..0.3 m closes the entrance's ground gap. Its top is flush with the porch at z=0, on an inferred 0.25 m concrete slab. A fitted 0.15 m base provides 2.40 m² of support and the retained grade beam provides the remaining 1.20 m². The lawn transition has a 150 mm riser; this is explicitly not a step-free-access claim. Actual adjoining faces and ground support are checked separately from the door opening.

### 6.3 Exterior concrete frame

Exterior concrete shafts stand proud of the enclosure and widen into chamfered bearing shoulders. Concrete remains visibly different from the finer timber window frames and pale metal fascia. Generic flush columns or decorative cubes pasted onto glass would not preserve the reference system.

Before the first render, the Builder identified an internal dimensional conflict: a 0.85 m-deep shoulder around a 0.60 m shaft projects only 0.125 m on each side. The Designer increased its estimated depth to 1.00 m to provide the specified 0.20 m seats, while preserving the 1.30 m facade width and 0.60 m height. Actual beam-end bearing must still be checked in the built geometry.

### 6.4 Courtyard and circulation

The low courtyard insert has two levels, rooflights and side glazing. An open garden and eastern passage remain. Four curved stairs retain open wells and connect the occupied levels; enclosing them in cylinders or replacing them with square flights was rejected. Exact unseen interior partitions are inferred from the single supplied plan.

After v01 confirmed stair-to-facade collisions, the Designer moved the west/east stair centres inward and the north stair southward. The revised nominal rail-to-facade gaps are 160, 160 and 210 mm. Short corridor jogs beside the west/east stairs preserve circulation; the exterior grid, stair radii and 22 treads are retained. Minimum usable passage and actual core clearances remain Builder checks.

The initial south-stair clearance correction to y=7.25 m with reversing northern half-turns was rejected: retracing flights created inadequate headroom near their common endpoints. A 130-degree flight plus landing was also rejected because it shortened the tread going excessively. Version 2 used 180-degree rising flights with 22 risers and 50-degree landings, advancing 230 degrees per storey. This passed headroom but failed actual exit routes where landings faced the facade. The south centre moves to y=9.20 m so its entire radial envelope fits behind the ground glazing. Inclined-glass endpoints and the exterior grid remain fixed.

An unrendered version 3 trial used full revolutions with fixed landings and 28 risers. Although it improved local exits, the north circular aperture blocked the complete north link. Before relocating a reference-positioned stair, the Coordinator required a fresh reading of image 08. That revealed the root interpretation error: the four stair symbols are semicircular, with straight galleries along their diameters. The north half-circle lies north of a continuous gallery joining the wings; image 03 also shows curved flights beside a straight gallery. The full-circle/full-turn assumption was therefore rejected on source-fidelity grounds.

The corrected version 3 design repeats each semicircular flight in the same direction at every storey. A straight floor gallery connects each arrival to the next departure without retracing the rising flight. This preserves the plan-supported stair locations and radii while restoring circulation on the opposite side of the diameter. Actual room doors move away from partition junctions to room midpoints, and stair/gallery connections receive real openings. The Builder must verify all 20 stair/floor routes and the upper circulation loops against generated solids, with clear labelled plans of the office/corridor/laboratory arrangement.

The west, east and north flights occupy their northern half-discs; the south flight occupies its southern half-disc. Each rises 3.60 m over 22 inferred risers, with 1.40 m-deep straight gallery and endpoint landing strips. The inferred north core rotates and moves to (27.10, 111.35) m, giving a nominal 1.425 m bypass above the y=108 m column, 0.205 m to the stair envelope and 0.255 m to the facade. A local south corridor return moves from y=12.8 to 13.95 m to clear the route beyond the y=12 m column. These local interior corrections retain the facade, grid and source-supported stair positions.

The insert's two floors need actual access from the west wing. The initial model left a 0.85 m gap and an uninterrupted facade. The Designer specifies a compact enclosed connection at y=74..76 m, with flush floor levels at z=0 and 3.6 m, roof at 7.2 m and aligned 1.40 x 2.40 m door openings. Its supported decks and ledgers bridge only that existing gap; the previously incomplete insert west enclosure is closed around the frame. This completes the intended connection without adding an unsupported internal stair. The doorway location and concealed support details are inferred, not visible in the source photograph.

Version 2's circular openings and perimeter rims are superseded by the source-corrected semicircular openings and gallery-edge support in version 3. Support details remain inferred connections, not engineered historic reconstructions. Verification must establish actual header continuity, 2.10 m headroom, 1.20 m exit passages and 0.15 m clearance from nonconnecting members. Intentional structural support joints are checked separately from free circulation clearances.

### 6.5 Roof and support assumptions

The roof remains a flat ring with limited plant housings. Inferred foundations and service cores establish a qualitative support system without claiming to reproduce concealed historic details. Reinforcement and prestressing are not fabricated as visible model details.

The version 3 bearing audit identifies a local exception at column 81, x=45 m,y=6 m, where the south core interrupts the usual beams. Of 876 nominal seat cases, the design retains 866 ordinary seats, eight reduced-width seats and two alternate core-supported seats. The two alternate ledges provide the intended 0.20 x 0.40 m seat area and connect into continuous core walls. The eight upper exceptions retain 0.20 m bearing length but only 0.325 m width, or 0.065 m² contact area: an 18.75% reduction from the nominal width and area. Their capacity is unverified. This exception is recorded explicitly rather than claiming that all 876 cases meet the nominal section.

## 6b. Independent structural improvements

The independent review of frozen v04 set aside source appearance and examined actual bearing faces and support paths. It found two real support omissions: the exterior courtyard stair's 19 tread blocks and top landing had no meaningful downward support, and the north terrace slab had no underside fill or support. Occasional roughly 7.6 micrometre overlaps between consecutive tread edges were not bearing seats. No waist or stringer existed beneath them. These findings reopen structural convergence despite the zero-pair/zero-floating result, since rails and edge contacts can connect a model without providing a gravity load path.

The ordinary slab-end audit then found 261 genuine perimeter gaps among 4,534 tested ends. At the north, slabs end at y=113.70 m and the supporting beam starts at 113.80 m; at the upper south, slabs start at y=0.30 m while the beam ends at 0.20 m. The 100 mm separation affects 153 north ends and 108 south ends. The other 4,273 ordinary ends pass the adopted 120 mm bearing test, with internal station ends generally providing about 200 mm. Another 1,960 small, notched or decomposition faces were excluded explicitly; they were not falsely counted as individual physical panels or passed seats.

Version 5 implements integral beam-edge ledgers with actual 200 mm slab seats, a supported exterior stair waist and landing, and contained backing beneath the terrace. Walking tops, visible slab outlines and primary frame axes stay fixed. The terrace fill has independent containment: its northern edge adjoins ground-floor glazing, which cannot retain earth. These supports and their reinforced connections are architectural inferences, not recovered historic details. The final independent structural review accepts all three corrections on measured bearing faces, rooted connections and founding evidence; see `structural_review_v05.md`.

Six south-corner seats required local fitting of buried 30 mm metal closure strips. The concrete ledgers replace those intersecting hidden volumes so each floor has a complete 200 mm concrete seat; a metal weather closure is not counted as floor support. The trim lies only at y=0.30..0.50 m and z=F-0.45..F-0.25 m for F=10.8, 14.4 and 18 m. Exposed faces and the continuous envelope remain fixed, with actual enclosure-to-concrete joints verified. The terrace's north edge retains its intentional 30 mm cantilever to keep containment clear of glazing; it is not represented as fully earth-supported over that narrow strip.

Positive findings include all 24 floor/roof interfaces to the four cores in both plan directions, fully seated plant plinth feet, and rooflight support beams bearing on the insert structure. Core interfaces require inferred shear anchorage and calculated forces beyond this reconstruction. Insert beams have full column-side joints; their support interpretation is an inferred cast-integral concrete connection, with no claim that those joints provide precast horizontal seats.

The insert audit distinguishes 67 seated end cases from 45 internal continuous-concrete interfaces. All 45 internal interfaces have complete adjoining concrete face coverage, totaling 13.8749976 m², and full support immediately beyond on 0.40 m beam bands. There are no actual gaps at those interfaces, and the outer ends at y=66/96 m pass. The Designer therefore accepts an explicitly inferred continuous cast-concrete slab/beam system for the insert. Treating the geometric subdivisions as separate precast units would have misclassified these joints. No insert geometry change is required; reinforcement, moment transfer and section capacity remain unverified.

## 7. Detailed geometry numbers

The concept is the dimensional source for the Builder. Coordinates use x east, y north, z up; z=0 is the ground occupied floor, with the south entrance at y=0. Except the counted bays and levels, these are reconstruction assumptions.

| Item | Concept dimension |
|---|---|
| Structural axes | x=0..54 m in 9 m bays; y=0..114 m in 6 m bays |
| Wings | x=0..18 m and x=36..54 m |
| Links | South y=0..12 m; north y=108..114 m |
| Occupied floor tops | z=0, 3.6, 7.2, 10.8, 14.4 m |
| Roof and parapet | Roof slab top z=18 m; parapet top 18.45 m; columns top 18.6 m |
| Typical slab / beam | 0.25 m slab; 0.40 x 0.65 m beam |
| Typical shaft / corbel | 0.60 m square; shoulder 1.30 m wide, 1.00 m deep, 0.60 m high |
| Facade | 0.55 m recess from column axes; 0.22 m panels; nominal 3 m panel units |
| Typical windows | Sill floor+1.10 m, head floor+3.05 m; ground sill 0.45 m |
| South glass slope | Lower edge y=6 m,z=3 m; upper y=0.75 m,z=8 m |
| Courtyard insert | x=18.55..31.50 m, y=66..96 m; roof z=7.2 m |
| Stairs | Revised centres (3.65,61), (50.35,61), (32.4,110.30), (40.2,9.20) m; outer radius 2.7 m; inner 1.1 m |
| Site bounds | x=-18..72 m; y=-24..132 m |

Fine window divisions, cores, plant, retaining geometry and foundations remain inferred. Final stair, core, corridor and insert-link adjustments are recorded in section 6.4. These dimensions organize the reconstruction; they are not measurements of the original building.

## 8. Verification

Version 1 passed script grid/level assertions but failed geometric and preliminary visual checks. It contains 18,828 members, 85,230 penetrating pairs and two floating members. Four overall views were rendered; no independent Inspector was assigned because the overlap count exceeds the 20-pair gate.

The Builder identified a concrete cause: out-of-domain opening rectangles supplied to the tiling helper expanded slabs and beams beyond their intended bounds, covering the courtyard. Version 2 clips opening inputs at both experiment call sites. It also corrects the displaced landing and isolated site patch, fits repeated construction junctions, adds explicit support at discontinuities and implements the revised stairs. These were implementation defects, not accepted design simplifications.

The frozen version 2 standard render reports **31,149 members, zero penetrating pairs above 1 mm and zero floating members at 2 mm contact tolerance**. All 27 original Workbench views and four supplementary detail views were rendered. Five independent storey inspections confirm the corrected courtyard, principal facade and insert topology, exterior frame, five occupied bands and open stairs. Three muted Cycles views show the south front, courtyard and stair gallery; independent inspection confirms transparent glazing with visible internal structure and distinct materials in that representative subset, not every pane.

The reported member counts are geometric model elements. Fitting openings and junctions divides some physical members into multiple touching convex pieces, so these counts are not a historic bill of precast components.

Version 2 is not converged. The actual-model route diagnostic cannot connect either the west level-one or west top-floor landing to the corridor with a 1.20 m-diameter clearance disc. Its optimistic 50 mm raster uses actual floor/landing surfaces and obstacles 50 mm above the floor, omitting higher obstacles. The two landing components contain 277 and 210 cells respectively without reaching the corridor. This documents a route failure rather than certifying complete circulation. The 230-degree floor advance rotates some landings toward the narrow facade gap; version 3 must correct this inferred stair arrangement.

The final version 2 headroom check covers 512 walking regions and finds a 2.700 m minimum, with no violations below 2.10 m. All 16 raised stair rims have geometric contacts with retained beams or headers under the standard 2 mm contact predicate. Those checks do not prove route width, sufficient bearing area or connection strength. Interior partition organization remains insufficiently legible in the current images and requires further evidence.

### v03 numerical evidence

The frozen version 3 contains **30,003 geometric elements, zero penetrating pairs above 1 mm, and zero floating elements at 2 mm contact tolerance**. An independent rebuild reproduced the same geometry hash and element count. All 34 Workbench views and three muted Cycles views are saved.

Tests against the frozen geometry pass 47 continuous route cases: 20 stair exits, 20 endpoint galleries, four upper circulation loops, the ground east-to-courtyard route, and two insert approaches. The first 45 test a 1.20 m passage; the two insert approaches test 1.40 m. All use a 2.10 m vertical envelope. The test permits 20 micrometres of float32 seam residue. A separate headroom test covers 368 continuous walking regions, with a minimum of 2.700 m and no failure below 2.10 m. This is geometric evidence, not a regulatory approval.

The support audit passes 250 foundation/column/pedestal full-footprint seats, 16 raised stair support paths, and 22 local bearing or connection faces. An earlier summary's 249-seat figure was a transcription error, corrected against both saved support reports. Added core-base pieces close the actual vertical gaps to the foundations. The raised insert link bears directly on the existing west concrete edge beam; its minimum horizontal contact is 0.15 m by 2.0 m at each raised level. The 876 beam-seat cases comprise 866 ordinary seats, eight reduced-width seats and two alternate core-supported seats, as qualified in section 6.5.

The independent reviewer inspected all 34 Workbench and three Cycles views in five sequential storey subsets. The ring, insert, roof, corrected semicircular stairs and straight galleries are visibly present. Orthographic elevations show 19 longitudinal bays, six transverse bays and five occupied bands. Labelled plans extracted from the actual mesh establish the west/east room organization, doorway positions and enclosed insert link, closing the earlier R17 presentation gap. The only established new geometry defect is the interrupted south upper fascia/ribbon described in section 6.2. The dark stair transmission view is a presentation limitation, not evidence that its geometry is absent.

### v04 frozen-geometry evidence

Version 4 freezes **29,876 elements, zero penetrating pairs above 1 mm and zero floating elements at 2 mm**, under geometry digest `8a02c4b9865c497bbd2d1af58a76140a978e0863a98ebd97a32ff63a26951657`. An independent generator rebuild matches that identity exactly. All 48 continuous routes pass, including the added entrance-to-foyer-to-east-courtyard route. Forty-six use 1.20 m width; the two insert approaches use 1.40 m. All test 2.10 m height. Twenty-eight separate doorway and public stepped-route strips pass. The 368-region stair headroom test retains its 2.700 m minimum. The approach paving's 3.60 m² support footprint comprises fitted base areas of 2.10 and 0.30 m² plus 1.20 m² on the retained grade beam, whose foundation contact path is verified.

Exact geometry signatures match all 14,056 members in the named retained column, corbel, beam, edge-beam, floor, core, stair and insert families to v03. All 57 new facade bracket contact checks pass. The actual secondary-frame/corbel gap is 30.00003 mm. These tests verify the defined geometry families and contacts; they do not calculate bracket anchorage, facade wind resistance or concrete capacity. Five sequential storey reviews by the independent Luna Inspector and its separate interior review find no remaining actual visual defect.

The selected interior perspective 40 uses camera (33,10.1,5.2) looking toward (40.2,7.5,5.5), 35 mm, +2 EV, world strength 0.35 and neutral fill 0.75; 48 samples at 1400 x 1100. It studies source 03's curved-stair/gallery/frame relationships at the model's south stair, whose inclined glass derives from sources 02/05. It does not claim the exact source-03 camera location. Trials 38/39 were too close or dominated by a foreground soffit. Only cameras and lighting changed. The final perspective's doorway detail is not readable from that angle; separate mesh plans, aperture checks and route evidence show the actual openings.

The viewer export contains 5,007 boxes and 24,869 meshes (7,327,161 bytes), with zero unclassified elements. A readiness-checked local browser capture passed after outside-sandbox execution was approved. The Runner visually confirmed experiment 17, Astra, v04 and 29,876 elements, the recognizable building, and no red error banner. The model served over HTTP byte-matched the exact JSON. Earlier version close-out timeouts and failed browser attempts remain documented rather than rewritten as passes.

### v05 support corrections

The final v05 contains **30,167 elements, zero penetrating pairs above 1 mm and zero floating elements at 2 mm contact tolerance**. The complete generator reproduces preflight digest `6cd07366762f8213cb58508c746d180142bf48f2534813f8f0bb0b64dc922f4c`. At that stage, geometry signatures retain 29,870 original elements unchanged; six buried weather-return pieces are fitted, and 291 elements are added. The additions comprise 285 support/site pieces and six new closure fragments. The six trimmed volumes are approximately 0.0012 m³ each and are replaced by concrete; exposed envelope geometry is unchanged.

All 4,534 ordinary slab-end cases now pass their bearing tests, including complete 200 mm seats at the 261 corrected perimeter ends. The six corner filler pieces join adjacent parts of their integral ledgers through full 200 x 200 mm concrete interfaces, approximately 0.04 m² each, with named paths into retained beams. They are parts of a single physical ledger represented by multiple convex pieces.

The exterior stair has actual full underside support and connected bearing paths to its bottom footing and retaining-wall ledge. Terrace fill, base, containment and subsoil unions pass the new support tests, retaining the explicit 30 mm edge cantilever. All 48 current route envelopes, 28 public walking/aperture cases and 368 headroom regions pass; minimum stair headroom remains 2.700 m. The independent Inspector finds no actual defect across all 41 Workbench and four Cycles images and the assigned mesh plans. The Designer closes R22/R24/R30/R32 after reviewing actual support evidence; no geometry correction remains within the architectural scope.

The render harness reassigns object transforms, introducing measured float32 rounding. Exact hash equality is therefore not claimed across saved models. Standard overlap/contact checks ran on master digest `9968993522e362026e472282a4226d99961ec4017ae27497458e024213082417`. Relative to generated geometry, only 19 court treads (maximum 0.238419 micrometre) and ten inclined-glass rails (3.814698 micrometres) change world coordinates; all local meshes remain exact. All 19 rendered tread underside unions were rerun and pass the existing 20 micrometre seam allowance. Secondary Workbench/Cycles batches use digest `927586e39708935f92af4fad3e359e617db733e09cde56b39918195250bd6975`, differing from master only on two court handrails (0.476837 micrometre) and two insert glazing rails (3.814698 micrometres). All main and new support/bearing geometry remains exact. The Designer accepts this narrow numerical exception, recorded in `render_identity_difference_v05.json` and `render_support_bridge_v05.txt`; it does not permit arbitrary geometry drift.

The final viewer JSON contains 5,007 boxes and 25,160 meshes, totaling 30,167 elements and 7,403,925 bytes, with zero unclassified elements. Its SHA256 is `695f650dda49bf892d4340424ce499c5e3fffcd63a5a48ddc535a9d6d449cf09`. The readiness-checked browser probe served the exact JSON over HTTP; independent screenshot review confirms Astra v05, the element count, expected building and no red error banner. A separate coordinate comparison checks all 30,167 exported objects against both generated and standard-master snapshots at the exporter's five-decimal precision, with zero missing objects and zero differences for either. This does not erase the distinct higher-precision hashes above. Canonical export timeouts and their verified direct-export recovery remain recorded in the close-out reports.

V05 close-out completed eight effective required steps with no unresolved mechanical failure; its raw export timeout and direct-export recovery remain visible. That run's preflight passed all 13 checks and its 32 requirements were marked complete within the recorded scope. The later user review reopens affected claims and adds R33–R40; v05's earlier acceptance is not substituted for the corrected versions' verification.

### v06 user-review correction evidence

The corrected generated model contains **29,976 elements**, digest `523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416`. All 1,250 chamfered wings have the approved global-X projection. No EdgeBeam or prohibited ground/earth/base family remains, and the approved below-incline opaque-panel region is empty. The main shafts, Beam members, floor slabs and stair walking geometry remain stable. Compared by name with v05, 23,710 objects are unchanged, 2,703 retained names have changed geometry, 3,754 names are removed and 3,563 are added; those last counts include refitted fragment naming, not only physical additions/removals.

The corrected fixture families total 6,959 pieces: 5,414 TimberFrames, 215 SteelFrames, 178 SkylightFrames and 1,152 StairRims. Both named window-frame examples pass the mapping check, and actual structural concrete retains its frame classification. Of these fixture objects, 6,145 retain geometry and 814 have separately inventoried fitting changes; classification alone does not alter geometry.

All 4,534 ordinary slab-end cases and all 261 corrected perimeter seats pass without EdgeBeam credit. The 876 beam-seat cases are measured again: 866 ordinary 0.35 x 0.40 m seats (0.140 m²), eight reduced-width 0.35 x 0.325 m seats (0.11375 m²), and two first-raised core-ledger seats (0.080 m²). The reduced width remains 18.75% below the current ordinary seat, with no capacity equivalence claimed. The old 0.065 m² value belongs to earlier versions. Tests also pass 250 foundation footprint seats, 22 local connection faces, eight core-base unions and 16 rim/header paths. Restored raised west link ledgers provide 0.20 m attachment to the real slab and 0.15 m deck bearing.

Exact corbel-profile fitting restores 0.007971 m³ of landing plate, 0.001921 m³ of ledge and 0.560853 m³ of terrace walls outside actual shoulder intersections. The full 1.379996 m² landing underside is covered; distinct ledge and corbel seats measure 0.439993 m² and 0.050000 m². All 24 checked wall sections and 12 supplementary point probes pass. Current terrace support is reported as 11.399927 m² of actual concrete seats, 172.690040 m² of deliberately unmodeled earth-supported area and a separate 0.507057 m² north edge cantilever. None of the omitted earth is silently reinstated or described as current mesh support.

All 48 continuous route envelopes, 26 constructed public-route/aperture cases and 368 stair walking regions pass. Two former lawn/garden surface cases are excluded by the ground-removal scope. Gallery clearance is 2.100 m, with raw float32 tangency as low as 2.0999996 m accepted only within the existing 20 micrometre numerical allowance; the separately measured stair-region minimum is 2.700 m. The 57 south bracket contacts pass, and the new ribbon-to-corbel clearance is 180 mm.

The final v06 stock whole-model gate reports **29,976 elements, zero penetrating pairs and zero floating elements** on rendered master digest `25c4743bc414e69436a7b18e84e6fc5535ae58651dd41d9913a78b3ee06e6f1a`. Relative to the reproduced generated identity, the measured render bridge changes only 19 court treads and ten inclined rails by at most 3.814697 micrometres; local meshes are exact and all 19 actual rendered tread-seat unions pass. All 85 images are independently reviewed: 51 Workbench, four Cycles and 30 capped drawings. Extra views 53/54 resolve an occluded landing detail and show corrected fixture isolation. The entrance approach slab is explicitly classified as floors, correcting a generic-rule error found in the isolated view.

Version 6 remains structurally non-converged. A complete facade attachment audit finds 3,630 of 3,660 panel pieces with an actual primary-concrete path, including all changed south-corner fragments. Thirty CourtSouth pieces, in five bays over six bands, sit 250 mm outside the real slab edge without a current modeled attachment. Twenty-four lacked a path in v05; six formerly contacted the old corbel through timber frame joints and lose that contact after the correct rotation. The baseline comparison excludes glass from support paths. Even those small former timber contacts never established engineered gravity capacity. The attachment gap is real and is not waived as terrain removal or a numerical seam.

The approved v07 scope provides two discrete facade brackets per affected panel, using 60 measured contact envelopes on real slab edges. Concealed plate/web connections are inferred details with unverified anchors and capacity. They must not recreate a continuous longitudinal EdgeBeam or change the corrected frame, facade outlines or walking geometry. Exact dimensions and final verification belong to the new version's concept and reports.

### v07 discrete facade attachments

The frozen generated v07 contains **30,156 elements**, digest `6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed`. Exact comparison retains every one of the 29,976 v06 meshes, including local/world vertices, transforms, faces and collections. The only additions are 180 steel pieces making 60 discrete three-piece bracket assemblies. They belong to fixtures and bridge the actual CourtSouth panel/slab gap without replacing EdgeBeam or changing the corrected building geometry.

Each connection has two 10 mm end plates and a 10 mm central web. Upper-band plates/webs are 100 mm high; ground plates are 150 mm high with a continuous 300 mm stepped web. Actual faces are snapped to the retained concrete datums. All 120 concrete/end-plate interfaces and 120 web/end-plate interfaces pass full-area checks, as do 60 slab strips and their 200 mm-deep Beam/GradeBeam bearing bands. Upper concrete interfaces are 0.010 m², ground interfaces 0.015 m²; these vertical areas describe anchored transfer, not horizontal bearing or verified connection strength. All 48 continuous routes and the constructed public-route checks pass with the new steel in place. Local new-member collision checks pass. The glass-excluded panel-path audit now resolves all 3,660 facade pieces, including the 30 previous CourtSouth gaps. Independent structural and final visual acceptance closes the geometric findings.

The unmodified standard gate reports **30,156 members, zero penetrating pairs above 1 mm, zero overlap families and zero floating members at 2 mm**. It ran once on the saved canonical model. All five final saved masters share digest `1efe2518e65ac7d515c5fb795a9778603de1f95f6e026191dc32975ebde93ad0`. Relative to the generated digest, only 29 existing tread/rail world-coordinate sets change by at most 3.814697 micrometres. All local meshes, primary support geometry and 180 new bracket pieces remain exact; all 19 actual rendered tread underside unions pass. This measured numerical bridge is explicit rather than a false claim of equal generated/render hashes.

The final 91-image inventory includes every specified Workbench view, four selected Cycles images and 32 capped drawings. The independent reviewer directly inspected all 91 and checked their hashes, including 51 byte-identical batch-to-canonical copies. The occluded historical view 52 is supplemented by usable isolated view 53; view 54 confirms the corrected approach-slab/fixtures taxonomy. New views 55–58 and capped sections 55/56 establish the upper and ground connections. No unresolved geometry or visual correction remains. Export taxonomy passes eleven checks with zero unclassified elements, including all 180 new brackets as fixtures and preservation of the true structural seat-beam classification.

The final viewer export contains 4,943 boxes and 25,213 meshes, totaling 30,156 elements and 7,453,180 bytes; SHA256 `2a074a8867df408bdd16b5c3a24f0d7d5177bbb9f7a2a1e126a8ce07c2cf26b3`. The actual coordinate audit compares all objects against both generated and saved master snapshots at the exporter's five-decimal precision: zero missing objects and zero differences against either. The browser probe served the exact bytes, and independent screenshot inspection confirms experiment 17, Astra v07, the correct count and building, with no error banner. The browser's owned local server stopped cleanly. The screenshot precedes the final rationale text refresh but represents the final unchanged model and layer data.

Final v07 version close-out has eight effective required steps passed and zero unresolved mechanical failures. Its canonical export timeout is retained alongside the verified direct-export recovery. Run preflight passes all thirteen checks; all forty requirements are closed within their recorded scope. The full project-file manifest includes the historical versions and current deliverables. Transcript archival follows final report preparation as the last run action.

### Not verified

Structural adequacy, reinforcement, prestressing, connection design, and hidden construction details require evidence and engineering beyond visual reconstruction. Geometric overlap and contact checks do not prove these properties.

### Agent usage

Context and tool-call totals are not exposed in the collaboration notifications available to this run. No estimated totals are presented as measured usage.

## 9. Iterations

| Version | Change or finding | Members | Penetrating pairs | Floating | Status |
|---|---|---:|---:|---:|---|
| v01 | First complete implementation; slab/beam cut-out domain bug covers courtyard; displaced landing and isolated site patch | 18,828 | 85,230 | 2 | Failed; four orbits, inspection deferred |
| v02 | Bounded openings, fitted junctions, supported insert and revised curved stairs; 31 diagnostic views | 31,149 | 0 | 0 | Not converged: west landing exits fail; main visual topology passes |
| v03 | Source-correct semicircular stairs and galleries, tested stair/insert routes, room doors, insert link and foundation/bearing corrections; 34 diagnostic and three transmission views | 30,003 | 0 | 0 | Tested cases pass; upper south facade interrupted; later entrance audit also finds a blocked nominal door |
| v04 | Continuous supported upper south envelope, genuine entrance and fitted paving; 37 diagnostic views, three transmission views, selected interior perspective and 24 labelled plans | 29,876 | 0 | 0 | Visual review passes; phase 2 finds unsupported exterior stair/terrace and 261 perimeter slab-end gaps |
| v05 | Perimeter slab ledgers, supported courtyard stair and contained terrace backing; six buried closure fits preserve the exposed envelope | 30,167 | 0 | 0 | Visual and structural review pass; 41 Workbench, four Cycles and 28 plans; measured rendering roundoff explicitly accepted |
| v06 | User corrections: rotated corbels, removed EdgeBeam and ground, cleared south corner, repaired dependent supports and fixture taxonomy | 29,976 | 0 | 0 | Source and visual review pass across 85 images; 30 CourtSouth panel attachment gaps remain open |
| v07 | Sixty discrete facade connections close all thirty remaining panel attachments; 180 added fixtures, all v06 meshes retained exactly | 30,156 | 0 | 0 | All 91 final images and actual connection/support evidence independently accepted; no unresolved geometry finding |

## 10. Scope and known simplifications

This run represents one building. Laboratory equipment, temporary construction equipment, reinforcement, prestressing, concealed fixings, insulation and waterproofing are outside the reference-supported reconstruction. Foundations, retaining geometry, service cores, repeated unseen partitions, exact window divisions, partly obscured plant and the insert access link are architectural inferences. The model preserves their intended spatial or support roles without asserting historic accuracy.

The photographs and unscaled drawings establish topology and relative proportions more strongly than absolute dimensions. Historical colours and material weathering are approximated. Geometric verification demonstrates the tested clearances, intersections and support contacts only; it does not certify structural capacity, fire safety, accessibility or compliance. In particular, eight reduced-width beam seats retain an explicitly unverified capacity.
