# How to CLT: extracted notes

**Original PDF:** `manuals/Arkemi - How to CLT Handbook.pdf` (gitignored, not in the repo). If the file is missing, download it from https://arkemi.se/images/downloads/Arkemi_How-to-CLT_Handbook_30.pdf and save it under that name.

**Source:** How to CLT: architectural guidelines for early stages, Arkemi (Stockholm), second edition, 2024. Co-authors Narges Bahari, Emiline Elangovian, Kayrokh Moattar, Frantisek Orth, Niels Pettersson Sandmark, Sepideh Sarrafzadeh and Frida Tjernberg (structural engineer). Funded by Stockholms Byggnadsforening and ARQ. ISBN 978-91-527-4027-9. The PDF has 38 pages (each a landscape spread showing two consecutive printed pages), 70 printed pages in total.

**Scope of source:** Practical early stage design guidance for architects working with cross laminated timber (CLT). Deliberately limited to residential buildings of 3 to 8 floors with a load bearing structure more or less completely made of CLT, in a Swedish context (Swedish regulations, Swedish producers, Swedish snow zones). A companion Grasshopper script and Revit file are described but not included in the PDF. All dimensions are explicitly preliminary only, stated by the source to not replace a full static calculation. The book does not cover connection or fastener design, span tables beyond the rough ones given, fire resistance classification, acoustic calculation methods, or markets outside Sweden.

**Most useful for:** choosing a CLT structural system (panel honeycomb, parting wall, hybrid, or 3D-module) and sizing walls, floor slabs, roofs and openings for a 3 to 8 storey CLT residential building at early design stage. Also useful for the master panel, transport and envelope constraints that bound element geometry, and for build-up layer stacks of walls, floors and roofs.

Note on page numbers: this PDF is paginated as 38 landscape spreads, each showing two consecutive printed pages (left page even, right page odd). The Read tool and pdftotext address the 38 spreads, not the printed folios. Page numbers below are PDF page numbers unless marked "printed p."; the Contents table gives both.

---

## Contents of the source document

| Ch. | Title | PDF pp. (printed pp.) | Sections |
|---|---|---|---|
| 00 | Cover and table of contents | 1-2 (cover, i-ii) | Front cover, funding acknowledgement, table of contents |
| 01 | Introduction | 3-5 (2-7) | Acknowledgements, foreword, workflow (handbook, Grasshopper script, Revit file) |
| 02 | CLT and Swedish forestry | 6-12 (8-21) | Debate on sustainable forestry, designing with reduced impact, glossary |
| 03 | Collaborate with CLT | 13-18 (22-33) | Background, 6 principles for a close collaboration |
| 04 | Design with CLT for early stages | 19-26 (34-49) | Structural systems, CLT elements |
| 05 | Rules of thumb | 27-33 (50-63) | Rough dimensional rules, dimensional tables and library of elements |
| 06 | Postface | 34-37 (64-71) | Image references, references |
| - | Back cover | 38 (72) | Download QR code |

For procedural modelling the relevant material is in chapters 04 and 05 (see also "Rules for modelling" at the end).

---

## Quick reference

| Parameter | Value | Source |
|---|---|---|
| CLT master panel, length | about 16 m, up to 20 m on demand | PDF p. 28 |
| CLT master panel, width | about 3 m, up to 4.8 m on demand | PDF p. 28 |
| CLT master panel, thickness | up to 350 mm | PDF p. 28 |
| Panel layers | odd number (3, 5, 7, etc.); top and bottom layers share board direction, which sets the main structural axis | PDF p. 28 |
| Semi-trailer transport limit (planar panels) | 13.6 x 2.45 x 2.7 m (L x W x H) | PDF pp. 28-29 |
| Mega-trailer transport limit (planar panels) | 13.6 x 2.45 x 3.0 m | PDF pp. 28-29 |
| 3D-module transport limit | up to 4.15 m wide, 4.5 m high including trailer, 30 m long including truck | PDF p. 30 |
| Wall panel thickness, 3 to 8 floor housing | 140 to 220 mm | PDF p. 29 |
| Wall panel height | normally equals master panel width, about 3 m (one storey, platform framing) | PDF p. 29 |
| Wall panel used longitudinally (balloon frame, cores, shafts) | up to about 16 m | PDF p. 29 |
| Floor slab thickness, 3 to 8 floor housing | 200 to 260 mm | PDF pp. 30-31 |
| Floor slab span, basic CLT | up to 7 m | PDF p. 30 |
| Floor slab span, ribbed or reinforced with glulam or concrete | up to 9 m | PDF p. 30 |
| Roof panel thickness, 3 to 8 floor housing | 140 to 180 mm | PDF pp. 30, 33 |
| Roof span, basic CLT | up to 7 m, reinforceable like a slab | PDF p. 30 |
| CNC-routed opening, max width | 1500 mm (edge opening), 2000 mm (second opening) | PDF p. 24 |
| Opening formed with slab support, min pier and min opening | 200 mm min pier, 500 mm min opening | PDF p. 24 |
| Opening formed with lintel support, min pier | 500 mm min | PDF p. 24 |
| Edge distance to opening | 300 mm min at panel edge, 600 mm min between openings | PDF p. 24 |
| Hybrid CLT plus timber frame (glulam or LVL), span | up to 7.5 m | PDF p. 21 |
| Hybrid CLT plus concrete or steel frame, span | up to 9 m | PDF p. 21 |
| Storey range, modular (3D-module) system | 4 to 8 storeys | PDF p. 21 |
| Storey range, honeycomb system | 6 to 16 storeys | PDF p. 21 |
| Storey range, parting wall system | 4 to 12 storeys | PDF p. 21 |
| Storey range, hybrid with CLT core | 4 to 16 storeys | PDF p. 21 |
| Storey range, hybrid CLT plus timber frame | 1 to 3 storeys with planed lumber, 1 to 5 storeys with glulam or LVL | PDF p. 21 |
| Storey range, hybrid CLT plus concrete or steel | up to 7 storeys (table prints "?-7") | PDF p. 21 |
| Longitudinal (balloon) wall application | best for buildings up to 3 storeys | PDF p. 29 |
| Transverse (platform) wall application | mostly used in multi-storey buildings | PDF p. 29 |

