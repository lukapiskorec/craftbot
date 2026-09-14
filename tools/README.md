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
| `geometry2d.py` | no | half-plane clipping (`clip`, `clip_lin`, `clip_rect`, `clip_u`, `inset`), `strip`, `rect`, `area`, `line_isect`, `point_in_loops`, `scan_intervals`; member spacing `positions`, `count_fit`, `columns` (boards across a run, a sliver remainder shared by the last two); ranges `split_range`, `strips`, `split_rows`, `enforce_max` (splices on supports for members over stock length); `lap_length` (halving-joint zone of two crossing members); `tile` (sheets with holes), `wall_pieces` (polygon minus openings as piers / sills / lintels) |
| `planes.py` | yes | half-spaces `hs`, `vx`/`vy`/`vz`, `vertical_hs`, `cheek`, `mitre_clip`, `guarded_hs` (a clip applied only when the member's far end lies inside it); planes `vplane`, `plane_nd`, `isect`; `Roof` plane object; `Frame`, `frame_prism` (polygon in any plane, cut by half-spaces on both faces), `slab_clip`, `subtract`; members `member` (box between two points, bearing insets), `sloped_member` (vertical-plane member with sloped top, clipped), `bar` |
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
| `render_views.py` | Run an experiment headless, render Workbench views (default) or Cycles presentation views (`--style cycles`), save the `.blend`, run the overlap and contact checks. Cycles defaults to a foundation-free render, supports paired states, and records settings in JSON. |
| `cycles_style.py`, `views_cycles_study.py` | Nishita blue-sky Cycles setup, white plaster and desaturated material palettes. Opaque presentation shaders ignore sub-millimetre and back-facing shadow hits to prevent black patches where closed members touch or intersect (`--overlap-shadow-epsilon`, default `.001`); camera rays and ordinary front-facing shadows are unchanged. The study view file supplies low orthographic cameras, sun variants and Fable v09 material roles. |
| `views_cycles_layer_series.py`, `presentation_facades.py` | Four matched full/open/frame views. Visibility comes from `layers.py`; facade labels support cardinal and signed-axis names with a geometric fallback. |
| `compose_presentation_batch.py` | Apply the default Grade 3 Levels adjustment and adaptive 1 px line composite to every source pair, then write a manifest and HTML gallery. |
| `render_gallery.py` | Build a local HTML comparison gallery from a Cycles `<prefix>_settings.json`, with palette/light filters, a foundation toggle and full-resolution links. No Python dependencies. |
| `run_experiment_headless.py` | The original minimal runner (four views, no outlines, no check). Kept for the README examples. |
| `check_overlaps.py` | Separating-axis interpenetration check over every pair of mesh objects; run on a saved `.blend` or import `find_overlaps`. Cannot see missing geometry, so always look at the renders too. |
| `check_contacts.py` | Contact check: every mesh object must have another within 2 mm (touching counts). Lists floating members, which the overlap check cannot see: treads on nothing, boards nailed to nothing, studs short of their plate. |
| `triage.py` | Groups penetrating pairs into name families (pure Python): one row per geometric cause with a count, depth and example, so a version with hundreds of pairs reads as three or four fixes. |
| `api_card.py` | Generates `API.md`, the compact card of every kit function and class with signature and first docstring sentence, from the source with `ast`. `--check` fails when the card is stale. Agents read the card, not the modules. |
| `closeout.py` | One command per close-out: `version NN vXX` (export, layers bake and audit, index, view set, renders, viewer screenshot) and `run NN --session-id ID` (rationale sections, hand-off files, prompt file, callouts, API card, index, transcript copy last). Writes `closeout_*.md` with pass or fail per step. |
| `experiment_template.py` | Starting point for a new experiment script (parameter block, derived levels, kits, named collections). Renders clean through `render_views.py`. |
| `views_template.py` | Starting point for an experiment's `views_<slug>.py` (view keys explained, mandatory views, colours). |
| `export_model_json.py`, `export_all_models.py`, `model_export_core.py`, `layers.py`, `callouts.py` | Web viewer export pipeline (see the root README). |
| `capture_knoll.mjs` | Records the viewer's knolling sequence to an mp4 (by default model, stacked, flat, back to the model; `--sequence` picks the arrangements and their order, `--lock` holds one framing so only the geometry moves) by driving headless Chrome over the DevTools protocol. Node, no dependencies; needs ffmpeg on PATH. `--help` lists the style, view, camera, timing and frame-size options; the root README has the table. |

```
blender --background --python tools/render_views.py -- <experiment.py> <abs_out_prefix> [--views views.py] [--lib <dir>] [--only 01,02] [--tol 1.0]
blender --background model.blend --python tools/check_overlaps.py -- [tolerance_mm]
blender --background model.blend --python tools/check_contacts.py -- [tolerance_mm] [ignore_prefix,...]
python tools/api_card.py [--check]
python tools/closeout.py version 14 v09 [--agent "Opus 5.1"]
python tools/closeout.py run 14 --session-id <id> [--agent "Opus 5.1"]
node tools/capture_knoll.mjs [--model <exp>/<agent>_<v>.json] [--style mono] [--help]
```

A views file is plain Python with a `VIEWS` list (and optional `COLORS`,
`RESOLUTION`); start from `views_template.py`. `M` is the experiment's
namespace so a section cut can be placed at `M["z_floor"](3) + 1.3`. The
per-experiment `Fable/render_fable.py` files are the pre-tools renderer;
their `VIEWS` lists show a full view set for each building.

### Cycles presentation study

Use `--factory-startup` to avoid loading interactive user add-ons in a headless run.
The timestamped directory keeps each comparison batch together:

```bash
prefix="outputs/$(date +%Y-%m-%d_%H%M%S)_cycles_style/fable_v09"
blender --background --factory-startup --python-exit-code 1 --python tools/render_views.py -- \
  experiments/14_Becher_Studies_Amalgamated_Structure/Fable/experiment_14_fable_v09.py \
  "$prefix" --style cycles --views tools/views_cycles_study.py
python tools/render_gallery.py "${prefix}_settings.json"
```

The study renders 3072 × 3072 PNGs at 128 samples with adaptive sampling and
denoising. It prefers an available GPU (OptiX first), otherwise CPU. For a quick
preview add `--only white_crosslight --resolution 1024x1024 --samples 32 --no-check`.
`--only` takes base view names and always includes both foundation states.

Copy the study views file to tune `CYCLES` (sky strength, sun diameter/intensity,
exposure, samples, noise threshold, foundation collections and collection-to-material
roles). Per-view `palette`, `sun_rotation`, `sun_elevation`, `azim`, `elev`, and
`margin` control the comparison. Negative camera elevation looks up from below.
Hide lists work as in Workbench; paired views use identical framing. All palettes
keep glass clear (transmission 1, roughness .015, neutral tint, IOR 1.45), including
white plaster. Collection/object names provide automatic material roles; use
`--material-role COLLECTION=ROLE` for ambiguous names. Foundations are detected
by collection name, or specified with `--foundation-collections`. Missing explicit
names fail; a model without detected foundations produces one foundation-free state.

`<prefix>_settings.json` records camera transforms, sun angles, colors, visibility
counts, render time and quality settings for each completed PNG. The `.blend`
retains the final camera/material/light setup with collections shown, matching
the harness's existing save behavior. The original model script is unchanged.

```bash
blender --background --factory-startup --python-exit-code 1 --python tools/tests/cycles_smoke.py
```

### Render any model with CLI controls

No views file is required. Both `.py` generators and saved `.blend` models work.
From the repository root in bash or zsh:

```bash
model='experiments/14_Becher_Studies_Amalgamated_Structure/Fable/experiment_14_fable_v09.py'
out="outputs/$(date +%Y-%m-%d_%H%M%S)_cycles_lines"
blender --background --factory-startup --python-exit-code 1 --python tools/render_views.py -- \
  "$model" "$out/cycles" --style cycles --resolution 3072x3072 --samples 128 \
  --palettes washed --edges none \
  --azimuth 305 --elevation -25 --margin 1.16 \
  --sun-rotation -160 --sun-elevation 45 --sun-size 3 --sun-intensity 0.4 \
  --world-strength 0.2 --fill-strength 0.25 --exposure 0 \
  --glass-transmission 1 --glass-roughness 0.015 --glass-ior 1.45 \
  --foundation hide --foundation-collections Foundation --no-check
blender --background --factory-startup --python-exit-code 1 --python tools/render_views.py -- \
  "$model" "$out/lines" --style workbench --workbench-line-mask \
  --resolution 3072x3072 --azimuth 305 --elevation -25 --margin 1.16 \
  --foundation hide --foundation-collections Foundation --no-check
blender --background --factory-startup --python-exit-code 1 \
  --python tools/adjust_line_levels.py -- \
  "$out/lines_view_main.png" "$out/lines_levels.png" \
  --shadow-anchor .90 --output-white .96
blender --background --factory-startup --python-exit-code 1 \
  --python tools/composite_line_overlay.py -- \
  "$out/cycles_view_main_washed_none_no_foundation.png" \
  "$out/lines_levels.png" "$out/composite.png" \
  --light-strength .28 --dark-strength .88 --gamma .75 \
  --mask-threshold .03 --line-width 1
```

These presentation values are also stored as defaults in code: pale-washed
materials and the `305/-25` cross-light view in `cycles_style.DEFAULT_VIEW`,
foundation hiding and Cycles quality in `cycles_style.DEFAULTS`, Grade 3 Levels
in `adjust_line_levels.py`, and the adaptive 1 px blend in
`composite_line_overlay.py`. The explicit values above keep each render auditable.

For the four-view series, use `--views tools/views_cycles_layer_series.py` for
both the Cycles and Workbench source renders. It fixes one camera across full,
south/east open, south/west open and exposed-frame views. The open views hide
only exterior and interior cladding assigned by `layers.py`; windows remain.
The frame view shows exactly the viewer's frame layer, including wall
substructure, and hides every other layer. `views_cycles_presentation_series.py`
is retained as a compatibility name for the same series.

Pass `--foundation show` to both source renders to retain foundations. For the
seven above-camera views, use `--views tools/views_cycles_layer_series_above.py`:
roof-on and roof-off each include full, south/east open and south/west open
states, followed by a frame view. Roof-off hides the viewer's roof layer while
keeping structural rafters and trusses. A uniform background for camera,
glass-transmission and glossy reflection rays, sampled from the approved sky as sRGB
`(0.57647, 0.66275, 0.75686)`, prevents the Nishita lower hemisphere from
rendering black directly, through glazing or in glazing reflections without
changing diffuse lighting.

`--isolate A,B` renders only the named collections and descendants and excludes
everything else from camera fitting. This separates compound scripts cleanly;
for example, experiment 07 Fable uses `--isolate Old_House` and
`--isolate Wrap,Cube`, while experiment 08 ChatGPT uses
`--isolate Structure,WallPanels` and `--isolate Structure,WallSlats`.

Change `$model` and the foundation collection names for another model. Omit
`--foundation-collections` to detect foundation/footing/plinth/podium collections
automatically. Models with no detected foundations get a single state. Use
`--material-role MyGlass=glass --material-role MySteel=metal` to override automatic
name matching. Roles are `timber`, `cladding`, `concrete`, `metal`, `glass`.
Imported meshes need their panes and cladding boards to be separate geometry;
these settings cannot add seams to a single unsegmented wall or separate glass
that has been joined into its frame.

| Option | Meaning |
|---|---|
| `--palettes white` | One palette; comma-separated lists expand the view matrix |
| `--workbench-line-mask` | Flat white, opaque Workbench render with thin black object outlines |
| `adjust_line_levels.py --shadow-anchor .90` | Preserve line gray values at or below `.90` |
| `adjust_line_levels.py --output-white .96` | Linearly map the light-gray range toward `.96`; lower values make faint lines darker |
| `--light-strength .28` | Composite line opacity over light Cycles pixels |
| `--dark-strength .88` | Composite line opacity over dark Cycles pixels |
| `--gamma .75` | Curve controlling how quickly line strength rises as the source gets darker |
| `--mask-threshold .03` | Ignore near-white background variation when extracting the adjusted line mask |
| `--line-width 1`, `2` | Preserve the native line width or use a two-pixel raster kernel |
| `--fill-strength .25` | Neutral diffuse environment fill; `0` reproduces the original dark undersides |
| `--glass-transmission 1` | Full transmission in every palette, including white |
| `--glass-roughness .015` | Clear glass; increasing this makes it frosted |
| `--glass-ior 1.45` | Refraction and Fresnel reflection; 1 removes the interface reflection |
| `--hide Cladding,Roof` | Hide named collections and descendants for frame views |
| `--isolate Old_House` | Render and frame only named collections and descendants |
| `--foundation both`, `hide`, `show` | Paired states, foundation-free only, or foundation only shown |
| `--sun-rotation`, `--sun-elevation`, `--sun-size` | Degrees; the first two set direction, the last controls shadow softness |
| `--sun-intensity`, `--world-strength`, `--exposure` | Sun, sky and overall exposure controls |
| `--azimuth`, `--elevation`, `--margin` | Orthographic framing; negative elevation looks upward |
| `--resolution 3072x3072`, `--samples 128`, `--noise-threshold .015` | Output size and sampling quality |

The line workflow renders the same camera twice. Workbench supplies a white opaque
image with gray antialiased object outlines; Cycles supplies materials, sky, glass and light.
`adjust_line_levels.py` preserves dark lines and linearly compresses only the
light-gray part of the sRGB spectrum. `composite_line_overlay.py` then derives a
mask and multiplies it over the Cycles pixels. The source geometry and Cycles shading
remain unchanged. Separate cladding boards produce separate outline boundaries;
a single joined wall does not gain invented internal seams.

There is no added ground plane. Nishita alone provides little illumination to
downward-facing surfaces. Fill is added only for diffuse rays, preserving the
camera's sky and the environment seen through/reflected in clear glass. A numeric
cube test gave identical underside brightness at world Z=0 and Z=-1000 (0.0087),
and brightness 0.1937 with fill .25, so lowering the model/ground is unnecessary.

For the focused Fable revision, pass `--views tools/views_cycles_refinements.py`
instead of the palette/camera options above: 24 renders include main and frame
views. CLI values override file settings. `--only white_main,white_frame` limits
that matrix. Run the renderer with `-- --help` to see every option.

`API.md` is the generated card of the kits; regenerate it after changing a
docstring or a signature (`closeout.py run` checks that it is current).

Run folders: every subfolder of `experiments/<exp>/` except `input/` and
`references/` is one run, named after the model that produced it (`Fable`,
`ChatGPT 5.1`, `Opus 5.1`). File names inside use the slug, the folder name
in lower case with only letters and digits kept (`fable`, `chatgpt51`,
`opus51`); `agent_slug` and `run_folders` in `export_all_models.py` are the
one place this is defined. `closeout.py` needs `--agent` only when an
experiment has more than one run folder.

## Tests

```
python -m unittest discover tools/tests                                   # pure-Python modules
blender --background --python tools/tests/blender_smoke.py                # every Blender kit, 0 overlaps expected
```
