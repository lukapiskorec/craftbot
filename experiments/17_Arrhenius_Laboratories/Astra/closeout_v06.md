# Close-out of 17_Arrhenius_Laboratories Astra v06

Written by `tools/closeout.py` on 2026-09-17 12:21.

| step | result | detail |
|---|---|---|
| script exists | pass | experiments\17_Arrhenius_Laboratories\Astra\experiment_17_astra_v06.py |
| export to viewer | FAIL | [1/1] 17_Arrhenius_Laboratories/astra_v06.json ... FAILED  indexed 180 models / failed this run: 1  --- FAILED 17_Arrhenius_Laboratories/astra_v06.json TIMEOUT |
| layers baked | pass | baked viewer\models\17_Arrhenius_Laboratories\astra_v01.json baked viewer\models\17_Arrhenius_Laboratories\astra_v02.json baked viewer\models\17_Arrhenius_Laboratories\astra_v03.json baked viewer\models\17_Arrhenius_Laboratories\astra_v04.json baked viewer\models\17_Arrhenius_Laboratories\astra_v05. |
| layers audit: nothing in 'other' | pass | 0 elements in 'other' |
| index.json rebuilt | pass | indexed 180 models |
| view set complete | pass | frame-only, from-below and section views present |
| renders present | pass | 51 view PNGs |

6 passed, 1 failed.

## Supplemental recovery, provenance and viewer inspection

The canonical results above are preserved. Its exporter reached the known 120-second subprocess timeout. The prior direct factory-startup export in `export_v06_direct.log` completed with exit 0: **4,943 boxes + 25,033 meshes = 29,976 elements**, 7,402,700 bytes. The source is `experiments/17_Arrhenius_Laboratories/Astra/experiment_17_astra_v06.py`; the exporter executed that source rather than loading the later render master. No frozen geometry was changed during close-out.

The actual file `viewer/models/17_Arrhenius_Laboratories/astra_v06.json` has SHA256 **3418977bac8e7bb2913c6d7eef4ee381396477601414db8d4cffdc6956d23a80**, unchanged after canonical close-out. This includes the Builder's metadata correction assigning the retained `EntranceApproachSlab` to floors. The direct and canonical audits report zero elements in `other`. `fixture_layers_v06.txt` records **6/6 checks passed**: 5,414 timber-frame members, 215 steel-frame members including fixture brackets, 178 skylight-frame members and 1,152 StairRim members are fixtures; the four concrete RooflightSeatBeam members remain frame. The viewer index contains 180 models.

### Geometry identities and measured correspondence

- Generated and independently reproduced geometry: `523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416`.
- Saved standard-checked render master: `25c4743bc414e69436a7b18e84e6fc5535ae58651dd41d9913a78b3ee06e6f1a`.

`reproduction_v06.txt` confirms exact full-generator reproduction of the generated snapshot. `render_identity_difference_v06.json` and `render_support_bridge_v06.txt` retain the distinct saved identity: 93 transform changes, 29 objects with changed world coordinates, maximum 3.814697265625 micrometres. All local meshes and every primary-support world vertex remain unchanged; changed geometry is confined to court treads and inclined-glazing rails. All 19 actual final tread underside unions pass the recorded 20-micrometre float32 seam allowance. These are measured numerical differences, not equal raw hashes.

Runner independently compared every object's actual exported coordinates with both saved snapshots at the exporter's five-decimal precision. `export_saved_identity_v06.json` records **29,976 objects, zero missing objects and zero quantized-coordinate differences against either snapshot**. Consequently the existing viewer export accurately represents both at its stored precision; no regeneration or new browser capture was needed.

### Actual viewer proof

The Coordinator executed the prepared browser probe outside the sandbox. `closeout_v06_viewer_probe.log` records the exact current JSON hash above, byte-matched HTTP200 root/model readiness, a fresh GUID profile, GPU enabled, Chrome exit 0 after 5.343 seconds and owned-server cleanup. The HTTP log records successful viewer/model/rationale/callout responses; only the favicon returned 404.

**Actual screenshot inspection: PASS.** `closeout_v06_viewer.png` visibly identifies experiment 17 Arrhenius Laboratories, Astra, iteration v06 and **29,976 elements**. The elongated ring, courtyard, rooftop plant and continuous upper south facade are visible, with no red error banner. The displayed rationale still describes the earlier accepted v05; the Coordinator owns its final revision. This capture verifies model loading, not structural acceptance.

### Artifact status and unresolved design issue

The final evidence set is **51 Workbench views** (01-37 and 41-54), **four selected Cycles views** (muted 12/15/28 and interior 40), and **30 plan images**: **85 final images**. One earlier Cycles trial and two separately named detail copies are retained in addition, as is the viewer screenshot. Builder reports the completed stock checks **29,976 members / 0 penetrating pairs / 0 floating**, and independent visual review passes.

**Effective mechanical version close-out: 8 required steps passed, 0 unresolved mechanical failures**: six canonical passes, recovered direct export and separately verified viewer. The additional export-coordinate comparison also passes.

**v06 is not converged.** Actual structural review leaves 30 CourtSouth facade panels without a modeled primary attachment path: 24 inherited cases and six whose previous jamb/corbel path was lost after the frame rotation. A zero-pair/zero-floating result and successful viewer export do not resolve that issue. The Coordinator has authorized v07 for the correction; ownership remains with its Designer and Builder. No transcript archival or run-level acceptance was performed here.

Runtime exception retained: the Coordinator assigned these mechanical Runner duties to the former v03 Builder, an Astra judgement agent, because the original Runner could not resume at the runtime thread limit. The v06 Builder and independent reviewers retain geometry, tests and review ownership.