---

## 01 Introduction

### Foreword
CLT (cross laminated timber) is a prefabricated engineered wood product made by gluing together layers of sawn boards into panels capable of carrying loads in all three major axes. It was introduced in the early 1990s in Austria and Germany and is now one of the most important mass timber materials.

The Swedish building industry was responsible for about 21 percent of the country's domestic CO2 emissions in 2019. In 2020 only 2 in 10 new apartment buildings were built in wood, although 70 percent of Sweden is forest. Most Swedish builders and architects have little experience with budgeting, planning and building CLT buildings, so constructing larger buildings in anything but concrete and steel is seen as unnecessary risk-taking.

An architect's influence peaks in the initial design phases and then declines, so the handbook limits its scope to architectural work in early stages, and to residential buildings of 3 to 8 floors with a CLT load-bearing structure. The authors caution that CLT's environmental benefit depends entirely on where the raw material comes from (clear-cutting, colonisation of Sapmi), and that using timber or CLT in a project does not automatically make it sustainable architecture.

### Workflow, three components
1. Handbook (this document). Structural systems and individual CLT elements (chapter 04), rules of thumb on dimensioning with limiting factors from production, transportation and structure, and a library of build-ups with dimensional tables (chapter 05).
2. Grasshopper script. Input is a simple plan sketch plus general building parameters (for example number of floors); output is a parametric 3D model plus economic and ecological estimates (area calculations, material costs, carbon footprint, timber consumption, element volumes). The model can be baked into Rhinoceros.
3. Revit file. A BIM version of the build-up library plus schedules that automatically calculate material and quantity take-offs. It is a library to copy from, not a modelling file.

Workflow diagram, PDF p. 5: Brief, then Schematic Design (where How to CLT provides output), then Developed Design, Detailed Design, Construction. The handbook supplies material, structural and dimensional knowledge; the Grasshopper script supplies economic and ecological calculation plus a parametric model, feeding a preliminary cost calculation; the Revit file supplies preliminary build-ups, material take-off and a BIM model, feeding a preliminary design.

---

## 02 CLT and Swedish forestry

### Debate on sustainable forestry
Forest management is only truly sustainable if it supports ecological and social functions at multiple scales, not just economic ones. The Swedish forestry model manages 28 million ha of forest with a focus on maximising harvest. The industry was established in the 1850s for pulp and paper; natural forests were converted to single-age, single-species plantations, with government-approved clear-cutting from the 1950s. Rotation is 70 to 110 years, and standing timber volume has increased since the mid 1900s.

Continuous Cover Forestry (CCF) is supported by Naturskyddsforeningen and Greenpeace as a less interventionist, more diverse alternative that maintains consistent carbon in biomass and soil. Clear-cut forests emit carbon for the first 20 years or so, due to soil scarification; a natural forest reaches full carbon capacity in about 150 years. Climate accords have net emission caps due in 7 to 27 years, which the authors argue does not leave time to wait for clear-cut plantations to regrow.

Only about 20 percent of harvested wood goes into long-lasting products such as buildings and furniture; 80 percent is burned or used for short-lifespan products. The substitution effect (claiming wood displaces higher-emission materials) requires a corresponding decrease in fossil supply to actually work. Boreal forest resilience under warming is uncertain, and CCF (unevenly aged stands) is considered more resilient.

On biodiversity, about 1400 forest species are endangered, over 90 percent of Swedish forests have been clear-cut since the 1950s, and industry retains about 3 percent of clear-cut area for conservation. Skogsforsk recommends 10 percent of managed forests as CCF; Plockhugget uses CCF only and sells clear-cut-free timber ("hyggesfri travara"). On the Sami people: lichen, the primary reindeer food, has declined by over 70 percent of lichen-rich forest in 60 years, and only large forest companies are legally required to consult the Sami.

