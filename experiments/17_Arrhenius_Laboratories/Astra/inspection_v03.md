# v03 merged independent visual inspection

Frozen model: **30,003 meshes; 0 penetrating pairs; 0 floating members.** Geometry SHA256: `3c85bdc6c1282389ab1659f8295bba9d183fde50345fd2ae74b3dec840fd2216`. Quantitative reports and generator reproduction identify this same snapshot. All 34 Workbench views and three muted Cycles views were reviewed across the five storey subsets, followed by readable actual-mesh plan supplements.

## Findings summary

1. **R09 OPEN: south upper facade mismatch.** Five intermediate front shafts/corbel stacks and exposed horizontal bands break the fascia/ribbon into six structural bays. Reference reading calls for a continuous upper enclosure with porch supports below. Preserve v03; correct envelope/support presentation in a new version after the Designer's handoff.
2. **R17 plan presentation resolved.** Capped plans32/33 show actual west offices/corridor/laboratories, asymmetric east cells, doorway gaps and ground courtyard gallery. The reviewer confirms readable representative topology; these drawings do not independently measure every clear width.
3. **R13 access presentation resolved.** Plan34 shows the west-wing room approach, enclosed link and insert doorway without an intervening wall. The two continuous actual-mesh insert routes use 1.40 m width and 2.10 m height. Separate face checks establish the recorded deck/ledger/beam/lintel contacts; images do not certify capacity.
4. Same-direction semicircular flights, opposite-side straight galleries, open wells, fine guards and retained rim/header members are visible on all occupied levels. Actual-mesh evidence separately passes twenty floor exits, twenty endpoint galleries and four upper loops at 1.20 m width, and all 368 headroom regions with a 2.700 m minimum.
5. Complete ring, courtyard, partial northern two-level insert, east passage, five occupied facade bands, 19 longitudinal/six transverse bays, exposed long-facade frame and sparse roof plant remain present. No extra whole storey or accidental court covering was observed.
6. Cycles12/15/28 show representative glass transmission. Cycles28 is too dark and distant for a strong comparison to the bright interior reference; improve a supplementary perspective/exposure in the next version. This is a presentation limitation, not grounds to alter the stairs.
7. Exact proportions within 5%, statutory compliance, retaining/diaphragm design, anchor forces and structural capacity remain unverified by this visual review. The eight reduced corbel seats retain their explicit capacity limitation. R22-R24/R28/R32 remain subject to formal review.

**Converged: no.** R09 is an actual unresolved geometry/source-fidelity issue. R30 cannot pass while it remains open.

## Reviewer independence and report references

Fresh Inspector threads and the original Designer thread were unavailable at the runtime thread limit. The Coordinator explicitly authorized the existing independent `/root/stair_exits` reviewer to inspect five storey subsets sequentially. This was one independent reviewer, not five independently spawned reviewers; no geometry scripts were read or changed. Each report records the runtime exception. Their capped-plan addenda supersede their earlier temporary plan-legibility reservations.

- [Ground](inspection_v03_ground.md): south facade, glazing, site/grade, insert and ground program.
- [Level1](inspection_v03_level1.md): stair/gallery, insert, courtyard and connection evidence.
- [Level2](inspection_v03_level2.md): long facade, frame, plan and corbel appearance.
- [Level3](inspection_v03_level3.md): stair/core galleries, rim framing and interior transmission.
- [Level4](inspection_v03_level4.md): upper approach, roof/plant, elevations and whole-building scope.

Numeric evidence: `route_envelopes_v03.txt`, `routes_v03.txt`, `headroom_v03.txt`, `supports_v03.txt`, `rim_contacts_v03.txt`, `reproduction_v03.txt`. Actual mesh-derived raster evidence: `plan_v03_32.png`, `plan_v03_33.png`, `plan_v03_34.png`, and twenty `plan_v03_route_<stair><floor>.png` crops. Workbench view numbers32-34 are separate north-gallery/south-gallery/insert-section views and should not be confused with these labelled plan numbers.
