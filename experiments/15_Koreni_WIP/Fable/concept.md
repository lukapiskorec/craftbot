# Concept, experiment 15 (Koreni), Fable run

Version 2, 2026-09-09, after the research round (`sources.md`). Three variations of a long house on the Koreni plot, all three in one model on three copies of the terrain strip. Every number below has its datum and its source; "mine" marks my own derivation; "AHCD", "CMHC", "LHDG" cite the clauses in `sources.md`.

## 1. Site and terrain

### 1.1 Roles of the input images

| Image | Role | What it fixes |
|---|---|---|
| `input/site_02.png` | cadastral and contour plan, 1 : 500 style, north assumed up | plot outline and dimensions, contour spacing, the road |
| `input/site_01.png` | the same plot rotated with the axis horizontal, with the sketched house and section lines | where the house line sits in the plot, the pavilion at the road end, the section lines |
| `sketch_diagram_01` | base plan diagram | pavilion, bar, tick marks (bay/section lines), the fork at the far end (rejected, 2.1) |
| `sketch_diagram_02` | plan with green edges | which long side of each segment is the open side |
| `sketch_diagram_03` to `06` | plan parti options: fork, bent bar, hooked bent bar, straight bar with an ellipse | the straight bar of 06 is adopted; the ellipse is read as the far-end view/terrace |
| `sketch_diagram_07` to `09` | long sections | three principal rooms stepping down the slope, one folded roof, stairs at the level changes |
| `references/reference_01..43` | inspiration only (brief) | nothing; not compared against |

### 1.2 Coordinate system (mine)

- x runs along the plot axis from the road boundary (x = 0) downhill; y runs across the plot; z is height.
- z = 0 at the ground on the axis at x = 5 m, where the 0.5 m index contour that starts the house zone crosses the axis.
- Orientation: `site_02` read north-up. The west boundary runs from the road corner up-right at 25 degrees east of north (425 px across, 900 px along), so +x has bearing N25E. The road is at the SSW end, uphill. In the model +y points toward the WNW boundary (the side with the trees in `site_01`); the ESE neighbour (parcel 5537) is at low y. Label: ESE face = y_min face, WNW face = y_max face. The far end faces NNE, downhill.

### 1.3 Plot (site_02, dimensions printed on the drawing)

- West boundary 96.42 m; east boundary 72.23 + 1.61 jog + 23.04 m; far (NNE) end 20.11 m; road end 11.29 + 5.51 m on a skew.
- Calibration of `site_02`: 96.42 m over 995 px = 10.3 px/m (checked against 20.11 m over 207 px).
- The plot is a strip 96 m long, 16.8 m wide at the road widening to 20.1 m at the far end. Modelled as a rectangle 20 m wide (the taper is dropped: the house sits on the axis and never reaches a long boundary; recorded deviation).

### 1.4 Ground profile (mine, from the contour count)

Contours in `site_02` were counted by sampling pixels along the axis from the road end to the far end (method in `design_notes.md`): 19 orange index lines and 74 blue intermediates over 96 m. Read as 0.5 m index lines with 0.1 m intermediates, which gives 9.4 m of fall. The alternative reading (0.5 m intermediates) gives 46 m of fall, which the section sketches contradict (their own scale gives 8.4 to 10.8 m). The index lines cross the axis at x = 5.0, 16.0, 25.2, 32.4, 38.7, 44.5, 49.8, 53.9, 58.0, 61.9, 65.7, 69.5, 73.2, 77.2, 81.0, 84.1, 87.9, 91.6 m: the spacing tightens from 11 m per 0.5 m near the road to 3.7 m per 0.5 m beyond 50 m. Simplified to three straight segments, slopes increasing downhill (a concave profile, so the solid under it is convex, which the kits need):

| Segment | x range | fall | z at start | z at end |
|---|---|---|---|---|
| road shoulder | -6 to 0 | 5 % | +0.55 | +0.25 |
| upper | 0 to 26 | 5 % | +0.25 | -1.05 |
| middle | 26 to 50 | 8 % | -1.05 | -2.97 |
| lower | 50 to 100 | 14 % | -2.97 | -9.97 |

z(x) is used everywhere below; spot values: z(5) = 0.00, z(11) = -0.30, z(17) = -0.60, z(21) = -0.80, z(23) = -0.90, z(29) = -1.29, z(35) = -1.77, z(45.4) = -2.60, z(47) = -2.73, z(53) = -3.39, z(56) = -3.81, z(59) = -4.23, z(60) = -4.37, z(62) = -4.65, z(65) = -5.07, z(66) = -5.21, z(70) = -5.77, z(71) = -5.91, z(96) = -9.41.

No cross fall is modelled: the contours run close to perpendicular to the axis in the middle of the plot; the zigzags near the road (a small gully) and the oblique far-end contours are dropped. Stated assumption; the surface is a ruled sheet z = z(x) across the whole strip width. The CMHC rule that finished grade falls away from every wall at 5 percent (10 percent in the first 2 m) is recorded as not modelled: the skin keeps the surveyed profile.

