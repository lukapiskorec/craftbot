# Experiment 16 — GPT-6 research hand-off

Scope: the three questions in `concept.md`, Construction concept and Research gaps only. The manuals provide precedents and prescriptive low-rise details; they do not certify the proposed 6 m tall, 36 x 90 mm paired-slat truss system. No geometry or capacity calculation is implied below.

## 0. Verdict per question

| Topic | Verdict | Number and clause settling the question |
|---|---|---|
| Q1 — narrow floor/roof boards at 600 mm supports; thickness, bearing and joints | partly covered | CMHC Table 22 gives lumber subfloor minimum 19 mm at 600 mm joist spacing; CMHC Ch. 12 gives 19 mm nominal lumber roof sheathing (17 mm only at supports 400 mm or closer). FRIM gives 22 x 145 mm tongue-and-groove floor boards over 610 mm-centred joists, groove blind-nailed through the tongue at 40–50°. Neither source validates a 24 x 90 mm board as a structural diaphragm or supplies a complete end-bearing rule for this pavilion. |
| Q2 — truss sizes, span, nodes/gussets, inter-truss bracing; limits of 36 x 90 paired slats | partly covered | FRIM Appendix I Sheet 9: 5,770 mm bearing-to-bearing truss span, 1,195 mm apex rise, all truss members 35 x 72 mm; 9 mm plywood gussets each side, 3.3 x 63 mm nails, 46 mm along-grain / 23 mm across-grain spacing and 16 mm edge distance. Roof plan uses 22 x 97 mm diagonal and horizontal braces between trusses at 1,220 mm centres. These are a low-rise precedent only, not capacity evidence for 36 x 90 mm paired chords, 6 m columns, six 500 mm bays, 3.2 m clear/4.4 m exterior spans, or concealed connections. |
| Q3 — 6 m braced slat-truss column; transferable opening/base/bearing rules | not covered | CMHC Table 25’s applicable roof-only exterior case is 3.0 m; the table maxima reach 3.6 m for exterior cases and 4.2 m for interior cases. No manual covers a 6 m laterally braced slat-truss column, even with proposed 1.5 m bracing levels. Transferable analogies are conditional: FRIM 120 x 120 mm post on a footing in a 6 x 100 mm U-strap with two 12.7 mm bolts; CMHC beam end bearing at least 89 mm on masonry/concrete; CMHC openings under 3 m use one jack stud each side and openings exceeding 3 m use doubled jacks. None establishes adequacy, uplift, overturning, or connection design here. |

## 1. Source → rule → number

