# Brief as understood

Experiment 15 is a new design, not a reconstruction: a long, modern, open house in concrete, steel and glass on the sloped site at Koreni, with the terrain itself modelled so that the way the house meets the slope is visible in every view. Because it is an early-stage study, three variations of the house are developed side by side, and they must differ in how the building takes the slope (for example bridging over it, cutting into it, or stepping down it), not only in dimensions or finishes. Each variation is a complete model with its interior spaces (rooms, level changes, stairs, the fixed elements that define the plan) and its construction details (slab and wall thicknesses, columns, beams, glazing frames, footings and retaining walls where the house meets the ground). The site images and sketch diagrams in `input/` fix the slope, the orientation and whatever parti the sketches carry; the 43 reference images in `references/` are inspiration only, since the brief says to match them less and to develop a strong concept instead. Dropped: timber construction as the primary system (the manuals in `manuals/` are timber manuals and serve only for secondary timber elements and for general rules such as bearing and spans), furniture, landscaping beyond the terrain surface, and services.

## Materials overridden

- `references/reference_01.png` to `reference_43.png`: demoted from targets to inspiration by the brief. The comparison round of phase 2 compares the model against the sketch diagrams and the site images in `input/`, and against the concept's own rules, not against the reference photos.

## Ambiguities resolved

- "Three different variations": three complete houses, each with its own interior and details, on the same site. They differ in their section and slope strategy, which is a scope decision so that the variations are alternatives and not one design at three sizes.
- One script and one model per version holds all three variations, placed side by side on three copies of the same terrain strip with a fixed spacing, so that the overlap and contact checks, the viewer and the iteration slider cover all three at once. Interior views and sections are per variation.
- "Model the actual terrain": a terrain surface built from the contour and slope information in the site images and sketches, with the fall stated as a number in `concept.md`; where the site images do not give a number, the Designer states the assumption.
- "Construction details": modelled members and layers (slabs, walls, columns, beams, mullions, footings, retaining walls, parapets and roof build-up) with dimensions the Designer derives and labels as derivations; rebar, connections and waterproofing are not modelled.
- Materials: concrete for slabs, cores, retaining walls and footings; steel for columns, beams and glazing frames; glass for the long facades. Where a timber secondary element is used the timber manuals apply.
- Version limit: the default, 10 per phase.

## Status at pause, 2026-09-10

The user stopped the run after v04 (message in `input/experiment_15_prompts_fable.txt`). State on disk, for a later continuation:

- Phase 1 (build to the brief) ran v01 to v04. v04: 1296 members, 0 penetrating pairs, 0 floating, 49 views, 47 of 50 phase-1 lines ticked. Every version is closed out (`closeout_v01.md` to `closeout_v04.md`, all steps passing from v03 on) and exported to the viewer.
- Phase 2 started on v04 and was cut short by usage limits. Done: the structural review (design_notes.md "after v04: structural review", requirement lines R-51 to R-55; R-52 and R-55 ticked as built, R-51, R-53, R-54 open) and the rewrite of R-27 (A's lower box) and R-46 (C's L3 room order). Partly done: the comparison round; the Inspector's table is in `inspection_v04_comparison.md`, but the Designer had not yet carried it into `design_notes.md` and `requirements.md`, so R-50 is unticked.
- Not started: v05 (which carries R-27, R-46, R-51, R-53, R-54, the strip-window placement fix and the zone-list printout from `version_notes.md` v04), the rationale, the callouts, the run close-out and the transcript archive.

To continue: read `agent.md`, this file, `concept.md`, `requirements.md`, `design_notes.md`, `version_notes.md` and `closeout_v04.md`; have the Designer finish the comparison round from `inspection_v04_comparison.md`; then the Builder runs v05 onward under the phase-2 loop.

Wrapped up on 2026-09-11 at the same state: the design rationale (`experiment_15_fable_design_rationale.md`, section 3b carries the comparison table and the five unruled proposals, section 10 the open items), the callouts (`experiment_15_fable_callouts.json`, 15 callouts against v04), `closeout_run.md` and the transcript archive were written so the run is complete as a paused run. A continuation updates the rationale and re-runs the close-out.
