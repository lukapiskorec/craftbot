# Close-out of 17_Arrhenius_Laboratories Astra v04

Written by `tools/closeout.py` on 2026-09-17 05:19.

| step | result | detail |
|---|---|---|
| script exists | pass | experiments\17_Arrhenius_Laboratories\Astra\experiment_17_astra_v04.py |
| export to viewer | FAIL | [1/1] 17_Arrhenius_Laboratories/astra_v04.json ... FAILED  indexed 178 models / failed this run: 1  --- FAILED 17_Arrhenius_Laboratories/astra_v04.json TIMEOUT |
| layers baked | pass | baked viewer\models\17_Arrhenius_Laboratories\astra_v01.json baked viewer\models\17_Arrhenius_Laboratories\astra_v02.json baked viewer\models\17_Arrhenius_Laboratories\astra_v03.json baked viewer\models\17_Arrhenius_Laboratories\astra_v04.json |
| layers audit: nothing in 'other' | pass | 0 elements in 'other' |
| index.json rebuilt | pass | indexed 178 models |
| view set complete | pass | frame-only, from-below and section views present |
| renders present | pass | 37 view PNGs |

6 passed, 1 failed.

## Supplemental recovery and viewer verification

The canonical results above are preserved. Its exporter reached the known 120-second subprocess limit; this does not invalidate the completed direct export. `export_v04_direct.log` records a successful factory-startup export from the frozen v04 script: **5,007 boxes + 24,869 meshes = 29,876 elements**, 7,327,161 bytes. The JSON source field names `experiments/17_Arrhenius_Laboratories/Astra/experiment_17_astra_v04.py`. No geometry was changed during this recovery.

The exact viewer artifact is `viewer/models/17_Arrhenius_Laboratories/astra_v04.json`, SHA256 **f53238ad649b6e96f8566e9467c4671071456a289c1e372f7d745c0b3dc46e7d**. Its hash remained identical after canonical close-out. The isolated v04 bake/audit and the subsequent canonical experiment-wide bake/audit both completed; zero elements remain in `other`. The index contains 178 models. No additional layer override was needed for v04.

The Coordinator separately ran the prepared viewer probe outside the sandbox. `closeout_v04_viewer_probe.log` records HTTP200 readiness with the root page and exact v04 JSON byte-matched to their local files; Chrome exited 0 after 5.313 seconds, using a fresh GUID profile with GPU enabled. The owned local server was stopped. `closeout_v04_viewer_http.log` confirms successful viewer modules, model, rationale and callout responses; the sole favicon404 does not affect the model.

**Actual screenshot inspection: PASS.** `closeout_v04_viewer.png` visibly identifies experiment17 Arrhenius Laboratories, agent Astra, iteration v04 and 29,876 elements. It shows the complete elongated ring, open courtyard, sparse roof plant and corrected continuous south upper fascia. No red error banner is present. The screenshot is therefore evidence of the intended model loading, not merely a nonempty PNG. The displayed rationale predates final document edits; the final run index rebuild will refresh its copy.

The canonical view check finds all 37 Workbench PNGs and the required frame-only, underside and section definitions. Builder handoff also confirms the three standard Cycles views12/15/28, final interior perspective40 and final standard geometry checks of29,876/0pairs/0floating. Earlier perspectives38/39 are retained detail trials. Geometry identity reported by the Builder is `8a02c4b9865c497bbd2d1af58a76140a978e0863a98ebd97a32ff63a26951657`; the viewer JSON hash above is a different serialization identity.

**Effective version close-out: 8 passed, 0 unresolved mechanical failures** (six canonical passes, recovered export, separately verified viewer). Source/proportion/structural review and final run documents remain Coordinator/Designer responsibilities. No transcript archival was performed.

Runtime exception: the original Runner could not resume because of the agent thread limit. The Coordinator assigned the former v03 Builder, an Astra judgement agent, these bounded mechanical Runner duties. It did not change v04 geometry, tests or inspection reports; the separate v04 Builder owns those artifacts.