Conclusion of the chapter: CLT is no panacea, but storing wood in buildings for a long time is preferable to short-shelf-life products.

### Designing with reduced impact, architect's checklist
- Do not demolish buildings. Protect and retrofit instead.
- Use as little raw material as possible. In buildings up to four storeys a wooden frame construction may be more suitable than a CLT panel system; reuse elements where possible, including glulam arches, for example through the CCbuild platform.
- Use traceable material, such as clear-cut-free certified timber ("hyggesfri travara" or Plockhugget).
- Design with foresight, meaning flexibility, durability and disassembly so elements can be reused.
- Use your political voice for transparency and stricter PEFC or FSC certification criteria.
- Educate yourself. Further reading given: Journal of Forest Policy and Economics; Forestry: An International Journal of Forest Research; the Royal Swedish Academy of Sciences webinar on Boreal Forests and Climate Change; Naturskyddsforeningen; Skogsforsk; Architects Climate Action Network (ACAN); and the documentaries More of Everything and Slaget om skogen (SVT).

### Glossary (PDF p. 12, printed pp. 20-21)
Rotation period, ecosystem services, substitution effect, tipping points, clear-cutting, continuous cover forestry, retention forestry, carbon leakage, public commons, silviculture.

---

## 03 Collaborate with CLT

### Background
Rivka Oxman's concept of "material-based design", a computational process integrating structure, material and form within fabrication logic, is used to frame CLT construction: an engineered material that requires digital design and CNC-driven prefabrication, where on-site assembly dictates much of the formal and structural logic. The chapter compares this moment to the CAD to BIM shift of the 2000s, where an opportunity for interdisciplinary collaboration was largely lost, and argues CLT's still-forming processes are another chance. Sources are academic papers, an interview with Tomas Alsmarker (Svenskt Tra), and a questionnaire to architects and structural engineers. The proposed model is early engagement of the structural engineer as a sounding board, similar to common practice in reconstruction projects, rather than as an equal partner in conceptual design.

### 6 principles for a close collaboration
1. Start collaborating as early as possible. This limits costly re-designs; early design support from a structural engineer is comparatively cheap.
2. Establish a common goal. Value-based goals, such as a municipal urban planning strategy or an environmental certification workshop (for example BREEAM), transcend discipline-specific priorities.
3. Build trust and let go of prestige. The saying "an architect's dream is an engineer's nightmare" captures a common mistrust; treat trust as an intentional practice, at industry level (for example the Swedish network TranatverkA) and at project level (in-person workshops).
4. Understand each other's expertise. Architects think in rhythm, flow, proportion and scale; engineers in strength, ductility and loads. Avoid jargon and ask for clarification.
5. Create interoperable methods and tools. The hand-drawn sketch is the common tool (the number one workshop activity named by respondents); the How to CLT Grasshopper script works as a real-time cooperative sketching tool; also useful are collaborative BIM model files and "big-room meetings".
6. Transcend disciplinary boundaries through tectonics. Tomas Gustavsson's two modes are: structure subordinate to spatial design, or structure as one of several starting points (the tectonic approach, recommended). Subordinated structure tends toward "coulisse-like" results. Examples given: Centre Pompidou (tectonic) versus Gehry's LUMA Arles (hidden skeleton); Wisdome Stockholm (Elding Oscarsson).

10 good reads (PDF p. 15, printed p. 26): An Engineer Imagines (Peter Rice, 1996); Architect and Engineer, a study in sibling rivalry (Andrew Saint, 2008); Arkitektur och Barverk (Dan Engstrom et al, 2004); Collaborations in Architecture and Engineering (Clare Olsen, 2014); Conceptual Structural Design (Popovic Larsen and Tyas, 2003); Constructing Architecture (Andrea Deplazes, 2018); Introducing Architectural Tectonics (Chad Schwartz, 2016); Structure as Architecture (Andrew Charleson, 2018); Studies in Tectonic Culture (Kenneth Frampton, 2001); The Structural Basis of Architecture (Sandaker, Eggen and Cuvellier, 1989).

---

## 04 Design with CLT for early stages

### Structural systems

CLT can be load-bearing or non-load-bearing; the handbook only covers CLT as part of the structural system.

#### Panels or 3D-modules, two approaches
- Panel system: prefabricate panels in a factory, transport them, and assemble a stable structure on site. This is the most common approach.
- 3D-module system: prefabricate and assemble panels into portable, stable 3D room modules, then stack the modules on site.

#### 3D-module systems
Benefits: very fast to assemble, since most work happens in the factory (good for harsh climates and dense urban sites); resource efficient, due to repeatable processes and CNC precision; clear design configuration, since room-sized self-stable modules give the architect a legible set of stacking arrangements to explore.

