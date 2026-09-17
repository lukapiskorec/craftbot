# Close-out of 17_Arrhenius_Laboratories Astra v07

Written by `tools/closeout.py` on 2026-09-17 13:27.

| step | result | detail |
|---|---|---|
| script exists | pass | experiments\17_Arrhenius_Laboratories\Astra\experiment_17_astra_v07.py |
| export to viewer | FAIL | [1/1] 17_Arrhenius_Laboratories/astra_v07.json ... FAILED  indexed 181 models / failed this run: 1  --- FAILED 17_Arrhenius_Laboratories/astra_v07.json TIMEOUT |
| layers baked | pass | baked viewer\models\17_Arrhenius_Laboratories\astra_v01.json baked viewer\models\17_Arrhenius_Laboratories\astra_v02.json baked viewer\models\17_Arrhenius_Laboratories\astra_v03.json baked viewer\models\17_Arrhenius_Laboratories\astra_v04.json baked viewer\models\17_Arrhenius_Laboratories\astra_v05. |
| layers audit: nothing in 'other' | pass | 0 elements in 'other' |
| index.json rebuilt | pass | indexed 181 models |
| view set complete | pass | frame-only, from-below and section views present |
| renders present | pass | 55 view PNGs |

6 passed, 1 failed.

## Supplemental recovery, provenance and actual viewer inspection

The canonical results above are preserved. Its exporter reached the known 120-second subprocess timeout. The completed direct factory-startup export in `export_v07_direct.log` passed with exit 0: **4,943 boxes + 25,213 meshes = 30,156 elements**, **7,453,180 bytes**. It executed `experiment_17_astra_v07.py`, including its local support modules; it did not load the later saved render master. No frozen geometry was changed during close-out.

The actual exported file is `viewer/models/17_Arrhenius_Laboratories/astra_v07.json`, SHA256 **2a074a8867df408bdd16b5c3a24f0d7d5177bbb9f7a2a1e126a8ce07c2cf26b3**. This hash remains unchanged after canonical close-out and exactly matches the Coordinator's browser probe. The actual-file layer audit reports zero elements in `other`; the index contains 181 models.

`fixture_layers_v07.txt` records **11/11 checks passed**. All 5,414 TimberFrames, 395 SteelFrames including 180 new CourtFacadeBracket pieces, 178 SkylightFrames and 1,152 StairRim members are fixtures. Every one of the 180 bracket names and its Facade/SteelFrames collection is checked against the complete expected family. Named examples `SouthInclineRafter_31_0` and `Window_East_5_3_Sill` are fixtures. The concrete `EntranceApproachSlab` is floors and all four concrete `RooflightSeatBeam` members remain frame.

### Distinct geometry identities with exact export-precision correspondence

- Generated/preflight geometry: `6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed`.
- Canonical standard-checked master and all four other saved Workbench/batch/Cycles masters: `1efe2518e65ac7d515c5fb795a9778603de1f95f6e026191dc32975ebde93ad0`.

The Builder's measured bridge records 93 changed transforms and 29 objects with changed world coordinates, with a maximum difference of 3.814697265625 micrometres. All local meshes, primary supports and the 180 new bracket pieces remain exact. The changed world coordinates are confined to pre-existing court treads and inclined glazing rails. All 19 actual rendered tread underside unions pass their recorded 20-micrometre float32 seam allowance. `render_identity_difference_v07.json`, `render_evidence_v07.json` and `render_support_bridge_v07.txt` retain the complete measured bridge. The two raw geometry hashes are not claimed equal.

Runner independently compared every object's actual exported coordinates against both `preflight_v07.blend` and the canonical `experiment_17_astra_v07_blender.blend`, using the exporter's five-decimal rounding. `export_saved_identity_v07.json` records **30,156 objects, zero missing objects and zero quantized-coordinate differences against either saved snapshot**. The existing JSON therefore represents both at its stored precision; no re-export or replacement screenshot was required.

### Viewer verification

The Coordinator ran the prepared probe outside the sandbox. `closeout_v07_viewer_probe.log` records the exact current JSON hash and byte size above, HTTP200 root/model readiness with byte equality, a fresh GUID profile, GPU enabled, Chrome exit 0 after 7.016 seconds, and owned-server cleanup. The HTTP log shows successful viewer/model/rationale/callout responses; only the irrelevant favicon returned 404.

**Actual screenshot inspection: PASS.** `closeout_v07_viewer.png` visibly identifies experiment 17 Arrhenius Laboratories, Astra, iteration v07 and **30,156 elements**. The expected elongated ring, courtyard, rooftop plant and south facade appear, with no red error banner. The screenshot's rationale predates the Coordinator's final document refresh; this capture proves correct model loading and is not presented as the final document revision. Runner launched no duplicate browser.

### Artifacts and acceptance

The accepted evidence inventory contains **55 Workbench images** (01-37 and 41-58), **four Cycles images** (muted 12/15/28 and interior 40), and **32 final plan/section drawings**: **91 accepted images**. The superseded `plan_v07_support_55_caption_initial.png` is retained separately and excluded from that count, as is the viewer screenshot. Actual filesystem inventory confirms these files.

The final unmodified stock gate reports **30,156 members / 0 penetrating pairs / 0 floating**. Independent final visual and structural review accepts the v07 correction. The former 30 unresolved CourtSouth panel attachments now have 60 discrete three-piece assemblies, with 240 measured interfaces, 60 continuous slab strips and 60 actual Beam/GradeBeam seats passing; all 3,660 panels have modeled primary paths. All 29,976 v06 baseline meshes are retained exactly, and all 48 circulation envelopes pass with the new hardware. Reviewer reports retain the limitations on inferred anchors, welds, reinforcement, capacities and deliberately unmodeled earth; mechanical close-out does not add engineering certification.

**Effective version close-out: 8 required steps passed, 0 unresolved mechanical failures**: six canonical passes, recovered direct export and separately verified viewer. Additional coordinate correspondence and taxonomy checks pass. Run-level document checks and transcript archival remain separate; **no archival has been performed here**.

Runtime exception retained: the Coordinator assigned this mechanical Runner work to the former v03 Builder, an Astra judgement agent, because the original Runner could not resume at the runtime thread limit. The v07 Builder and independent Designer/reviewer retain geometry, testing and acceptance ownership.
