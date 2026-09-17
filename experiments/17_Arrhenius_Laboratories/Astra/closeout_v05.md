# Close-out of 17_Arrhenius_Laboratories Astra v05

Written by `tools/closeout.py` on 2026-09-17 07:24.

| step | result | detail |
|---|---|---|
| script exists | pass | experiments\17_Arrhenius_Laboratories\Astra\experiment_17_astra_v05.py |
| export to viewer | FAIL | [1/1] 17_Arrhenius_Laboratories/astra_v05.json ... FAILED  indexed 179 models / failed this run: 1  --- FAILED 17_Arrhenius_Laboratories/astra_v05.json TIMEOUT |
| layers baked | pass | baked viewer\models\17_Arrhenius_Laboratories\astra_v01.json baked viewer\models\17_Arrhenius_Laboratories\astra_v02.json baked viewer\models\17_Arrhenius_Laboratories\astra_v03.json baked viewer\models\17_Arrhenius_Laboratories\astra_v04.json baked viewer\models\17_Arrhenius_Laboratories\astra_v05. |
| layers audit: nothing in 'other' | pass | 0 elements in 'other' |
| index.json rebuilt | pass | indexed 179 models |
| view set complete | pass | frame-only, from-below and section views present |
| renders present | pass | 41 view PNGs |

6 passed, 1 failed.

## Supplemental recovery, provenance and actual viewer inspection

The canonical results above are preserved. Its exporter hit the known 120-second subprocess timeout. The completed direct factory-startup export in `export_v05_direct.log` already passed: **5,007 boxes + 25,160 meshes = 30,167 elements**, 7,403,925 bytes. The JSON source is `experiments/17_Arrhenius_Laboratories/Astra/experiment_17_astra_v05.py`. The final isolated and canonical layer audits both report zero elements in `other`; the Builder's narrow experiment17 terrace-base/fill mapping accounts for the twelve previously unclassified new members. The index contains 179 models.

The actual exported file is `viewer/models/17_Arrhenius_Laboratories/astra_v05.json`, SHA256 **695f650dda49bf892d4340424ce499c5e3fffcd63a5a48ddc535a9d6d449cf09**. This hash is unchanged after canonical close-out and matches the Coordinator's browser probe. The exporter executed the versioned source; it did not load the later saved render master.

### Distinct snapshot identities, with an explicit measured correspondence

- Generated/preflight geometry: `6cd07366762f8213cb58508c746d180142bf48f2534813f8f0bb0b64dc922f4c`.
- Saved standard-checked render master: `9968993522e362026e472282a4226d99961ec4017ae27497458e024213082417`.
- Secondary render batches have their separately recorded identity in `render_identity_difference_v05.json`; they are not asserted byte-identical to the master.

The Builder's `render_support_bridge_v05.txt` records unchanged local meshes, with round-trip transform drift affecting nineteen court treads by less than 0.24 micrometres and ten inclined-glazing rails by at most 3.815 micrometres between preflight and master. Every other world vertex is identical, including the slab seats, terrace, cores and insert interfaces. Actual final tread-seat unions were checked on the saved master and pass within the recorded 20-micrometre float32 seam allowance. The Designer accepted this measured numerical correspondence; it is not a claim of equal raw one-micrometre hashes.

Runner independently compared **every exported object's actual stored coordinates** with both saved snapshots using the exporter's five-decimal rounding. `export_saved_identity_v05.json` records 30,167 objects, zero missing objects and **zero quantized coordinate differences against either preflight or the checked master**. Consequently no model regeneration or screenshot refresh was necessary: the current viewer JSON represents both at its actual export precision. No frozen model was edited.

### Viewer proof

The Coordinator ran the prepared probe outside the sandbox; no second browser was launched by Runner. `closeout_v05_viewer_probe.log` records byte-matched HTTP200 root/model readiness, the exact JSON hash above, a fresh GUID profile, GPU enabled and Chrome exit0 after5.156 seconds. The owned local server stopped cleanly. `closeout_v05_viewer_http.log` shows successful viewer-module/model/rationale/callout responses; only the irrelevant favicon request returned404.

**Actual screenshot inspection: PASS.** `closeout_v05_viewer.png` visibly identifies experiment17 Arrhenius Laboratories, agent Astra, iteration v05 and **30,167 elements**. The recognizable complete elongated ring, courtyard, sparse roof plant and continuous south upper fascia are present. No red error banner appears. This proves the intended model loaded, rather than merely that a PNG exists. The rationale visible in this capture predates the Coordinator's final document refresh; it does not change model identity.

### Artifacts and status

Actual file inventory confirms **41 Workbench PNGs** (01-37 and41-44), **four Cycles PNGs** (standard12/15/28 plus final interior40) and **28 labelled plan PNGs**. Builder reports final full standard checks **30,167 members / 0 penetrating pairs / 0 floating**, and completed independent visual and structural acceptance. The source and local `support_geometry_v05.py` reproduce the generated geometry; earlier versions remain immutable.

**Effective version close-out: 8 required steps passed, 0 unresolved mechanical failures**: six canonical passes, recovered export, separately verified viewer. The additional coordinate correspondence check passes. R31 naming/location/artifact evidence is complete for the version. Final run document/callout checks and transcript archival remain separate; **no archival has been performed here**.

Runtime exception retained: the Coordinator assigned this bounded mechanical Runner work to the former v03 Builder (Astra judgement agent) because the original Runner could not resume at the runtime thread limit. The independent v05 Builder and Designer retain geometry, tests and review ownership.
