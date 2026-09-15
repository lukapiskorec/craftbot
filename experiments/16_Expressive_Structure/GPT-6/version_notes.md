# Experiment 16 version notes — GPT-6

## v01 — phase 1, 2026-09-14

Implemented the released 3.000 × 3.000 × 6.000 m clear room with one 0.900 × 2.100 m entrance, two open high clerestories, flat red vertical boarding and a level timber ceiling. Seven transverse frames carry paired pale timber chords, red web triangles, varying outer-column profiles and a fully boarded faceted roof. The geometry starts from `tools/experiment_template.py` and uses `craftbot_lib`, `geometry2d`, `planes` and `framing`; no shared toolkit was changed.

The crossed ground mat includes the Designer-approved continuous sole runners within its upper layer, z=-0.060..-0.024. Transverse sleepers butt to those runners, with lower longitudinal sleepers directly below their centerlines. A ripped edge slat carries both entrance-jamb plies. The doorway header has 90 mm seats. Side-wall rails are ripped to the specified 31 mm attachment gap; end rails terminate against the inner-chord faces. Wall butt joints stagger on rail heights and individual wall boards are at most 3.000 m long.

Column-chord turns use complementary mitres. Roof chords are split at web nodes; their upper faces bevel to the additive roof facets. Short B roof boards span adjacent 0.500 m frame stations and meet on complementary vertical facet boundaries. Ceiling boards are face-fixed to the lower chords: concealed fixings carry their gravity load; the boards do not bear on the tops of members above them.

Longitudinal ties and end-bay diagonals connect the transverse frames. Roof-plan crossed braces occupy separate 36 mm layers between the lower-chord faces. Ground-plan diagonals fit between the crossed sleeper network in its two thickness layers. These members name the lateral load path; boarding alone is not called a diaphragm, and the concealed connections remain undesigned.

### Verification

- Final rendered model: **2,101 members, 0 penetrating pairs >1 mm, 0 floating members at 2 mm contact tolerance, 0 overlap families**.
- No ignored contact families and no changed check tolerances.
- Initial unrendered preflight: 2,031 members, 86 pairs, 0 floating. Its two causes were longitudinal ties crossing column rungs (70 pairs) and longitudinal diagonals crossing transverse column webs (16 pairs). Fitting these members to the web faces removed both causes; the segmented ties add 70 members. Both preflights occurred before the first render, so there is only one rendered v01.
- Script assertions check clear room and entrance volumes against every member's bounds, exact room ratio, frame spacing/count, clerestory limit, roof-facet count, declared catalogue/material, floor support spacing, sole/support centerline alignment, header seats and rail spacing.
- The full renderer ran successfully in Blender 4.3.2; all views **01–19** were rendered. Views include four orbits, top/front/east elevations, frame-only, from below, room section, roof profile, heel, layered column node, base, entrance, roof boarding, roof-plan bracing, mat underside and interior front.
- Saved model: `experiment_16_gpt6_v01_blender.blend`; pair report: `experiment_16_gpt6_v01_blender_pairs.txt`. The version is immutable after these renders.
- Closeout's textual view-schema check initially missed the valid frame-only view because it recognizes only a double-quoted inline hide list or a variable named `COVER`. View 08's identical hide values were inlined using double quotes; camera, visibility and rendered view identity did not change. No rerender was necessary.

### Bearing audit beyond the contact check

**R-16 remains open.** A horizontal cut through each sloping outer-column foot produces a horizontal width of **90.008–91.505 mm**, against the 90.000 mm sole/support width. The maximum unsupported edge is **0.753 mm on each side**. The contact check correctly reports contact but cannot prove full footprint bearing. The next version must add adjacent ripped S sole/lower-support strips with fitted transverse-mat cuts, or fit a local foot-end bevel within the S stock. Preserve the released column profile, mat datums and clear-room dimensions.

### Inspection and requirements

The fresh single-room Inspector reviewed all 19 views and reported no clear major missing geometry, unintended envelope void, misplaced member or floating member. The room, entrance, upper light, seven frames, layered chords and expressive roof are visually confirmed. Detailed observations are in `inspection_v01_room.md`; the merged result and Builder dispositions are in `inspection_v01.md`.

R-14, R-15, R-21, R-22 and R-23 contain details that cannot be measured or seen fully in these renders. Their generation rules, dimension chains, fitted-plane construction and named ceiling face fixing supply the Builder evidence; there is no contrary visual finding. The requirement checkboxes now record **26 of 28 satisfied**: R-13 awaits phase-2 reference comparison, and R-16 remains open. Thus **phase 1 is not converged**. No other visual correction was requested for v02.

