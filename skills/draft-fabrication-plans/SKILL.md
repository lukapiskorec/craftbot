---
name: draft-fabrication-plans
description: Use when asked for fabrication files, production drawings, printable A2 or A3 plans, sections, elevations, glue-up templates, a cut list or a stick or material order for building a physical scale model of a finished CraftBot experiment model. Not part of an experiment run.
---

# Draft fabrication plans

## Overview

A fabrication set turns one finished model version into what a person needs to build it by hand from stock sticks: a model regenerated at the real stick sizes, a cut list and order, and sheets drawn 1:1 to the physical model so sticks can be laid on the paper. It lives in `experiments/<NN>/fabrication/<Run>/`, where `<Run>` is the name of the run folder the model comes from (`GPT-6`, `Fable`), so the sets of different models of one experiment never mix. One set per run, for one version; the README and the title block name the version. The run folder itself is a finished record: read it, never edit it.

The code is the fabrication kit in `tools/`. Read `tools/API_FABRICATION.md`, not the modules. The worked example is `experiments/16_Expressive_Structure/fabrication/GPT-6/` (README, three short scripts); copy its shape.

## Decisions that are the user's

Ask before building, one question at a time, each with a recommendation:

1. Which run and version (default: the latest version of the named run). An experiment often has several run folders; never guess between them, and never write into another run's fabrication subfolder.
2. The stock: supplier page, profiles, stick length. Open the page and read every variant with its price and whether it is in stock. An out-of-stock profile is not an option.
3. Paper size (default A2) and whether the whole model or a part is built.
4. Scale and profile pairing, once you have computed the candidates below.

## Scale and sticks

Scale is set by the paper, not by taste. The sheets are templates, so the largest view must fit one sheet at model size:

```
blender --background <version>.blend --python tools/export_members.py -- x.json     # prints extent and smallest scale for A2
```

Then for each candidate scale, real section x 1000 / scale gives the ideal stick. Offer the nearest in-stock profiles and say what each does to the design (a 36 x 90 slat at 1:15 is 2.4 x 6, so 3x5 means 45 x 75 real). Prefer whole sticks over ripped ones, and a wider board over an exact one when it cuts the piece count. Check the longest member against the stick length. Give a rough stick count and cost per option.

## Procedure

1. **`fab_model.py`**: a parametric copy of the version script. Replace the stock sizes by stick mm x scale, and derive every number that encoded the old section (wall build-ups, laps, offsets written as literals). Tag each member `obj['stock'] = '3x5'` (thickness x face in mm). A part that is not cut from sticks (a slab, a sheet panel) gets no tag: it is drawn, and left out of the cut list. Keep the overlap and contact checks and end with `export_members.write_members(...)`, passing the frame lines and levels the drawings need as extra keys.
2. **Make it buildable, and write each change in the README.** One long member instead of one piece per bay. Webs and rungs run to the far edge of what they join, for a glue lap. No stubs under 5 mm. A piece as long as the stick has zero slack: say so.
3. **`fab_cutlist.py`**: prices (`{'3x5': 0.40}`, EUR per stick) and supplier text, then `cutlist.write_cutlist`. It asserts every tagged piece fits its stick section, which catches a wrong tag and a slab tagged as a stick.
4. **`fab_drawings.py`**: the sheet list with `drafting.SheetSet`. Usual set: plans per layer, a plan section, elevations, two sections, one glue-up template per planar assembly (frame, wall panel), an unrolled sheet for any folded or ruled surface, axonometrics per viewer layer. One drawing per sheet is one call; a composed sheet is built by hand:

```python
sheets = SheetSet(scale, 'Experiment NN - Title', 'Run vXX, stick model', viewer_url=URL, studio='{protocell:labs}')
wall = Drawing(panel, X, Z)                                    # viewer at cross(X, Z) = -y
add_marks(wall, 'level', [(0, '+0'), (100, '+100')])           # positions in model mm
sheets.view('Wall template', wall, note, labelled=panel, layers=depth_layers(panel, wall.toward))

sheet = sheets.blank()                                         # several drawings on one sheet
ox, oy = place(main.bounds(), sheet.w, sheet.h)                # raises if it does not fit at 1:1
main.paint(sheet, ox, oy); paint_extras(sheet, main, ox, oy)
annotate(sheet, main, frame, layers, ox, oy)
side.paint(sheet, ox + main.bounds()[2] + 24 - side.bounds()[0], oy)
sheets.add('Frame template', sheet, note)                      # title block and number
sheets.write(os.path.join(HERE, 'pdf'), os.path.join(HERE, 'svg'))      # HERE = fabrication/<Run>/
```

