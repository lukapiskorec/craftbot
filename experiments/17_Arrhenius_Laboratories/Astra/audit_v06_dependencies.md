# v06 dependency audit before revised-concept implementation

Read-only audit of `experiment_17_astra_v05.py`, its versioned support helper, checks, final notes/close-out, and actual v05 viewer coordinates. No input images were read by Builder. Designer owns the reference interpretation. No v06 geometry, rendering or whole-model checks have run. `query_v06_dependencies.py` reproduces the coordinate inventory from the existing export (five-decimal export precision).

## 1. Existing corbels and main beams

There are 125 shafts, 1,250 CorbelWing pieces, 1,250 CorbelSeat pieces and 848 fitted Beam pieces. Every column uses the same global plan orientation. The shaft is square, so its plan appearance is unchanged by a 90-degree rotation; the correction concerns its shoulders.

Relative to each column centre `(cx,cy)`, v05 wings occupy X `[-.50,+.50]`, Y either `[-.65,-.30]` or `[+.30,+.65]`, with chamfer profile in YZ. Rectangular seats occupy X `[-.50,-.30]` or `[+.30,+.50]`, Y `[-.30,+.30]`. Top is `floor-.25-.65`; bottom varies through the .60-high shoulder. For example Column6 at `(0,36)`, first level: east seat X `.30...50`, Y `35.70..36.30`, Z `2.10..2.70`; north wing X `-.50...50`, Y `36.30..36.65`, same Z extrema.

Main Beam runs in X on six-metre Y stations, .40 wide in Y and .65 deep; its top meets slab underside. A global 90-degree shoulder rotation gives main wings along X to +/-.65 and Y thickness 1.00. The ordinary transverse beam can bear .35 in X instead of the old .20. Actual full .40 beam width is available except separately identified core fits and the shifted first-raised south beam.

**First-raised y6 exception:** beam is deliberately centred at y6.35, occupying y6.15..6.55, z2.70..3.35. Rotated shoulders end at y6.50, creating a real .05 rear-width deficiency. Designer proposed a local integral positive-Y nib y6.50..6.55, z2.50..2.70, over actual X wing-bearing intervals. It clears inclined glass, whose lowest rafter bound is z2.9862. It does intersect the final .04-.05m of ordinary exterior ground window jamb/glass at end columns; structure must take precedence and infill be refitted. Do not fit the nib around infill and leave an unsupported notch. Exclude the Column81 ends replaced by independent core ledges.

Column81 at `(45,6)` has its first-level Beam ends at x43.675 and46.925, on existing CoreBeamLedge seats. Higher-level actual beam width is .325 due to the core wall. Rotation changes the geometric seat area and invalidates blindly carrying the old .065m2 area statement; full actual end-face coverage must be recomputed and the reduced beam-width limitation retained.

## 2. EdgeBeam dependencies

There are **760 EdgeBeam solids**, generated as longitudinal strips on x `.30,17.70,36.30,53.70` at levels1..5, .40 wide and .65 deep below slab underside. They are split at transverse beams, columns, cores and stair holes. Removing only final objects is insufficient: regeneration must eliminate them before infill/ledger fitting.

| Dependency | Present behavior | Required v06 treatment |
|---|---|---|
| Inclined-glazing generation | `front_beam_cuts` builds convex cutters from EdgeBeam and removes glass patches | Remove obsolete cutter dependency so real glazing is restored; fit to retained true structure |
| Global joinery | EdgeBeam priority2 clips slabs, panels, frames and link ledgers | Omit family at generation; regenerate all affected fits |
| Raised west insert-link deck | Actual deck X17.55..18.70,Y74..76 sits on EdgeBeam over west .15m seat | Restore the already-parametrized west ledger X17.35..17.70; infer anchored attachment to actual west-wing slab |
| West link ledger | Actual v05 ledger clipped to X17.35..17.50,Y74..76,Z3.20..3.35 at level1 | Existing adjacent slab X16.80..17.55,Y72..78,Z3.35..3.60 proves restored .20x2m attachment and .15x2m deck seat are spatially viable; repeat at roof7.20 |
| North perimeter slab seats | Completion report explicitly credits EdgeBeam for portions of20 of the261 repaired perimeter cases | Regenerate versioned perimeter-ledger helper without EdgeBeam cutters; prove all 261 and full ordinary-end set anew |
| Perimeter ledger roots | Many north ledger pieces use EdgeBeam side interfaces in the recorded contact union | Recompute actual retained Beam/Column roots after regeneration; direct X-running ledgers remain required |
| Stair rims/headers | Existing numeric selection admits EdgeBeam and foundation graphs include it | Rebuild16 rim/header paths using only real transverse Beam, headers, corbels, columns and foundations; fixtures classification does not remove structural role |
| Slab discontinuities | Structural follow-up allows EdgeBeam in support list | Re-run actual end/edge faces without obsolete support credit; retain opening rims/headers/core and approved transverse perimeter ledgers |
| Facade panels | Constructor calls EdgeBeam a facade ledger, but facade panel depth lies mostly inward of its outer strip | Keep actual spandrels/parapets, regenerate concrete/slab attachment and record inferred panel anchors; do not rename EdgeBeam and preserve invented structure |

