# Experiment 16: a simple red room inside undulating slat trusses

## 0. About this document

Agent: GPT-6; harness: Codex; started 2026-09-14, completed review 2026-09-15. The harness reports GPT-6 without an exact deployment identifier. Designer and Builder inherit that model. Researcher, Inspector and Runner use gpt-5.6-luna. This document records the GPT-6 run only. No other model's run was consulted. Final geometric model: v02. Numeric, visual, reference-comparison and version close-out checks passed. Final run close-out and transcript status are recorded separately in closeout_run.md.

## 1. Brief as understood

This single-variation run builds a square room twice as tall as its clear width, with one entrance and daylight from the roof or openings close to it. Thin timber slats form the enclosure and the exterior structure. The red building photographs guide construction character and scale; the other two images guide a series of undulating trusses that give the outside an expressive profile while preserving a simple interior. The 2:1 proportion applies to the clear room, with the exterior trusses allowed to project beyond it. No reference feature is deliberately dropped at this stage; dimensions inferred from photographs must be identified as estimates.

Concept-stage scope decisions are appended in brief.md. The adopted clear room is 3.00 x 3.00 x 6.00 m. It is a pavilion with open clerestories, without demonstrated weatherproofing. A low timber mat replaces the reference's raised floor and stair. A 0.90 x 2.10 m entrance replaces its unusually low aperture. These later interpretations supplement the initial paragraph above.

## 2. How to run and outputs