| Source (section / figure / page) | Rule taken | Value in model or design decision (datum) |
|---|---|---|
| FRIM, *Construction Manual of Prefabricated Timber House*, Ch. 6 and Table 1 item A7, p. 21; Appendix I Sheet 1, PDF p. 50 | Floor uses tongue-and-groove strip boards; drawings and schedule agree against a conflicting prose value. | 22 x 145 mm floor-board precedent; board runs across joists. For this concept, 24 x 90 mm remains **mine**, not sourced. |
| FRIM, Ch. 6 Fig. 20, p. 32; Appendix I Sheet 1, PDF p. 50 | Floor boards are laid across joists and blind-nailed through the tongue; header joist closes exposed joist ends. | Blind nail angle 40–50° into joist; header at floor-board top. Joint/bearing arrangement is an analogy, not certification of narrow boards. |
| FRIM, Appendix I Sheet 1, PDF p. 50; construction sequence | Joists are 47 x 145 mm at 610 mm centres. | 610 mm support precedent, nearest manual analogue to the requested 500 mm grid. |
| CMHC, Appendix A Table 22, printed p. 287 / PDF p. 306 | Minimum lumber/panel subfloor thickness varies by maximum joist spacing. | 19 mm minimum lumber at 600 mm support spacing (datum: support centre spacing), a useful upper-bound comparison for the concept’s 500 mm frame repetition but not a 24 x 90 board capacity check. Snippet: `references/manual_cmhc_p287_table22_subfloor_thickness.png`. |
| CMHC, Ch. 9, printed p. 103; Table 23, printed p. 287 | Lumber subfloor boards may be laid at right angles or 45° to joists. Table 23’s panel attachment schedule is not a fastening rule for the concept’s solid slats. | Orientation analogy only; no 150/300 mm panel nailing schedule is transferred to or required for the 24 x 90 slats. |
| CMHC, Ch. 12, printed p. 136; Appendix A Table 35, printed p. 305 / PDF p. 324 | Lumber board roof sheathing is 19 mm nominal; 17 mm is allowed only where supports are 400 mm or closer. | At 600 mm roof supports, use 19 mm as the manual threshold (datum: truss/rafter centre spacing). Snippet: `references/manual_cmhc_p305_table35_roof_sheathing_thickness.png`. |
| FRIM, Appendix I Sheet 9, PDF p. 58, Truss View V | Gable truss has 5,770 mm span between bearings, 1,195 mm apex height; members all 35 x 72 mm. | Precedent only; proposed span and member family differ. Do not infer capacity or scale the dimensions to the 6 m room. Snippet: `references/manual_frim_sheet9_p58_truss_elevation_heel_span.png`. |
| FRIM, Appendix I Sheet 9, PDF p. 58, plywood gusset detail | Nailed gusset node uses 9 mm plywood both sides, 3.3 x 63 mm nails; 46 mm along grain, 23 mm perpendicular, 16 mm edge distance. | Connection precedent only. The concept forbids plywood gussets, so this is explicitly not implemented as a material rule. Snippet: `references/manual_frim_sheet9_p58_truss_gusset_nailing.png`. |
| FRIM, Appendix I Sheet 9, PDF p. 58, roof framing plan | Trusses at 1,220 mm centres use 22 x 97 mm diagonal and horizontal bracing in a diamond pattern. | Inter-truss bracing precedent; proposed 500 mm frame repetition and timber-only exposed slats still require engineering. Snippet: `references/manual_frim_sheet9_p58_roof_bracing_plan.png`. |
| CMHC, Ch. 11 Fig. 80–81, printed pp. 120–121 | Prefabricated trusses are erected with temporary bracing, then permanent lateral top-chord, web and diagonal bracing repeated about every 6 m. | Bracing is required conceptually; 6 m repetition is a low-rise manual rule and not a design limit for this pavilion. |
| FRIM, Appendix I Sheet 7, PDF p. 56, post/footing detail | 120 x 120 mm post bears on a plate in a 6 x 100 mm mild-steel U-strap, fixed with two 12.7 mm bolts. | Transferable base-detail analogy only; do not claim adequacy for truss-column reactions or uplift. Snippet: `references/manual_frim_sheet7_p56_post_footing_ustrap_bolt.png`. |
| CMHC, Ch. 9 quick reference, printed p. 94 | Beam end bearing on masonry/concrete is at least 89 mm. | Conditional bearing datum for any masonry/concrete support; not a timber sole-runner or slat-joint design. |
| CMHC, Ch. 10 Fig. 68, printed p. 109 | Wall opening framing uses lintel, king/jack studs and cripple studs; openings under 3 m use one jack each side, openings exceeding 3 m use doubled jacks. | 0.900 m entrance opening falls in the “under 3 m” analogy, but the source is light-frame wall framing and does not design the all-slat truss wall. Snippet: `references/manual_cmhc_p109_fig68_wall_opening_lintel_jack_cripple.png`. |
| CMHC, Ch. 11 Fig. 86, printed p. 125 | Rafter heel bears/notches over wall top plate; intermediate struts are not less than 45° to horizontal. | Heel-bearing and brace-angle analogies only; no direct transfer to the faceted truss columns. Snippet: `references/manual_cmhc_p125_fig86_rafter_heel_loadbearing_wall.png`. |
| CMHC, Ch. 7 Fig. 47, printed p. 79 | Treated wood sleeper can lie on slab/granular layer with polyethylene damp separation below. | Ground interface/weather separation is a conditional detail; pavilion’s crossed slat sleeper mat, anchors and weatherproofing remain unverified. Snippet: `references/manual_cmhc_p079_fig47_wood_sleeper_on_slab.png`. |

## 2. Figures consulted

The exact local PDF pages corresponding to the figure-index references were consulted for the FRIM truss, gusset, roof-bracing and post-base sheets (Appendix I PDF pp. 56 and 58), and the CMHC Table 22, Table 35, Fig. 68, Fig. 86 and Fig. 47 pages. Existing crops are reused; provenance is recorded in `experiments/16_Expressive_Structure/references/captions.md`. No new snippet was needed.

## 3. Not covered / recommended defaults

- No manual covers a 6 m tall laterally braced slat-truss column, the proposed 36 x 90 mm paired-chord sandwich, a 3.0 m clear square with seven frames, or its concealed fixings and hold-downs. Treat all such geometry and capacity as requiring structural engineering.
- For visual massing only, retain the concept’s 24 x 90 mm slats as **mine**; do not label them as span-approved. If a temporary modelling threshold is required, the closest documented board thresholds are 19 mm lumber at 600 mm supports (CMHC) and FRIM’s 22 x 145 mm floor boards at 610 mm centres, but neither validates the proposed section.
- Use drawn bearing/brace arrangements as analogies, with explicit sole runners, node bearing and anchorage left as design requirements. Do not imply that a boarding layer alone forms a diaphragm.

## 4. Contradictions and resolution

FRIM Ch. 6 prose says 30 x 145 mm floor boards, while its Table 1 and Appendix I drawings say 22 x 145 mm. Per the reference-document rule, the table and drawings prevail; 22 x 145 mm is reported. FRIM’s source is a Malaysian low-rise prefabricated house; its dimensions and connection details are precedents, not a capacity basis for the proposed pavilion.

## 5. External material

None used for this question set. The existing `external_ledged_braced_door.md` concerns a separate prior gap and is not used here.