Deviation from the sketches: sections 07 to 09 draw the ground steepening only beyond the last room (x about 66); the survey steepens from x = 50. The survey wins (brief: "model the actual terrain"), so the last room of the stepping variation stands higher above the ground than the sketch shows, and the bridge gets a taller undercroft.

### 1.5 Terrain model (recipe for the Builder)

- One terrain strip per variation: x from -6 to 100, y from 0 to 20 within its own strip origin, 106 x 20 m.
- Modelled as a skin, not a solid: a 0.30 m thick plate under the ground surface (top face at z(x)), one convex piece per profile segment (a parallelogram in (x, z) extruded along y: `prism_y`), so that sections show the ground as a line like the blue line of the sketches. The soil below is not modelled.
- Every element that crosses the skin (columns, walls, footings) gets a hole cut in the skin around it (`planes.Frame` on the segment's plane + `subtract`, or split the skin into strips along x at the crossing walls); footing tops sit below the skin underside. Where a house is cut into the ground, the skin stops at the outer face of the retaining wall and the retaining wall is the cut face.
- Three copies at strip origins y = 0, 30, 60 (strip width 20, gap 10): A on 0..20, B on 30..50, C on 60..80. Within each strip the bar sits on y = 7..13 (strip axis y = 10) and the pavilion on y = 9..15.

## 2. What the three variations share

### 2.1 Plan parti (sketches 01, 05, 06; sizes mine)

- The pavilion P at the road end: 6.0 x 6.0 m outside, x = 5..11, y = 9..15 (offset 2 m toward the WNW boundary: the hook of sketch 05 and the offset square of sketch 01). Sketch 01 reads it at 5.6 x 5.9 m (85 x 90 px at 15.2 px/m). It is the garage and entry: floor at +0.15 (CMHC: slab top 150 above the adjacent grade, z(5) = 0.00), garage door 2.4 x 2.4 in the x = 5 face, entrance door opening 0.95 wide with a 0.30 nib on the latch side (LHDG 3.1.4), a door in the x = 11 wall into the bar.
- The bar: straight, on the strip axis, 6.0 m wide outside (y = 7..13), from x = 11 to x = 66 (B and C) or 71 (A). Sketch 01 reads the bar at 3.5 to 4 m; widened to 6.0 m so an open plan fits (5.7 m clear between the glass lines); recorded deviation. The fork (sketch 03), bend (04) and hook wing (05) are rejected: the brief makes the section the variable, one plan isolates it, and sketch 06 shows the straight bar as one of the drawn options.
- The building line: 5 m from the road boundary (site_01 and the section sketches place the first volume one setback in from the boundary: 87 px at 16.6 px/m = 5.2 m).
- Far end: the house zone ends at x = 66 where the survey has fallen 5.2 m; A overshoots to 71 as a cantilever (sketch 06 draws the bar running past the bank).

### 2.2 Open side and closed side (sketch 02)

The green edges of sketch 02 alternate sides along the bar. Read as: each segment has one fully glazed long side and one closed side. Mapped to x (sketch px to m at 15.2 px/m from the road boundary at 340 px):

| Segment | x | open (glazed) side | closed side |
|---|---|---|---|
| 1 | 11..28 | ESE (y_min) | WNW (y_max) |
| 2 | 28..44 | WNW (y_max) | ESE (y_min) |
| 3 | 44..60 | ESE (y_min) | WNW (y_max) |
| 4 | 60..66 (A: 60..71) | WNW (y_max) | ESE (y_min) |

The closed side is a solid wall from floor to roof (200 mm concrete in B and C; in A a 200 mm insulated steel-stud panel, modelled as one solid, so the bridge does not carry a concrete wall). Doors and one 900 mm high strip window per segment are the only openings in it (LHDG 5.5.1: glazing at least 20 percent of a room's floor area; a 3 x 4 m room with a 900 x 4000 strip has 30 percent). The open side is glass in the facade grid of 2.3. At a switch (x = 28, 44, 60) the corner is glass to glass on both sides. Cores and partitions stand against the closed side.

### 2.3 Facade grid and members

Sources per line: AHCD = Architect's Handbook of Construction Detailing, CMHC = Canadian Wood-Frame House Construction, LHDG = London Housing Design Guide; clauses in `sources.md` section 1.

- Posts: steel SHS 150 x 150 at 4.0 m centres on the glazed side, x = 11, 15, ..., to the end, centre 0.10 m inside the outer face, from the floor slab top to the roof beam underside. On the closed side the wall carries the beam and there is no post. (mine)
- Roof beams: steel IPE 330 (modelled 160 x 330) transverse, one per post line, spanning between the post and the closed wall. (CMHC Table 18 by analogy: a 200 to 250 deep W section spans 5.8 m under a wood floor at 4.2 m tributary; one size up for a concrete deck; labelled)
- Roof deck: 200 mm concrete slab on the beams spanning 4.0 m (L/20, ACI practice, labelled); above it the insulation as a wedge 150 mm thick at the y_min edge rising at 2 percent to 270 mm at the y_max edge (AHCD 5-15 and CMHC: low-slope roofs drain at 2 percent minimum by tapered insulation; the drain line at the ESE edge is not modelled); in A and B a concrete parapet 200 thick, 600 above the slab top on all edges (AHCD 1-21: at least 305 above the roof surface; 270 + 305 = 575, rounded to 600); C's folded roof has a 150 mm fascia and no parapet (AHCD 5-37: gravel-stop face at least 100).
- Glazing: an AHCD storefront (6-6), glass supported within the one-storey opening between the slab and the roof beam. Mullions and transoms 51 x 152 (AHCD 6-6 catalogue sizes) at 1.333 m (three panes per 4 m bay; AHCD 6-11: spacing compatible with the bay), sill transom on the slab top, head transom 6 mm below the beam underside (the slip joint of AHCD Fig. 6-6(b)), glass 25 mm insulating units (AHCD 6-11) as one plate per pane on the mullion centreline, captured pressure-plate glazing (one solid mullion box includes the cover). The glazed end walls follow the same grid.
- Floor slabs: 200 mm concrete on ground over a 150 mm gravel layer (AHCD 1-1 minimum 100 for the slab; CMHC minimum 100 gravel plus 0.15 mm polyethylene, not modelled); 300 mm where suspended between plinth walls 5.5 m apart (L/20, ACI practice, labelled). Slab tops at least 150 mm above the adjacent finished grade or paving (CMHC ch. 7).
- Cores: 200 mm walls from the floor slab to the roof slab underside with pockets where a roof beam crosses them, no lid (full height after the structural review: they are the shear walls across y for the roof diaphragm, which has no other support between the pavilion and the far end); concrete in B and C, sheathed steel-stud panels in A (R-51). Core 1 of every variation holds a built-in store 1.2 x 2.5 m, 2.0 m high (LHDG 4.7.1: 3.0 m2 for five persons). Partitions between bedrooms 100 mm, stopped 25 mm under the roof beam or roof slab (they carry nothing; timber-framing skill).
- Concrete walls: pavilion, lower box and plinth walls 250 mm (CMHC Table 5: 250 retains up to 2.30 m when supported at the top); retaining walls 300 mm stems (CMHC Table 5 top entry: 1.50 m free-standing, 2.30 supported). Cantilever L-wall bases: width 0.6 H (H from the footing underside to the stem top), toe 0.15 H in front of the stem, 0.4 thick (standard cantilever-wall proportions, labelled; the manuals stop at braced basement walls).
- Footings: strip 0.8 x 0.4 m under every concrete wall (CMHC Table 4: at least 450 wide; projection 250 not more than the 400 thickness); pad 1.8 x 1.8 x 0.6 m under steel columns with a 300 x 300 x 30 base plate (CMHC Table 4 note 1 scaled from 3 m to 12 m column spacing; thickness at least the projection from the base plate); footing undersides 1.2 m below the finished grade at the wall face (CMHC Table 3, the only stated threshold; a local frost depth is not known). On sloping ground the strip footings step: each step at most 0.6 m high with a run of at least 0.6 m, joined by a 0.15 thick riser the width of the footing (CMHC Fig. 35).
- Stairs: risers 150 to 165 mm, going 280 mm, width 1.2 m, solid concrete flights (`framing.flight`), landings 1.2 m deep (at least the flight width), headroom at least 2.1 m above the nosing line (CMHC 1.95, AHCD tread at least 279 and riser at most 178, LHDG riser at most 170 and going at least 250: all met). A dogleg's upper flight starts one going beyond the lower flight's last riser (AHCD Fig. 3-10).
- Guards: 1.07 m at every interior stair void and open flight side (AHCD 3-10, 3-15; CMHC 1.07 above a 1.8 m drop); terrace balustrades 19 mm glass 1.10 m high in a floor shoe at the slab edge (AHCD 3-15), on every open edge more than 0.6 m above the ground.
- Doors: openings 0.9 x 2.1 m internal (LHDG 4.3.1 with hallways at least 0.9 wide); garage door 2.4 x 2.4; terrace door thresholds flush (LHDG 4.10.2, upstand at most 15 mm).
- Steel connections are drawn, not detailed: a girder seats on a cap plate 300 x 300 x 30 on a column; a transverse beam butts the girder web or the column face with top flanges flush; posts stand on the slab; roof beams sit on posts and walls. Bolts, welds, anchors, waterstops, drains, membranes and rebar are not modelled (brief).

### 2.4 Programme (mine; checked against LHDG in sources.md Q8)

Entry and garage 36 m2 (the pavilion, not counted in the GIA); living 60 to 80 m2; kitchen and dining 35 to 45 m2 (LHDG 4.4.1: the two together at least 29 m2, and 4.4.3: two separate living spaces for three or more bedrooms); study 12 m2; master bedroom 16 m2 with ensuite 6 m2; two bedrooms 12 m2 each (LHDG 4.5.2: a double at least 12 m2 and 2.75 m wide, met at the minimum); family bathroom 6 m2; utility and plant 8 m2; store 3 m2; a covered terrace at the far end at least 8 m2 (LHDG 4.10.1). About 215 m2 net against a 3b5p minimum of 86 to 102 m2 (LHDG 4.1.1); the bar gives 330 to 360 m2 gross. Ceilings 3.3 m clear or more everywhere against LHDG 2.5.

## 3. Variation A, the bridge

### 3.1 Spatial concept

One level floor at z = +0.90 from the pavilion to the far end, 60 m long, held clear of the falling ground. The house is a bridge with two abutments: the concrete pavilion at the road end and a concrete bedroom box that lands on the ground at x = 53..65; between them three pairs of steel columns; beyond the box a 6 m cantilevered terrace over the bank.

Levels: pavilion floor +0.15; bridge floor +0.90 (five risers of 150 mm inside the pavilion); lower box floor -3.30. The floor was +0.60 in version 1; raised 0.30 so the girders clear the ground by at least 300 mm at the pavilion (CMHC crawl-space rule used as the proxy, sources.md Q10).

Rooms along x on the bridge (y = 7..13): 11..15 entry hall with core 1 (utility, WC and the 3 m2 store, 4.0 x 2.4 m against the closed WNW side); 15..28 living; 28..44 kitchen and dining with core 2 (pantry and WC, 3.0 x 2.4 against the closed ESE side); 44..53 study and guest room with core 3 (bathroom 3.0 x 2.4); 53..59 stair hall (dogleg stair down through a slab opening 2.6 x 4.6 m, guard 1.07 around the void); 59..65 master bedroom with ensuite (core 4, 3.0 x 2.4); 65..71 covered terrace (roof continues, no glass, 1.10 m glass balustrade on the three open edges).

Lower box (concrete, x = 53..65, y = 7..13, floor -3.30, 4.0 m clear to the bridge slab underside at +0.70): 53.25..58.3 stair arrival hall (the lower flight and its landing take x = 53.7..58.24 across y = 9.4..12.0, so the hall is the room the stair lands in), a full-width partition at 58.3 with a door, 58.35..61.15 bedroom 2 (15.4 m2), 61.25..64.75 bedroom 3 with core 5 (bathroom 2.5 x 2.4 against the y_max wall at 62.25..64.75; 13.3 m2 net). Version 1 had bedroom 2 at 56..60, which the dogleg's footprint reduced to a 6.5 m2 alcove; rewritten after v04. Its far wall stands 1.77 m above the ground at x = 65 (z = -5.07); its near wall is cut 0.09 m into the ground at x = 53. Openings: a glass door 0.95 x 2.1 in the far wall onto the bank, and one window 1.2 x 1.2 with its sill 0.9 above the floor in the y_min wall of each bedroom (x = 59.2..60.4 and 62.4..63.6), the CMHC egress rule for below-grade bedrooms (opening at least 0.35 m2, sill at most 1.5 m above the floor); the y_min wall stands 0.8 to 1.3 m clear of the ground there, so the windows are above grade.

Ground clearance under the bridge girders (underside at +0.90 - 0.20 - 0.70 = 0.00): 0.30 m at x = 11 (the girder seats on the pavilion wall), 0.90 at x = 23, 1.77 at x = 35, 2.73 at x = 47, 3.39 at x = 53, 5.91 at x = 71.

```
z
+0.9 ____________________________________________________________ bridge floor
     |P |  |      |      |      |   |   lower box  |  terrace
 0.0 |__|  |      |      |      |   |______________|
  -1     \__|      |      |      |   |              |
  -2        \______|______|      |   |              |
  -3               ground \______|___|              |
  -4                              \  |______________|
  -5                                  \_____________\___
     x=5 11 15    23     35     47   53          65  71
```

### 3.2 Construction concept, bearing stack from the ground up

1. Pad footings 1.8 x 1.8 x 0.6 m under the three column pairs at x = 23, 35, 47 (undersides 1.2 m below z(x)); strip footings 0.8 x 0.4 m under the pavilion walls and the lower box walls, undersides 1.2 m below z(x), the box's long-wall footings stepped three times (0.56 m at x = 56, 59, 62; CMHC Fig. 35).
2. Base plates 300 x 300 x 30 on the pads; steel columns HEB 240 (240 x 240) from the base plates to the cap plates (300 x 300 x 30) under the girders, three pairs at y = 7.3 and 12.7; the pavilion's rear wall (concrete 250, x = 11) and the lower box's walls (concrete 250, x = 53 and 65) are the abutments.
3. Two longitudinal welded plate girders 700 deep x 300 wide, centred on y = 7.3 and 12.7, continuous from x = 11 to x = 71, top at +0.70; they bear on the pavilion rear wall, on the cap plates, on the lower box's two cross walls, and cantilever 6 m beyond x = 65. Spans 12, 12, 12, 6, 12 (over the box, seated on both walls), cantilever 6. Depth L/17 for the 12 m spans (mine; the manuals do not size plate girders).
4. Transverse floor beams IPE 300 (150 x 300) at 4.0 m from x = 11 to x = 71 between the girders, top flanges flush with the girder tops; at the column lines the transverse beam is the portal's cross member (moment-connected; drawn butting the girder web).
5. Floor slab 200 mm concrete on the girders and beams, top at +0.90, x = 11..71, y = 7..13, with the stair opening at x = 53.4..58.0, y = 9.4..12.0.
6. The bridge slab is also the lower box's roof: the box walls (250 mm) rise to the girder underside at 0.00 and the girders sit on them; between the girders the slab underside at +0.70 is the box ceiling.
7. Posts SHS 150 at 4.0 m on the glazed side, from the slab top to the roof beams; the closed-side panel wall carries the other end; roof beams IPE 330 transverse; roof slab 200, insulation wedge, parapet 600: roof slab top at +0.90 + 3.30 + 0.33 + 0.20 = +4.73, parapet top +5.33. Over the terrace the roof continues on posts without glass.
8. The pavilion: concrete box, walls 250, floor slab 200 on ground at +0.15 with the slab edge 0.15 above z(5) and a plinth at the downhill edge, roof slab 200 with its top at +3.65 (3.3 clear), parapet to +4.25; garage door in the x = 5 face; the door into the bar through the rear wall at x = 11 (the abutment), with the five risers just inside the bar.

Lateral system (corrected in the structural review after v04). The steel columns are pinned at both ends (base plate on the pad, cap plate under the girder; the transverse beam at a column line butts the girder web at the top flange, so no moment path exists and the "portal" of version 1 is withdrawn). Along x and across y alike, the bridge deck (200 slab, 6 m deep) is a diaphragm spanning 42 m between the two concrete boxes, the pavilion abutment at x = 11 and the lower box at 53..65, both on strip footings; depth to span 1:7. The roof: along x the closed-side panels are sheathed shear walls; across y the cores, full height from the slab to the roof underside and built as the same 200 mm sheathed steel-stud panels (a concrete core on a 200 slab mid-span between floor beams is the wrong load path on a bridge), take the roof diaphragm's reaction down to the deck; the pavilion box closes the uphill end.

## 4. Variation B, the cut

### 4.1 Spatial concept

One level floor at z = -2.60, the ground level of the axis at x = 45.4. Uphill of x = 45 the house is cut into the slope; downhill it stands on a concrete plinth of the excavated fill. The long glass sides of the cut half look at concrete retaining walls across a 2.0 m wide sunken strip (a linear courtyard along both sides, paved 0.15 below the floor); the plinth half looks out over the falling land. Cut and fill balance roughly: the trench 10 m wide by 34 m long by 1.2 m average depth removes about 400 m3; the plinth 6 x 21 m by 1.3 m average takes 165 m3 back and the rest grades the courtyard ends (approximate, mine; CMHC p. 64 states the principle).

Levels: pavilion +0.15 (garage and entry at road level); house floor -2.60, reached by a straight stair of 17 risers x 161.8 mm, going 280 (4.48 m run) inside the first bay of the bar, descending along x from x = 11.2 to 15.7 against the closed WNW wall, with a 1.2 m landing at the top inside the door and a 1.07 guard on its open side.

Rooms along x (y = 7..13): 11..16 stair and entry with core 1 (utility, WC, store) under the stair's high end; 16..30 living; 30..42 kitchen and dining with core 2; 42..48 study and family bathroom (core 3); 48..60 bedrooms 2 and 3 with a 100 mm partition at x = 54; 60..66 master bedroom with ensuite (core 4). A 4 m covered terrace at x = 66..70 on the plinth, roof continuing, glass balustrade 1.10.

Retaining walls: along both sides of the cut half at y = 5.0 and y = 15.0 (2.0 m from the glass), from x = 11 to x = 46, stem 300, stem top following the ground z(x) (from -0.30 at x = 11 down to -2.65 at x = 46, where the wall runs out), stem bottom at -3.15 on a base 0.4 thick; an end wall across at x = 11 from y = 5 to 15, which continues up as the pavilion's rear wall. These walls retain 2.3 m free-standing at x = 11 and the end wall 2.75 m: beyond the CMHC Table 5 limits (1.50 free-standing, 2.30 braced), so they are engineered cantilever L-walls, base 0.6 H (side walls H = 2.85 at x = 11: base 1.7 m; end wall H = 3.55: base 2.1 m), toe 0.15 H toward the courtyard, heel under the ground. Recorded in the deviation ledger. The courtyard paving at -2.75 is a 150 mm slab between the glass line and the wall. Downhill plinth: concrete walls 250 mm under both long faces and across the end (x = 70 for the terrace), from the slab underside down to a sloped bottom on a strip footing 1.2 m below z(x) (through any fill to undisturbed ground, CMHC p. 66).

```
z
  0.0 |P |
 -1   |__|\__ ground                              retaining wall top = ground
 -2        |  \______
 -2.6      |_______________________________________|______ floor
 -3        end wall        \______                 |plinth| terrace
 -4                                \______         |      |
 -5                                        \_______|______|__
     x=5  11        26        45.4          53     66     70
```

### 4.2 Construction concept, bearing stack from the ground up

1. L-wall bases 1.7 x 0.4 m (side walls) and 2.1 x 0.4 m (end wall), undersides at -3.55; strip footings 0.8 x 0.4 under the plinth walls and cores, undersides 1.2 m below z(x), stepped in 0.6 m steps.
2. Retaining wall stems 300 mm from the base to z(x): a trapezoid profile along x, split at x = 26 where the ground slope changes so each piece stays convex.
3. Floor slab 200 mm on ground from x = 11 to 46 (top -2.60) over a 150 mm gravel layer; suspended slab 300 mm from x = 46 to 70 spanning 5.5 m between the plinth walls. Courtyard slabs 150 mm, top -2.75, from the glass line to the retaining walls.
4. Posts SHS 150 at 4.0 m on the glazed side from the slab to the roof beams; the closed side per 2.2 is a 200 mm concrete wall floor to roof that carries the roof beams.
5. Roof beams IPE 330 transverse at 4.0 m; roof slab 200 with its top at -2.60 + 3.30 + 0.33 + 0.20 = +1.23; insulation wedge; parapet to +1.83. The stair bay x = 11..15.28 is a high bay: its roof is the pavilion's (slab top +3.65, parapet +4.25), because the entry landing at +0.15 sits above the low roof's beam underside at +1.03 and needs 2.1 m of headroom; the high bay's WNW side is the closed concrete wall carried up to +3.65, its ESE side the storefront to +1.03 with a 200 mm concrete spandrel wall above, and a transverse 200 mm wall closes it at x = 15.28 above the low roof. The stair hall is 5.9 m tall from -2.60 to the high roof underside. From the road the house shows the pavilion, the high bay beside it and beyond them the low parapet 2.1 m above the ground at x = 15 (z = -0.50). (Decided after v02; version 1 had the whole bar under the low roof, which left 0.9 m over the landing.)
6. The pavilion as in A, floor +0.15, roof slab top +3.65, but its rear wall at x = 11 is continuous with the end retaining wall below: one 300 mm concrete wall from the base at -3.55 to +3.65. Its floor slab bears on that wall and on the ground; the stair from the pavilion into the bar leaves through a door in the rear wall at +0.15 onto the landing and descends inside the bar.

Lateral system (corrected after v04). Along x: the retaining walls and the foundation and plinth walls below the floor, the closed-side concrete walls above it, the cores. Across y: below the floor the end wall at x = 11, the foundation walls and the plinth end wall; above it the end wall, the high bay's step wall at x = 15.28 (full width to the high roof) and the full-height cores (R-51); the roof beam frames are pinned (posts pinned, beams seated in pockets) and brace nothing. The slab on ground and the suspended slab are the floor diaphragm, the roof slab the roof diaphragm. The plinth 46..70 is a hollow undercroft as built (no earth pressure on its inside faces), not the filled box of version 1; the excavated soil grades the courtyard ends; an access opening in the x = 70 wall (R-53).

## 5. Variation C, the steps

### 5.1 Spatial concept

The floor steps down with the ground in four levels under one folded roof (sketches 07 to 09). Each level is about 18 m long, cut up to 1.3 m into the ground at its uphill end and standing up to 1.3 m above it at the downhill end, so every step has a retaining wall at its uphill end and a plinth at its downhill end. The roof is a single folded plane: it rises from the pavilion to a ridge at x = 11, where the tall living hall begins (sketch 09 puts the ridge at the uphill end of the second box), then falls at 8.2 percent to the far end, so every level has a tall uphill end and a 3.1 to 3.4 m downhill end.

Levels and rooms (y = 7..13 for the bar):

| Level | z floor | x | ground z at start / end | use |
|---|---|---|---|---|
| L0 | +0.15 | 5..11 | 0.00 / -0.30 | pavilion: garage and entry |
| L1 | -1.20 | 11..29 | -0.30 / -1.29 | living hall (tall end), core 1 (utility, WC, store) at 11..14 beside the stair |
| L2 | -2.55 | 29..47 | -1.29 / -2.73 | kitchen and dining, study, core 2 (bathroom) |
| L3 | -3.90 | 47..66 | -2.73 / -5.21 | stair hall 47..52 where stair 3 arrives, with core 3 (family bathroom) beside the flight at 49.4..51.9 on the y_max side; bedroom 2 at 52.1..56.0; bedroom 3 at 56.1..60.0; master bedroom with ensuite (core 4) at 60.1..66 (rewritten after v04: version 1 had the master at 47..54 with stair 3 arriving inside it) |
| terrace | -3.90 | 66..70 | -5.21 / -5.77 | covered terrace on plinth walls, balustrade 1.10 |

Stairs: three straight flights along x against the closed side of each segment, all 9 risers x 150 mm (1.35 m), going 280 (run 2.24 m): L0 to L1 at x = 11.0..13.3, L1 to L2 at x = 29.0..31.3, L2 to L3 at x = 47.0..49.3; 1.07 guards on the open side of each flight. Headroom under the roof at every flight is above 2.1 m (the roof underside is at least 3.1 m above the lower level everywhere).

Where a level is cut, a sunken strip 1.5 m wide runs along the glazed side between the glass and the side retaining wall, paved 0.15 below the floor (CMHC slab-above-grade rule).

Roof: plane R1 top from z = +3.40 at x = 5 to +3.90 at x = 11 (rising 8.3 percent over the pavilion, 3.05 clear at the low end); plane R2 top from +3.90 at x = 11 to -0.60 at x = 66 (falling 8.2 percent), continuing to x = 70 over the terrace (-0.93). Clear heights (floor to roof slab underside = top - 0.20): L1 4.9 m at x = 11, 3.42 m at x = 29; L2 4.77 m at x = 29, 3.30 m at x = 47; L3 4.65 m at x = 47, 3.10 m at x = 66. The rule is at least 3.0 m clear at every downhill end (LHDG 5.4.1 asks 2.5); version 1 said 3.3, which was the roof top minus the floor without the slab.

```
z
 +4  ridge
 +3  /---\____ roof R2 (8.2 %)
  0 |P |      -----_____
 -1 |__|L1          -----_____
 -2    ¯¯|___ L2           -----_____
 -3      ¯¯¯¯¯¯¯¯|___ L3          -----____
 -4 ground        ¯¯¯¯¯¯¯¯¯¯¯|________________ terrace
 -5                            ¯¯¯¯¯ \_____
     x=5 11        29         47          66  70
```

### 5.2 Construction concept, bearing stack from the ground up

1. Strip footings 0.8 x 0.4 m under every concrete wall, undersides 1.2 m below z(x), stepped in steps of at most 0.6 m with runs of at least 0.6 m (every 7.5 m on the 8 percent segment, every 4.3 m on the 14 percent segment).
2. Step retaining walls: at x = 11 (from -1.70 to +0.15, retaining the ground under the pavilion floor), x = 29 (from -3.05 to -1.20) and x = 47 (from -4.40 to -2.55), 300 mm, full bar width y = 7..13 plus the courtyard returns; they are braced at the top by the upper slab and retain at most 1.35 m (CMHC Table 5: within the 300 mm supported limit). Side retaining walls where a level is cut: along both long faces from the level's uphill end to where z(x) meets the floor, 300 mm, stem top on z(x), 1.5 m outside the glass line, free-standing at most 1.3 m (within the 1.50 limit), base 1.5 x 0.4. Plinth walls 250 where a level stands above z(x), under both long faces and across the downhill end, bottoms on the stepped strip footings.
3. Floor slabs 200 mm on ground over 150 mm gravel where cut, 300 mm suspended where on the plinth (split where z(x) crosses the level, rounded to the 4 m post bay: L1 crosses at x = 27.9, split at 27; L2 crosses at x = 44.8 and its last 2 m stand only 0.18 m above ground, so L2 is all on ground with a low plinth from x = 45; L3 crosses at x = 56.6, split at 55).
4. Posts SHS 150 at 4.0 m on the open side; the closed side a 200 mm concrete wall floor to roof whose top follows the roof plane (a trapezoid).
5. Roof beams IPE 330 transverse at 4.0 m, each at the height of the roof plane at its x; the roof slab 200 mm as one sloped parallelogram prism per plane (`prism_y`), R1 over x = 5..11 and R2 over x = 11..70, insulation 150 as a parallel layer (the 8.2 percent fall exceeds the 2 percent drainage minimum), 150 mm fascia at the edges, no parapet; the roof drains along its fall to the far end (gutter not modelled).
6. The pavilion as in A and B, floor +0.15, its roof being plane R1.

Lateral system (corrected after v04). Along x: the side retaining walls and foundation walls below the floors, the closed-side walls and the cores above. Across y: the ridge wall at x = 11 (full height to the roof) and, below the floors, the step walls at 29 and 47 and the plinth end wall; above the floors only the full-height cores (R-51), since the step walls stop at the upper floor level and the roof beam frames are pinned. Each level's slab is its diaphragm, the folded roof slab the roof diaphragm; the L3 plinth 55..70 is a hollow undercroft with an access opening in the x = 70 wall (R-53).

## 6. Comparison rule set for phase 2 (sketches and site images, not the reference photos)

The Inspector compares the last version's matched views with `input/` only. Calibration: `site_02` 10.3 px/m from the 96.42 m boundary; `site_01` 15.4 px/m from the same boundary drawn at 1480 px; sketches 01 to 06 15.2 px/m (plot 96 m over 1460 px, road boundary at 340 px); sections 07 to 09 16.6 px/m (outer red lines 1603 px apart = 96.4 m).

| Rule | Statement | Source |
|---|---|---|
| S-01 | The plot is a strip about 96 m long, 17 to 20 m wide; the model strip is 106 x 20 m per variation | site_02 dimensions |
| S-02 | The ground falls 9.4 m from the road boundary to the far boundary, 5 % then 8 % then 14 % with the knees at x = 26 and 50 | contour count of site_02 |
| S-03 | The road is at the uphill end; the house line runs downhill from it | site_02 (road at the SSW end), sections 07 to 09 (ground falls away from the first volume) |
| S-04 | The first volume is a square pavilion about 6 x 6 m at the building line 5 m from the road boundary, offset to the WNW side | sketch 01 (85 x 90 px), site_01, sketch 05 |
| S-05 | The house is a straight bar on the plot axis from the pavilion to about x = 66 | sketch 06, site_01 main bar; fork, bend and hook rejected |
| S-06 | The bar is one storey high above its floor (about 5 m in the sketch, 3.3 m clear here), never two storeys stacked | sections 07 to 09 (box heights 85 px = 5.1 m) |
| S-07 | The open side alternates: segments 11..28 ESE, 28..44 WNW, 44..60 ESE, 60..end WNW | sketch 02 green edges |
| S-08 | Variation C: three principal rooms step down the slope with stairs at the level changes; one folded roof with its ridge at the uphill end of the tall hall | sketches 07 (three boxes), 08 (folded red roof), 09 (ridge at box 2's uphill end, stairs between boxes) |
| S-09 | Variation A: the bar runs level past the top of the bank and ends over the fall | sketch 06 (bar past the bank), sections' level roof lines |
| S-10 | The far end carries the terrace and the view downhill | sketch 06 ellipse |
| S-11 | Bay rhythm: the sketches' tick marks fall at about 10 to 11 m; the model uses 4 m bays, so ticks land on every second or third bay; not a fixed rule, a note | sketch 01 ticks at 160 px |

Verdicts in the comparison table are: within tolerance (0.5 m in plan, 0.3 m in level, since the sketches are diagrams), fix, or kept with reason.

## 7. Build order and budget (for the Builder)

Terrain skins (3 x 3 pieces) first; then per variation: footings, concrete walls and retaining walls, floor slabs, steel columns and girders (A), posts and roof beams, roof slabs, insulation wedges and parapets, glazing grid, cores and partitions, stairs, guards and balustrades. Estimated member count: about 400 per house, 1250 in all. Mandatory views: the four orbits of the whole strip set, a long section on each strip axis (y = 10, 40, 70) looking WNW, a from-below view of A, an interior view per level (A: bridge and box; B: the one level; C: L1, L2, L3), a frame-only view per variation (skins, glass and slabs hidden), close-ups of A's girder seat on a column and on the box wall, B's retaining wall base, C's step wall with the stair.

## 8. Deviation ledger (concept versus sources and sketches)

| Item | Source says | Concept does | Cause |
|---|---|---|---|
| Plot taper | 16.8 to 20.1 m wide | 20 m rectangle | never reached by the house; tooling |
| Ground steepening | sketches: beyond x = 66 | survey: from x = 50 | the brief says model the actual terrain |
| Bar width | sketch 01: 3.5 to 4 m | 6.0 m | an open plan needs 5.7 m clear |
| Plan wings | sketches 03, 04, 05 | straight bar (06) | section is the variable; kits are axis-aligned |
| C's three boxes | sketch 07: three rooms, two stairs | pavilion plus three levels, three stairs | survey slope |
| B's retaining walls | CMHC Table 5 stops at 1.50 free-standing, 2.30 braced | 2.3 to 2.75 m, engineered L-walls at base 0.6 H | the cut strategy needs them; labelled outside the manuals |
| Footing depth | CMHC 1.2 m (Canadian clay) | 1.2 m | no local frost depth known |
| Glass thickness | AHCD 25 mm IGU | 25 mm | adopted |
| Grade falling away from walls | CMHC 5 % (10 % in the first 2 m) | not modelled | the skin keeps the surveyed profile |
| Drains, membranes, rebar, bolts, control and isolation joints | drawn in AHCD and CMHC | not modelled | brief |
