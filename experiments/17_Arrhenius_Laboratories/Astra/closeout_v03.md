# Close-out of 17_Arrhenius_Laboratories Astra v03

Written by `tools/closeout.py` on 2026-09-17 01:36.

| step | result | detail |
|---|---|---|
| script exists | pass | experiments\17_Arrhenius_Laboratories\Astra\experiment_17_astra_v03.py |
| export to viewer | FAIL | [1/1] 17_Arrhenius_Laboratories/astra_v03.json ... FAILED  indexed 176 models / failed this run: 1  --- FAILED 17_Arrhenius_Laboratories/astra_v03.json TIMEOUT |
| layers baked | pass | baked viewer\models\17_Arrhenius_Laboratories\astra_v01.json baked viewer\models\17_Arrhenius_Laboratories\astra_v02.json |
| layers audit: nothing in 'other' | pass | 0 elements in 'other' |
| index.json rebuilt | pass | indexed 176 models |
| view set complete | pass | frame-only, from-below and section views present |
| renders present | pass | 34 view PNGs |
| viewer loads the model | FAIL | no screenshot: d unexpectedly: exit_code=-1073741790 [1648:22944:0917/013641.682:ERROR:content\browser\gpu\gpu_process_host.cc:1054] GPU process exited unexpectedly: exit_code=-1073741790 [1648:22944:0917/013641.682:FATAL:content\browser\gpu\gpu_data_manager_impl_private.cc:417] GPU process isn't us |

6 passed, 2 failed.

## Supplemental recovery evidence

The original close-out results above are preserved. A direct export was retried
with Blender 4.3.2 `--factory-startup` and a longer runtime. It completed with
30,003 elements: 5,043 boxes and 24,960 meshes, writing
`viewer/models/17_Arrhenius_Laboratories/astra_v03.json` (7,360,471 bytes).

The recovered models were baked and the index rebuilt (177 models indexed). The
current layer audit reports three elements in `other`:
`Insert/InsertFloors/InsertLinkDeck`. The Builder owns the layer override
decision.

The canonical viewer check failed on Chrome's GPU process. A single escalated,
readiness-checked subprocess probe was then requested with a fresh GUID profile,
GPU enabled, and a 120-second real wait. That tool call was interrupted after
approximately 292 seconds before returning any output; no screenshot or logs
were created. Viewer loading therefore remains unverified for v03. The review
identified a south fascia fidelity issue requiring v04.

After the Builder added the narrow `InsertLinkDeck` override, v03 was rebaked
and audited in isolation. The audit now reports `0 elements in 'other'`.
