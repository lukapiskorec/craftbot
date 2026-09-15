# Experiment 16 concept — GPT-6

Concept-stage release for v01, 2026-09-14, with the recorded sole-runner clarification. The brief controls the synthesis; all measurements below are metres unless mm is written. Values marked **mine** are design assumptions, not measured or engineered facts. This specification preceded geometry; the built v02 review is recorded in design_notes.md on 2026-09-15.

## Spatial concept

One square, empty room, with red vertical timber slats enclosing a quiet shaft. Clear inner faces are x/y = +/-1.500; finished floor z = 0; flat ceiling underside z = 6.000. Thus clear width and depth are 3.000 and clear height is exactly twice either dimension. These are **mine**, selected as a compact room scale consistent with the red references, not a surveyed size. No intermediate floor, stair, gallery or furniture is required. One centered entrance faces negative y; clear opening 0.900 wide by 2.100 high (**mine**, normal passage replacing the unusually low aperture in the interior photograph). An open doorway is the one entrance; a movable leaf is not required by the brief.

Daylight enters a 0.750-high open clerestory band on the two x walls, z = 5.250 to 6.000, immediately below the level ceiling (**mine**). Timber posts and rails cross that band but no opaque infill does. North and south walls remain boarded to the ceiling, echoing the high central red wall in the interior reference. The opening has no glazing: the all-slat brief is interpreted as an open-air architectural pavilion, with rain-tightness and conditioned occupation outside this geometric model. This assumption must remain visible in the report. The lower wall boarding and roof cover are geometrically closed, so intentional daylight openings remain concentrated above.

## Construction concept — research questions cite this section

Seven parallel transverse truss frames span x and repeat along y; their nominal stations are -1.500, -1.000, -0.500, 0, 0.500, 1.000, 1.500 (**mine**, six bays at 0.500). Side-wall inner chord lines remain vertical outside the square enclosure. Each frame combines triangulated deep side columns with a triangulated roof span. The outer chord varies by height and frame station, so a family of straight-stock polygonal trusses makes a waving exterior around the straight interior. End-wall boarding is held by light rails and jamb assemblies tied into the first and last transverse frames. The two side walls carry the roof; the entrance wall does not require a roof transfer across its doorway.

Released catalogue: enclosure, floor and ceiling slats B = 24 x 90 mm; primary chords and diagonals S = 36 x 90 mm. Primary chords use two separately legible S slats straddling one S web plane; timber packing/node straps use the same stock. No solid glulam, plywood gussets, thick posts or sheet cladding. Slat sizes are **mine**; the Researcher's scope verdict finds useful thin-member precedents but no capacity certification. Thin paired chords are connection analogies, not a nailed-truss design taken from a manual. Ripped edge slats and packers may be smaller than the catalogue but never larger in either cross-section dimension.

Ground to roof: a flat grade datum below the floor; built-up crossed slat sleeper mat on grade; close-laid floor slats; column inner and outer feet on continuous slat sole runners; column webs delivering roof reactions and wind shear to those feet; roof lower chords seated on paired side-column heads; triangulated webs to faceted upper chords; short roof slats spanning between adjacent frame top chords. Level ceiling slats are face-fixed to roof lower chords and establish the simple 6.000 m room datum. The ceiling is held by concealed fixings, not falsely described as bearing on supports above it. All splice positions land on nodes or supports. Concealed fixings, hold-downs and damp separation remain connection/performance design requirements, not invented timber capacity.

Lateral concept: triangulation of each x-z side/roof frame handles transverse action; longitudinal y-z bracing in the exterior side-wall depth connects the seven frames at several heights; explicit timber diagonals at roof and floor levels collect shear to these braced lines. A boarding layer alone is not claimed as a diaphragm. Both longitudinal end bays are braced; entrance remains free. Whole-building uplift, overturning, foot anchorage and connections require engineering beyond the manuals.

## Photo rule set

P-01 — 01-soane-front.jpg gives overall topology: a tall compact red enclosure sits inside exposed slender timber framing. The visible main face has five prominent paired vertical frame lines/four bays; the new seven-frame depth rhythm is a deliberate synthesis with the roof references, not a count copied from that face.

P-02 — 02-soane-outside.jpg gives construction character: paired thin members, open gaps, diagonal braces, and modest short horizontal projections. Preserve that assembled, slender reading; do not substitute chunky solid posts.

P-03 — 03-soaneinterior-1.jpg gives spatial character: uninterrupted tall red vertical boards, a level timber floor, one centered low aperture, and light concentrated at the top. Preserve the room and high-light hierarchy; normalize the opening to a usable entrance. Board end joints may stagger but wall planes remain flat.

