# Experiment 13 – Fable run: design rationale

Single record of *what* was built and *why*, written by the model at the end of
the run (2026-08-20/21). Kept because Claude Code transcripts redact the model's
thinking; only messages, tool calls and tool results survive in the `.jsonl`.

## 0. About this document (template)

This file is the template for future experiment runs
(`experiment_NN_<model>_design_rationale.md`). Sections and their purpose:

| § | Section | Purpose |
|---|---------|---------|
| 0 | About this document | Template note (this table). |
| 1 | How to run / outputs | Exact command, view legend, file naming, collections — enough to regenerate everything. |
| 2 | Reading the inputs | Which manual figures/pages were used and how they became numbers and rules; where the model deliberately deviated from the source. |
| 3 | Reading the reference code | Key dimensions and conventions inherited from earlier scripts; mistakes made while reading them. |
| 4 | Why the frame/model had to change | Problems found in the inherited model that blocked the task, and the fix chosen vs. alternatives. |
| 5 | Core modelling decisions | The few decisions that made the result possible (representation, algorithms), with rejected options. |
| 6 | Detailed geometry | Derivations, edge cases, evolution across versions and why each earlier variant was dropped. |
| 7 | Verification | Visual and numeric checks, their false positives, what was *not* verified. |
| 8 | Iterations | One row per saved version: change → what the renders/checks showed. |
| 9 | Scope and known simplifications | What was deliberately left out or approximated. |

Sections can be added, merged or renamed as the experiment demands (e.g. a
"Parameter study" or "Structural check" section); keep the numbering and the
"what vs. why, including rejected options" spirit. Write the rationale at the
end of the run while the reasoning is still in context, then archive the
session transcript last.

## 1. How to run / outputs

Every iteration `experiment_13_fable_vNN.py` was executed in background
Blender 4.3 by `render_fable.py` (Workbench, object outlines on so coplanar
boards stay distinguishable), producing `*_blender_view_NN.png` and a `.blend`.
Run from this folder:

```
blender -b --python render_fable.py -- experiment_13_fable_v04.py ../input <abs_out_prefix> [01,05,...]
```

Views: 01–04 orbit, 05 top, 06 framing only, 07/09 dormers (with/without
boards), 08 south wing, 10 dormer close-up, 11 wing valley, 12 east hip apex.
v01 has views 01–09 only (10–12 were added from v02).

Construction rules applied (CMHC Fig. 98, closed method): 19 × 184 mm boards
edge to edge, parallel to the eaves on every facet, last row ripped at the
ridge; every joint over a rafter (0.6 m main grid, 0.4 m dormer grid), 3.6 m
stock, odd rows start with a half board; mitred ends at hips, valleys, ridges.
Collections: `Timber_Framing/{Main_Roof,South_Wing,Dormers}` and
`Sheathing/{Main_Roof,South_Wing,Dormers}`. Final model: v04, 622 boards.

## 2. Reading the inputs

- `wood_board_roof_sheating.png` (CMHC Fig. 98) and
  `canadian_wood_frame_roof_extracted.md` §Lumber boards: closed method = boards
  edge to edge, ends supported, joints staggered; 19 mm thick; ≤ 286 mm wide;
  boards ≤ 184 mm take two nails per bearing → chose 184 mm (8 in. nominal) as
  the board width: it is the widest "two-nail" board and gives a readable
  number of rows. Boards run perpendicular to the rafters, i.e. parallel to the
  eaves, on every facet including hip triangles (the previous ChatGPT run had
  boards running up-slope on the E/W hips, which contradicts Fig. 98).
- Fig. 88 (dormers): sheathing is installed first, dormer framed on top,
  sheathing cut flush around the opening. I followed the "cut flush around the
  framing" rule for the main-roof cutout but did **not** add the bottom plate on
  the sheathing because the v18 frame stands its studs directly on the rafters;
  changing that would be a frame redesign, outside the sheathing scope.
- Fig. 99: sheathing fitted tightly at hips and valleys and nailed to the
  hip/valley rafter → boards must end *on* the hip/valley line with bevelled
  ends, not short of it.

## 3. Reading the reference code (v18 frame – key numbers that drove decisions)

Main roof 18 × 9 m, slope 1:2, plate z = 0, ridge z = 2.25, rafters 38 × 184 at
0.6 m. Wing 6 × 6 m, ridge z = 1.5, valley top at (0, −1.5, 1.5). Dormers:
`half_w = (stud_width + 2·1.5·spacing)/2 = 0.94`, overhang 0.2 → eave at
ox ± 1.14, 35° pitch, top plate z = 1.22, ridge z = 2.018, header at y = 0.46.

