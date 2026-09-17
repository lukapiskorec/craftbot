# v04 merged independent visual inspection

Frozen model: **29,876 meshes, 0 penetrating pairs, 0 floating members**, SHA256 `8a02c4b9865c497bbd2d1af58a76140a978e0863a98ebd97a32ff63a26951657` (sorted names/world vertices at one micrometre). An independent full generator rebuild reproduces this identity. All 37 Workbench views, three standard transmission views and final perspective 40 are saved. The completed standard checks are recorded in `render_v04.log` and the final pair file.

## Findings summary

1. **R09 visual defect resolved.** Matched south views 06/12/13, transmission view 12, and support/corner details 35/36 show continuous metal fascia and recessed ribbon, restrained projection and closed returns. The concrete support line is concealed above the porch, not removed. The numeric comparison separately finds no changes in 14,056 specifically named frame/floor/core/stair/insert members; 57 bracket connection checks pass and minimum rail/corbel clearance is 30.00003 mm.
2. **R11 entrance corrected.** The actual-mesh entrance plan and Workbench 37 show the open porch-to-foyer portal and approach. The exact 2.40 x 2.40 m aperture, 1.20 m foyer-to-east-gallery route and 150 mm lawn step pass geometric tests. The paving has 3.60 m2 total support: 2.40 m2 fitted compacted base and 1.20 m2 retained grade beam. The doorway location and open movable-leaf state are explicit inferences.
3. **R14 stepped court route verified.** The insert/exterior stair is visually continuous. Actual walking strips cover the garden/path transition, all 20 rises, top landing, retaining-wall top and terrace, with 1.20 m width and 2.10 m height. No tested terrain volume enters the modelled occupied interiors. This is a stepped pedestrian route, not a step-free route or regulatory certification.
4. All five occupied levels retain the semicircular flights, straight galleries, open wells, guards, connected room/corridor topology, courtyard insert access and ring circulation. The exact 48 supported route envelopes pass; 368 walking regions retain minimum 2.700 m headroom. The insert's two access routes use 1.40 m width.
5. Long-side columns/corbels, precast bands, window rhythm, open courtyard, flat roofs and sparse plant remain legible. No missing major volume, unintended enclosure breach or out-of-site element was found by the reviewer.
6. **Final perspective 40** gives a bright, legible curved stair, gallery floor, void, overhead frame and genuine daylight through glazing. The core-doorway detail is not legible from this camera; it remains a narrow presentation limitation for the Designer's phase-2 review. Earlier perspectives 38/39 are retained detail trials. No geometry was altered to improve these images.
7. Section capacities, reinforcement, anchors, soil, retaining restraint and diaphragm forces remain unverified. The eight 0.065 m2 reduced corbel seats retain their explicit capacity limitation. Exact source proportions and the formal independent structural review remain phase-2 responsibilities.

**No actual visual defect remains in the assigned version review.** Standard numeric checks also pass. Formal phase-2 reference/structural review remains a separate gate; this visual report does not waive it.

## Independence and report references

A fresh `gpt-5.6-luna` Inspector was spawned with no inherited conversation. A second fresh storey Inspector failed with the runtime message `agent thread limit reached`. The Coordinator authorized sequential reuse of that one independent reviewer for all five storey subsets. These are five separate reports from one reviewer, not five independently spawned reviewers. The Inspector did not read geometry scripts. Its initially stale pending-view lines and several incorrect view labels were returned for correction; the final reports below supersede those statements.

- [Ground](inspection_v04_ground.md): south enclosure/projection, retained supports, entrance, insert and site.
- [Level 1](inspection_v04_level1.md): stairs, galleries, rooms and insert access.
- [Level 2](inspection_v04_level2.md): side frame, corbels, window rhythm and circulation.
- [Level 3](inspection_v04_level3.md): stair voids, guards, landings and exposed frame.
- [Level 4](inspection_v04_level4.md): upper bands, circulation, roofs and plant.
- [Interior perspective](inspection_v04_interior.md): Cycles 40 compared with source 03, including its doorway-legibility limitation.

Numeric evidence: `south_v04.txt`, `public_routes_v04.txt`, `route_envelopes_v04.txt`, `routes_v04.txt`, `headroom_v04.txt`, `supports_v04.txt`, `rim_contacts_v04.txt`, `reproduction_v04.txt`. Actual-mesh capped plans: `plan_v04_32.png` through `plan_v04_35.png` plus twenty `plan_v04_route_<W/E/N/S><0..4>.png` crops. These plan numbers are separate from the Workbench view numbers.
