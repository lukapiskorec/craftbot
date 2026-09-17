# Experiment 17 — Arrhenius Laboratories

## Outcome

Final version **v05** contains **30,167 geometric elements**, with **zero penetrating pairs** above 1 mm and **zero floating elements** at 2 mm contact tolerance. Independent visual inspection and architectural structural review pass. Deliverables include 41 Workbench images, four Cycles images, 28 labelled mesh plans, the Blender model, generator and browser-viewer export.

## Brief as understood

Build a single-variation, faithful architectural model of the Arrhenius Laboratories building shown in the eight experiment input images, using the user-supplied HIC article to clarify the building's organization and construction. Preserve the visible forms, proportions, facade rhythm, material contrasts, exterior concrete structure, courtyard, and characteristic inclined entrance glazing. Represent the complete building to the extent established by the references; record inferred dimensions and unseen details as estimates. Detailed laboratory equipment and hidden construction assemblies are omitted where the references provide no evidence, so the model remains an architectural reconstruction rather than a claim of surveyed or engineered accuracy.

## Sources and fidelity

All eight supplied images govern the reconstruction: 01/07 establish the concrete member hierarchy; 02/05 the entrance and continuous south facade; 03 the stair/gallery relationships; 04 the courtyard insert; 06 the five occupied bands; and 08 the ring plan, bay counts, stairs and section. The [HIC article](https://hicarquitectura.com/2026/09/carl-nyren-arhenius-laboratories/) supplies material and spatial context. Its four-storey wording conflicts with the five visible bands in the supplied images; the images govern and the discrepancy remains recorded.

The complete building retains 19 longitudinal bays, six transverse bays, unequal end links, an open courtyard, a two-level insert and four semicircular stairs with straight galleries. Two measured gross drawing ratios differ by -1.923% and +3.964%; these are bounded comparisons, not validation of all dimensions.

## Versions

| Version | Main change or finding | Elements | Pairs | Floating |
|---|---|---:|---:|---:|
| v01 | Initial complete model; opening-domain defect | 18,828 | 85,230 | 2 |
| v02 | Corrected openings and junctions; two stair exits still fail | 31,149 | 0 | 0 |
| v03 | Source-correct stairs, galleries, room doors and insert access | 30,003 | 0 | 0 |
| v04 | Continuous south facade and genuine supported entrance; structural review finds support gaps | 29,876 | 0 | 0 |
| v05 | Corrected 261 slab ends, courtyard-stair support and terrace containment | 30,167 | 0 | 0 |

## Verification and limits

All 4,534 ordinary slab-end cases pass their bearing tests; the 261 corrected ends have 200 mm seats. Tests pass 48 continuous circulation envelopes, 28 public route/aperture cases and 368 stair-headroom regions, with 2.700 m minimum headroom. Independent review covers the final diagnostic and presentation views. The viewer shows the correct model and count without an error banner, and all exported objects match the generated and checked master snapshots at viewer precision.

Measured Blender transform rounding of at most 3.815 micrometres is documented separately from the generator's exact reproduction. Targeted rendered tread-support checks pass. No false equality of the distinct saved-model hashes is claimed.

Absolute dimensions, hidden structure and unseen layouts remain inferred. Guard infill, soffits and small fittings are simplified. Structural capacities, reinforcement, anchors, soil/retaining stability, accessibility and regulatory compliance are unverified. Eight reduced-width beam seats retain an explicit capacity limitation. There are no remaining identified geometry or visual corrections within the stated architectural scope.

## Deliverables

- Model: [experiment_17_astra_v05_blender.blend](experiment_17_astra_v05_blender.blend)
- Generator: [experiment_17_astra_v05.py](experiment_17_astra_v05.py)
- Exterior preview: [Cycles view 12](experiment_17_astra_v05_cycles_view_12_muted_none_no_foundation.png)
- Interior preview: [Cycles view 40](experiment_17_astra_v05_cycles_view_40_interior.png)
- Reasoning and evidence: [design rationale](experiment_17_astra_design_rationale.md), [structural review](structural_review_v05.md), [inspection](inspection_v05.md)
- All created/changed project paths, including historical versions, references, viewer files and shared edits: [file manifest](file_manifest.md)
- Viewer model: `viewer/models/17_Arrhenius_Laboratories/astra_v05.json`; shared updates: `viewer/models/index.json`, `tools/layers.py`.

Version close-out has eight effective required steps passed and zero unresolved failures; the canonical export timeout is retained alongside the verified direct-export recovery. Final run preflight passes all 13 checks. All 32 requirements are marked complete with scoped evidence.

Per-agent token/context/tool-call and monetary totals are unavailable in this runtime; no estimates are presented as measurements. No commit was made. Suggested commit message: `Add Arrhenius Laboratories experiment 17 Astra reconstruction`.

The final run close-out and transcript copy follow this prepared report; their actual outcome is recorded in `closeout_run.md`. Archival is the final tool action of the run.