Drawbacks for the architect: the system limits structural configuration, because module size is bound by trailer limits, which decide the maximum span widths of the whole building, and stability requires modules to be stacked with their longitudinal load-bearing walls aligned, producing a rigid system; it requires high repetition to be cost-effective, meaning modules must be plentiful and near-identical; it limits the architect's influence on apartment and room sizes, volumes and facades, and many producers offer their own proprietary modular systems; and it results in double layers of CLT, because each module has its own floor, walls and roof, so a small-gap double layer occurs wherever two modules meet, costing area, wasting material, and raising moisture and fire-safety questions.

Conclusion: 3D-modules can be well designed and cost-efficient, but they greatly limit the design, so they are less interesting to an architect than panel systems.

#### Panel systems
The key early decision is whether the structure is mainly CLT panels acting as load-bearing walls and slabs, or mainly framed (solid timber beams and columns carrying CLT slabs). The handbook focuses on load-bearing CLT panel structures ("CLT buildings"), in two categories:

- Honeycomb layout: a grid of load-bearing CLT walls, mostly structural, which spreads loads efficiently and lets wall and floor panels shrink to minimum thickness. Because forces transfer through lined-up walls, the plan layout must be more or less the same on every floor, limiting flexibility. The system is extremely robust and efficient and gives great freedom in the non-load-bearing facade; it suits complex buildings.
- Parting wall layout: core walls, exterior walls and the walls between apartments are load-bearing, using CLT walls and slabs with glulam or steel beams where wider spans are needed. This gives full flexibility within apartments, and building layout stays flexible as long as parting walls line up between storeys. It suits buildings of various heights and shapes, of lesser complexity.

Both are quick to assemble but require fixed wall locations and a reasonably constant floor layout.

#### Hybrid systems
Walls around lift shafts and stair cores are built in CLT for stiffness, combined with a grid of columns and beams where flexibility is needed, or CLT around the perimeter with a framed interior. Hybrids are more complex and technically demanding but give the highest flexibility, with structural elements kept to a minimum.

#### Table, variations of structural solutions using load-bearing CLT elements (PDF p. 21, printed p. 39)

| System | Made of | Characteristics | Suitable height |
|---|---|---|---|
| Modular system | Room-size modules built in the factory with CLT panels | Very fast assembly on site. Usually needs a secondary structure. Brings limitations in the design. High levels of repetition | 4 to 8 storeys |
| Honeycomb system | Walls and floors of load-bearing CLT in a grid | Robust and strong structure. Limitations in plan layout. Almost the same layout on all floors. Efficient use of materials | 6 to 16 storeys |
| Parting wall system | Load-bearing CLT elements, non-load-bearing elements from any material | Loads transferred mainly through the parting walls. More freedom in laying out the plan. Flexible structure | 4 to 12 storeys |
| Hybrid system with CLT core | CLT stabilising core and floors, with timber frame structure | Flexible. Strong structure for high-rise. Efficient use of materials. More aesthetic freedom and diversity | 4 to 16 storeys |
| Hybrid system, CLT and timber frame | CLT floors with timber frame structure of either planed lumber or glulam/LVL | Flexible layout. Cheap and convenient building process. Big spans up to 7.5 m | 1 to 3 storeys with planed lumber, 1 to 5 storeys with glulam/LVL |
| Hybrid system, CLT and concrete/steel | CLT floors with a concrete or steel frame structure and concrete stabilising core | Flexible layout. Cheap and convenient building process. Big spans up to 9 m. Strong structure for high-rise. Efficient use of materials | up to 7 storeys (table prints "?-7") |

Each row in the source also has a plan diagram (blue hatched for CLT walls, white for other) and an axonometric.

#### Ground floor and foundation (PDF p. 22, printed p. 41)
CLT buildings usually sit on a concrete podium level that raises the timber off the wet, dirty ground. The podium also transfers loads where the ground floor program (entrance halls, shared spaces, retail, parking) needs a different arrangement than the floors above. Concrete is also used for basements or partial basements acting as foundation. Figure on PDF p. 22 shows two common foundations, a concrete ground floor versus a concrete basement, both under a CLT block.

### CLT elements

Cross-lamination lets a panel span in two perpendicular directions. Unlike linear timber components (logs, rafters, studs), CLT is a planar component, structurally closer to pre-cast concrete panels. It can be used vertically as a wall, or horizontally as a floor or roof.

Diagram "Timber architecture evolving from linear to planar" (PDF p. 23, printed p. 42):

| | Lumber, timber log construction | Laminated timber panel, platform frame construction | Cross-laminated timber panel, mass timber construction |
|---|---|---|---|
| Span direction | one axis, linear | one axis, planar, single grain | two axes, planar, crossed grain |
| Characteristics | Linear configuration of elements. Perpendicular-to-grain loads. Limited spans. Small openings with limited dimensions | Structural elements in a grid. Parallel-to-grain loads. Openings within the structural grid. Several joints in the structure | More freedom in configuration of structural elements. Parallel-to-grain loads. Free opening location and size. Fewer joints in structure |

