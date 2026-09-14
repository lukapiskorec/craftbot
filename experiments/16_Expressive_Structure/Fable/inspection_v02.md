# Inspection, experiment 16, Fable run, v02

Two Inspectors on the mechanical model, spawned together on views 01 to 22; the Builder rendered views 23 to 26 afterwards for the items both said they could not judge at the set's zoom, and looked at those four itself. Ring part: `inspection_v02_ring.md`. The box Inspector returned its findings inline and wrote no part file; they are recorded here.

## Summary

One defect, older than v02 and invisible to both checks: the two webs at every apex node are stubs. `RingWeb_03_17F` spans x -0.157..0.116 and `RingWeb_03_18R` x -0.105..0.133 (probe on the .blend), where each should run 0.45 m from the apex node to the outer vertex at x = +/-0.39. The corner-node clip in `inner_clips` (stay inside the other run's outer face) is right at the eave corners and wrong at the apex, where the other slope's outer face, extended, passes under the web body. 22 stubs, no web reaches the apex node, the Warren zigzag is broken over two panels per truss. Seen as the pale "bowtie" above the inner chord at the apex (views 06, 13, 14, 23) and confirmed by hiding RingWebs (gone) and RingChords (stands alone). R-11 not met. Everything else the Inspectors raised resolved on the close-ups: joints stagger (24), the eave corner reads as construction (25), the door leaf has three ledges and two braces from the hinge side low to the latch side high (26), the mitred eave corner is clean at d = 0.33 (22, ring Inspector).

## Ring part (from `inspection_v02_ring.md`)

- v01 finding (b) resolved: view 22 shows the mitred outer-chord corner at truss 3 (d = 0.33) as a clean join, no chamfer, no cut into the inner chord.
- Question on R-20: in the top view the braces and ties seem to stop short of the outermost trusses. Builder: they end at y = +/-3.25, the end trusses' centreline, and cover 60 of the 120 mm of the end leg face; construction, not a defect.
- v01 finding (a) not resolved from the views: a faint dark mark at the ring apex in view 13. Builder: this is the apex web stub defect above.
- R-02/03, R-09, R-10, R-11 (as far as the views show; the stub defect was found afterwards), R-13, R-14, R-23 read as met on views 01 to 07, 11, 13, 17, 19, 21, 22.
- View 17's crop excludes the leg contacts of the braces. Builder: the brace plane x = 2.230..2.260 lies on the leg inner face at 2.26 over every crossing by construction.
- Photo rule 9 ("depth about a metre"): the model runs 0.33 to 0.93 and reads shallower at the troughs. Design intent, recorded.

## Box part (returned inline)

| Finding | View | Requirement | Severity | Builder's resolution |
|---|---|---|---|---|
| Dark block above the ring inner chord at the apex | 13, 14 | R-11 | defect | apex web stubs, see summary; v03 |
| Board joints read as continuous seams across the wall | 06, 20 | R-15 | defect as reported | view 24: joints alternate column by column at 1.95 and 3.25; resolution of the elevation, not geometry; met |
| Pale bowtie at the ridge apex where the deck should be closed | 06 | R-05, R-17 | question | the same web stubs of the front truss; the deck is continuous (16); not a hole |
| Eave heel: deck on the truss tails on the head plate, slot open between heels | 12, 20 | R-17, R-34 | ok | the open slot is the Designer's v02 decision (R-34) |
| Corner post and notch at the gable-side junction not resolvable | 12, 20 | (v01 item c) | cannot judge | view 25: four-slat corner post from the side head plate to the gable plate, gable plate under the deck, tails on the head plate; construction |
| Door leaf open about 90 degrees, void reads through to daylight | 10, 15, 18 | R-04 | ok | met |
| Door leaf ledge count and brace direction not resolvable | 03, 04 | R-33 | cannot judge | view 26: boards, three ledges, two braces low at the hinge side, high at the latch side; met |
| Clear gap between wall faces and ring legs, nothing of the ring in the box or the band | 01-04, 13-16, 20 | R-08, R-13 | ok | met |
| 7 trusses with king, queen posts and diagonals; level side head plates, sloped gable plates | 06, 08, 13, 20 | R-17, R-18 | ok | met |
| No structure other than trusses and bracing before the door wall | 01-04, 10 | R-23 | ok | met |

## Verdicts by requirement line

Met: R-04, R-05, R-08, R-10, R-13, R-15, R-17, R-18, R-20, R-23, R-33, R-34. Not met: R-11 (apex web stubs). Not judged by the Inspectors: R-21 (splice positions; the Builder holds it open for the Designer's new gable stud rule).
