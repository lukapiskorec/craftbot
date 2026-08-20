# How to CLT — Extracted Notes

**Source:** *How to CLT: architectural guidelines for early stages*, Arkemi (Stockholm), Second Edition, © Arkemi 2024, ISBN 978-91-527-4027-9. Co-authors: Narges Bahari, Emiline Elangovian, Kayrokh Moattar, Frantisek Orth, Niels Pettersson Sandmark, Sepideh Sarrafzadeh & Frida Tjernberg (structural engineer). Funded by Stockholms Byggnadsförening and ARQ. Extracted from `Arkemi - How to CLT Handbook.pdf` (70 pp., landscape spreads).

**Scope of source:** Practical early-stage design guidance for architects working with Cross Laminated Timber (CLT). Deliberately limited to **residential buildings of 3–8 floors with a load-bearing structure more or less completely made of CLT**, in a Swedish context (Swedish regulations, producers and snow zones). Accompanied by a Grasshopper script and a Revit file (not included in the PDF). Dimensions are explicitly **preliminary only — not a substitute for a full static calculation**.

---

## Contents of the source document

| Ch. | Title | Page | Sections |
|---|---|---|---|
| 01 | Introduction | 2 | Acknowledgements · Foreword · Workflow (Handbook, Grasshopper Script, Revit File) |
| 02 | CLT & Swedish Forestry | 8 | Debate on sustainable forestry · Designing with reduced impact · Glossary |
| 03 | Collaborate with CLT | 22 | Background · 6 Principles of Collaboration |
| 04 | Design with CLT for Early Stages | 34 | Structural Systems · CLT Elements |
| 05 | Rules of Thumb | 50 | Rough Dimensional Rules · Dimensional Tables and Library of Elements |
| 06 | Postface | 64 | Image References · References |

