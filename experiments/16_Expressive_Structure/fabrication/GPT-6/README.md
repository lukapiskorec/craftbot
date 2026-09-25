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
python fab_frontpage.py [out.pdf]      # the two text pages alone, to iterate on them
```

| File | Written by | Contents |
|---|---|---|
| `members.json`, `fab_model.blend` | `fab_model.py` | every member as a mesh in model mm, with stick and group; the script also runs the overlap and contact checks |
| `order.md` | `fab_cutlist.py` | sticks to order per profile, with 10 % spare and price |
| `cutlist.csv` | `fab_cutlist.py` | every distinct piece: stick, part, length, rip width, square or angled ends, quantity |
| `pdf/NN_*.pdf`, `pdf/00_all_sheets.pdf` | `fab_drawings.py` | 26 A2 sheets, all portrait, vector; the drawings 1:1 to the model |
| `svg/` | `fab_drawings.py` | the same sheets for a quick look in a browser |

The scripts hold what is specific to this model: the parametric geometry,
the prices, the sheet list, the frame template, the unrolled roof, the
pedestals (`fab_pedestal.py`) and the text of the front pages
(`fab_frontpage.py`). The drawing, measuring, packing, hidden-line, newsprint
and PDF code is the fabrication kit in `tools/` (`export_members`, `cutlist`,
`drafting`, `title_blocks`, `hidden_lines`, `vector_pdf`, `qr_code`,
`newsprint`, `fonts`, `organigram`; see `tools/README.md`). `fab_cutlist.py`
needs only the Python standard library. `fab_drawings.py` also needs numpy,
for the axonometrics, Pillow, for the text widths of the front pages, and
Chrome, which prints the PDFs and embeds the fonts (Segoe UI, Times New
Roman, MEK-Mono). The title block is footer `r` of `tools/title_blocks.py`,
the default; pass `footer='a'` to `'q'` to `SheetSet` for an older one.

## Sheet layout and title block

Every sheet is A2 portrait, so the set binds as a booklet. A view that is
wider than tall (the three plans, the unrolled roof) is drawn on a landscape
blank, centred for the portrait sheet by `SheetSet.place`, and turned a
quarter turn when it is added: its bottom edge lies along the right edge and
the drawing reads with the sheet turned clockwise, while every label (piece
lengths, lollipops, frame axes, bay names) reads upright on the portrait
sheet, because a blank that will be turned sets its labels at -90 degrees
(`Sheet.turn_labels`, `Sheet.offset`). Sheet 25 was recomposed for portrait
instead of turned.

Footer `r`, 32 mm, runs left to right: the QR code to the viewer; two list
columns with DATE, SUPERVISION, AGENTS, WORKFLOW, DISCLAIMER and SOURCE
CODE (`CREDITS` in `fab_drawings.py`), spread between the top and bottom of
the QR code; SCALE ('1:15, drawn 1:1 to the model, units mm') over a print
check bar of 1 m real, 67 mm on the paper, on the QR code's bottom line;
TITLE over PROJECT ('Experiment 16 - Expressive Structure, GPT-6 v02') over
the studio mark; and the sheet number in a black box at the right edge, so
the number shows first in a bound folder. It grew out of the footer study
of 2026-09-25 (`tools/footer_study/pdf/`): `l` is the 40 mm version with a
credits band, `m` to `q` the other 32 mm trials.

## Front pages

Sheets 01 and 02 are text only, without a title block: the CraftBot
description, then the run's `brief.md`, `concept.md`, `design_notes.md` and
`version_notes.md` unedited, in that order of priority, flowed by
`tools/newsprint.py` into four justified columns of Times New Roman like an
old newspaper, with a masthead, a QR code to the repository and the agent
team organigram (`tools/organigram.py`, a vector redrawing of
`visuals/craftbot_agent_team_organigram.tex`) across two columns.
A credits paragraph (author, studios, the art-ai-fact initiative) closes the
second page. `fab_frontpage.py` picks the largest type at which everything
fits two pages (about 3.4 mm, 9.6 pt, which fills both) and would cut the
text after the second page if it did not fit at 2 mm. Tables are set as one
paragraph per row with the first cell bold; the closing sentence of the
description, which says the run documents follow, is mine.

## Sheets

01 and 02 the text pages. 03 ground mat plan, 04 plan section, 05 roof
framing plan, 06 roof boards unrolled. 07 to 10 elevations. 11 cross section
(first bay, looking at the door wall from inside), 12 long section. 13 to 19
one template per frame F0 to F6. 20 side wall, 21 door wall, 22 far wall
templates. 23 axonometric of the viewer layer "frame", 24 axonometric of
"cladding ext" and "fixtures" (both 1:20). 26 the model on its tall
exhibition pedestal (1:4), the pedestal exploded into its boards and a side
view with a 1.75 m visitor (both 1:10), from `fab_pedestal.py`. The visitor
is `person` of `tools/drawing_assets.py`.

The pedestal is 418 x 418 x 1200 mm, 1688 mm with the model. Four uncut
18 x 400 x 1200 boards are the sides, each lapping the edge of the next. A
fifth board gives the 382 x 382 top and bottom panels, set inside the sides and
flush with their ends. Everything is screwed. The bottom panel carries about
20 kg of ballast: empty, a 30 N push at the top edge tips the pedestal.

25 is a second pedestal design on trial, also from `fab_pedestal.py`: a low
900 x 900 x 450 mm pedestal, 938 mm high with the model. The model stands
40 mm from the far edge, turned so its door faces the visitor, and the 26 A2
sheets of this set lie open in front of it. The axonometric (1:5) on top
shows them as a spiral-bound booklet, open 850 x 594 mm, with the long
section and the frame F0 template laid on its pages (the sheets' own polygons
and lines put through the axonometric, text as fine bars; `OPEN_AT` names
the sheets by title, so the numbers follow the set); under it the side view
(1:10) and two 1:15 diagrams of the booklet and the alternative, an accordion
of the sheets joined along the long edge (10.92 m unfolded). The open booklet
leaves about 20 mm to the model and to the front edge. The pedestal is drawn
as one volume; its boards are not designed yet.

Dimension lines, leaders, level datums and axis ticks on every sheet use the
`FINE` line weight (0.07 mm) of `tools/vector_pdf.py`, thinner than any line of
the drawing itself.

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
  The repository QR code on sheet 01 has not been scanned from a print yet.
- The front pages break lines with the widths of the installed Times New
  Roman file (Pillow) and fit each justified line to its column with the SVG
  `textLength`, so the columns print even. Without Pillow the widths fall
  back to a Helvetica guess and the justification gets rough.
- The longitudinal ties are cut between the frame webs, as designed. That
  makes 3 mm end stubs. Running each tie as one 210 mm stick past notched
  webs would be easier to build.
- Stick sizes vary a little, as Karapori notes. Check the 3 mm and 5 mm
  dimensions on delivery before cutting to the drawings.