Important: I initially mis-estimated the dormer half-width as 0.49 m (forgot the
`2 · support_half` term) and designed the first cutout on that basis → v01's
self-intersecting cutout. Lesson recorded: derive dormer dimensions with the
same function the frame uses (`dormer_geom` replicates
`build_dormer_on_north_slope`) rather than by hand.

Member orientation conventions needed for the protrusion math:
`create_prismatic_member` puts width on local X (horizontal, across the member),
depth on local Y (perpendicular to the member in the slope plane), length on Z;
`rafter_between` puts length on X, width on Y, depth on Z. The generic
protrusion formula Σᵢ eᵢ·|aᵢ·n| over the three scaled local axes avoids caring
about which convention a member used.

## 4. Why the frame had to be corrected before sheathing

The user asked only for sheathing, but "no geometric inconsistencies" is
impossible on the v18 frame as-is:

- **Hips are deeper than commons** (184 + 50 mm) and centred on the plane
  intersection, so their top edge sits ≈ 111 mm above the centre-plane versus
  92 mm for the rafter tops: they would pierce the boards by ~25 mm. Wing hips
  and valleys (1.25 × depth) pierce by ~24 mm. Standard carpentry fix is
  "dropping the hip" (lower the seat cut); I implemented that as a translation
  along the member's own depth axis, computed per member from the adjacent
  facets, rather than hand-tuning numbers. Alternative rejected: thin the hip
  section to 181 mm — hides the issue instead of modelling the real detail.
- **Dormer valley rafters** in v18 run from `(x_left, back_y)` to the header,
  which lies in the main plane but *not* in the dormer roof plane (130 mm off at
  the foot), so the dormer valley jacks would poke out of the dormer boards.
  Rebuilt on the true plane intersection, extended to seat on the doubled
  rafter at `x_left` (foot ends up at y ≈ 1.72 instead of 2.1). Everything
  depending on that line (jacks, braces, trimmed commons) was regenerated by
  name — `craftbot.place_element` deletes a same-named object, so re-creating
  by name is a clean way to override single members without copying 1200 lines
  of v18.
- **Dormer valleys vs dormer boards**: the dormer rafters are only 80 mm deep,
  so the 184 mm valley (main-rafter section) is 59 mm proud of the dormer
  sheathing underside → dropped 59 mm (it is then also 50 mm under the main
  boards, which is fine; jacks still land on it).
- **Square-edged ridge boards** have corners above the two sloped undersides
  (dormer ridge 11 mm, main/wing ridge 1 mm) → same drop pass.
- Collar ties and side top plates grazed boards by millimetres → trimmed.

## 5. Core modelling decisions

### 5.1 Boards are polygon meshes, not scaled cubes

The ChatGPT approach (one scaled cube per row) gives square ends. At a hip the
square ends of two facets' boards either overlap or leave a sawtooth gap,
because the hip line is diagonal in each board's frame. A board that is cut on
site has a bevelled (mitred) end. Modelling that requires a prism whose top and
bottom outlines differ → built directly with `bpy.data.meshes.new` from two
2D outlines. This is the single decision that made "no interpenetration, no
gaps" achievable.

### 5.2 Facet/outline model and the offset-plane trick

Every facet is described by origin O, eave direction U, up-slope V, normal N,
and the underside offset (half rafter depth). Outline vertices are never typed
in; each is the intersection of three planes (`isect`): two roof planes (hip,
valley, ridge) or a roof plane and vertical boundary planes (eave lines,
dormer eave x = const, front beam y = const). Doing this at two offset levels
("underside" and "top") means a shared edge between facets A and B is
A(h)∩B(h) for both facets at both levels → the two boards share one end face.

Evolution, with the reason each earlier variant was rejected:

1. **v01/v02 – clip at the centre-plane line (offset 0) for convex edges, at the
   top-surface line for concave edges.** Reasoning: centre-plane clipping at a
   convex edge leaves a V-gap but never overlaps; top-surface clipping at a
   concave edge (valley, dormer junction) makes tops meet and the end faces
   diverge downward. Worked, but the V-gap at hips/ridge is see-through once the
   hip is dropped (visible in v02 views 11/12), and the dormer ridge/junction
   apex did not lie on both lines, giving a slightly skewed top board.
2. **v03 – two outlines per board (underside + top).** Removes both problems and
   also makes the dormer apex consistent because three planes at one level meet
   at a single point that is on both of its edges.

