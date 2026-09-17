# Independent structural review - v07 bracket evidence

## Disposition

**Concept10/R40 passes independent actual-evidence and final visual review.** All sixty discrete assemblies connect their thirty intended panels to real slabs and Beam/GradeBeam seats. The previously missing CourtSouth paths are geometrically closed. Final whole-model diagnostics, all91 images, rendered identity correspondence and exported fixtures verification now pass. This is architectural connection plausibility, not calculated anchor, weld, steel, concrete or foundation capacity.

The Coordinator assigned this review to the former v05 Builder as independent Designer fallback. This reviewer specified concept10 but did not author v07 or read its geometry code. Evidence consists of actual saved-model reports and independently viewed final images, not implementation assertions alone. The initial numeric review was followed by all nine visual subsets under the recorded one-reviewer exception.

## Identity and scope

Reviewed `preflight_v07.blend`: **30,156 meshes**, SHA256(names/world vertices at one micrometre) **6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed**. This identity appears in `delta_v07.json`, `brackets_v07.json`, `panel_roots_v07.json`, `public_routes_v07.txt` and `route_envelopes_v07.txt`.

`delta_v07.json` compares against v06 preflight hash523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416: all **29,976 existing meshes** retain exact local/world vertices, faces, transforms and collections; removed=[] and changed=[]. Exactly **180 new steel pieces** are added, all fixtures, comprising sixty root-plate/web/receiving-plate assemblies. The local SAT check covers every addition against all meshes and reports no penetrating pair. The separate final standard whole-model gate also passes:30,156 members, zero penetrating pairs, zero families and zero floating members.

This exact retention supports carrying forward the named v06 concrete bearing, slab/perimeter, rim/header/core, insert, R39 and earth-boundary findings in `structural_review_v06.md`. The added brackets receive their own full interface and circulation tests below. V06 remains historically nonconverged; the repair belongs only to v07.

## Actual geometry and finite interfaces

`brackets_v07.json` contains sixty connections: ten each at ground and F3.60,7.20,10.80,14.40,18.00. Each of the thirty target panels receives exactly two. The measured centres are the ten authorized values21.20,22.70,24.20,25.70,27.60,28.60,30.20,31.70,33.20,34.70. Three-piece actual dimensions match the concept:100 mm-wide/10 mm-thick end plates,10 mm-thick central web across the230 mm clear plate gap;100 mm upper heights;150 mm ground plate heights and300 mm continuous ground web. Maximum measured dimension deviation from these nominal sizes is **2.136230469 micrometres**.

The root and receiving outer faces lie on the real slab/panel datums, nominal Y12.30/12.55. The representative ground report measures12.3000001907/12.5500001907. Its root plate occupiesZ-0.150000006..0, receiverZ0..0.150000006, and continuous web spans the complete300 mm vertical interval. Upper pieces occupy F-0.20..F-0.10 below walking tops. The current member family is `CourtFacadeBracket_{bay}_{band}_{side}_{Root|Web|Receiver}`; the naming differs from the illustrative concept name without changing construction.

The report evaluates both opposed faces of every interface, **240 physical interfaces /480 face-side evaluations**:

| Physical interface | Count | Nominal area, upper / ground | Largest reported uncovered area |
| --- | ---: | --- | ---: |
| Slab to root plate | 60 | 0.010 /0.015 m2 | 0.000000228882 m2 |
| Root plate to web | 60 | 0.001 /0.0015 m2 | 0.000000068665 m2 |
| Web to receiving plate | 60 | 0.001 /0.0015 m2 | 0.000000068665 m2 |
| Receiving plate to named panel | 60 | 0.010 /0.015 m2 | 0.000000228882 m2 |

These residuals are float32 boundary differences within the established20 micrometre coordinate allowance; they are not unreported physical holes or zero-width graph contacts. Nominal full-face coverage is accepted with that explicit tolerance. Web interfaces retain10-by100/150 mm finite dimensions. The two concrete ends are **vertical anchorage/shear interfaces**, not horizontal bearing seats. End anchorage and continuous weld action are declared construction inferences, not modeled bolt/rebar details.