#### CLT as a wall
Surface finish comes in three grades: visible quality, industrial quality and built-in quality, with increasing knot content (PDF p. 23, printed p. 43). Visible and industrial quality may be left exposed, finished with paint, varnish, wax or oil. Fire, acoustic and work-environment regulations may still require plastering or gypsum as a finishing layer.

Openings (PDF p. 24, printed p. 44): cross-lamination lets several openings for doors, windows and services be cut without jeopardising structural capability, but openings should be managed consciously to minimise waste and maximise stability. Three methods:

| Method | Pros | Cons |
|---|---|---|
| CNC-routed opening, cut from a single panel | Fast assembly on site. Freedom of form | Wastes material in production. Short spans or small openings. Expensive production, cheap assembly |
| Opening formed with slab support, separate panels with a slab bridging the opening | Efficient use of material. Clear and simple structure | Short spans or small openings. Needs more lifts and joints on site. Cheap production, expensive assembly |
| Opening formed with lintel support, separate panels plus a lintel | Efficient use of material. Wide spans, big openings possible. Clear and simple structure | Needs more lifts and joints on site. Cheap production, expensive assembly |

Approximate max dimensions annotated on the wall elevation figure (PDF p. 24, left to right): edge pier 300 mm min, opening max 1500 mm, pier 600 mm min, opening max 2000 mm, pier 200 mm min, opening 500 mm min (formed), pier 1500 mm max, 500 mm min, 1500 mm max, 300 mm min.

Envelope (PDF p. 24, printed p. 45): CLT is kiln-dried, essentially untreated softwood, so it is susceptible to moisture and weathering. External CLT walls need a continuous shielding envelope providing airtightness, thermal insulation, a breathing zone for the CLT, and protection against rain. The section diagram lists layers from outside to inside: roof finish, path of roof ventilation, roofing breather membrane, insulation, cross-laminated timber, service void, interior finishing.

Interior walls: CLT is generally limited to load-bearing walls, such as apartment-separating walls. Because CLT is lightweight compared to concrete or gypsum, acoustic performance is usually achieved with supplementary sound-insulating layers, or with double CLT walls with insulation between, which is cheaper than a thicker panel unless the structure requires the extra thickness.

#### CLT as a floor slab
This is one of the most common applications, including in hybrid solutions. Slabs usually sit on two supports, either a line support along the panel length or point supports at set intervals. Structural homogeneity makes CLT slabs very good at distributing loads, so comparably large holes for shafts can be cut without reinforcement.

The simplest form is a CLT panel of sufficient thickness; acoustic regulations usually require a suspended ceiling or insulating layers of different densities on top. Other uses include a structural layer in cassette floors or hollow structures, and the bottom layer of a composite CLT-concrete floor, for better acoustics without bulky additions.

| Floor type (PDF p. 25, printed p. 46) | Description |
|---|---|
| CLT slab floor structure | CLT slab, with cladding panels and insulation added if necessary |
| CLT ribbed panel floor structure | CLT slab with added web joists for extra stiffness; in a hollow floor, spaced web joists are sandwiched between two CLT slabs to create a hollow unit |
| CLT-concrete composite floor structure | CLT slabs working together with a cast concrete slab |

All three are suitable for prefabrication. CLT also has good heat storage capacity and low thermal conductivity, so it feels warmer to the touch than concrete.

#### CLT as a roof
Like slabs, roofs transfer loads well and can include substantial openings without extra support, and suspended ceilings or building services are easily installed. For long unsupported spans a CLT roof imposes less load than a concrete deck, but may need an unjustifiably thick CLT panel, so it is often more economical to reduce the span with intermediate beams.

Pitched roofs can be mono-pitch or double-pitch. For double-pitch roofs of limited dimensions, CLT panels can be tilted against and fixed to one another without supporting members; larger spans need portal frames, trusses or beams.

Roof types constructible in CLT (PDF p. 25, printed p. 47, 9-part diagram): flat roof, pitched roof, pitched roof with wooden truss, double pitched roof, pitched roof with ridge beam support, pitched roof with wooden truss and joists, mono pitched roof, pitched roof with supporting wall and beam, folded plate roof.

#### CLT as stairs and services
Lift shafts and service cores are built in CLT, and factory accuracy allows rapid fixing of equipment. Mass-timber stairs are a lightweight, economical alternative to pre-cast concrete, especially when built from CLT offcuts. They can be straight, dog-leg, or custom. Photo, PDF p. 26 (printed p. 49): a solid CLT stair flight, stepped profile cut from a thick panel.

---

## 05 Rules of thumb

### Rough dimensional rules

#### The master panel
A CLT cross-section has an odd number of board layers; the top layer has the same orientation as the bottom one, and that direction sets the panel's main structural axis. A panel can have longitudinal or transverse board orientation.

All CLT elements should fit within the maximum dimensions of a master panel, which varies by producer but is typically about 16 m (up to 20 m on demand) long, 3 m (up to 4.8 m on demand) wide, and up to 350 mm thick.