P-04 — Erne_Dachbau_778.webp gives roof articulation, not room size: changing-depth trusses with triangulated webs and segmented chord direction. Model actual web triangles and changing roof depth; a wave-shaped solid panel is insufficient.

P-05 — Tchumi-02.jpg gives an outer-edge rule: repeated slender straight pieces form rising and falling profiles, with projected ends creating depth and shadow. Apply this to the frame series and outward side-column profiles; its glass and dense facade screening are not copied.

P-06 — Calibration is approximate. In the 933 x 1400 front photo, the outer stair rises about 280 image pixels over approximately 10 risers. Assuming 0.170 m/riser gives 165 px/m near that stair plane. The principal face spans about 470 px and the red-plus-upper enclosure about 680 px, suggesting roughly 2.8 m width and 4.1 m enclosure height under that local scale. Perspective, stair/face depth separation and obscured levels make those figures low confidence (at least +/-25%); they cannot establish clear room size or override the brief's exact 2:1 ratio. Adopted 3.000/6.000 dimensions are programme decisions. The low interior aperture is not used as a standard-door calibration.

P-07 — Colour follows the red-building references: muted oxide-red boarding and selected web slats, natural pale timber for paired chords and roof/ground slats. Colour is a finish on timber, not another construction material.

## Questions settled by the research verdict below

Q1: Which manuals justify narrow solid-timber floor and roof boarding at 600 mm support centers; minimum thickness and end-bearing/joint rules?

Q2: What manual truss member sizes, clear spans, node/gusset and inter-truss bracing figures offer a valid precedent; which parts do not establish capacity for the proposed 36 x 90 paired-slat system?

Q3: Does any manual cover a 6.0 m tall laterally braced slat truss column; what limits must explicitly be recorded, and what bearing/opening/base-detail rules can be transferred without claiming adequacy?

## Fixed geometry and construction numbers for the Builder

All values in this section are **mine**, unless the source table below says otherwise. Profiles are centerlines; faces must be offset by actual member sections and clipped at joints. No part may invade the clear 3.000 x 3.000 x 6.000 room other than the plane of its enclosure. Assembly tolerances may close joints but may not change headline room dimensions.

| Symbol / family | Fixed value and datum | Purpose |
|---|---|---|
| ROOM_W / ROOM_H | 3.000 / 6.000, inner finished faces | Exact user ratio |
| FRAME_Y | -1.500 + 0.500 j, integer j=0..6 | Seven frames |
| B | thickness 0.024, visible face width 0.090 | Wall, floor, ceiling and roof slats; final course ripped to boundary |
| S | thickness 0.036, in-plane face width 0.090 | Chords, webs, rails, ledgers, braces and sleepers |
| WALL_FACES | inner x/y = +/-1.500; outer faces = +/-1.524 | Flat vertical B boarding; outer structure never moves these faces |
| COLUMN_INNER_X | +/-1.600, centerlines | Nearest chord face +/-1.555 leaves room for wall attachment battens |
| COLUMN_Z | -0.024, 1.500, 3.000, 4.500, 6.024 | Five nodes, four column panels |
| COLUMN_DEPTH | d(0,j)=0.300; d(4,j)=0.600; intermediate d(k,j)=0.300+0.300 sin²(pi*k/4+pi*j/6) | Outer chord x = +/-(1.600+d); visible lateral wave; depth 0.300..0.600 |
| CHORD_LAYERS | paired S centerplanes y=FRAME_Y +/-0.036, thickness 0.036; web plane y=FRAME_Y, thickness 0.036 | Faces meet at y=FRAME_Y +/-0.018; total built-up thickness 0.108; each chord remains visibly a thin slat |
| ROOF_X | -2.200, -1.600, -0.800, 0, 0.800, 1.600, 2.200 | Seven roof panel stations, supports exactly over inner and outer column heads |
| ROOF_BOTTOM | lower chord centerline z=6.069, underside z=6.024 | Direct 0.090-wide seat on column heads; ceiling top z=6.024 |
| ROOF_TOP | upper chord node z=6.650+0.300 sin²(pi*(x+2.200)/4.400)+0.200 sin(2*pi*j/6) | Faceted changing-depth roof; approximate upper centerline range 6.477..7.123; seven ribs sampling three offset levels through a rise and fall, same flat inner ceiling |
| ROOF_COVER | B slats run generally along y between adjacent frame stations; ends land on top chords | Additive x/y height field gives planar quadrilateral facets, allowing straight stock; joints shared at support stations |
| FLOOR_STACK | B z=-0.024..0; upper sleepers z=-0.060..-0.024; lower sleepers z=-0.096..-0.060; flat grade z=-0.096 | Two crossed thin-slat bearing layers under the floor and column feet |
| GROUND_MAT | outer envelope 4.600 x 3.220, centered; upper transverse S sleepers at each FRAME_Y; lower longitudinal S sleepers at <=0.500 spacing plus all column-foot lines | Ground-level load distribution; no cantilevered thin sole beneath a column |
| SOLE_RUNNERS | continuous longitudinal S runners at inner/outer column-foot lines, integrated in upper layer z=-0.060..-0.024; upper transverse sleepers stop against runner faces | Feet remain at z=-0.024; lower longitudinal sleepers directly beneath each runner support every foot footprint; no third layer or overlapping cross-joint |
| WALL_RAILS | S horizontal attachment rails at vertical spacing <=0.750; add at z=0, 2.100, 5.250, 6.000 as applicable | End joints supported; trim rails clear of entrance and clerestory; side battens fill the 0.031 gap to inner chord faces |
| WALL_STOCK | B board joints at rail heights, maximum individual length 3.000 | Stagger adjacent board joints; no unsupported butt joint |
| ENTRANCE | x=-0.450..+0.450, y negative wall, z=0..2.100 | Clear opening; doubled S jambs and S header side plies with >=0.090 seat each end; red board infill above carried through header to jambs |
| BRACING | longitudinal braces in both end bays of both side walls, between column node levels; S rails link all seven frames at node levels | y-direction shear carried to ground without relying on skin |
| PLAN_BRACING | S diagonal pairs in roof and ground-mat planes, crossing in separate thickness layers | Collect shear across 3.000 m room; transverse x-z frames carry x-direction action |
| SPLICES / NODE_STRAPS | paired S splice straps nominal length 0.360, centered on a supported splice; all member ends on shared node planes | Visible timber contact; exact nail or screw schedule is unverified; do not substitute plywood gussets |

