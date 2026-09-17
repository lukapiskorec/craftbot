# Arrhenius Laboratories — user review round 1

## Outcome

The corrected v07 model contains **30,156 geometric elements, zero penetrating pairs and zero floating elements**. It implements the six requested corrections and adds discrete attachments for thirty courtyard parapet pieces exposed by the support audit. Independent structural and visual review accepts all 91 final images. The browser displays the correct model without errors, and every exported object matches both generated and checked snapshots at viewer precision.

## Review brief

Correct the column/corbel orientation and the beam-to-slab support arrangement against images 01, 02, 06 and 07. Remove invented EdgeBeam members while retaining the actual facade parapets and providing the reference-supported Beam/corbel/slab system. Remove extra side facade panels beneath the inclined south glazing. Remove all modeled ground planes and distracting landscape/soil/base masses; retain actual building floors, foundations and constructed stairs/terraces as building components. Assign window-frame families and StairRim elements to the viewer's fixtures layer. This is a correction of the existing single building, recorded in a new version; earlier versions remain historical evidence.

## Changes

| User finding | Implemented correction |
|---|---|
| Columns/corbels appear rotated 90 degrees | Rotated the shoulder profiles to align their principal wings with the real transverse beams. Square shafts retain their positions. Recomputed actual beam seats and fitted the local offset-beam and courtyard interfaces. |
| EdgeBeam is not part of the photographed system | Removed all 760 historical EdgeBeam pieces before regenerating affected fittings. Retained the true beams, slabs and facade parapets; repaired the insert ledgers and perimeter-seat dependencies. |
| Construction photos show corbel → beam → slab | Direct rereading of images 01/07 and corrected structural/detail views establish that hierarchy. Ordinary current beam bearing is 350 mm long; reduced-width and core-ledger cases remain separately documented. |
| Extra panels beneath the inclined facade | Removed 23 fitted opaque pieces using the actual inclined-plane boundary. The local side opening remains open, without invented triangular glazing. |
| Distracting ground planes | Removed the 122 identified landscape, soil, fill and base objects. Actual building floors, foundations, paving, stairs and terrace construction remain. Earth support is explicitly unmodeled. |
| Window frames and StairRim assigned to frame | Mapped all relevant timber, steel and rooflight-frame assemblies plus StairRim to fixtures. Both named window examples pass. Structural rooflight seat beams remain frame; the approach slab is floors. |

The deeper facade audit found thirty CourtSouth parapet pieces without current slab attachments: twenty-four inherited omissions and six paths lost after the correct corbel rotation. V07 adds two discrete steel assemblies per panel. Their 180 pieces bridge the actual 250 mm gap to real slab edges; they do not recreate a continuous EdgeBeam. All 29,976 existing v06 meshes retain exact geometry and collections.

## Sources and verification

All eight original images and the [HIC article](https://hicarquitectura.com/2026/09/carl-nyren-arhenius-laboratories/) remain the source set. This round rereads images 01/07 for the construction hierarchy, 02 for the inclined corner, and 06 for the corbel/window/parapet distinction. The images' five occupied bands continue to govern over the article's four-storey wording. Absolute metric dimensions remain estimates.

Measured checks pass all 240 new bracket interfaces, sixty slab strips and sixty Beam/GradeBeam bearing bands. The glass-excluded facade audit resolves all 3,660 panel pieces. Exact baseline retention carries the verified main bearings, 4,534 ordinary slab ends, 261 perimeter seats, sixteen stair support paths and corrected landing/terrace geometry. Current checks pass 48 continuous routes and 26 constructed public-route/aperture cases. Gallery clearance is 2.100 m; the separate 368-region stair test has 2.700 m minimum headroom. Two removed lawn/garden cases are excluded by scope.

The export has 4,943 boxes and 25,213 meshes, totaling 30,156 elements and 7,453,180 bytes. All eleven taxonomy checks pass, including the 180 new bracket fixtures, both user-named window members, StairRim, the approach slab and structural rooflight seats. No elements are unclassified. The final image set comprises 55 Workbench views, four Cycles images and 32 capped mesh drawings. Generated and rendered hashes differ only by the measured float32 transform rounding recorded in the rationale; every primary support and new bracket remains exact, and all nineteen affected rendered tread seats were rechecked.

## Version record

| Version | Main change or finding | Elements | Pairs | Floating |
|---|---|---:|---:|---:|
| v01 | Initial model; opening-domain defects | 18,828 | 85,230 | 2 |
| v02 | Corrected openings and junctions; stair exits still fail | 31,149 | 0 | 0 |
| v03 | Corrected stairs, galleries, room doors and insert access | 30,003 | 0 | 0 |
| v04 | Continuous south facade and genuine entrance; support omissions identified | 29,876 | 0 | 0 |
| v05 | Perimeter bearings, courtyard stair and terrace support | 30,167 | 0 | 0 |
| v06 | User's geometry/ground/layer corrections; thirty facade attachments remain open | 29,976 | 0 | 0 |
| v07 | Discrete facade attachments; all retained v06 geometry unchanged | 30,156 | 0 | 0 |

## Deliverables and limits

- [Final Blender model](experiment_17_astra_v07_blender.blend)
- [Generator](experiment_17_astra_v07.py)
- [Exterior preview](experiment_17_astra_v07_cycles_view_12_muted_none_no_foundation.png)
- [Upper attachment detail](experiment_17_astra_v07_blender_view_55.png)
- [Ground attachment detail](experiment_17_astra_v07_blender_view_56.png)
- [Design rationale](experiment_17_astra_design_rationale.md) and [structural review](structural_review_v07.md)
- [Complete project-file manifest](file_manifest.md), including all versions, diagnostics, viewer models, index and narrow shared layer changes

The source geometry and measured interfaces do not establish structural capacity. Reinforcement, welds, anchors, local slab design, soil/retaining stability and regulatory compliance remain unverified. Concealed brackets and exact dimensions are architectural inferences; the retained fine-detail simplifications remain documented. Ground removal does not make the terrace a suspended structure or establish a step-free route.

Per-agent token/context/tool-call and monetary totals are unavailable in this runtime. No commit was made. Suggested commit: `Correct Arrhenius structure, facade openings and viewer layers`.

Version close-out passes eight effective required steps with zero unresolved mechanical failures; the canonical export timeout and verified direct-export recovery remain recorded. Final run preflight passes all thirteen checks, and all forty requirements are closed within their stated scope. No geometry or visual correction remains open.

Transcript archival follows this prepared report as the final run action. Its actual outcome is recorded in `closeout_run.md`.
