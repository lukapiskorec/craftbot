# Close-out of 17_Arrhenius_Laboratories Astra v01

Written by `tools/closeout.py` on 2026-09-16 07:41.

| step | result | detail |
|---|---|---|
| script exists | pass | experiments\17_Arrhenius_Laboratories\Astra\experiment_17_astra_v01.py |
| export to viewer | FAIL | [1/1] 17_Arrhenius_Laboratories/astra_v01.json ... FAILED  indexed 174 models / failed this run: 1  --- FAILED 17_Arrhenius_Laboratories/astra_v01.json TIMEOUT |
| layers baked | pass |  |
| layers audit: nothing in 'other' | pass | 0 elements in 'other' |
| index.json rebuilt | pass | indexed 174 models |
| view set complete | FAIL | no frame-only view (non-empty hide list) |
| renders present | pass | 4 view PNGs |
| viewer loads the model | FAIL | no screenshot: ing used by another process. (0x20) [34240:35120:0916/074108.271:ERROR:content\browser\gpu\gpu_process_host.cc:1054] GPU process exited unexpectedly: exit_code=-1073741790 [34240:35120:0916/074108.271:FATAL:content\browser\gpu\gpu_data_manager_impl_private.cc:417] GPU process isn't us |

5 passed, 3 failed.

## Supplemental recovery evidence

The original close-out results above are preserved. A direct export was retried
with Blender 4.3.2 `--factory-startup` and a longer runtime. It completed with
18,828 elements: 15,482 boxes and 3,346 meshes, writing
`viewer/models/17_Arrhenius_Laboratories/astra_v01.json` (2,149,703 bytes).

The recovered model was baked and the index rebuilt (175 models indexed). A
fresh layer audit found 61 elements in `other`, in these families: roof drains,
roof parapet ends/longs, roof plant seams, and site paths, garden, terrace, and
ground. These families require the Builder's layer override decision.

Viewer screenshot recovery was unavailable. The sandboxed unique-profile
Chrome attempt produced no PNG after the GPU-process failure; the escalated
retry was interrupted while awaiting execution. No screenshot result is being
claimed.