Use a single alternating diagonal per roof or column panel plus posts/ties at panel boundaries, so each panel is a genuine triangle system rather than decorative fins. At crossing braces use separate faces, not overlapping volumes. Chord-to-web connections are layered face contacts; chord-to-chord corners use complementary mitres and, where needed, paired S straps. Roof lower and upper chords are continuous or spliced at web nodes. Roof boarding meets the actual faceted upper-chord bearing plane; do not raise boards until they float above supports. An exact joint may require a short S blocking/cleat derived from the stated member faces; this is a connection detail within the catalogue, not authority to add heavy members.

Base assembly clarification for v01: the continuous sole runners form part of the upper crossed-mat layer, not an extra layer above it. Each foot bears on the runner top at z=-0.024; that runner bears on the lower sleeper top at z=-0.060, and the lower sleeper bears on grade at z=-0.096. Upper transverse sleeper segments butt to the longitudinal runner faces with concealed connection design unverified. Maintain full foot bearing within the stated thin-slat catalogue and floor supports at <=0.500 m; no unsupported runner projection carries a column. All base-detail dimensions here are **mine**.

Side walls use flat red B slats to z=5.250 and open clerestories above. End walls use flat red B slats to z=6.000 except the entrance. Floor and ceiling B slats run along y, with ends on the 0.500 frame grid. Ceiling fixings carry its gravity load into lower chords. Roof B slats fully cover their facets; edge seams are allowed, open decorative gaps through the roof are not. No construction claim of rain-tightness is made for board seams or valleys.

Roof edge boarding extends to the outer faces of the edge chords, at most 0.045 beyond the outer x node and 0.054 beyond the first/last y frame. This minor extension closes the cover over the frame faces, not a new cantilever. Wall corners use complementary cuts or one wall stops at the other's inner face; double thickness at a corner must not reduce clear dimensions. Bearing at column heads and entrance-header ends is 0.090, a **mine** timber seat, not an application of the manual's masonry bearing minimum. Roof board ends split on frame centerplanes and bear on the relevant 0.036-wide chord ply; connection and splitting adequacy are unverified.

## Source-to-rule-to-number verdict before geometry