The script already gives the insert west ledger its original full width before priority fitting. No new link shape is necessary beyond restoring it when the obsolete EdgeBeam cutter disappears. Ledger anchors transfer to actual wing slab spanning between y72/y78 transverse beams; capacity remains inferred.

## 3. Side panels below the south inclined glazing

Named target `Panel_East_1_0_Fit0_ShoulderFit0` has actual bounds X53.23..53.45,Y3.56..5.7525,Z3.05..4.70. West counterpart is X.55...77 with the same YZ. Their sibling ShoulderFit1 extends Y4.2875..5.7525,Z3.30476..4.70. Multiple additional fragments from modules0/1 and spandrel levels0/1 meet/cross the inclined plane, so suffix/name deletion would leave fragments or remove valid upper portions.

Reference plane is `z=8-(y-.75)*5/5.25`, for y.75..6. Terminal west rafter spans X.5175...5825,Y.73905..6.01095,Z2.9862..8.0138. The east side has the corresponding final end station plus the x53.05 station. Side panel masks must use the approved spatial region and that plane before fitting; retain upper/later regular spandrels and real primary frame. Designer must define whether transparent side infill is required when the opaque portions are removed. Existing rectangular side glazing alone does not fill the exposed trapezoidal area between z3 and the incline.

## 4. Ground and earth removal

Current counts from actual export:

| Family | Count | Scope disposition |
|---|---:|---|
| SiteGround | 4 | Remove broad ground masses |
| CourtyardGarden | 1 | Remove landscape surface |
| CourtSubsoil | 1 | Remove prepared-earth solid |
| TerraceSubsoil | 102 | Remove fitted prepared-earth solids |
| TerraceFill | 6 | Remove engineered-earth solids |
| TerraceBase | 6 | Remove granular-base solids |
| EntranceApproachBase | 2 | Remove fitted granular-base solids |
| CourtPathEast | 1 | Retain actual paved path |
| NorthTerrace | 10 | Retain actual constructed terrace paving |

Also retain concrete foundations, retaining walls/strips, entrance slab, court stairs/waist/landing/footing and terrace containment. Their dimensions do not become a new suspended structural system when earth display solids are omitted. Founding and ground-bearing slab support terminate at an explicit unmodeled ground boundary.

Tests must distinguish this omission from a geometric failure. v05 public-route cases Lawn/CourtGarden no longer have modeled surfaces and must be reported excluded by scope, while Paving/Porch/CourtPath/treads/top/terrace/door remain checked. The old paving full-footprint support assertion credits 2.40m2 granular base plus1.20m2 grade beam: retain measured concrete seat, report remaining earth-bearing footprint as unmodeled. The old terrace 184.09m2 direct base support claim becomes historical; current proof must separate actual wall seats, .507m2 north cantilever and omitted earth-supported underside. Do not introduce hidden replacement soil solely to satisfy checks.

## 5. Viewer taxonomy

Generic rules assign `rafter` and collection `frame` before fixtures, so current Facade/TimberFrames (5,134 objects), Facade/SteelFrames (215) and Insert/SkylightFrames (178) are vulnerable. StairRim is caught by Structure before the later stair rule (1,152 pieces). Use narrow experiment17 overrides ahead of generic rules for window-frame collections/families and StairRim. Preserve concrete Beam/Column/Corbel/core classification, rooflight structural seat beams, slab/floor and cladding classifications. Whether facade support brackets are included should follow the approved collection-level definition; they belong to the window/facade fixture assembly, not the main building frame. The named SouthInclineRafter and Window_East_5_3_Sill must both be explicit regression cases.

A layer override changes presentation only. StairRim stays in all structural support/route/headroom tests. Existing scripts and historical geometry remain immutable; baking older JSON layer metadata is a separate Runner action within the user's taxonomy correction, not a geometry change.

## 6. Implementation and evidence boundary

Copy v05 to a new v06 generator and copy the support helper to `support_geometry_v06.py`; do not edit earlier geometry or make v06 depend on modifying v05. New checks must refer to the current frozen v06 geometry, not carry affected v05 hashes/evidence forward. Preserve original stable camera numbering and append focused shoulder/beam, side-incline and restored link-ledger views.

Required regressions: actual rotated shoulder and nib full-face beam support; reduced/core-ledger cases; all ordinary slab ends and261 perimeter seats; restored six link deck seats/ledger attachments;16 rim/header paths; core bases/diaphragm interfaces;57 south brackets; retained structural insert joints; interior/public route/headroom; no forbidden names/collections; layer audit; standard overlaps/contact; independent visual/source review. Every affected retained-geometry assertion needs a precise new allowed-change list instead of suppressing mismatch reports.

**Open before implementation:** revised concept confirmation of local nib, exact side-panel mask/transparent return treatment, and taxonomy scope. No new geometry is authorized by this audit itself.
