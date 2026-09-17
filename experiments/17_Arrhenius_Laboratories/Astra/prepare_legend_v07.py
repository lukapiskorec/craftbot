"""Build the stable v07 camera legend and final subset handoff."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
legend=(HERE/'view_legend_v06.md').read_text(encoding='utf-8').replace('# v06 exact','# v07 exact')
legend+='''
- 53: isolated actual landing/corbel/wall support, azimuth225/elevation-12, target(35.1,95.8,2.65), span1.5.
- 54: complete fixtures layer, current layer classification, same camera as50.
- 55: upper CourtSouth bracket atX21.20, sectionX21.20, azimuth0/elevation0, target(21.20,12.30,3.40), span0.65. Context includes the intended panel, floor slabs and actual supporting Beam.
- 56: ground CourtSouth bracket, same section/camera, target(21.20,12.30,0), span0.65. Context includes intended base panel, ground slab and GradeBeam.
- 57: isolated three-piece ground bracket, azimuth45/elevation24, target(21.20,12.425,0), span0.30; reveals thin web and stepped end plates.
- 58: all60 discrete bracket assemblies only, azimuth110/elevation15, fixtures array.

## Render inventory and provenance

Required Workbench set is exactly01–37 and41–58 (55images). No38/39 trials are part of v07. Number40 is the dedicated Cycles interior perspective. Canonical prefix:experiment_17_astra_v07_blender_view_.png.

Disjoint source batches: canonical master55–58; batcha10–25; batchb26–37/41–54; batchc01–09. The original unquoted shell filter converted01–09 to unpadded numbers, so the dedicated quoted batchc supplies those images. It does not repeat the stock gate. Each final canonical copy must have identical bytes to its batch image, recorded in render_batches_v07.json. Every saved batch master is measured against preflight_v07 in render_identity_difference_v07.json.

Cycles final:12/15/28 muted material views and40_interior. Capped drawings:plan_v07_32/33/34/35; route_W/E/N/S at each level0–4; support41/42/43/44/51/52/55/56. Total32 actual-mesh drawings. Their sections use preflight_v07; existing route polylines are the same v06 paths explicitly reverified against full v07 meshes.

## Independent review subsets

- Shared:WB01–11 and16/17; source relationships12–15/25/26/35/36/45–48. Bracket55–58 and capped55/56 apply across all six bands.
- Ground:WB20/25/31/34/37/41/42/48/51/53/56/57; capped33/34/35, routeW0/E0/N0/S0 and support41/42/51/52/56.
- Level1:WB21/27/30/32/33/34/43/48/55; capped32/34, routeW1/E1/N1/S1 and support43/55.
- Level2:WB22 plus shared stair sections18/27/28; routeW2/E2/N2/S2.
- Level3:WB23/35/36/44 plus shared stair sections; routeW3/E3/N3/S3 and support44.
- Level4/roof:WB24/29 plus shared top05, elevations06–09 and stair sections; routeW4/E4/N4/S4.
- Layers:WB10/49 primary frame;50/54 fixtures including all new steel;58 isolated bracket array.
- Presentation:the four final Cycles images. WB52 remains an occluded historic camera;53 provides the usable actual landing detail. Both are retained and reviewed honestly.

Checks are complementary:images judge visible construction and scope;actual face/route reports establish geometric interfaces. Neither claims engineered capacity.
'''
(HERE/'view_legend_v07.md').write_text(legend,encoding='utf-8')