Panels nested on the same master panel should be equally wide, to minimise waste and ease mounting and packaging; it is worth developing a system of wall heights and floor span widths early in the design. Fewer joints and bigger panels are structurally more favourable, giving a more coherent structure with fewer critical points, but must still respect master panel limits.

Diagram, PDF p. 28 (printed p. 52): a room assembled from CLT panels, with a 16000 mm long by 3000 mm wide master panel, showing nested wall panels (with openings) and floor panels.

#### Transportation
Transport limits are generally equal to or more restrictive than a producer's own maximum dimensions, so they are crucial for floor heights and panel sizes. Oversize permits are possible but expensive and best avoided. Rule of thumb: stay within a semi-trailer's 13.6 x 2.45 x 2.7 m or a mega-trailer's 13.6 x 2.45 x 3.0 m (length x width x height). Diagram, PDF p. 28 (printed p. 52): vertical load in a mega-trailer (panel standing, 3000 mm high) and horizontal load in a semi-trailer (panels stacked flat, 2700 mm high).

Diagram, PDF p. 29 (printed p. 54), on dimensional systems: "Optimized" (all panels one type), "Systematized" (a few panel types), "Non-Systematized" (every panel different). The chapter recommends establishing a dimensional system for efficient, easily constructable buildings.

#### Wall
Thickness is determined by imposed load and required fire resistance class, both of which depend on use and number of floors; thicker walls on lower floors are possible but not necessarily economical. For 3 to 8 floor housing, wall thickness is 140 to 220 mm. Panel height normally equals the master panel width, about 3 m; for balloon-frame structures, service cores and communication shafts, panels can be used longitudinally, up to about 16 m.

Common applications (PDF p. 29, printed p. 55):

| Application | Description | Use |
|---|---|---|
| Longitudinal in balloon | Wall panels continuous over several floors (boards vertical), floors hung between them | Best for buildings up to 3 storeys |
| Transverse in platform | One-storey wall panels, floor slab laid on top, next wall built on the slab | Mostly used in multi-storey buildings |
| Longitudinal in core | Tall continuous panels forming a stair or lift core | Used across building types, for extra stability and workability |

#### Slab
Thickness is determined by span and acoustic design. Basic CLT slabs span up to 7 m; up to 9 m with reinforcement (glulam ribs or concrete). For 3 to 8 floor housing, slab thickness is 200 to 260 mm. Diagram, PDF p. 30 (printed p. 56): a ribbed CLT panel, with LVL or glulam beams glued underneath as open ribs, or sandwiched to form a closed box, to span further.

#### Roof
Thickness is determined by span and snow load. CLT roofs usually span up to 7 m and can be reinforced like slabs. For 3 to 8 floor housing, roof thickness is 140 to 180 mm.

#### 3D-modules
The determining factor is transportability to site, given route limits and dense urban areas. Stable modules can be transported larger than planar elements, up to 4.15 m wide, 4.5 m high including the trailer, and 30 m long including the truck; larger still with escort, road blocks and route approval.

### Dimensional tables and library of elements

The preliminary dimensions given are for more or less pure CLT structural systems (hybrids differ), for 3 to 8 storey residential buildings in Sweden, using Swedish regulations and Swedish-market products. The same parameters are implemented in the Grasshopper script and Revit file. The CLT industry lacks a common system of dimensions, since each producer publishes its own handbook, so the authors compiled data from all Swedish producers plus interviews with a mass-timber construction engineer. The scheme adapts to a choice of light or heavy floor superstructure, which also affects wall dimensions. The source repeats: "these dimensions are only intended as an assistance for the preliminary stages and can not replace a full static calculation."

CLT thickness is shown in red in the source; it is marked in bold below.

#### Floor slabs (PDF p. 31, printed p. 59)

CLT with light superstructure, top to bottom:

| Thickness | Layer |
|---|---|
| 15 mm | Flooring |
| 2x13 mm | Floor gypsum |
| 22 mm | Chipboard subflooring |
| 220 mm | Acoustic floor with insulation |
| 200 / 240 mm | CLT |
| 15 mm | Fire protect board / gypsum |

CLT with heavy superstructure, top to bottom:

| Thickness | Layer |
|---|---|
| 15 mm | Flooring |
| 80 mm | Cast concrete |
| - | Moisture proof membrane |
| 20 mm | Acoustic mat |
| 220 / 260 mm | CLT |
| 15 mm | Fire protect board / gypsum |

CLT dimensioning table for floor slabs:

| Span (m) | Light, CLT (mm) | Light, total (mm) | Heavy, CLT (mm) | Heavy, total (mm) |
|---|---|---|---|---|
| under 5 | 200 | 498 | 220 | 350 |
| 5 to 7 | 240 | 538 | 260 | 390 |

#### Exterior walls (PDF p. 32, printed p. 60)

Exterior wall clad with wood panels, outside to inside:

