# tools/

Code shared by CraftBot experiments. Two groups: the **modelling kits** an
experiment script imports (extracted from the Fable runs of experiments
01-13), and the **harness scripts** that run, check and export a model.
The skills in `skills/` say when and why; this folder is the how.

Start a new experiment from `experiment_template.py`. Put `tools/` on
`sys.path` (the template does it) and import what you need:

```python
import craftbot_lib as craftbot          # place_element, box, prism, collections
from planes import member, sloped_member, vz, Roof
import framing, sheathing, geometry2d as g2
```

## Modelling kits

| Module | Needs Blender | Contents |
|---|---|---|
| `craftbot_lib.py` (V 2.0) | yes | `place_element` (unchanged from V 1.1), `clear_scene`, nested `get_collection("A/B")`, `move_to`, `box` from corner coordinates, `prism` / `prism_x` / `prism_y` (convex, winding normalized), `mesh_prism` from two rings |
| `geometry2d.py` | no | half-plane clipping (`clip`, `clip_lin`, `clip_rect`, `clip_u`, `inset`), `strip`, `rect`, `area`, `line_isect`, `point_in_loops`, `scan_intervals`; member spacing `positions`, `count_fit`; ranges `split_range`, `strips`, `split_rows`; `tile` (sheets with holes), `wall_pieces` (polygon minus openings as piers / sills / lintels) |
| `planes.py` | yes | half-spaces `hs`, `vx`/`vy`/`vz`, `vertical_hs`, `cheek`, `mitre_clip`; planes `vplane`, `plane_nd`, `isect`; `Roof` plane object; `Frame`, `frame_prism` (polygon in any plane, cut by half-spaces on both faces), `slab_clip`, `subtract`; members `member` (box between two points, bearing insets), `sloped_member` (vertical-plane member with sloped top, clipped), `bar` |
| `ruled.py` | yes | `Ruled` bilinear surface, `ruling_member`, `quad_frame` / `surface_quad` (boards on best-fit patches, residual recorded), `surf_extent` |
| `framing.py` | yes | `stud_wall` (plates, studs, framed openings, noggins), `clad` (upright sheets), `tile_sheets` (decks), `boards`, `wall_along_x` / `wall_along_y` (solid walls with openings), `roof_profile` / `roof_piece` (split at the ridge), `flight` (stair), `halved_brace`, `rect_fn` |
| `sheathing.py` | yes | `Facet`, `sheathe_facet` (rows of mitred boards from two-level outlines), `row_pieces`, `make_board`, `drop_member`, `report_protrusions` |

Where each helper came from is in the module docstrings. Rules the kits
enforce so the overlap check stays exact: every solid is convex, a
member with a bird's mouth is body + tail, a wall with a hole is pieces,
prisms are wound outward, and `place_element` replaces an object of the
same name (name every piece with all its loop indices).

## Harness scripts

| Script | Purpose |
|---|---|
| `render_views.py` | Run an experiment headless, render Workbench views (outlines on, per-collection colours, hide lists, close-ups, section cuts), save the `.blend`, run the overlap check, print the pair families and the contact check, write every pair to `<prefix>_pairs.txt`. Views come from a small Python file passed with `--views`; the default is four orbit views. |
| `run_experiment_headless.py` | The original minimal runner (four views, no outlines, no check). Kept for the README examples. |
| `check_overlaps.py` | Separating-axis interpenetration check over every pair of mesh objects; run on a saved `.blend` or import `find_overlaps`. Cannot see missing geometry, so always look at the renders too. |
| `check_contacts.py` | Contact check: every mesh object must have another within 2 mm (touching counts). Lists floating members, which the overlap check cannot see: treads on nothing, boards nailed to nothing, studs short of their plate. |
| `triage.py` | Groups penetrating pairs into name families (pure Python): one row per geometric cause with a count, depth and example, so a version with hundreds of pairs reads as three or four fixes. |
| `api_card.py` | Generates `API.md`, the compact card of every kit function and class with signature and first docstring sentence, from the source with `ast`. `--check` fails when the card is stale. Agents read the card, not the modules. |
| `closeout.py` | One command per close-out: `version NN vXX` (export, layers bake and audit, index, view set, renders, viewer screenshot) and `run NN --session-id ID` (rationale sections, hand-off files, prompt file, callouts, API card, index, transcript copy last). Writes `closeout_*.md` with pass or fail per step. |
| `experiment_template.py` | Starting point for a new experiment script (parameter block, derived levels, kits, named collections). Renders clean through `render_views.py`. |
| `views_template.py` | Starting point for an experiment's `views_fable.py` (view keys explained, mandatory views, colours). |
| `export_model_json.py`, `export_all_models.py`, `model_export_core.py`, `layers.py`, `callouts.py` | Web viewer export pipeline (see the root README). |

```
blender --background --python tools/render_views.py -- <experiment.py> <abs_out_prefix> [--views views.py] [--lib <dir>] [--only 01,02] [--tol 1.0]
blender --background model.blend --python tools/check_overlaps.py -- [tolerance_mm]
blender --background model.blend --python tools/check_contacts.py -- [tolerance_mm] [ignore_prefix,...]
python tools/api_card.py [--check]
python tools/closeout.py version 14 v09
python tools/closeout.py run 14 --session-id <id>
```

A views file is plain Python with a `VIEWS` list (and optional `COLORS`,
`RESOLUTION`); start from `views_template.py`. `M` is the experiment's
namespace so a section cut can be placed at `M["z_floor"](3) + 1.3`. The
per-experiment `Fable/render_fable.py` files are the pre-tools renderer;
their `VIEWS` lists show a full view set for each building.

`API.md` is the generated card of the kits; regenerate it after changing a
docstring or a signature (`closeout.py run` checks that it is current).

## Tests

```
python -m unittest discover tools/tests                                   # pure-Python modules
blender --background --python tools/tests/blender_smoke.py                # every Blender kit, 0 overlaps expected
```
