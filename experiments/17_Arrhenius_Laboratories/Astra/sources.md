# Research sources — Arrhenius Laboratories

## 0. Verdict per question

| Topic | Verdict | Number / rule for the model |
|---|---|---|
| Applicable direct dimensions or figures for the concrete structure | partly covered | The manuals index is timber-focused. *Architect's Handbook of Construction Detailing*, Chapter 1, lists precast spandrels, beams/double tees, panel tolerances, panel size/configuration, connections and floor/beam erection tolerances (printed pp. 22–49; PDF pp. 40–67), but explicitly supplies no structural sizing, span tables or load calculations. Use the concrete topology from the brief/HIC; do not transfer timber member rules. |
| Image 08 bay and section counts | covered | Plan: 19 longitudinal north–south bays and 6 east–west bays (20 and 7 grid stations). Section/photo reading: ground plus four upper occupied levels = 5 visible window bands. The HIC text says “four-storey”; the supplied plan/section and photo 06 govern, as recorded in the concept on 2026-09-16. |
| Independent scale calibration and absolute dimensions | partly covered | No reliable independent calibration is available: image 08 has no scale bar, and people/lamp objects in photographs are oblique or too distant to transfer a plan scale. Treat all absolute dimensions as designer estimates: 6.0 m longitudinal module, 9.0 m transverse module, 54.0 m × 114.0 m envelope, 3.6 m storey height. These preserve image ratios; they are not surveyed values. |

## 1. Source → rule → number

| Source | Rule / observation | Number in model (datum) |
|---|---|---|
| `concept.md`, §1; image 08 plan (`input/Arrhenius Laboratories 08.png`) | Two long wings linked by shallow north and deeper south links; plan station count is 20 north–south and 7 east–west. | 19 equal longitudinal bays and 6 equal transverse bays, measured between grid stations. |
| `concept.md`, §1; image 08 section and photo 06 (`input/Arrhenius Laboratories 06.png`) | Occupied section reads ground + four upper levels; photo 06 visibly repeats five horizontal window bands. | 5 occupied levels; plant remains above and is not a sixth occupied floor. |
| Visual-reference procedure, image 08 | A plan without a scale bar supplies topology and ratios, not absolute metres. | No external scale constant; 6.0 m × 9.0 m modules and 54.0 m × 114.0 m envelope remain designer estimates. |
| Visual-reference procedure, image 06 | A person can calibrate only when its height and image plane are usable; the visible person is oblique, distant and not on the facade datum. | No person-based calibration adopted; no absolute façade dimension is source-backed. |
| *Architect's Handbook of Construction Detailing*, Ch. 1, §§1-10–1-23 (printed pp. 22–49; PDF pp. 40–67) | Precast concrete envelope and erection/detailing conditions are represented, but this reference does not provide member sizing or spans. | No concrete member dimensions imported. Model’s concrete proportions are visual/design estimates and require engineering validation. |
| HIC, “Carl Nyrén > Arrhenius Laboratories” (2026-09-09) | The kit of parts comprises an outside pillar, post-tensioned beam, floor slab, spiral stair and structural façade plate; the skin is insulated precast sandwich panels with horizontal wood-framed windows. | Preserve external columns, post-tensioned beam/slab logic, structural sandwich-panel facade and timber windows. No source dimensions. |

## 2. Figures and snippets consulted

| Source | What it settles | Snippet |
|---|---|---|
| `input/Arrhenius Laboratories 08.png` | Plan topology, station/bay counts, two wings, two links; lower drawing gives section levels. | [`references/reference_image08_plan.png`](../references/reference_image08_plan.png), [`references/reference_image08_section.png`](../references/reference_image08_section.png) |
| `input/Arrhenius Laboratories 06.png` | Repeated exterior columns and corbels, horizontal spandrels, five visible window bands; perspective scale is not independently calibratable. | [`references/reference_image06_facade.png`](../references/reference_image06_facade.png) |

## 3. External material

**HIC article:** [Carl Nyrén > Arrhenius Laboratories](https://hicarquitectura.com/2026/09/carl-nyren-arhenius-laboratories/) (retrieved 2026-09-16; direct fetch failed, indexed page text used after authorized site-restricted search). The article describes a prefabricated system of exterior pillars, post-tensioned beams, floor slabs, spiral stairs and structural façade plates; insulated precast sandwich panels carry horizontal fixed/operable wood-framed windows. It describes two north–south wings linked by two narrow east–west elements around a narrow outdoor courtyard, and a skylit two-storey room inserted into that courtyard. It calls the building four-storey, which conflicts with the supplied section/photo count; the latter governs this model.

No broader web search was used. HIC material supplies topology and material relationships, not dimensions.

## 4. Not covered / recommendations

- No consulted manual supplies a direct Arrhenius concrete bay, column, beam, slab, sandwich-panel or corbel dimension. Keep those as explicit visual/design estimates and do not cite timber tables for them.
- Hidden foundations, reinforcement, post-tensioning anchorage and lateral-system design remain unverified. The concept’s inferred cores/walls may be modelled diagrammatically only.

## 5. Contradictions and resolution

- HIC says “four-storey”; image 08’s section and photo 06 show five occupied window bands. Per the coordinator’s 2026-09-16 ruling and the concept, use ground + four upper levels and do not invent a sixth occupied level.
- The plan has no scale bar and photographs do not yield a transferable calibration. Preserve counts/ratios, while labelling 6 m, 9 m, 54 m, 114 m and 3.6 m as designer estimates.
