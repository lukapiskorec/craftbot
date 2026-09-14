# Inspection, experiment 16, Fable run, v03

Three Inspectors on the mechanical model. Ring and box spawned together on the orbits plus the changed-family views (05, 08, 11, 13, 14, 19, 23, 27, 28); a third on the six splice close-ups 29 to 34 that the Builder appended after the box Inspector could not read the 20 px stud bands of 27 and 28. Parts: `inspection_v03_ring.md`, `inspection_v03_box.md`, `inspection_v03_splices.md`.

## Summary

Nothing open. The v02 defect is gone: on view 23 (truss 3 face on) both apex webs run from the inner apex node to their outer vertices and the zigzag is continuous through the ridge; view 08 and the orbits show the same on all 11 trusses, no bowtie, nothing above the mitred outer chord, no web crossing another. R-11 met. The splice rule of R-21 reads on the close-ups: one cut per frame at 4.55 (29), 9.10 (30), 3.25 (31, 33) and 7.80 (32, 34), and the sill rail block at 9.51 to 9.63 clean in every frame that holds it (30, 32, 34), where v02 had the third cut. The splices Inspector raised a faint line at about z 8.70 across the B slat in 32 and 34; the Builder's probe on the .blend lists StudN0B and CrippleSB as three pieces each with joints at 3.25 and 7.80 only, and the Builder sees no line at 8.70 in 34. Resolved as a misread, not geometry.

Two "cannot judge" lines are subset limits, not findings. The ring Inspector could not count the braces (R-20) without view 17; the bracing is unchanged since v02, where 17 settled it. The box Inspector could not separate the door framing (R-19) in 08 because that view hides the boards but not the ring bracing behind; R-19 is a script check, ticked since v01 and unchanged.

## Ring part (from `inspection_v03_ring.md`)

- Apex webs fixed on every truss: 23, 08, 01 to 04, 13. R-11 met.
- R-09, R-10, R-13, R-14, R-23 met on 01 to 04, 11, 13, 19, 23.
- R-20 cannot judge from the subset (no view 17); unchanged geometry, ticked in v02.
- Shared checklist: raft centred under the building, envelope closed except the band and the door, nothing outside the raft.

## Box part (from `inspection_v03_box.md`)

| Finding | View | Requirement | Severity | Builder's resolution |
|---|---|---|---|---|
| Stud bands in 27 and 28 show rail ticks but no distinct splice line at 20 px | 27, 28 | R-21 | cannot judge | views 29 to 34 appended, see the splices part |
| Door framing members not separable from the ring bracing behind the frame-only view | 08, 14 | R-19 | cannot judge | script check, unchanged since v01; a frame-only view with the ring hidden is a suggestion for phase 2 |
| Building centred on the raft, envelope closed except band and door | 01 to 05 | shared | ok | |
| Door open, leaf modelled | 03, 04 | R-04 | ok | |
| Light only from the band, deck closed | 01 to 05 | R-05 | ok | |
| Plain box, ring outside the wall and band zone | 13 | R-08 | ok | |
| Board joints alternate, no regression | 27, 28 | R-15 | ok | |
| 7 roof trusses, deck of slats | 08, 13 | R-17 | ok | |
| Gable studs to the sloped head plate | 13 | R-18 | ok | |
| Eave slot open as designed | 13 | R-34 | ok | |

## Splices part (from `inspection_v03_splices.md`)

| View | Slat | Cut seen at | Sill rail | Severity |
|---|---|---|---|---|
| 29 | N stud A | 4.55 only | not in frame | ok |
| 30 | N stud A | 9.10 only | clean | ok |
| 31 | N stud B | 3.25 only | not in frame | ok |
| 32 | N stud B | 7.80; faint line queried at 8.70 | clean | ok; query resolved by the probe |
| 33 | S cripple B | 3.25 only | not in frame | ok |
| 34 | S cripple B | 7.80; faint line queried at 8.70 | clean | ok; query resolved by the probe |

## Verdicts by requirement line

Met this version: R-11, R-21. Confirmed again: R-04, R-05, R-08, R-09, R-10, R-13, R-14, R-15, R-17, R-18, R-23, R-34. Not judged (subset limits, unchanged, ticked earlier): R-19, R-20. Nothing not met.
