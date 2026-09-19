# Fabrication set, experiment 16 GPT-6 v02

Drawings and a stick order for a 1:15 model built from Karapori Mäntyrima
30 cm sticks (https://karapori.fi/products/mantyrima-3-x-3-mm).

This folder is `fabrication/GPT-6/`: one subfolder of `fabrication/` per run
folder of the experiment, under the same name, so the sets of different
models never mix. The source is `../../GPT-6/`, version v02.

## Decisions

- Scale 1:15. The model is 307 x 225 mm in plan and 488 mm tall, so every
  frame fits one A2 sheet at model size and the sheets work as glue-up
  templates.
- Two sticks. 3x5 mm replaces the 36 x 90 slat (45 x 75 mm real). 2x10 mm
  replaces the 24 x 90 board (30 x 150 mm real), which gives 20 boards per
  wall instead of 33.
- `fab_model.py` is a parametric copy of `../../GPT-6/experiment_16_gpt6_v02.py`.
  Room, frame spacing, column undulation and roof field are unchanged. What
  changed to suit the sticks:
  - the inner chord line moved from 1.600 to 1.6125 m so a whole 3x5 rail
    fits between wall board and chord (v02 ripped the rail to 31 mm);
  - the mat overhang at the ends is two whole slats, which seat the door jambs;
  - the crossed roof-plan braces stack to 90 mm and stand 15 mm above the
    75 mm lower chords;
  - floor and ceiling boards run the full 3 m as one stick (`CONTINUOUS_FLOOR`);
  - each roof lower chord ply is one continuous 4.5 m member, which is a whole
    uncut 300 mm stick;
  - column rungs and roof posts run to the far edges of the chords they join
    (half a chord face longer at each end) for a full glue lap. The post tops
    stop just under the roof boards.
- Half model later: set `FRAMES = list(range(4))` in `fab_model.py`. The door
  wall stays, the far wall is dropped, and every script downstream follows.

## Run

```
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" --background --python fab_model.py
python fab_cutlist.py
python fab_drawings.py
```

| File | Written by | Contents |
|---|---|---|
| `members.json`, `fab_model.blend` | `fab_model.py` | every member as a mesh in model mm, with stick and group; the script also runs the overlap and contact checks |
| `order.md` | `fab_cutlist.py` | sticks to order per profile, with 10 % spare and price |
| `cutlist.csv` | `fab_cutlist.py` | every distinct piece: stick, part, length, rip width, square or angled ends, quantity |
| `pdf/NN_*.pdf`, `pdf/00_all_sheets.pdf` | `fab_drawings.py` | 22 A2 sheets, vector, drawn 1:1 to the model |
| `svg/` | `fab_drawings.py` | the same sheets for a quick look in a browser |

The three scripts hold what is specific to this model: the parametric
geometry, the prices, the sheet list, the frame template and the unrolled
roof. The drawing, measuring, packing, hidden-line and PDF code is the
fabrication kit in `tools/` (`export_members`, `cutlist`, `drafting`,
`title_blocks`, `hidden_lines`, `vector_pdf`, `qr_code`; see
`tools/README.md`). `fab_cutlist.py` needs only the Python standard library.
`fab_drawings.py` also needs numpy, for the axonometrics, and Chrome, which
prints the PDFs and embeds the title block fonts (Segoe UI, MEK-Mono). The
title block is footer `k` of `tools/title_blocks.py`, the default; pass
`footer='a'` to `'k'` to `SheetSet` for another.

## Sheets

01 ground mat plan, 02 plan section, 03 roof framing plan, 04 roof boards
unrolled. 05 to 08 elevations. 09 cross section, 10 long section. 11 to 17 one
template per frame F0 to F6. 18 side wall, 19 door wall, 20 far wall templates.
21 axonometric of the viewer layer "frame", 22 axonometric of "cladding ext"
and "fixtures" (both 1:20).

Print at 100 %, no "fit to page". Each sheet has a 100 mm check bar. Every
number on a sheet is model mm, the level marks included.

On a template the number on a piece is its cut length. The circle beside it
gives the stick profile and the layer. L1 is the layer that lies on the paper,
higher numbers stack towards you.

A frame template shows three views. The main view has the web layer L3 in grey,
the chords L2 and L4 as heavy outlines and the straps L1 and L5 as thin
rectangles. The side view on the right shows the five layers edge on, with the
web layer grey. The axonometric in the room opening is at 1:40.

Sheet 04 unrolls the roof. Each bay is a strip of six planar panels that fold
along lines parallel to the boards, so the strip lies flat without distortion.
Heavy lines mark the folds.

## Known limits

- Plans, elevations, sections and templates remove hidden lines by painting
  faces back to front by mean depth. That is exact for axis-aligned views only.
- The axonometrics use `tools/hidden_lines.py`: every edge is clipped against every face
  of the other members that is nearer to the viewer. A face that only touches
  the edge hides nothing, so flush joints keep their lines. It relies on every
  member being convex and on members not intersecting, which `fab_model.py`
  checks. All nine views take about 5 s.
- The axonometrics are lines only, so the web layer is not grey there. The
  side view on each frame template carries the grey.
- The drawings cull back faces, so every face must be wound outwards.
  `fab_model.py` asserts it. The v02 script winds its `RoofUpper` chords
  inwards (Blender's renders don't show it); the fabrication copy swaps the
  two rings passed to `mesh_prism`.
- Length labels sit at the piece centre (upright pieces 15 % above it, and
  dropped 5 mm below any rail they would land on). Each lollipop goes to the
  side of its piece with fewer circles and less drawing under it. Pieces
  that share one outline in a view (the two jamb plies, a sole runner on its
  sleeper) are labelled once, with their layer codes joined (`L2+L3`).
- The QR code was scanned from the screen on 2026-09-18 and opens the viewer.
- The longitudinal ties are cut between the frame webs, as designed. That
  makes 3 mm end stubs. Running each tie as one 210 mm stick past notched
  webs would be easier to build.
- Stick sizes vary a little, as Karapori notes. Check the 3 mm and 5 mm
  dimensions on delivery before cutting to the drawings.