### Scope and evidence limits

CMHC board-thickness examples and the FRIM slender-truss drawing are precedents, not capacity evidence for this assembly. The 6 m slat columns are outside the cited prescriptive stud cases; FRIM plywood gussets do not validate the modeled paired-slat joints. No plywood, metal shoes, glazing, concrete or invented heavy beams are modeled. The low threshold replaces the reference stair, the usable doorway replaces its unusually low aperture, and the exact 2:1 clear height follows the user's brief.

This is a pavilion with open high clerestories. Structural adequacy, fastener and connection design, uplift/overturning anchorage, weatherproofing, durability, fire, soil bearing and moisture separation are not verified. Sections are plausible visual propositions, not calculated. These limitations do not waive geometric bearing or inspection findings.

### Next version and Designer questions

1. Correct the quantified R-16 foot-seat deficit with an in-catalogue local assembly detail; the two alternatives above preserve the design. No scope change is requested.
2. No additional visual defects were identified. Recheck the base close-up, full numeric model and required full phase-ending views in a fresh v02; do not overwrite v01.

No open design-authority question at this stage. Usage/context statistics are not exposed to this Builder and are not estimated.

## v02 — phase 1 foot-bearing correction, 2026-09-14

Copied the immutable v01 script and corrected R-16 with fitted foot-end bevels. Each sloping first chord segment has two additional cut planes: they run from the edges of the 90 mm horizontal seat to the original stock edges 90 mm above that seat. Above this short end detail the original chord profile remains. The cuts remove material from the S36x90 blank, keep every solid convex, and retain the fixed column centerlines, room dimensions, sole runners and ground-mat datums. No support strips or other members were added. The alternative of adjacent ripped supports would require new mat cuts and more pieces; the fitted bevel resolves the local deficit directly.

### Verification

- **2,101 members; 0 penetrating pairs >1 mm; 0 floating members at 2 mm contact tolerance; 0 overlap families.** No ignored members or changed harness tolerances.
- A new assertion selects the four actual mesh vertices of each horizontal chord foot and checks that its full rectangle lies within both the sole-runner and lower-sleeper footprint. It also checks the support top levels and requires a full 90 mm seat. The 1 micrometre assertion tolerance accommodates Blender mesh precision; it is distinct from the overlap/contact tolerances.
- Test-first evidence: before the bevel was added, that assertion failed on `ColumnOuter_-1_00_-1_00` against `SoleRunner_00`. After the correction, all **56 foot faces** passed, with measured widths **90.000–90.000 mm**. The previous maximum 0.753 mm unsupported edge is removed.
- Full Blender 4.3.2 render completed with exit code 0; every stable view **01–19** was rendered. No view definition changed. The base is shown by views 14 and 18, with frame and underside context in 08 and 09.
- Artifacts: `experiment_16_gpt6_v02.py`, `experiment_16_gpt6_v02_blender.blend`, `experiment_16_gpt6_v02_blender_pairs.txt`, and 19 `experiment_16_gpt6_v02_blender_view_XX.png` renders. No changes to v01 geometry or shared tools were made by this Builder. Runner owns viewer export and close-out.

### Inspection and requirements

The fresh single-room Inspector completed all 19 views and found no missing member, unintended envelope gap, clearly floating member or new absence. Base view 14 shows seated feet without a visible gap; the small bevel itself is below reliable visual measurement, so the full-foot assertion supplies the exact support evidence. Frame, underside, heel, node, roof-board and bracing views show no regressions. Its saved report `inspection_v02_room.md` was complete before the final-message usage interruption; the continuation on 2026-09-15 merged it into `inspection_v02.md` without repeating renders or inspection.

R-16 is now checked. **27 of 28 requirements are satisfied, and phase 1 is converged:** 0 pairs, 0 floating, no open visual defect, and every phase-one requirement satisfied. R-13 alone remains pending for phase-2 reference comparison. Runner's `closeout_v02.md` records **8 passed, 0 failed**, including exported model, layers, all 19 renders and viewer screenshot.

### Scope and Designer questions

The named load path remains chord foot → continuous upper sole → directly aligned lower sleeper → grade. Full geometric bearing is verified; fastener forces, buckling, capacity, anchorage, soil/moisture design and weatherproofing remain unverified. The open clerestory pavilion and all v01 scope interpretations remain in force. Sections are a visual proposition, not calculated.

No open design-authority question. No shared helper promotion is proposed. Usage/context statistics are not exposed to this Builder and are not estimated.