| Source | Rule taken | Model number / disposition | Verdict |
|---|---|---|---|
| User brief; P-06 photographic scale | Square clear room; clear height twice width | ROOM_W=3.000; ROOM_H=6.000 | Brief controls ratio; width is a photo-informed estimate |
| P-01/P-02 red-building photos | Thin paired framing and flat red vertical enclosure | S=36 x 90 mm paired; B=24 x 90 mm | Sizes mine; construction character retained |
| CMHC Table 22, p.287; Table 35, p.305 | Lumber-board thickness depends on supports | Source minimum19 mm at600 mm; adopted B24 mm at500 mm | Useful thickness precedent; no certification of narrow boards or diaphragm |
| FRIM Table1 / Appendix I Sheet1 | Drawings and schedule govern conflicting floor-board prose | Source22 x145 mm at610 mm supports; adopted24 x90 mm at500 mm | Narrower slats are brief-driven, mine; source30 mm prose rejected |
| FRIM Appendix I Sheet9, PDF p.58 | Actual web triangles, upper/lower chords, slender stock | Source35 x72 mm over5.770 m, rise1.195 m; adopted S36 x90 with paired chords,3.200 m inner support span /4.400 m outer span | Precedent only; no scaling or capacity claim |
| FRIM Sheet9 roof plan; CMHC Ch.11 permanent truss bracing | Connect trusses with longitudinal and diagonal restraint | Source22 x97 mm braces at1.220 m trusses; adopted S braces tying500 mm frames at column levels and roof/floor planes | Bracing topology transferred; sizes and spacing mine |
| FRIM Sheet9 gusset detail | Nodes need designed fasteners and force transfer | Source9 mm plywood each side with3.3 x63 mm nails; spacing46/23 mm and edge16 mm | Not implemented: plywood conflicts with all-slat brief; paired S node straps and concealed connections require engineering |
| CMHC Table25, p.290 | Prescriptive stud cases have limited unsupported height | Roof-only exterior case3.0 m; table maxima3.6 m exterior and4.2 m interior; adopted6.0 m truss-column with1.5 m panels | Not covered: no claim of stud-table or truss-column adequacy |
| CMHC Fig.68, p.109 | Opening infill transfers through header to jambs | Clear entrance0.900 x2.100 m; doubled S jambs,0.090 header seats | Opening grammar transferred; member/connection sizes mine |
| CMHC Fig.86, p.125 | Roof reactions require real seats and aligned supports | Inner/outer column heads align x=+/-1.600,+/-2.200 with roof nodes;0.090 seats | Bearing logic transferred; roof is a truss, not a rafter/collar-tie prescription |
| FRIM Sheet7 base; CMHC Fig.47, p.79 | Bases require support, anchorage and moisture separation | Model crossed slat mat0.096 m under floor; no invented steel shoe/concrete footing | Ground contact modeled; anchors, uplift, moisture and soil capacity not verified |
| Erne and Tchumi images, P-04/P-05 | Segmented triangulated depth and repeating wave | Seven ribs; fixed COLUMN_DEPTH and ROOF_TOP formulas above | Geometric synthesis, no literal industrial dimensions transferred |

Builder figure set (shared provenance retained): `../references/manual_frim_sheet9_p58_truss_elevation_heel_span.png`, `../references/manual_frim_sheet9_p58_roof_bracing_plan.png`, `../references/manual_frim_sheet9_p58_truss_gusset_nailing.png`, `../references/manual_cmhc_p109_fig68_wall_opening_lintel_jack_cripple.png`, `../references/manual_cmhc_p125_fig86_rafter_heel_loadbearing_wall.png`, and `../references/manual_cmhc_p079_fig47_wood_sleeper_on_slab.png`. The gusset and base images explain what is not copied, as well as the connection principles.

Sections are plausible visual propositions for a thin-slat pavilion, not calculated. Whole-building strength, buckling, joint forces, fastener spacing, uplift/overturning anchorage, soil bearing, fire, durability and weatherproofing are not verified.

## Adopted dimensions against photo estimates

| Quantity | Reference estimate | Adopted | Verdict |
|---|---|---|---|
| Compact enclosure width | about 2.8 m, at least +/-25% uncertainty | 3.000 m clear | +7% before unknown wall thickness; reasonable room-scale inference |
| Tall enclosure height | about 4.1 m in front projection, at least +/-25% uncertainty | 6.000 m clear | Deliberate brief override to achieve exact 2:1 |
| Prominent front frame rhythm | five lines / four bays | seven transverse frames / six depth bays | Synthesis with expressive repeated roof; not a photographic replica |
| Low aperture | no reliable absolute scale | 0.900 x 2.100 m clear | Programme assumption for a usable entrance |
| Raised floor and exterior stair | present in reference | floor 0.096 m above grade; no stair | Single room brief does not require raised tower access; simple low threshold |