| Thickness | Layer |
|---|---|
| 22 mm | Vertical facade panel |
| 25 mm | Batten |
| 27 mm | Counter batten |
| - | Wind barrier |
| 200 mm | Insulation |
| 140 to 200 mm | CLT |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

Exterior wall clad with bricks, outside to inside:

| Thickness | Layer |
|---|---|
| 108 mm | Facade brick |
| 40 mm | Ventilated cavity |
| 30 mm | Wind resistant sheathing |
| 200 mm | Insulation |
| 140 to 200 mm | CLT |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

CLT dimensioning table for exterior walls:

| Floors | Light floor, CLT (mm) | Light, total panel (mm) | Light, total brick (mm) | Heavy floor, CLT (mm) | Heavy, total panel (mm) | Heavy, total brick (mm) |
|---|---|---|---|---|---|---|
| I to III | 140 | 442 | 546 | 160 | 462 | 566 |
| IV to VI | 160 | 462 | 566 | 180 | 482 | 586 |
| VII to VIII | 180 | 482 | 586 | 200 | 502 | 606 |

#### Partitioning walls (PDF p. 32, printed p. 61)

Partitioning wall with single CLT, side to side:

| Thickness | Layer |
|---|---|
| 15 mm | Fire resistant gypsum board |
| 13 mm | Gypsum board |
| 120 to 180 mm | CLT |
| 40 mm | Ventilated cavity |
| 70 mm | Insulation plus studs |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

Partitioning wall with double CLT, side to side:

| Thickness | Layer |
|---|---|
| 15 mm | Fire resistant gypsum board |
| 13 mm | Gypsum board |
| 80 to 110 mm | CLT |
| 170 mm | Insulation |
| 80 to 110 mm | CLT |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

CLT dimensioning table for partitioning walls:

| Floors | Light, single CLT (mm) | Light, single total (mm) | Light, double CLT (mm) | Light, double total (mm) | Heavy, single CLT (mm) | Heavy, single total (mm) | Heavy, double CLT (mm) | Heavy, double total (mm) |
|---|---|---|---|---|---|---|---|---|
| I to III | 120 | 286 | 80+80 | 386 | 140 | 306 | 90+90 | 406 |
| IV to VI | 140 | 306 | 90+90 | 406 | 160 | 326 | 100+100 | 426 |
| VII to VIII | 160 | 326 | 100+100 | 426 | 180 | 346 | 110+110 | 446 |

#### Roof (PDF p. 33, printed p. 62)

Roof clad with metal, outside to inside:

| Thickness | Layer |
|---|---|
| 50 mm | Seamed metal roofing |
| 1 mm | Underlayment paper |
| 22 mm | Tongue and groove board |
| 25 mm | Ventilated cavity |
| - | Wind barrier |
| 200 mm | Insulation |
| - | Vapour barrier |
| 140 to 180 mm | CLT |
| 13 mm | Gypsum board |

Roof clad with tiles or shingles, outside to inside:

| Thickness | Layer |
|---|---|
| 80 mm | Shingle/tile roofing |
| 25 mm | Batten |
| 25 mm | Counter batten |
| 1 mm | Underlayment paper |
| 22 mm | Tongue and groove board |
| 25 mm | Ventilated cavity |
| - | Wind barrier |
| 200 mm | Insulation |
| - | Vapour barrier |
| 140 to 180 mm | CLT |
| 13 mm | Gypsum board |

CLT dimensioning table for roofs:

| Span (m) | Snow zone 1 to 3.5, CLT (mm) | Total, metal (mm) | Total, tiles/shingles (mm) | Snow zone 4.5 to 5.5, CLT (mm) | Total, metal (mm) | Total, tiles/shingles (mm) |
|---|---|---|---|---|---|---|
| under 5 | 140 | 451 | 531 | 160 | 471 | 551 |
| 5 to 7 | 160 | 471 | 551 | 180 | 491 | 571 |

Snow zones are Swedish snow-load zones in kN/m2.

---

## 06 Postface, selected references

Technical references used for dimensioning (full list, PDF pp. 35-36, printed pp. 66-69):
- Bergstrom and Frobel, The CLT Handbook: CLT structures, facts and planning, Svenskt Tra, 2019.
- Exova BM TRADA, Cross-laminated Timber: Design and Performance, 2017.
- Norman, Structural Timber Elements: a Pre-scheme Design Guide, 2nd edition, TRADA, 2016.
- Crawly, Cross Laminated Timber: A design stage primer, Routledge, 2021.
- Zumbrunnen, Pure CLT, Concepts and Structural Solutions for Multi Storey Timber Structures, IHF, 2017.
- Waugh Thistleton Architects, 100 Projects UK CLT, 2018.
- Producer brochures: Mayr-Melnhof (MM Crosslam), Stora Enso, Hasslacher, KLH, Setra, Leno (ZUBLIN), Martinsons.
- Esbjornsson, Magnusson and Ford, Urban Timber, Chalmers, 2014.
- Deplazes, Constructing Architecture, Springer, 2005.