## Root-to-primary-structure path

For each connection, `brackets_v07.json` separately measures the actual **100-by300 mm =0.030 m2 continuous slab strip** from the root toward the support line; all sixty have zero uncovered area. The slab's **100-by200 mm =0.020 m2 underside band** likewise has zero uncovered area. Its opposed actual Beam/GradeBeam top union covers the intended200 mm seat with maximum residual **0.000000019074 m2**. Named genuine support members are listed individually; the ground example is FloorSlab_0_2_Row2_2_0 on GradeBeam_2_0_2_0. No deleted EdgeBeam is credited.

The upper load path is panel -> receiving plate/anchorage -> welded web -> root plate/anchorage -> continuous retained slab -> transverse Beam -> corrected corbel -> shaft/pedestal/footing -> unmodeled earth. Ground assemblies use the real ground slab and GradeBeam/foundation. This topology preserves the approved beam/slab hierarchy and does not introduce a substitute longitudinal beam.

`panel_roots_v07.json` records **3,660/3,660 panels rooted; unresolved=[]** and expressly excludes glass. Each of the thirty repaired target panels has a bracket-first path. For example Panel_CourtSouth_3_0 reaches Receiver -> Web -> Root -> FloorSlab_1_2_Row2_6_0 through approximately0.010000029/0.001000022/0.001000022/0.010000029 m2 faces. The independent per-connection table proves both attachments per panel; a single graph path is not substituted for that two-connection test. Existing3,630 panel paths remain available. Other existing facade timber attachment assumptions are retained as inference; the new CourtSouth paths do not use timber or glass for gravity transfer.

## Routes, retained limitations and final gates

`route_envelopes_v07.txt` has **48 passing continuous envelopes**, no failures and no obstacle hits; `public_routes_v07.txt` reports failures=[] and retains the2.40 m doorway, constructed court/entry routes and explicit omitted-earth boundaries. New ground brackets do not obstruct these tested routes. Gallery headroom remains2.10 m, separate from the unchanged368 stair regions'2.700 m result. Exact baseline retention preserves the R39 landing/corbel/wall fit and the terrace's11.399926567 m2 concrete support,172.690039864 m2 omitted earth-bearing area and0.507056778 m2 intentional north cantilever. No new soil-contact claim follows from the added steel.

**No additional geometry correction is requested.** Final standard SAT/contact is30,156 members/0 penetrating pairs above1mm/0 families/0 floating within2mm. All55 Workbench,4 Cycles and32 capped images pass independent review, including upper/ground attachment details and source preservation. All180 additions export as fixtures; eleven taxonomy checks pass with zero other. R40 is accepted and Builder has closed its checkbox. On the Coordinator's explicit final reconciliation assignment, R22/R28/R30/R32/R34/R38 are also closed against this evidence. R31 remains Runner-owned. V06's nonconvergence is preserved historically.

`inspection_v07_identity.md` binds the complete evidence: all91 image SHA256 values and51 batch-copy identities independently pass. All five saved masters share hash1efe2518e65ac7d515c5fb795a9778603de1f95f6e026191dc32975ebde93ad0, distinct from preflight6c135010…. Every local mesh/primary support/new bracket is exact;29 retained tread/inclined-rail world changes stay within3.814697micrometres. The explicit narrow rounding exception is accepted on19/19 actual final rendered tread-seat unions, with the20micrometre seam allowance retained. No new hardware/support relies on this exception. Export hash2a074a8867df408bdd16b5c3a24f0d7d5177bbb9f7a2a1e126a8ce07c2cf26b3 is independently verified.

Capacity, eccentricity, anchors/embedments, weld sizes, reinforcement, local slab design, soil and durability remain unverified engineering details; face areas do not establish resistance. Gallery2.10m and stair2.700m headroom remain separate, as do actual terrace concrete support, omitted earth bearing and the intentional30mm cantilever. These limitations are retained, not waived by successful visual or contact checks.