Valley vs hip asymmetry considered: with symmetric offsets the top-surface
intersection is directly above the centre-line intersection for both, so the
same code handles hips, valleys and ridges. For the dormer/main junction the
offsets differ (40 vs 92 mm underside) so the junction line shifts ≈ 75 mm
toward the dormer ridge at the foot; the main boards therefore cantilever a few
cm past the valley rafter centre — within "fit tightly at valleys" tolerance and
preferable to a hole.

## 6. Detailed geometry

### 6.1 Main-roof cutout around a dormer (three attempts)

- Attempt A (design notes only): rectangle between doubled rafters + triangle
  where the dormer roof is above the main roof. Abandoned on paper because it
  would leave a void between the triangle base and the plate end and cut boards
  unsupported next to the studs.
- Attempt B (v01): heptagon rect ∪ triangle. Self-intersected because the
  dormer eave (±1.14) is outside the doubled rafters (±0.9 + stud half-width).
- Attempt C (v02+): pentagon = two eave lines + front beam face + two junction
  lines up to the apex. The dormer roof covers everything inside; the main
  boards run under the overhang up to the eave line. Side top plates were
  shortened to start where the main sheathing top passes under them (y ≈ 2.35)
  so the plate's back end does not sit inside a board.

### 6.2 Row layout, joints, stagger

- Rows start at the eave with full 184 mm boards; the ridge row is ripped
  (slivers < 40 mm merged into the previous row, as a carpenter would).
- Joint positions = rafter lines projected to the facet's u axis; a board run is
  cut at the farthest rafter within 3.6 m of its start; odd rows start with a
  1.8 m board → joints stagger and always fall on a rafter. Rafter grids: main
  x = −8.7…8.7 step 0.6 (commons + jacks happen to share one grid), E/W y = 0.6k,
  wing y = −4.5 − 0.6i and x = −3 + 0.6k, dormers y = 3.7 − 0.4i.
- Scan-line construction: a row strip is intersected with the outline (even-odd
  over outer + hole loops) at its bottom and top edge; matching interval counts
  give trapezoids with exactly bevelled ends. Where an outline vertex falls
  inside a row (valley apex, dormer apex, eave-back corner) the row is split
  into bands at those v values so each band is again trapezoidal. Alternative
  rejected: general polygon clipping with holes (a lot of code for three
  vertices), or decomposing facets into convex pieces (would create joints at
  arbitrary lines, not on rafters). The only remaining approximation is a
  ≈ 1 cm band at valley apexes where the underside and top vertex v differ and
  square ends are used.

## 7. Verification

- Visual: 12 fixed views incl. framing-only and close-ups; outlines on so
  coplanar boards are distinguishable; per-view bounding-box camera fit (the
  bounding-sphere fit from `tools/run_experiment_headless.py` left the model at
  ~40 % of the frame).
- Numeric: `report_protrusions` — for every framing member, if its bounding-box
  corners straddle a facet's underside and a corner lies inside the sheathed
  region (point-in-polygon, even-odd), report the excess. First version flagged
  dormer rafter tails that are entirely *above* the main boards (true positives
  of the test, false positives for the question), fixed by requiring the member
  to straddle the underside. v04: 0 hits.
- Not verified numerically: board-vs-board overlap. Argued by construction
  (shared planes/lines); a BVH overlap test would report touching faces too and
  was not worth the noise.

## 8. Iterations

| v | change | result |
|---|--------|--------|
| 01 | first full implementation | boards OK; dormer cutout self-intersecting (dormer eave overhangs the doubled rafters), collar ties graze dormer boards, bounding-sphere camera wastes frame |
| 02 | cutout = eave lines + front beam + valley lines; collar ties trimmed; per-view camera fit | clean layout; thin see-through gap along hips/ridge because boards were clipped at the rafter centre-planes |
| 03 | two-level outlines → mitred board ends; exact valley-apex rows | hips/valleys/ridge closed; dormer ridge board top corners 7 mm into boards |
| 04 | ridge boards included in the drop pass | 0 protrusions, 622 boards, final |

## 9. Scope and known simplifications

Rafter tails square-cut; no fascia/soffit; dormer wall bottom plate; ventilation
details; nailing. `tools/run_experiment_headless.py` untouched (a run-specific
renderer was added instead of changing the shared tool).
Frame numbers: hips dropped 28 mm (main) / 26 mm (wing hips, valleys),
dormer valleys 59 mm, dormer ridges 11 mm, main and wing ridge 1 mm. The ≈ 1 cm
band at each valley apex uses square instead of mitred ends.
