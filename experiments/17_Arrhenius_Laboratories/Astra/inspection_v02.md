# Inspection v02

## Summary

The standard frozen-model check reports 31,149 members, zero penetrating pairs above 1 mm, and zero floating members at 2 mm. Independent ground and upper-storey reviews confirm the open courtyard, partial northern insert, east passage, five occupied bands, exterior columns/corbels, repeated facade members, and four open curved stair stacks. The v01 court-covering and orphan-landing defects are visually resolved.

The version is **not converged**. The required 1.20 m landing exits and continuous routes around perimeter-side landings remain open; a clean overlap/contact check and adequate vertical headroom do not establish usable horizontal circulation. Exact bearing areas and complete load paths require the Designer's structural review. Reference proportions and counts within 5% require phase 2 comparison.

## Numeric evidence on the frozen geometry

- `render_v02.log` and `experiment_17_astra_v02_blender_pairs.txt`: standard 31,149 / 0 pairs / 0 floating.
- `headroom_v02.txt` and `headroom_v02_final.log`: 512 convex usable tread/landing regions, minimum vertical clearance 2.700 m, zero violations below 2.10 m. This covers the stated usable polygons; it does not prove exit widths or regulatory compliance.
- `rim_contacts_v02.txt`: all 16 raised stair rims have actual contacts with retained beam/header members under the standard 2 mm SAT-gap predicate. This confirms geometric contacts, not joint strength or minimum bearing area.

## Independent parts

- [Ground storey](inspection_v02_ground.md): south sequence, courtyard/site and entrance; grade route and material transmission require closer evidence.
- [Level 1, z3.6](inspection_v02_level1.md): courtyard insert, stair connection and internal frame; circulation and supporting details remain unconfirmed.
- [Level 2, z7.2](inspection_v02_level2.md): long facade and transverse section; Workbench does not establish transmission.
- [Level 3, z10.8](inspection_v02_level3.md): stair stack and rim detail; precise widths, bearings and continuity remain builder/Designer checks.
- [Level 4, z14.4](inspection_v02_level4.md): top occupied storey and roof review.

## Supplementary findings and handoff

`routes_v02.txt` records a 50 mm grid diagnostic built from the actual frozen floor/landing faces and actual convex obstacle sections 50 mm above floor. A 1.20 m disc has 271 valid landing centres on west level1, but its reachable component has only 277 cells and does not reach the x9 corridor. West level4 has 210 valid landing centres and a component of only 210 cells, also disconnected. Higher obstacles are omitted optimistically. The sampled diagnostic supports a real circulation defect at the outward-facing landings; it does not claim a continuous clearance proof or code compliance. R15 and R18 fail this review and require a new version.

Supplementary Workbench views28-31 are complete. View29 independently confirms the narrow facade-side landing situation. View30 still does not make the west office/corridor/laboratory organization legible; this is an unresolved evidence issue, not proof that every partition is absent. A horizontal near-plane cut leaves vertical wall edges without solid section caps, which may contribute. R17 remains open.

Cycles views12/15/28 are complete with explicit concrete/timber/metal/glass collection roles; `render_v02_cycles_muted.log` ends DONE. Files use the suffix `_muted_none_no_foundation.png`. The ground Inspector independently confirms visible transmission in the south glazing, courtyard insert skylight/east screen and enclosed stair: interior columns, flights and rails remain legible. Materials remain distinguishable in these views. R20/R26 are satisfied for the required representative south/court/stair subset; this is not a pane-by-pane assertion across the whole building. Initial white-palette view12 is a superseded presentation diagnostic. No material render changes model geometry.

View31 independently shows a stepped grade route beside the insert and no visible terrain penetration into occupied volume. Exact retaining continuity and grade dimensions remain unverified, so R14 is not fully closed.