From the repository root, use installed Blender and the version-specific script:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 4.3/blender.exe' --background --python tools/render_views.py -- 'experiments/16_Expressive_Structure/GPT-6/experiment_16_gpt6_v01.py' 'C:/Users/lukap/Documents/GitHub/craftbot/experiments/16_Expressive_Structure/GPT-6/experiment_16_gpt6_v01_blender' --views 'experiments/16_Expressive_Structure/GPT-6/views_gpt6.py' --lib 'experiments/16_Expressive_Structure/input'
```

The version table below identifies the versions. v01 and v02 each have 19 rendered views and 2,101 timber members. Their numeric checks found zero penetrating pairs and zero floating members; v02 also corrects the foot-seat issue described below. Replace v01 by v02 in both script and output-prefix arguments to render v02. Viewer models use viewer/models/16_Expressive_Structure/gpt6_vXX.json. PATH Python is an inaccessible WindowsApps stub; Blender's bundled Python is available for close-out tools without installing dependencies.

Views 01-04 are exterior orbits; 05 top; 06 front; 07 east side; 08 frame-only; 09 from below; 10 room section; 11 roof profile; 12 heel; 13 layered column node; 14 base; 15 entrance; 16 roof boarding; 17 roof bracing; 18 mat underside; 19 interior front. Each version also has a viewer screenshot.

Collections are Bracing (GroundPlan, LongitudinalDiagonals, LongitudinalTies, RoofPlan), Ceiling, Entrance, Facade (EndBoards, SideBoards), Floor, Ground (LowerSleepers, SoleRunners, UpperSleepers), RoofCover, RoofStructure (LowerChords, RoofWebs, UpperChords), Structure (ColumnChords, ColumnWebs, NodeStraps), and WallSupport (EndRails, SideRails).

## 3. Reading the inputs

| Source | Rule | Adopted number or decision |
|---|---|---|
| 01-soane-front.jpg | Compact tall red enclosure within slender exterior framing | 3.00 m clear width; seven transverse frames |
| 02-soane-outside.jpg | Separate paired slats and diagonal bracing | 36 x 90 mm structural slats, two chord plies around one web layer |
| 03-soaneinterior-1.jpg | Flat vertical red boards, uninterrupted room, upper light | 6.00 m level ceiling; clerestories at 5.25 to 6.00 m |
| Erne_Dachbau_778.webp | Segmented chords and changing truss depth | Seven-node faceted roof profile with actual web triangles |
| Tchumi-02.jpg | Repeating rising and falling exterior edges | Variable roof rib height and exterior column depth |
| CMHC Tables 22 and 35 | 19 mm board precedent at 600 mm supports | 24 mm boards at 500 mm; assumed narrow-board section, not certified |
| FRIM Sheet 1 | 22 x 145 mm floor boards on 610 mm support grid | Narrower 24 x 90 mm slats on 500 mm grid; source-informed assumption |
| FRIM Sheet 9 | 35 x 72 mm truss members, 5.770 m span and 1.195 m rise | Paired 36 x 90 mm chord proposition; no capacity transfer |
| FRIM roof plan | 22 x 97 mm horizontal and diagonal inter-truss braces | Explicit timber ties and braces across 500 mm frame intervals |
| CMHC Table 25 | Prescriptive wall heights below this proposal | 6 m slat columns are outside source coverage |
| CMHC Figures 68 and 86 | Header/jamb load path and real roof seats | 0.90 m entrance, doubled jambs, 90 mm assumed timber seats |
| FRIM gusset/base drawings; CMHC sleeper detail | Connections, anchors and moisture separation need design | No plywood/steel/concrete modeled; unresolved performance is recorded |

These manual rules are the Researcher's verdict, not an independent capacity calculation. Sources.md contains exact chapters, figures and qualifications. Shared manual crops retain their provenance.

The front photograph's stair gives a weak calibration: approximately ten assumed 170 mm risers over 280 pixels yields about 165 pixels/m at the stair plane. Apparent facade width suggests about 2.8 m and enclosure height about 4.1 m, each with at least 25% uncertainty. Perspective and unknown depth separation prevent surveyed dimensions. The chosen 3.00 m clear width stays close to the estimate; 6.00 m clear height deliberately follows the user's 2:1 ratio. An initial 3.60 m width was rejected because it enlarged the inferred width unnecessarily.

Deliberate deviations: seven frames replace a literal copy of the reference's five prominent front lines; the raised floor/stair and tiny aperture become direct low access and a usable entrance. Glazing from the expressive reference and plywood/metal from the manuals are omitted from the all-slat model. Upper openings remain open. The model does not claim to be rain-tight.

## 3b. Comparison round

The independent comparison Inspector reviewed the five actual input images, six concept-cited manual figures and v02 views 01-04, 06-08 and 10-19. All five photo rows were retained as faithful transfers or deliberate synthesis; no concrete geometric correction was identified. The detailed report is inspection_v02_comparison.md.

| Reference | In the model | Kept or changed, with reason |
|---|---|---|
| 01-soane-front.jpg: compact red tower within thin framing, five prominent paired lines and raised access | Tall red room, pale exposed framing, centered low-level entry; matched front view 06 | Keep construction character. Seven depth frames and exact 2:1 clear room are stated synthesis; raised stair omitted. |
| 02-soane-outside.jpg: paired thin members, open gaps, braces and short projections | Paired chords, red webs, red boards and projecting rails in exterior/frame views | Keep; the strongest transfer of assembly character. Projection lengths and roof are not literal copies. |
| 03-soaneinterior-1.jpg: red vertical boards, high side light and low aperture | Flat room, level ceiling, upper side bands and normal doorway in front/section/interior views | Keep the quiet room and upper-light hierarchy; normalize the entrance to 0.90 x 2.10 m. |
| Erne_Dachbau_778.webp: repeated triangulated trusses and varying depth | Seven transverse trusses with changing roof profile and full slat cover | Keep as a compact pavilion interpretation; no equivalence to industrial member capacity. |
| Tchumi-02.jpg: straight pieces making an undulating exterior, with glass and dense screening | Faceted side and roof profiles, projected depth, open upper band | Keep wave/repetition; glass and unrelated screening omitted under the timber-pavilion scope. |

The six manual-figure comparisons confirmed transfer of truss/heel topology, inter-truss bracing, header/jamb arrangement and distributed sleeper bearing. Plywood gussets, metal fasteners, concrete and damp-proof layers shown by those manuals are not modeled. Their omission is a material/scope interpretation with unresolved performance, not a claim that all-timber substitutions have equivalent capacity.

Reference and model cameras, lighting and scale differ. View 19 hides end boarding to expose the interior assembly; views 06 and 10 also supply the enclosing-room evidence. Neither these views nor the photo estimates establish a measured daylight distribution or weatherproof enclosure. The review retains v02 without a speculative third version.

## 4. Reading the reference code

No inherited experiment geometry is used. The Builder starts from tools/experiment_template.py and tools/views_template.py and uses craftbot_lib, geometry2d, planes and framing. Other model runs remain independent. Version v02 starts from the rendered v01 script with a surgical bearing correction.

## 5. Construction logic settled before geometry

The enclosure and structural profiles have separate roles. Inner wall faces stay at x/y = +/-1.500 m and the ceiling underside at z = 6.000 m. The exterior chords change position outside those boundaries. Truss depth is made by separating narrow chords and joining them with triangulated webs.

Roof reactions pass through inner and outer column-head seats into the triangulated columns, then into sole runners over a crossed timber mat. Longitudinal ties and diagonals connect frames; separate roof and floor-plane diagonals collect shear. Boarding alone is not called a structural diaphragm. Header and jamb assemblies carry boards above the single entrance. The ceiling is face-fixed beneath lower chords, requiring fasteners; it is not described as bearing on a support above it.

The initial base wording implied an extra sole-runner layer above the fixed mat. That would have raised the column feet by 36 mm. A focused Designer review resolved the conflict by integrating continuous sole runners into the existing upper layer at z = -0.060 to -0.024 m. Transverse sleepers butt against them, and lower longitudinal sleepers directly support every foot footprint. Floor and column datums remain unchanged; no unsupported sole cantilever is accepted.

## 6. Core modelling decisions

### 6.1 A quiet inner room

The clear room is 3.00 x 3.00 x 6.00 m. Flat red vertical slats preserve its simple interior. A wavy ceiling or internal expressive frame was rejected because it would undermine that part of the brief.

### 6.2 A series of actual trusses

Seven transverse frames stand at 0.50 m spacing. Paired chords straddle a single web layer, and each panel has real triangulation. Decorative fins were rejected because they would not articulate the requested truss construction.

### 6.3 Straight stock makes the wave

The roof uses an additive height field sampled into planar facets. Each rib changes depth across the room and elevation along the series. Straight short boards can cover the facets; an arbitrary doubly curved skin would require twisted stock. The exterior column profile varies while its inner chord stays vertical.

### 6.4 Two thin stock sizes

Enclosure slats are 24 x 90 mm and structural slats are 36 x 90 mm. Smaller ripped closure pieces are permitted. Deep solid beams, sheet cladding and plywood gussets were rejected. All modeled building members remain timber slats; hidden fixings and anchorage are unresolved construction necessities.

### 6.5 Light at the top

Open clerestories occupy the upper 0.75 m of both side walls. The lower walls remain opaque and the end walls continue to the ceiling. A slat roof fully covers the faceted exterior roof geometry. Weatherproofing is not inferred from geometric closure.

## 6b. Independent structural improvements

The Designer reviewed v02 on 2026-09-15 using the Builder's numerical/assembly evidence and the independent room inspection, with references set aside. The detailed table is in design_notes.md. No further geometric change was justified.

| Condition | Built evidence and disposition |
|---|---|
| Roof boards and trusses | Short boards meet fitted chord planes; triangulated chords/webs meet column-head seats. Retained; capacity and joint forces not calculated. |
| Ceiling and wall boarding | Ceiling is face-fixed below lower chords; wall rails and supported board joints transfer loads through fixings. Retained; concealed fixings require design. |
| Entrance | Header seats on doubled jambs and supported mat edge; roof frames avoid requiring the doorway wall as their main support. Retained. |
| Feet and ground mat | Actual-mesh audit establishes all 56 full 90 mm foot seats in v02; lower sleepers directly align. No added strips or thicker sole layer justified. |
| Transverse lateral action | Triangulated x-z frames and roof diagonals provide a named path to separated column feet. Force continuity and ground hold-downs remain undesigned. |
| Longitudinal lateral action | Node-level ties, end-bay diagonals and roof/ground-plane bracing connect the seven frames. Fasteners must transfer forces through fitted and segmented joints. |
| Slenderness | 36 mm chord plies and 1.5 m panels require stability and restraint design. Their geometry does not establish composite action or effective buckling length. |
| Ground and weather | No anchor, damp break or waterproof drainage system is demonstrated. Compression contact does not provide tensile restraint against overturning. |

As a dimensional warning only, the Designer calculated a single 36 mm ply's weak-axis radius of gyration as 36/sqrt(12), about 10.4 mm. Assuming a 1.5 m effective length would give L/r about 144. Neither that effective length nor paired-ply composite action is established, so this is not a capacity calculation or proof of stability.

Roof and doorway seats have Builder dimension/assembly evidence with visually consistent details; they do not have the comprehensive actual-mesh audit used for the feet. Partially hidden roof-board joints, rail spacing, stock lengths and ceiling fixings remain qualified evidence. The review rejected arbitrary larger posts, plywood gussets, glazing or extra base layers because they would alter the brief without an established geometric need or engineered design.

## 7. Detailed geometry numbers

All adopted dimensions below are design assumptions or explicit programme dimensions; the manual table above gives their limits.

| Item | Dimension and datum |
|---|---|
| Clear room | 3.000 x 3.000 m; floor z = 0 to ceiling underside z = 6.000 m |
| Entrance | 0.900 x 2.100 m, centered on negative-y wall |
| Clerestories | z = 5.250 to 6.000 m on x walls |
| Frame stations | y = -1.500 + 0.500j m, j = 0 through 6 |
| Boarding / structure | 24 x 90 / 36 x 90 mm |
| Paired chord layers | centers y = frame station +/-36 mm; web at station; assembly 108 mm overall |
| Column inner chord | x = +/-1.600 m centerline |
| Column panels | nodes z = -0.024, 1.500, 3.000, 4.500, 6.024 m |
| Column depth | 0.300 to 0.600 m according to fixed concept profile |
| Roof profile stations | x = -2.200, -1.600, -0.800, 0, 0.800, 1.600, 2.200 m |
| Roof lower chord | centerline z = 6.069 m; underside 6.024 m |
| Roof upper chords | approximately z = 6.477 to 7.123 m centerline |
| Ground mat | 4.600 x 3.220 m envelope; grade z = -0.096 m |
| Wall support rails | at most 0.750 m vertical spacing |
| Individual wall boards | maximum length 3.000 m; supported staggered end joints |

The exact COLUMN_DEPTH and ROOF_TOP equations and assembly datums are in concept.md. Actual constructed counts and any fitting deviations belong in version_notes.md and this document's verification/iteration sections.

## 8. Verification

v01's final rendering harness reports 2,101 members, zero penetrating pairs deeper than 1 mm, zero floating members at the unchanged 2 mm contact tolerance, and zero overlap families. All 19 views and the Blender scene exist. A fresh single-room Inspector found no additional visible defects. Builder evidence supports details hidden or unmeasurable in the views: fitted roof planes, board lengths, supported joints, and the ceiling's face-fixing connection. Geometric overlap/contact checks find collisions or isolated members; they do not establish sufficient bearing area, force transfer, fastener design or structural capacity.

A separate bearing audit identified a v01 defect despite those clean checks. Horizontal cuts through sloping outer feet measure 90.008 to 91.505 mm, against 90.000 mm soles, leaving at most 0.753 mm unsupported on each edge. v02 fits the bottom 90 mm of the affected chord pieces with a local bevel, preserving their centerlines, stock catalogue, ground datums and member count. A new actual-mesh bearing assertion first failed on the inherited v01 geometry, then passed the correction: all 56 feet measure 90.000 mm and are contained by both sole and lower sleeper, with a 1 micrometre mesh-precision tolerance. The 19-view v02 render reports 2,101 members, zero pairs, zero floating members and zero families. Its independent inspection found no new visual defects. The tiny bevel cannot be measured reliably in the renders; actual-mesh evidence supplies that check. The completed phase-2 reference comparison closes R-13: all 28 requirements are checked, with zero waivers and no open geometric finding.

The frame-only render initially failed close-out's textual schema check because of the hide-list expression syntax. Inlining the identical list satisfies that check without altering its camera, visibility or rendered identity. Blender 4.3's viewer exporter timed out despite producing valid JSON; the Runner completed export with Blender 5.1. A scoped tools/layers.py override maps the two ground sleeper families into the frame layer. An escalated close-out run resolved Chrome's GPU/profile error and captured the correct GPT-6 v01 model. Both v01 and v02 pass all eight close-out checks. The Runner visually confirmed that the v02 screenshot identifies GPT-6, v02 and 2,101 elements with no error banner.

Before any renders existed, the Builder found 86 clashes in longitudinal ties and end-bay braces. Fitting them to transverse web faces removed those clashes. The rendered v01 is immutable. Its Builder was resumed after a usage-limit interruption; no completed rendered version was overwritten.

Not verified: strength, buckling, joint forces, fasteners, uplift/overturning anchors, soil capacity, moisture/durability, fire and weatherproofing. The 6 m slat columns have no matching prescriptive manual design. No exact door hardware or moving leaf is required.

Cost record: the runtime has not supplied context/token totals or automatic tool-call counts. They are unavailable, not zero. The run used two Designers (one concept/phase-2 Designer, one focused base-detail Designer), one Researcher, two fresh Builders, three Inspectors (v01 room, v02 room, v02 comparison), one standing Runner and the root CraftBot. Usage-limit interruptions required resuming unfinished work; completed renders and inspections were retained. No token or tool-call totals are invented.

## 9. Iterations

| Version | Change | Members | Penetrating pairs | Floating | Finding |
|---|---|---:|---:|---:|---|
| v01 | Initial concept; ties/braces fitted before rendering | 2,101 | 0 | 0 | 19 views inspected; foot-seat edge deficit up to 0.753 mm |
| v02 | Local foot bevel; actual-mesh full-foot bearing assertion | 2,101 | 0 | 0 | All 56 feet fully supported; 19 views inspected; viewer close-out 8/8 |

## 10. Scope and known simplifications

One architectural pavilion, one empty room and one entrance. No conditioned interior, glazing, membranes, stair, gallery, furniture, engineered foundation, fastener schedule or construction certification. Red and natural wood colours represent finishes; every structural and enclosure element is modeled separately as timber. Roof and wall geometry must close where specified despite the stated weatherproofing limit. All changes remain uncommitted for user review. Actual transcript archival is the final run action; the close-out adapter must select the root Codex rollout, not a subagent session.

The complete per-file handoff is in [files_created.md](files_created.md), including both scripts, 38 renders, two Blender scenes, inspections, viewer models, rationale/callouts, the prompt history and final close-out/archive paths. Shared net edits are the experiment-16 sleeper mapping in tools/layers.py and the viewer index. No new dependency was installed and no manual was downloaded. Suggested commit: `Add experiment 16 GPT-6 slat pavilion and verified viewer iterations`.
