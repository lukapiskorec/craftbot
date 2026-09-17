# Close-out of 17_Arrhenius_Laboratories Astra v02

Written by `tools/closeout.py` on 2026-09-16 23:03.

| step | result | detail |
|---|---|---|
| script exists | pass | experiments\17_Arrhenius_Laboratories\Astra\experiment_17_astra_v02.py |
| export to viewer | FAIL | [1/1] 17_Arrhenius_Laboratories/astra_v02.json ... FAILED  indexed 175 models / failed this run: 1  --- FAILED 17_Arrhenius_Laboratories/astra_v02.json TIMEOUT |
| layers baked | pass | baked viewer\models\17_Arrhenius_Laboratories\astra_v01.json |
| layers audit: nothing in 'other' | pass | 0 elements in 'other' |
| index.json rebuilt | pass | indexed 175 models |
| view set complete | pass | frame-only, from-below and section views present |
| renders present | pass | 31 view PNGs |
| viewer loads the model | FAIL | no screenshot: d unexpectedly: exit_code=-1073741790 [31724:3512:0916/230316.341:ERROR:content\browser\gpu\gpu_process_host.cc:1054] GPU process exited unexpectedly: exit_code=-1073741790 [31724:3512:0916/230316.341:FATAL:content\browser\gpu\gpu_data_manager_impl_private.cc:417] GPU process isn't us |

6 passed, 2 failed.

## Supplemental recovery evidence

The original close-out results above are preserved. A direct export was retried
with Blender 4.3.2 `--factory-startup` and a longer runtime. It completed with
31,149 elements: 5,059 boxes and 26,090 meshes, writing
`viewer/models/17_Arrhenius_Laboratories/astra_v02.json` (7,700,464 bytes).

The recovered models were baked and the index rebuilt (176 models indexed). The
current layer audit reports one element in `other`: `Insert/InsertFloors /
InsertEastShelf`. The Builder owns the layer override decision.

The original viewer screenshot check failed because Chrome's GPU process was
unusable. No retry was made for this failed iteration; no screenshot result is
claimed. The rationale and callouts are drafts and are not asserted final here.

### Escalated viewer diagnostic

One escalated run was attempted with a fresh local server on port 8124 and
Chrome's GPU path enabled. The exact effective Chrome arguments were:

```
--headless=new
--user-data-dir=C:\Users\lukap\AppData\Local\Temp\craftbot-astra-v02-viewer-profile
--screenshot=C:\Users\lukap\Documents\GitHub\craftbot\experiments\17_Arrhenius_Laboratories\Astra\closeout_v02_viewer.png
--window-size=1600,1200
--virtual-time-budget=8000
--enable-logging=stderr
--v=1
http://127.0.0.1:8124/?model=models/17_Arrhenius_Laboratories/astra_v02.json&anim=none
```

The command exited with code 0. Captured stdout/stderr were empty, and
`closeout_v02_viewer.png` was not created. The server process was PID 26788 and
was stopped after the check. Therefore no viewer model correctness or red
banner state can be claimed. The direct export remains valid; the layer audit
issue is `Insert/InsertFloors/InsertEastShelf` (1 element).

### Fresh-profile browser diagnosis

A read-only process check found no Chrome process using the prior
`craftbot-astra-v02-viewer-profile` profile. One final escalated run then used a
fresh profile and the same model URL, with GPU enabled and these arguments:

```
--headless=new
--user-data-dir=C:\Users\lukap\AppData\Local\Temp\craftbot-astra-v02-f0d9b803fc084595b548dc5c1107dd65
--screenshot=C:\Users\lukap\Documents\GitHub\craftbot\experiments\17_Arrhenius_Laboratories\Astra\closeout_v02_viewer.png
--window-size=1600,1200
--virtual-time-budget=8000
--no-first-run
--no-default-browser-check
--enable-logging=stderr
--v=1
http://127.0.0.1:8125/?model=models/17_Arrhenius_Laboratories/astra_v02.json&anim=none
```

The server was PID 36612 and was stopped afterward. Chrome exited immediately
without producing a screenshot; the captured exit code was unset, and both
`closeout_v02_chrome_stdout.log` and `closeout_v02_chrome_stderr.log` are zero
bytes. Viewer loading therefore remains unverified.

### Waited subprocess probe

To resolve the earlier PowerShell launch ambiguity, a temporary bundled-Python
helper used `subprocess.run([...], timeout=120, capture_output=True,
encoding="utf-8", errors="replace")` for Chrome, with a fresh GUID profile and
GPU enabled. The native Chrome return code was `0`; stdout was empty and stderr
contained Chrome diagnostics. It produced
`experiments/17_Arrhenius_Laboratories/Astra/closeout_v02_viewer.png` (21,474
bytes), but inspection shows Chrome's `ERR_CONNECTION_REFUSED` page for
`127.0.0.1:8126`, rather than the viewer. The helper started server PID 32312
and terminated that process in `finally`. This records a local-server startup
race; the v02 viewer model remains unverified.