For procedural modelling the relevant material is in **Chapters 04 and 05** (see also the [summary for procedural modelling](#summary-for-procedural-modelling) at the end).

---

## Key dimensions quick reference

| Parameter | Value |
|---|---|
| CLT master panel — length | ~16 m (up to 20 m on demand) |
| CLT master panel — width | ~3 m (up to 4.8 m on demand) |
| CLT master panel — thickness | up to 350 mm |
| Panel layers | odd number (3, 5, 7 …); top and bottom layers share the same board direction = main structural axis |
| Semi-trailer transport limit (planar panels) | 13.6 × 2.45 × 2.7 m (L × W × H) |
| Mega-trailer transport limit (planar panels) | 13.6 × 2.45 × 3.0 m |
| 3D-module transport limit | up to 4.15 m wide, 4.5 m high (incl. trailer), 30 m long (incl. truck) |
| Wall panel thickness (3–8 floor housing) | 140–220 mm |
| Wall panel height | normally = master panel width, ~3 m (one storey, platform framing) |
| Wall panel used longitudinally (balloon frame, cores, shafts) | max height ~16 m |
| Floor slab thickness (3–8 floor housing) | 200–260 mm |
| Floor slab span — basic CLT | up to 7 m |
| Floor slab span — ribbed / reinforced with glulam or concrete | up to 9 m |
| Roof panel thickness (3–8 floor housing) | 140–180 mm |
| Roof span — basic CLT | up to 7 m (can be reinforced like slabs) |
| CNC-routed opening — max width | 1500 mm (first), 2000 mm (second), 1500 mm typical |
| Opening formed with slab support — min pier/spacing | 200 mm min / 500 mm min |
| Opening formed with lintel support — min pier | 500 mm min |
| Edge distance to opening | 300 mm min / 600 mm min (per diagram p. 44) |
| Hybrid CLT + timber frame (glulam/LVL) — spans | up to 7.5 m |
| Hybrid CLT + concrete/steel frame — spans | up to 9 m |
| Storey range — modular (3D-module) system | 4–8 storeys |
| Storey range — honeycomb system | 6–16 storeys |
| Storey range — parting wall system | 4–12 storeys |
| Storey range — hybrid with CLT core | 4–16 storeys |
| Storey range — hybrid CLT + timber frame | 1–3 storeys (planed lumber), 1–5 storeys (glulam/LVL) |
| Storey range — hybrid CLT + concrete/steel | 3–7 storeys (table reads "?–7") |
| Longitudinal (balloon) wall application | best for up to 3-storey buildings |
| Transverse (platform) wall application | mostly used in multi-storey buildings |

---

## 01 Introduction

### Foreword
- **CLT** = prefabricated engineered wood product made by gluing together layers of sawn boards into panels capable of carrying loads in all three major axes. Introduced in the early '90s in Austria and Germany; now one of the most important mass-timber materials.
- Swedish building industry: ~21% of domestic CO₂ emissions (2019); in 2020 only 2/10 new apartment buildings were built in wood, though 70% of Sweden is forest.
- Most Swedish builders/architects have little experience with budgeting, planning and building CLT buildings → constructing larger buildings in anything but concrete and steel is seen as risk-taking.
- Architect's influence peaks in initial design phases then declines → handbook scope limited to **architectural work in early stages**, and to residential buildings of 3–8 floors with CLT load-bearing structure.
- Caveat: CLT's environmental benefit depends entirely on where the raw material comes from (clear-cutting, colonisation of Sápmi). "The use of timber or CLT in a project does not automatically make it sustainable architecture."

### Workflow — three components
1. **Handbook** (this document): structural systems and individual CLT elements (Ch. 04), rules of thumb on dimensioning with limiting factors (production, transportation, structure) and a library of build-ups with dimensional tables (Ch. 05).
2. **Grasshopper script**: input = simple plan sketch + general building parameters (e.g. number of floors) → output = parametric 3D model + economic and ecological estimates (area calculations, material costs, carbon footprint, timber consumption, element volumes). Model can be baked into Rhinoceros.
3. **Revit file**: BIM version of the build-up library + schedules that auto-calculate material and quantity take-offs. A library to copy from, not a modelling file.

Workflow diagram (p. 7): Brief → **Schematic Design** (where How to CLT provides output) → Developed Design → Detailed Design → Construction. Handbook provides material/structural/dimensional knowledge; Grasshopper provides economic/ecological calculation + parametric model → Preliminary Cost Calculation; Revit provides preliminary build-ups, material take-off, BIM model → Preliminary Design.

---

## 02 CLT & Swedish Forestry

### Debate on sustainable forestry
- Forest management is only truly sustainable if it supports ecological and social functions at multiple scales, not just economic.
- **Swedish forestry model:** 28 million ha of forest; focus on maximising harvest. Industry established 1850s (pulp/paper); natural forests converted to single-age, single-species plantations; government-approved clear-cutting from the 1950s. Rotation 70–110 years. Standing timber volume has increased since mid-1900s.
- **Continuous Cover Forestry (CCF):** supported by Naturskyddsföreningen and Greenpeace; less intervention, more diverse forests; maintains consistent carbon in biomass and soil. Clear-cut forests emit carbon for the first ~20 years (soil scarification). Natural forest reaches full carbon capacity in ~150 years.
- Climate accords have net emission caps in 7–27 years → can't wait for clear-cut plantations to regrow.
- **Raw material:** only ~20% of harvested wood goes into long-lasting products (buildings, furniture); 80% is burned or short-lifespan products. Substitution effect requires a corresponding decrease in fossil supply.
- Boreal forests' resilience under warming is uncertain; CCF (unevenly aged stands) is more resilient.
- **Biodiversity:** ~1,400 forest species endangered; >90% of Swedish forests clear-cut since 1950s; industry retains ~3% of clear-cut area. Skogsforsk recommends 10% of managed forests as CCF; Plockhugget uses CCF only and sells "hyggesfri trävara" (clear-cut-free timber).
- **Sámi:** lichen (reindeer food) — >70% of lichen-rich forest lost in 60 years; only large forest companies are required to consult Sámi.
- Conclusion: CLT is no panacea but storing wood in buildings for a long time is preferable to short-shelf-life products.

### Designing with reduced impact (architect's checklist)
- **Do not demolish buildings** — protect and retrofit.
- **Use as little raw material as possible** — in buildings up to **four storeys a wooden frame construction may be more suitable than a CLT panel system**; reuse elements (e.g. CCbuild platform, even glulam arches).
- **Use traceable material** — "hyggesfri trävara" certification / Plockhugget clear-cut-free products.
- **Design with foresight** — flexibility, durability, disassembly so elements can be reused.
- **Use your political voice** — transparency, stricter PEFC/FSC criteria.
- **Educate yourself** — further reading: Journal of Forest Policy and Economics; Forestry: An International Journal of Forest Research; Royal Swedish Academy of Sciences webinar on Boreal Forests and Climate Change; Naturskyddsföreningen; Skogsforsk; Architects Climate Action Network (ACAN); documentaries *More of Everything* and *Slaget om skogen* (SVT).

### Glossary (forestry)
Rotation Period · Ecosystem Services · Substitution Effect · Tipping Points · Clear-cutting · Continuous Cover Forestry · Retention Forestry · Carbon Leakage · Public Commons · Silviculture (definitions on pp. 20–21).

---

## 03 Collaborate with CLT

### Background
- Rivka Oxman: "Material-based design" — computational informing process integrating structure, material and form within the logic of fabrication technologies. CLT construction is a child of this evolution: engineered material requiring digital design and CNC-driven prefabrication; **on-site assembly dictates much of the formal and structural logic**.
- Compared to the CAD→BIM shift in the 2000s: opportunity for interdisciplinary collaboration largely lost. CLT's still-liquid processes are another chance.
- Sources: academic papers, interview with Tomas Alsmarker (Svenskt Trä), questionnaire to architects and structural engineers.
- Proposed model: **early engagement of the structural engineer as a sounding board** (common in reconstruction projects) rather than as equal partner in conceptual design.

### 6 Principles for a close collaboration
1. **Start collaborating as early as possible** — limits costly re-designs; early design support from a structural engineer is cheap.
2. **Establish a common goal** — value-based goals (e.g. municipality urban planning strategy, environmental certification such as BREEAM workshops) transcend discipline-specific priorities.
3. **Build trust and let go of prestige** — "an architect's dream is an engineer's nightmare"; treat trust as intentional practice; industry level (e.g. Swedish TränätverkA) and project level (in-person workshops).
4. **Understand each other's expertise** — architects: rhythm, flow, proportion, scale; engineers: strength, ductility, loads. Avoid jargon; ask for clarification.
5. **Create interoperable methods and tools** — the hand-drawn sketch is the common tool (respondents' #1 workshop activity); the How to CLT Grasshopper script as real-time cooperative sketching tool; collaborative BIM model files; "big-room meetings".
6. **Transcend disciplinary boundaries through Tectonics** — Tomas Gustavsson's two modes: (a) structure subordinate to spatial design, (b) structure as one of several starting points (= tectonic approach, recommended). Subordinated structure tends to "coulisse-like" results. Examples: Centre Pompidou (tectonic) vs Gehry's LUMA Arles (hidden skeleton); Wisdome Stockholm (Elding Oscarsson).

**10 Good Reads** (p. 26): *An Engineer Imagines* (Peter Rice, 1996); *Architect and Engineer: a study in sibling rivalry* (Andrew Saint, 2008); *Arkitektur och Bärverk* (Dan Engström et al, 2004); *Collaborations in Architecture and Engineering* (Clare Olsen, 2014); *Conceptual Structural Design* (Popovic Larsen & Tyas, 2003); *Constructing Architecture* (Andrea Deplazes, 2018); *Introducing Architectural Tectonics* (Chad Schwartz, 2016); *Structure as Architecture* (Andrew Charleson, 2018); *Studies in Tectonic Culture* (Kenneth Frampton, 2001); *The Structural Basis of Architecture* (Sandaker, Eggen & Cuvellier, 1989).

---

## 04 Design with CLT for Early Stages

### Structural Systems

CLT can be load-bearing or non-load-bearing; the handbook only covers CLT as part of the structural system.

#### Panels or 3D-Modules? — two approaches
- **Panel System:** prefabricate panels in a factory, transport, assemble on site into a stable assembly. Most common.
- **3D-Module System:** prefabricate and assemble panels into portable, stable 3D room modules; stack on site.

#### 3D-Module systems
Benefits:
- **Very fast to assemble** — most work in the factory; good for harsh climates, dense urban sites.
- **Very resource efficient** — repeatable processes, CNC precision.
- **Clear design configuration** — room-sized, self-stable modules; architect can explore stacking arrangements.

Drawbacks (for the architect):
- **Limits the structural configuration** — module size bound by trailer limits → decides max span widths of the whole building; stability requires modules stacked with longitudinal load-bearing walls aligned → rigid system.
- **Requires high repetition to be cost-effective** — modules must be plentiful and near-identical.
- **Limits design and the architect's influence** — restrictions on apartment/room sizes, volumes, facades; producers offer their own modular systems.
- **Results in double layers of CLT** — each module has own floor, walls, roof → double layers (with a small gap) wherever modules meet; loss of area, ineffective material use, possible moisture and fire-safety limits.
→ Conclusion: 3D-modules can be well-designed and cost-efficient but greatly limit the design; less interesting from an architect's point of view than Panel Systems.

#### Panel systems
Key early decision: structure mainly **CLT panels as load-bearing walls and slabs**, or mainly **framed** (solid timber beams and columns carrying CLT slabs). Handbook focuses on load-bearing CLT panel structures ("CLT-buildings"), in two categories:

- **Honey Comb Layout:** grid of load-bearing CLT walls, majority structural → loads spread efficiently, wall and floor panels reduced to minimum thickness. Forces transferred through **lined-up walls → plan layout must be more or less the same on every floor**, limiting flexibility. Extremely robust and efficient; great freedom in the non-load-bearing facade. Suitable for complex buildings.
- **Parting Wall Layout:** core walls, exterior walls and parting walls between apartments are load-bearing; CLT walls and slabs with glulam or steel beams where wider spans are necessary. Full flexibility within apartments; building layout flexible as long as **parting walls line up between storeys**. Suits various heights and shapes of buildings of lesser complexity.

Both are quick to assemble but require fixed wall locations / reasonably constant floor layouts.

#### Hybrid systems
- Walls around lift shafts and stair cores in CLT (stiffness) + grid of columns and beams where flexibility is needed. Or CLT around the perimeter + framed interior.
- More complex and technically demanding but highest flexibility; structural elements kept to a minimum.

#### Table — Variations of structural solutions using load-bearing CLT elements (p. 39)

| System | Made of | Characteristics | Suitable height |
|---|---|---|---|
| **Modular System** | Room-size modules built in the factory with CLT panels | Very fast assembly on-site · Usually needs a secondary structure · Brings limitations in the design · High levels of repetition | 4–8 storeys |
| **Honey comb System** | Walls & floors of load-bearing CLT in a grid | Robust and strong structure · Limitations in plan layouting · Almost same layout in all floors · Efficient use of materials | 6–16 storeys |
| **Parting Wall System** | Load-bearing CLT elements; non-load-bearing elements from any material | Transferring loads merely through the parting walls · More freedom in laying-out the plan · Flexible structure | 4–12 storeys |
| **Hybrid System: with CLT Core** | CLT stabilising core and floors, with timber frame structure | Flexible · Strong structure for high-rise · Efficient use of materials · More aesthetic freedom and diversity | 4–16 storeys |
| **Hybrid System: CLT and Timber Frame** | CLT floors with timber frame structure of either planed lumber or Glulam/LVL | Flexible layout · Cheap and convenient building process · Big spans up to 7.5 m | 1–3 storeys with planed lumber; 1–5 storeys with Glulam/LVL |
| **Hybrid System: CLT and Concrete/Steel** | CLT floors with frame structure of concrete or steel with concrete stabilising core | Flexible layout · Cheap and convenient building process · Big spans up to 9 m · Strong structure for high-rise · Efficient use of materials | ?–7 storeys |

Each row in the source has a plan diagram (blue hatched = CLT walls, white = other) and an axonometric.

#### Ground floor and Foundation (p. 41)
- CLT buildings usually sit on a **concrete podium level** raising the timber off the ground (wet/dirty). Podium also transfers loads where the ground floor program (entrance halls, shared spaces, retail, parking) needs a different arrangement than the floors above.
- Concrete also used for basements / partial basements acting as foundation. Figure: two common foundations — concrete ground floor vs concrete basement, both under a 4-storey CLT block.

### CLT Elements

Cross-lamination → structure spans in **two perpendicular directions**. Unlike linear timber components (logs, rafters, studs), CLT is a **planar** component — structurally more like pre-cast concrete panels. Usable vertically (wall) and horizontally (floor, roof).

Diagram "Timber architecture evolving from linear to planar" (p. 42):

| | Lumber / Timber Log Construction | Laminated Timber Panel / Platform Frame Construction | Cross-Laminated Timber Panel / Mass Timber Construction |
|---|---|---|---|
| Span direction | one axis (linear) | one axis (planar, single grain) | two axes (planar, crossed grain) |
| Characteristics | Linear configuration of elements · Perpendicular-to-grain loads · Limited spans · Small openings with limited dimensions | Structural elements in grid · Parallel-to-grain loads · Openings within the structural grid · Several joints in structure | More freedom in configuration of structural elements · Parallel-to-grain loads · Free opening location & size · Fewer joints in structure |

#### CLT as a Wall
- Surface finish qualities: **visible quality, industrial quality, built-in quality** (p. 43 shows three grades with increasing knots). Visible/industrial may be exposed; finish with paint, varnish, wax or oil. Fire, acoustic and work-environment regulations may require plastering or gypsum as finishing layer.
- **Openings** (p. 44): cross-lamination allows several openings for doors, windows and services to be cut without jeopardising structural capability. Manage openings consciously to minimise waste and maximise stability. Three methods:

| Method | Pros | Cons |
|---|---|---|
| **CNC-routed opening** (cut from a single panel) | Fast assembly on site · Freedom of form | Waste of material in production · Short spans / small openings · Expensive production, cheap assembly |
| **Opening formed with slab support** (separate panels, slab bridges opening) | Efficient use of material · Clear and simple structure | Short spans / small opening · Need for more lifts & joints on site · Cheap production, expensive assembly |
| **Opening formed with lintel support** (separate panels + lintel) | Efficient use of material · Wide spans / big openings · Clear and simple structure | Need for more lifts & joints on site · Cheap production, expensive assembly |

Approximate max dimensions annotated on the wall elevation (p. 44, left→right): edge pier 300 mm min · opening max 1500 mm · pier 600 mm min · opening max 2000 mm · pier 200 mm min · opening 500 mm min (formed) · pier 1500 mm max · 500 mm min · 1500 mm max · 300 mm min.

- **Envelope** (p. 45): CLT is kiln-dried, essentially untreated softwood → susceptible to moisture and weathering. External CLT walls need a continuous shielding envelope providing: **Airtightness · Thermal Insulation · Breathing Zone for CLT · Protection Against Rain**. Section diagram layers (outside→inside): roof finish / path of roof ventilation / roofing breather membrane / insulation / cross-laminated timber / service void / interior finishing.
- **Interior walls:** CLT generally limited to load-bearing walls such as apartment-separating walls. CLT is lightweight vs concrete/gypsum → acoustic performance achieved by **supplementary sound-insulating layers** or **double CLT walls with insulation between** — cheaper than a thicker panel unless structure requires it.

#### CLT as a Floor Slab
- One of the most common applications; also in hybrid solutions. Slabs usually on **two supports** — line support along the panel length or point supports at set intervals.
- Structural homogeneity → very good at distributing loads; **comparably large holes for shafts can be cut without reinforcement**.
- Simplest form: CLT panel of sufficient thickness; acoustic regulations usually require a suspended ceiling or insulating layers of different densities.
- Other uses: structural layer in cassette floors / hollow structures; bottom layer of composite CLT-concrete floor — better acoustics without bulky additions.

| Floor type (p. 46) | Description |
|---|---|
| **CLT Slab Floor Structure** | CLT slab; cladding panels and insulation added if necessary |
| **CLT Ribbed Panel Floor Structure** | CLT slab with added web joists for extra stiffness; in a hollow floor, spaced web joists are sandwiched between two CLT slabs to create a hollow unit |
| **CLT-Concrete Composite Floor Structure** | CLT slabs working in concert with a cast concrete slab |

All suitable for prefabrication.

- CLT has good heat storage capacity and low thermal conductivity → feels warmer to touch than concrete.

#### CLT as a Roof
- Like slabs, roofs transfer loads well and can include substantial openings without extra support; suspended ceilings / MEP easily installed.
- For long unsupported spans a CLT roof imposes less load than a concrete deck but may need unjustifiable CLT thickness → more economical to **reduce the span with intermediate beams**.
- Pitched roofs: mono-pitch or double-pitch. **Double-pitch roofs of limited dimensions: CLT panels tilted against and fixed to one another without supporting members.** Larger spans: portal frames, trusses or beams.

Roof types constructible in CLT (p. 47 diagram, 9 sections): Flat Roof · Pitched Roof · Pitched Roof with Wooden Truss · Double Pitched Roof · Pitched Roof with Ridge Beam Support · Pitched Roof with Wooden Truss and Joists · Mono Pitched Roof · Pitched Roof with Supporting Wall and Beam · Folded Plate Roof.

#### CLT as Stairs and Services
- Lift shafts and service cores in CLT; factory accuracy allows rapid fixing of equipment.
- Mass-timber stairs: lightweight, economical alternative to pre-cast concrete, especially from **CLT offcuts**. Straight, dog-leg or custom. Photo p. 49: solid CLT stair flight, stepped profile cut from a thick panel.

---

## 05 Rules of Thumb

### Rough Dimensional Rules

#### The Master Panel
- Cross-section = **odd number of board layers**; top layer has the same orientation as the bottom → defines the **main structural axis**. A panel can have longitudinal or transverse board orientation.
- All elements should fit within the **master panel**: approx **16 m (up to 20 m) long × 3 m (up to 4.8 m) wide × up to 350 mm thick** (varies by producer).
- Panels nested on the same master panel should be **equally wide** → minimise waste, ease mounting/packaging. Develop a **system of wall heights and floor span widths** early.
- Fewer joints / bigger panels = structurally more favourable (more coherent, fewer critical points) — but respect master panel limits.
- Diagram p. 52: a room assembled from CLT panels; master panel 16000 mm long, 3000 mm wide, with nested wall panels (with openings) and floor panels.

#### Transportation
- Transport limits are generally **equal to or more restrictive than producer's maximums** → crucial for floor heights and panel sizes. Oversize permits possible but expensive; avoid.
- Rule of thumb: stay within **semi-trailer 13.6 × 2.45 × 2.7 m** and **mega-trailer 13.6 × 2.45 × 3.0 m** (L × W × H). Diagram p. 52: vertical load in mega trailer (panel standing, 3000 mm high), horizontal load in semi trailer (panels stacked flat, 2700 mm).
- Diagram p. 54 — dimensional system: *Optimized* (all panels type "a"), *Systematized* (few types a/b/c), *Non-Systematized* (every panel different). Establish a dimensional system for efficient, easily constructable buildings.

#### Wall
- Thickness determined by **imposed load** and **required fire resistance class** (both depend on use and number of floors). Thicker lower-floor walls possible but not necessarily economical.
- **3–8 floor housing: wall thickness 140–220 mm.**
- Panel height normally = master panel width ≈ **3 m**. For balloon-frame structures, service cores and communication shafts panels can be used longitudinally, max height ≈ **16 m**.

Common applications (p. 55):

| Application | Description | Use |
|---|---|---|
| **Longitudinal in Balloon** | Wall panels continuous over several floors (boards vertical), floors hung between | Best for up to 3-storey buildings |
| **Transverse in Platform** | One-storey wall panels, floor slab laid on top, next wall on the slab | Mostly used in multi-storey buildings |
| **Longitudinal in Core** | Tall continuous panels forming stair/lift core | Different building types, for more stability and workability |

#### Slab
- Thickness determined by **span** and **acoustic design**.
- Basic CLT slabs span **up to 7 m**; **up to 9 m** with reinforcement (glulam ribs or concrete).
- **3–8 floor housing: slab thickness 200–260 mm.**
- Diagram p. 56: ribbed CLT panel — LVL/glulam beams glued under (open ribs) or sandwiched (closed box) to span further.

#### Roof
- Thickness determined by **span** and **snow load**.
- CLT roofs usually span **up to 7 m**; reinforceable like slabs.
- **3–8 floor housing: roof thickness 140–180 mm.**

#### 3D-Modules
- Determining factor: transportability to site (route limits, dense urban areas).
- Stable modules may be transported larger than planar elements: **up to 4.15 m wide, 4.5 m high incl. trailer, 30 m long incl. truck**. Larger with escort/road blocks/route approval.

### Dimensional Tables and Library of Elements

- Preliminary dimensions for more-or-less **pure CLT structural systems** (differ for hybrids), **3–8 storey residential buildings in Sweden**, Swedish regulations, Swedish-market products. Same parameters used in the Grasshopper script and Revit file.
- CLT industry lacks a common system of dimensions; each producer has its own handbook. Data compiled from all Swedish producers + interviews with a mass-timber construction engineer.
- Scheme adapts to the choice of **light or heavy floor superstructure** — this choice affects wall dimensions too.
- **"These dimensions are only intended as an assistance for the preliminary stages and can not replace a full static calculation."**

Legend: CLT thickness shown in red in the source (here in **bold**).

#### Floor Slabs (p. 59)

**CLT with light superstructure** (top→bottom):

| Thickness | Layer |
|---|---|
| 15 mm | Flooring |
| 2×13 mm | Floor gypsum |
| 22 mm | Chipboard subflooring |
| 220 mm | Acoustic floor with insulation |
| **200 / 240 mm** | **CLT** |
| 15 mm | Fire protect board / gypsum |

**CLT with heavy superstructure** (top→bottom):

| Thickness | Layer |
|---|---|
| 15 mm | Flooring |
| 80 mm | Cast concrete |
| – | Moisture proof membrane |
| 20 mm | Acoustic mat |
| **220 / 260 mm** | **CLT** |
| 15 mm | Fire protect board / gypsum |

**CLT Dimensioning Table for Floor Slabs**

| Span (m) | Light — CLT (mm) | Light — Total (mm) | Heavy — CLT (mm) | Heavy — Total (mm) |
|---|---|---|---|---|
| < 5 | **200** | 498 | **220** | 350 |
| 5–7 | **240** | 538 | **260** | 390 |

#### Exterior Walls (p. 60)

**Exterior wall clad with Wood Panels** (outside→inside):

| Thickness | Layer |
|---|---|
| 22 mm | Vertical facade panel |
| 25 mm | Batten |
| 27 mm | Counter batten |
| – | Wind barrier |
| 200 mm | Insulation |
| **140–200 mm** | **CLT** |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

**Exterior wall clad with Bricks** (outside→inside):

| Thickness | Layer |
|---|---|
| 108 mm | Facade brick |
| 40 mm | Ventilated cavity |
| 30 mm | Wind resistant sheathing |
| 200 mm | Insulation |
| **140–200 mm** | **CLT** |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

**CLT Dimensioning Table for Exterior Walls**

| Floors (num.) | Light floor — CLT (mm) | Light — Total Panel (mm) | Light — Total Brick (mm) | Heavy floor — CLT (mm) | Heavy — Total Panel (mm) | Heavy — Total Brick (mm) |
|---|---|---|---|---|---|---|
| I–III | **140** | 442 | 546 | **160** | 462 | 566 |
| IV–VI | **160** | 462 | 566 | **180** | 482 | 586 |
| VII–VIII | **180** | 482 | 586 | **200** | 502 | 606 |

#### Partitioning Walls (p. 61)

**Partitioning Wall with Single CLT** (side→side):

| Thickness | Layer |
|---|---|
| 15 mm | Fire resistant gypsum board |
| 13 mm | Gypsum board |
| **120–180 mm** | **CLT** |
| 40 mm | Ventilated cavity |
| 70 mm | Insulation + studs |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

**Partitioning Wall with Double CLT** (side→side):

| Thickness | Layer |
|---|---|
| 15 mm | Fire resistant gypsum board |
| 13 mm | Gypsum board |
| **80–110 mm** | **CLT** |
| 170 mm | Insulation |
| **80–110 mm** | **CLT** |
| 13 mm | Gypsum board |
| 15 mm | Fire resistant gypsum board |

**CLT Dimensioning Table for Partitioning Walls**

| Floors (num.) | Light — Single CLT (mm) | Light — Single Total (mm) | Light — Double CLT (mm) | Light — Double Total (mm) | Heavy — Single CLT (mm) | Heavy — Single Total (mm) | Heavy — Double CLT (mm) | Heavy — Double Total (mm) |
|---|---|---|---|---|---|---|---|---|
| I–III | **120** | 286 | **80+80** | 386 | **140** | 306 | **90+90** | 406 |
| IV–VI | **140** | 306 | **90+90** | 406 | **160** | 326 | **100+100** | 426 |
| VII–VIII | **160** | 326 | **100+100** | 426 | **180** | 346 | **110+110** | 446 |

#### Roof (p. 62)

**Roof clad with metal** (outside→inside):

| Thickness | Layer |
|---|---|
| 50 mm | Seamed metal roofing |
| 1 mm | Underlayment paper |
| 22 mm | Tongue and groove board |
| 25 mm | Ventilated cavity |
| – | Wind barrier |
| 200 mm | Insulation |
| – | Vapour barrier |
| **140–180 mm** | **CLT** |
| 13 mm | Gypsum board |

**Roof clad with tiles or shingles** (outside→inside):

| Thickness | Layer |
|---|---|
| 80 mm | Shingle/tile roofing |
| 25 mm | Batten |
| 25 mm | Counter batten |
| 1 mm | Underlayment paper |
| 22 mm | Tongue and groove board |
| 25 mm | Ventilated cavity |
| – | Wind barrier |
| 200 mm | Insulation |
| – | Vapour barrier |
| **140–180 mm** | **CLT** |
| 13 mm | Gypsum board |

**CLT Dimensioning Table for Roofs**

| Span (m) | Snow Zone 1–3.5 — CLT (mm) | Total Metal (mm) | Total T/S (mm) | Snow Zone 4.5–5.5 — CLT (mm) | Total Metal (mm) | Total T/S (mm) |
|---|---|---|---|---|---|---|
| < 5 | **140** | 451 | 531 | **160** | 471 | 551 |
| 5–7 | **160** | 471 | 551 | **180** | 491 | 571 |

(T/S = tiles/shingles. Snow zones are Swedish snow-load zones in kN/m².)

---

## 06 Postface — selected references

Technical references used for dimensioning (full list pp. 66–69):
- Bergström & Fröbel, *The CLT Handbook: CLT structures – facts and planning*, Svenskt Trä, 2019.
- Exova BM TRADA, *Cross-laminated Timber: Design and Performance*, 2017.
- Norman, *Structural Timber Elements: a Pre-scheme Design Guide*, 2nd ed., TRADA, 2016.
- Crawly, *Cross Laminated Timber: A design stage primer*, Routledge, 2021.
- Zumbrunnen, *Pure CLT – Concepts and Structural Solutions for Multi Storey Timber Structures*, IHF, 2017.
- Waugh Thistleton Architects, *100 Projects UK CLT*, 2018.
- Producer brochures: Mayr-Melnhof (MM Crosslam), Stora Enso, Hasslacher, KLH, Setra, Leno (ZÜBLIN), Martinsons.
- Esbjörnsson, Magnusson & Ford, *URBAN TIMBER*, Chalmers, 2014.
- Deplazes, *Constructing Architecture*, Springer, 2005.

Photo credits: Setra Group (Preschool in Surbrunnshagen, Falun; Vallaskolan, Sala — CLT interiors/stairs on pp. 23, 35, 49, 51).

---

## Figure index

| Page | Figure | Content |
|---|---|---|
| 7 | Proposed workflow | Brief → Schematic → Developed → Detailed → Construction; Handbook / Grasshopper / Revit outputs |
| 17 | Photos | Clear-cut plantation (Bollnäs) vs 85-year Douglas fir under CCF transformation |
| 26 | 10 Good Reads | Literature list |
| 31 | Photos | LUMA Arles (Gehry) vs Centre Pompidou |
| 37 | Panel system vs 3D-module system | Two buildings under construction with trucks delivering panels vs modules |
| 39 | Variations of structural solutions | 6 systems: plan + axon + characteristics + storey range |
| 41 | Two common foundations | Concrete ground floor vs concrete basement under CLT block |
| 42 | Linear → planar | Lumber / laminated panel / CLT; log / platform frame / mass timber |
| 43 | Surface finish qualities | Three knot grades |
| 44 | Common types of openings | Wall elevation with max/min dims; CNC-routed / slab support / lintel support |
| 45 | Well-designed envelope | Roof-wall section; airtightness, insulation, breathing zone, rain protection |
| 46 | CLT floor slab types | Slab / ribbed / CLT-concrete composite |
| 47 | Roof types in CLT | 9 section diagrams |
| 49 | CLT stairs | Photo |
| 52 | Master panel & dimensional limits | Room from panels; 16000 × 3000 master panel; semi/mega trailer |
| 54 | Dimensional system | Optimized / Systematized / Non-Systematized |
| 55 | Transverse/longitudinal applications | Balloon / Platform / Core |
| 56 | Ribbed CLT panel | Open-rib and box sections |
| 57 | CLT 3D module | 4.15 × 4.5 × 30 m transport limits |
| 59–62 | Build-up library | Floor, exterior wall, partition wall, roof sections + dimensioning tables |

---

## Summary for procedural modelling

Rules distilled for generating a CLT panel building (3–8 storey residential, Swedish context):

1. **Choose system.** Default to a **Panel System** (platform framing: one-storey transverse wall panels, slab on top, repeat). Honeycomb (walls line up on every floor, 6–16 storeys) or Parting Wall (only cores, exterior and apartment-parting walls load-bearing, must line up, 4–12 storeys). Add a **concrete podium/ground floor** under the CLT.
2. **Panel envelope.** Every element must fit a master panel **≤ 16 m × 3 m × 350 mm** and transport **≤ 13.6 × 2.45 × 3.0 m** (so wall panel length ≤ 13.6 m in practice, height ≈ 3 m storey; slabs ≤ 13.6 m long strips ≤ 2.45–3 m wide). Keep panel widths uniform; use a dimensional system (few panel types).
3. **Walls.** Thickness 140–220 mm; pick from the tables by storey count and floor type (e.g. exterior 140/160/180 mm for I–III/IV–VI/VII–VIII with light floors; +20 mm for heavy floors). Partition (apartment-separating) single CLT 120–180 mm or double 80+80 … 110+110 mm with 170 mm insulation. Balloon-frame/core panels may be up to 16 m tall.
4. **Openings.** Cut openings ≤ ~1.5–2 m wide with piers ≥ 300 mm at edges, ≥ 200–600 mm between; larger openings need lintel or slab support (separate panels).
5. **Slabs.** Two-way panels on two supports; span ≤ 7 m plain (200 mm <5 m, 240 mm 5–7 m light; 220/260 mm heavy), ≤ 9 m ribbed/composite; 200–260 mm thick. Shaft holes can be cut freely.
6. **Roof.** 140–180 mm (140/160 mm for <5 / 5–7 m in low snow zones; 160/180 mm in high snow zones); span ≤ 7 m plain; flat, mono-pitch, double-pitch (panels leaning on each other for small spans), or with ridge beam/truss/wall for larger spans; folded plate possible.
7. **Layers.** Exterior wall total ≈ 442–606 mm (CLT + 200 mm insulation + cladding); floor total ≈ 350–538 mm; roof total ≈ 451–571 mm — use the build-up tables above for exact layer stacks.
8. **Stairs/cores.** CLT cores (longitudinal panels) for stability; CLT stairs from offcuts.