5. **Look at every sheet** (below), then write the README: decisions, geometry changes, run commands, sheet list, known limits.

## Sheet conventions

- Every number on a sheet is model mm, levels included. Say so in the title block. Real metres appear only in the check bar.
- The length is written on the piece. A lollipop beside it carries the stick profile and the layer. **L1 lies on the paper**, higher layers stack towards the viewer; a template is drawn as seen from above the table.
- A layered assembly gets three views on one sheet: the template with the middle layer grey (`Drawing(..., shade=is_web)`, a function of a member), a side view with the layer codes, and a small axonometric. `annotate` labels plies that share one outline once, with the codes joined (`L2+L4`).
- `Drawing(members, right, up, cut=c)` removes what is nearer to the viewer than `c`, measured along the viewer axis cross(right, up). With `X, Z` the viewer stands at -y, so the section at y = 700 looking towards +y is `cut=-700`. A section plane that lands on a seam between boards cuts nothing: move it a fraction of a board.
- An axonometric that is not at model size needs its own `scale_text` ('Axonometric, scale 1:20.').
- Title block: sheet number and title, project, model, 100 mm check bar, studio mark in MEK-Mono, QR code to the viewer model, scale, units, date. Printing is at 100 %. The layout is `title_blocks.FOOTERS['k']`; `SheetSet(..., footer='a')` to `'k'` picks another, and `tools/footer_study/pdf/00_all_versions.pdf` shows them all. `subtitle` fills the MODEL field, so keep it short ('GPT-6 v02, stick model').
- `SheetSet.write` prints the PDFs with headless Chrome, which embeds the fonts (Segoe UI from Windows, MEK-Mono from `viewer/fonts`). The SVGs name the fonts without embedding them; `sheet_png.py` adds MEK-Mono when it rasterizes.

## Checking the sheets

`SheetSet.write` also writes SVG, the quickest thing to look at. Rasterize with `tools/sheet_png.py` (headless Chrome) and read the PNG:

```
python tools/sheet_png.py <set>/svg/11_frame_f0_template.svg out.png
python tools/sheet_png.py <set>/svg/11_frame_f0_template.svg zoom.png --zoom 150 120 60    # 60 mm square, mm from the top-left
```

Look at a whole sheet and at one joint at high zoom for every sheet type. Read one PDF with the Read tool to confirm it parses. When refactoring, keep a copy of `svg/` and compare byte for byte.

## Traps

| Symptom | Cause and fix |
|---|---|
| A member looks inside out or hollow in an axonometric, no lines missing | Faces wound inwards. Blender's renders hide it, the drawings cull back faces. `export_members` asserts it; fix the winding in `fab_model.py` (for `mesh_prism`, swap the two rings). Suspect this before calling odd geometry real. |
| Lines erased at joints in a Freestyle SVG | Freestyle drops edges lying in or near a touching face, and no inset cures it. Use `drafting.Axo` (`hidden_lines.py`): exact, seconds, not minutes. |
| Wrong overlaps in a tilted view | Painter's sorting (`Drawing`) is exact only for axis-aligned views. Tilted views are `Axo`. |
| `... does not fit the sheet` | The scale is too large for a 1:1 template. Use `min_scale`, or split the assembly. Do not shrink one drawing. |
| `SyntaxError` only inside Blender | Blender's Python is 3.11: no backslash inside an f-string expression. Anything `export_members` imports must parse there. |
| A patch script dies in bash with "unexpected EOF" | An apostrophe inside a heredoc. Write the script with the Write tool and run the file. |
| Tools not found when a script moves | The scripts reach `tools/` by a relative path: four levels up from `fabrication/<Run>/`. |
| `piece ... exceeds the stick` | A member longer than the stock. Splice it on a support in `fab_model.py`. |
| `... does not fit the 3x5 stick it is tagged with` | A wrong tag, or a slab or panel tagged as a stick. Fix the tag, or leave `stock` unset. |
| Two lengths overprinted, lollipops stacked | Pieces that overlap in the view without sharing an outline. Label one subset per sheet, or pass fewer members to `labelled`. |

`.blend` files are git-ignored; `fab_model.py` regenerates them. Commit scripts, `members.json`, the cut list, the order, `pdf/` and `svg/`.
