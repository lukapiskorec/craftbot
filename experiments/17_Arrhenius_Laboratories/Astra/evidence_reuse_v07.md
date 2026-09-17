# v07 baseline evidence and dependency coverage

Generated v07 has 30,156 meshes and geometry hash `6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed`. `delta_v07.json` compares the actual frozen scene with `preflight_v06.blend`, whose independently reproduced hash is `523cd725f671151f70fb591add45a53875bbd80cb619a85760088230495d1416`.

All 29,976 existing objects retain their names, every local/world vertex, transform, polygon and collection exactly. The only additions are 180 `CourtFacadeBracket_` steel members: two end plates and one web for each of 60 connections. The local SAT check tests every addition against every existing and added mesh at the standard 1 mm threshold; it reports zero penetrating pairs.

## Numeric evidence carried through exact retention

These reports remain v06 measurements. Their complete geometric inputs are unchanged in generated v07; their names and original identity are retained rather than rewriting historical evidence as freshly measured results.

| Prior evidence | Unchanged inputs and conclusion |
| --- | --- |
| `corrections_v06.txt`, `side_panel_changes_v06.json` | Corrected corbel axes, zero EdgeBeam, open side below the inclined glazing, omitted ground/soil/base families and retained walking construction. |
| `supports_v06.txt`, `connections_v06.txt` where not superseded by the all-plane panel graph | 866 ordinary beam seats, eight reduced-width seats, two core-ledger seats; corrected nib/shaft roots; foundation footprints, link seats, core-base and diaphragm interfaces. The former panel-screen failures are superseded by `panel_roots_v07.json`. |
| `completion_v06.txt`, `slab_end_faces_v06.json` | All 4,534 ordinary slab ends and 261 required 200 mm perimeter seats; unchanged ledgers/roots, waist, landing, terrace walls and explicitly unmodeled ground portions. |
| `landing_joints_v06.txt`, `fit_delta_v06.json`, `terrace_fit_probe_v06.txt` | Exact section 9.7 landing/wall repairs, finite plate interfaces and separate 0.439993/0.050000 m2 seats. |
| `rim_contacts_v06.txt`, `insert_joint_followup_v06.txt` | Sixteen stair rim/header routes, 45 integral insert interfaces and adjacent real beam bands; no EdgeBeam path. |
| `south_v06.txt`, `headroom_v06.txt` | Retained 57 south facade connections and 368 stair headroom regions. New steel is at CourtSouth Y12.30–12.55; it has zero local intersections and does not change these members or walking tops. |

## New measurements on v07

- `brackets_v07.json`: actual dimensions, all 120 concrete/plate interfaces, all 120 plate/web interfaces, 60 continuous slab root-to-beam strips and 60 actual 200 mm Beam/GradeBeam seats. Each panel has two direct steel-to-slab paths; neither glass nor timber provides these new connections.
- `panel_roots_v07.json`: all 3,660 panels have a primary root with glass excluded, including all 30 previously unresolved CourtSouth pieces. Existing 3,630 panel paths remain available because all their members and finite interfaces are exact.
- `route_envelopes_v07.txt` and `public_routes_v07.txt`: full actual v07 geometry, including the 150 mm-high ground connections, passes the 48 continuous route envelopes and retained constructed public strips. The exact 2.10 m gallery tangent uses the recorded 20 micrometre coordinate allowance; the separate stair minimum remains 2.700 m.
- Final whole-model diagnostics, rendered geometry identity, independent image review and viewer export are separate required gates; this baseline bridge does not substitute for them.

The brackets are inferred welded/anchored secondary facade hardware. Contact unions prove geometry, not steel, weld, anchor or local slab capacity. Founding and specified earth-bearing slab areas remain explicitly unmodeled.