Photo credits: Setra Group, for the preschool in Surbrunnshagen (Falun) and Vallaskolan (Sala) CLT interiors and stairs, PDF pp. 13, 19, 26, 27 (printed pp. 23, 35, 49, 51).

---

## Figure index

| PDF p. (printed p.) | Figure | Content |
|---|---|---|
| 5 (7) | Proposed workflow | Brief, Schematic, Developed, Detailed, Construction; handbook, Grasshopper and Revit outputs |
| 10 (17) | Photos | Clear-cut plantation (Bollnas) versus 85-year Douglas fir under CCF transformation |
| 15 (26) | 10 good reads | Literature list |
| 17 (31) | Photos | LUMA Arles (Gehry) versus Centre Pompidou |
| 20 (37) | Panel system versus 3D-module system | Two buildings under construction, trucks delivering panels versus modules |
| 21 (39) | Variations of structural solutions | 6 systems, plan plus axonometric plus characteristics plus storey range |
| 22 (41) | Two common foundations | Concrete ground floor versus concrete basement under a CLT block |
| 23 (42) | Linear to planar | Lumber, laminated panel, CLT; log, platform frame, mass timber |
| 23 (43) | Surface finish qualities | Three knot grades |
| 24 (44) | Common types of openings | Wall elevation with max/min dimensions; CNC-routed, slab support, lintel support |
| 24 (45) | Well designed envelope | Roof-wall section; airtightness, insulation, breathing zone, rain protection |
| 25 (46) | CLT floor slab types | Slab, ribbed, CLT-concrete composite |
| 25 (47) | Roof types in CLT | 9 section diagrams |
| 26 (49) | CLT stairs | Photo |
| 28 (52) | Master panel and dimensional limits | Room built from panels; 16000 x 3000 master panel; semi and mega trailer |
| 29 (54) | Dimensional system | Optimized, systematized, non-systematized |
| 29 (55) | Transverse/longitudinal applications | Balloon, platform, core |
| 30 (56) | Ribbed CLT panel | Open-rib and box sections |
| 30 (57) | CLT 3D module | 4.15 x 4.5 x 30 m transport limits |
| 31-33 (59-62) | Build-up library | Floor, exterior wall, partition wall and roof sections plus dimensioning tables |

---

## Rules for modelling

Rules distilled for generating a CLT panel building (3 to 8 storey residential, Swedish context):

1. Choose the structural system. Default to a panel system built as platform framing (one-storey transverse wall panels, slab on top, repeat). Alternatives: honeycomb (walls line up on every floor, suits 6 to 16 storeys) or parting wall (only cores, exterior walls and apartment-parting walls are load-bearing and must line up, suits 4 to 12 storeys). Add a concrete podium or ground floor under the CLT.
2. Respect the panel envelope. Every element must fit a master panel no larger than 16 m x 3 m x 350 mm, and pass a transport envelope no larger than 13.6 x 2.45 x 3.0 m (so wall panel length is about 13.6 m in practice, height about one storey around 3 m; floor slabs are strips up to about 13.6 m long by 2.45 to 3 m wide). Keep panel widths uniform, and use a small, repeated set of panel types.
3. Size the walls. Thickness 140 to 220 mm; pick from the tables by storey count and floor type (for example exterior walls 140/160/180 mm for storeys I to III / IV to VI / VII to VIII with a light floor, add 20 mm for a heavy floor). Partition (apartment-separating) walls: single CLT 120 to 180 mm, or double CLT 80+80 up to 110+110 mm with 170 mm insulation between. Balloon-frame or core panels can run up to about 16 m tall.
4. Size the openings. Cut openings up to about 1.5 to 2 m wide, with piers of at least 300 mm at panel edges and at least 200 to 600 mm between openings; larger openings need lintel support or slab support (built from separate panels rather than a single CNC-routed cut).
5. Size the slabs. Two-way panels on two supports; span up to 7 m plain (200 mm under 5 m, 240 mm for 5 to 7 m with a light floor; 220/260 mm with a heavy floor), up to 9 m if ribbed or composite; overall thickness 200 to 260 mm. Shaft holes can be cut freely without reinforcement.
6. Size the roof. Thickness 140 to 180 mm (140/160 mm for spans under 5 m / 5 to 7 m in low snow zones, 160/180 mm in high snow zones); span up to 7 m plain. Choose flat, mono-pitch, double-pitch (panels leaning against each other for small spans), or a roof with a ridge beam, truss or supporting wall for larger spans; folded plate is also possible.
7. Build the layer stacks. Exterior wall total is about 442 to 606 mm (CLT plus 200 mm insulation plus cladding); floor total is about 350 to 538 mm; roof total is about 451 to 571 mm. Use the build-up tables above for the exact layer order.
8. Add stairs and cores. Use CLT cores (longitudinal panels) for stability, and CLT stairs cut from offcuts where possible.
