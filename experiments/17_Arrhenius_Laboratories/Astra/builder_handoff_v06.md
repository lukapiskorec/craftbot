# v06 Builder handoff — current candidate

## Identity and completed corrections

The frozen candidate has **29,976 meshes**, with generated/preflight SHA256 `523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416`. A fresh factory-startup build reproduces it exactly (`reproduction_v06.txt`). Historical v01–v05 geometry is preserved.

The candidate implements concept 9.1–9.7: 90° corbel rotation; removal of all 760 invented EdgeBeam objects before fitting; restored real beam/ledger connections; the open south side beneath the incline; removal of 122 ground/soil/base objects; and fixtures classification for all facade/skylight frame collections plus StairRim. The 10 local 50 mm bearing nibs are integral with actual corbels. No triangular glass was added.

The exact landing/wall fit restores only concrete outside actual corbel volumes. R39 is independently accepted: full landing underside coverage, separate 0.439993 m² lower and 0.050000 m² upper seats, 12 finite plate paths, and complete wall/structure section unions with actual bottom seats. No capacity equivalence is claimed.

## Current numerical evidence

- 866 ordinary beam seats at 0.140 m², eight reduced seats at 0.11375 m², and two independent core-ledger seats were recomputed. All 1,250 wings and 1,250 seats have shaft roots; minimum actual area is 0.359998741151 m².
- All 4,534 ordinary slab ends pass 120 mm; all 261 repaired perimeter ends pass their specified 200 mm seat. Foundation footprint seats, 22 local connections, eight core-base unions and 16 rim paths pass.
- The 45 integral insert interfaces have complete 13.874997615814 m² vertical faces and adjoining 400 mm support bands. The 67 horizontal insert cases remain a separate classification.
- All 48 continuous circulation envelopes pass. Sixteen CorbelSeat ceilings intersect four route envelopes, with actual minimum 2.0999996185302727 m within the existing 20 µm coordinate tolerance. The 368 stair regions separately have minimum 2.700 m.
- The retained terrace requires 184.089966431 m² underside support: 11.399926567 m² is actual concrete and 172.690039864 m² terminates at explicitly unmodeled earth. The separate 0.507056778 m² northern strip is the declared 30 mm cantilever.
- All 6,959 requested fixture objects classify correctly. Reclassification does not remove StairRim from the structural support audit.

## Open structural issue: court-facing south facade

The all-plane attachment graph excludes glass from support paths. It connects 3,630 of 3,660 panel pieces to actual primary construction, including all eight changed corner fragments. **Thirty CourtSouth panel pieces remain without a modeled primary connection.** They occupy five bays (indices 1–5) and six vertical bands. The panel inward face at y = 12.55000019 is 250 mm beyond the real slab edge at y = 12.30000019; the genuine beam face is approximately 350 mm away.

The same graph on frozen v05 establishes 24 inherited unresolved pieces in bays 1, 2, 4 and 5. Bay 3's six pieces formerly reached the old Y-projecting corbel through a timber head/jamb; the corrected rotation removes that path. The old example is `Panel_CourtSouth_3_0 → Window_CourtSouth_3_0_Head → Window_CourtSouth_3_0_Jamb0_ShoulderFit2 → CorbelWing_122_1_1`, with respective face areas 0.29800109, 0.00649983 and 0.00249995 m². These are actual contacts, not capacity calculations.

Evidence: `panel_roots_v06.json`, `panel_baseline_v05_for_v06.json`, `panel_root_gaps_v06.txt`. The initial axis-only screen in `connections_v06.txt` also flagged 38 pieces later resolved through actual sloped faces or existing terrace footings; it is superseded by the all-plane graph. No hidden or invented member has been added to resolve the remaining 30. Designer/Coordinator disposition is pending; overall structural convergence is **not** claimed.

## Final rendering and review status

All **51 Workbench images, four selected Cycles images and 30 capped drawings (85 total)** are independently reviewed and inventoried in `render_evidence_v06.json`. The original49-view Workbench set is retained;53 corrects the occluded landing camera and54 corrects the approach-slab layer presentation. One white-material trial is excluded. All presentation findings are closed.

The unmodified stock gate passes **29,976 members / 0 penetrating pairs at1mm / 0 floating at2mm**, with zero overlap families. `render_v06.log` and the canonical pairs file are actual evidence, not carried preflight claims.

Main Workbench/Cycles saved masters share hash `25c4743bc414e69436a7b18e84e6fc5535ae58651dd41d9913a78b3ee06e6f1a`; the detail master is `eb8c41148a212fc5e40a778760eb1142a3e661c1ba7963af4f7dcc1ea6bc20a9`. All local meshes and primary-support world vertices are exact. The measured transform bridge records only sub4micrometre tread/rail roundoff and all19 rendered tread underside unions pass. No duplicate whole-model checks were run.

Fresh and reused Luna Inspector attempts failed with the runtime thread limit. The Coordinator assigned one independent Designer/reviewer fallback who did not author or read v06 geometry code. All five storey reports, source comparison, presentation and layer reviews are merged in `inspection_v06.md`. Sources01/02/06/07 confirm the requested corrected relationships; the30-panel attachment defect is not waived.

Runner's final metadata rebake moves only the erroneously matched EntranceApproachSlab from fixtures to floors. Current viewer JSON SHA256 `3418977bac8e7bb2913c6d7eef4ee381396477601414db8d4cffdc6956d23a80` has29,976 elements, zero unclassified objects and six taxonomy checks passed. Geometry was not re-exported for that correction.

`version_notes.md` now contains the full v06 entry. Component requirements are refreshed with actual v06 evidence. R22/R30/R32/R34/R38 and final close-out remain open for the CourtSouth repair. **v06 is not converged.** A read-only60-location connector probe and thin-plate/web proposal are available for the independently authorized next version; no v07 geometry exists here.
