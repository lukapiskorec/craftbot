"""Record verified v07 outcomes; Coordinator/Runner retain run close-out."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
evidence=json.loads((HERE/'render_evidence_v07.json').read_text(encoding='utf-8'))
delta=json.loads((HERE/'delta_v07.json').read_text(encoding='utf-8'))
panels=json.loads((HERE/'panel_roots_v07.json').read_text(encoding='utf-8'))
assert evidence['complete'] and len(evidence['images'])==91
assert len(evidence['geometry_bridges'])==5
assert delta['retained_exactly']==29976 and len(delta['added'])==180
assert not delta['removed'] and not delta['changed'] and not delta['local_pairs']
assert panels['rooted']==3660 and not panels['unresolved']
log_bytes=(HERE/'render_v07.log').read_bytes()
log=log_bytes.decode('utf-16' if log_bytes[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8',errors='replace')
assert 'OVERLAP CHECK: 30156 members, 0 penetrating pairs' in log
assert 'CONTACT CHECK: 30156 members, 0 floating' in log and 'DONE' in log

merged='''# v07 merged independent inspection

**Pass: all geometric and visual findings are closed.** The final unmodified stock gate reports **30,156 members, zero penetrating pairs at 1 mm, zero overlap families, and zero floating members at 2 mm**. The remaining CourtSouth attachment defect from v06 is repaired by sixty discrete three-piece steel assemblies. No capacity certification is implied.

## Reviewer and coverage

A fresh gpt-5.6-luna Inspector attempt failed with `agent thread limit reached`. The Coordinator retained one independent Astra Designer fallback, formerly the v05 Builder and concept10 author, who did not author or read v07 geometry code. The following are nine reports by that one independent reviewer, not nine independent agents:

- [Bracket details](inspection_v07_brackets.md): upper and ground connections, thin continuous stepped web, sixty discrete assemblies and corrected capped-section caption.
- [Ground](inspection_v07_ground.md) and [levels1](inspection_v07_level1.md), [2](inspection_v07_level2.md), [3](inspection_v07_level3.md), [4](inspection_v07_level4.md): shared building views, circulation, room/insert/stair/support evidence and all32 actual-mesh drawings.
- [Source preservation](inspection_v07_comparison.md): actual v07 views retain the accepted source01/02/06/07 relationships under exact retention of all29,976 v06 meshes; no invented EdgeBeam, ground or opaque under-incline return reappears.
- [Display layers](inspection_v07_layers.md): primary frame and fixtures remain distinct; all180 new pieces are fixtures and StairRim retains its separately checked support role.
- [Presentation](inspection_v07_presentation.md): all four selected Cycles images, with transmitted glass and legible stair/frame evidence. Dark cutaway28 is complemented by WB28 and interior40.

All **55 Workbench images (01–37 and41–58), four selected Cycles images (12/15/28 and40), and32 capped drawings:91 images** were directly inspected. The reviewer independently verified every image hash and all51 byte-identical batch-to-canonical copies. WB52 is still an occluded historical camera; actual isolated53 supplies the landing judgment. Section55's original caption is preserved as `*_caption_initial` and excluded from the final inventory; the corrected image states “capacity unverified.” No geometry changed for that caption.

## Numeric closure and identities

[Independent image and identity acceptance](inspection_v07_identity.md) records the reviewer's checks of all91 image hashes,51 byte-identical copies, five saved-model bridges and final canonical diagnostics.

`delta_v07.json` proves exact names, local/world vertices, transforms, polygons and collections for every29,976 baseline object. Only180 steel objects are added; local SAT is zero. `brackets_v07.json` passes all120 concrete/plate and120 web/plate interfaces,60 continuous slab strips and60 actual200 mm Beam/GradeBeam seats. `panel_roots_v07.json` resolves all3,660 panels with glass excluded, including all30 formerly unresolved pieces. Both new paths for each affected panel are direct steel-to-slab paths; glass and timber do not carry these new connections. All48 continuous route envelopes and retained constructed public routes pass with the ground hardware present. `evidence_reuse_v07.md` names retained bearing, core, rim, insert, R39 and ground-boundary evidence whose geometry is exact.

Generated/preflight identity: `6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed`.

All five saved Workbench/batch/Cycles masters share identity `1efe2518e65ac7d515c5fb795a9778603de1f95f6e026191dc32975ebde93ad0`. Every local mesh and all primary-support/new-bracket world vertices are exact. Each has only29 pre-existing tread/inclined-rail world changes, maximum3.814697265625 micrometres. These are measured distinct generated/rendered identities, not a claim of raw hash equality. All19 actual rendered tread underside unions pass the existing20 micrometre coordinate allowance. `render_evidence_v07.json` and `render_identity_difference_v07.json` retain the complete bridge; the stock gate ran once on the canonical saved master.

The viewer export has30,156 elements, zero unclassified objects, and11/11 fixture taxonomy checks passed. JSON SHA256 is `2a074a8867df408bdd16b5c3a24f0d7d5177bbb9f7a2a1e126a8ce07c2cf26b3`; Runner owns final export-coordinate/viewer/close-out evidence.

Anchors, welds, steel and local concrete capacities, reinforcement and founding remain uncalculated architectural inferences. Specified earth-bearing regions remain explicitly unmodeled. These limitations do not conceal a remaining geometric attachment gap.
'''
(HERE/'inspection_v07.md').write_text(merged,encoding='utf-8')

notes='''

## v07 — discrete CourtSouth attachments; 2026-09-17

### Change and scope

Implemented approved concept10 only: **60 discrete welded/anchored steel assemblies,180 convex meshes**, two for each of30 CourtSouth panels across five bays and six bands. Each assembly has100 mm-wide,10 mm-thick end plates and a10 mm web across the250 mm slab/panel gap. Upper hardware is100 mm high; ground end plates are150 mm high at staggered levels with one continuous300 mm-high web. Outer plates snap to the actual retained concrete planes. Anchors, weld details and capacities are inferred/unmodeled.

`delta_v07.json` proves all **29,976 v06 objects exactly retained**, including names, local/world vertices, transforms, polygons and collections. No removal or modification exists. Added hardware belongs to existing `Facade/SteelFrames` fixtures; no shared toolkit or layer changes were needed. The corrected corbels/Beam hierarchy, zero EdgeBeam, open under-incline side, omitted earth, walking surfaces, building outline and R39 landing/wall repair remain exact. The generator is a minimal v06 copy plus `facade_brackets_v07.py`; immutable `support_geometry_v06.py` remains its inherited support helper.

### Actual checks

All120 concrete/end-plate interfaces and120 web/end-plate interfaces pass full actual face unions; actual dimensions match the concept within2.136230469 micrometres. All60 continuous root-to-beam slab strips and60 actual100×200 mm Beam/GradeBeam seats pass. Upper concrete interfaces are nominal0.010 m2 and ground0.015 m2; weld interfaces0.001/0.0015 m2. These are anchorage interfaces, not horizontal gravity-bearing claims or capacity calculations.

The glass-excluded all-plane graph now roots **3,660/3,660 panels**; all30 prior CourtSouth failures are closed, and the former3,630 paths remain available on exact geometry. Both new connections for each panel reach its real slab without glass or timber gravity credit. Full48 continuous circulation envelopes and constructed public routes pass, including the150 mm-high ground hardware. The retained gallery tangent remains2.0999996185 m within the recorded20 micrometre coordinate allowance;368 unchanged stair regions separately retain the2.700 m minimum. `evidence_reuse_v07.md` maps every inherited concrete/slab/core/rim/insert/R39/ground-boundary check to exact retained inputs.

Local SAT reports0. **Final unmodified stock result:30,156 members,0 penetrating pairs at1 mm,0 overlap families,0 floating at2 mm.** `render_v07.log` ends DONE with exit0, and the canonical pairs file contains0. This whole-model gate ran once, on the final saved canonical render master.

### Renders, independent review and identity

Full final set: **55 Workbench01–37/41–58; four Cycles12/15/28/interior40;32 capped drawings;91 images**. New55/56 show upper/ground bracket sections,57 the thin stepped assembly,58 all60 assemblies; capped55/56 show actual mesh sections. Existing view numbers are preserved. WB52 remains occluded;53 is the usable isolated landing view. Section55's corrected “capacity unverified” caption closes the sole presentation wording comment; initial caption artifacts remain excluded. No geometry repair was needed after first rendering.

The shell's initial unquoted numeric filter removed leading zeroes. A quoted no-check batch supplies01–09. Final exact-name inventory verifies every required view;51 batch images are copied byte-identically to canonical names, with all source/copy hashes recorded. All rendering is from the frozen generated blend; no duplicate full gate was run for supplemental batches or Cycles.

Fresh Luna Inspector creation failed at the runtime thread limit. Coordinator retained the independent Designer/former v05 Builder, separate from the fresh v07 author. That one reviewer inspected all91 images, independently checked all91 hashes and51 batch copies, and accepted the new attachments, allfive storeys, source preservation, materials and display layers. Nine part reports merge into `inspection_v07.md`; `structural_review_v07.md` records independent geometry acceptance. No visual or geometric issue remains.

Generated hash: `6c1350108bbce626f83409e306f66fbd27001f2b5c602099927c60684f6082ed`. Allfive saved masters share `1efe2518e65ac7d515c5fb795a9778603de1f95f6e026191dc32975ebde93ad0`. Every local mesh and every primary-support/new-hardware world vertex is exact. Each saved master has29 pre-existing tread/inclined-rail coordinate changes, maximum3.814697265625 micrometres; all19 actual rendered tread underside unions pass. The distinct hashes and measured bridge are explicit in `render_identity_difference_v07.json` and `render_evidence_v07.json`.

Runner export:30,156 elements, other0,11/11 taxonomy checks; all180 new pieces are fixtures. JSON SHA256 `2a074a8867df408bdd16b5c3a24f0d7d5177bbb9f7a2a1e126a8ce07c2cf26b3`. Final mechanical/viewer close-out and run documents remain Coordinator/Runner responsibilities; no archive or commit was made by Builder. A preliminary local-check launch loaded user add-ons and hung on shutdown; the owned process was stopped after its checks completed. Clean factory-startup attachment/route checks and every final render/gate completed successfully; no geometry exception followed.

### Requirements and open questions

R40 closes on actual interfaces/roots, route tests, final0/0 stock gate, independent91-image review and exported fixture checks. R27 records the complete final view inventory. Designer/Coordinator own broader final acceptance wording and Runner owns R31 close-out. All model geometry and inspection issues are closed. Engineering limits and the explicitly unmodeled ground boundary remain unchanged.

1. **No open Designer geometry question.** The sole inherited CourtSouth attachment issue is resolved by the approved discrete hardware; no substitute longitudinal beam or ground support was introduced.
'''
path=HERE/'version_notes.md'
prior=path.read_text(encoding='utf-8')
assert '## v07 — discrete CourtSouth attachments' not in prior
path.write_text(prior+notes,encoding='utf-8')

path=HERE/'requirements.md'
rows=[]
for line in path.read_text(encoding='utf-8').splitlines():
    if line.startswith('R-40 |'):
        line=line.replace('| [ ]','| [x]',1).rsplit('|',1)[0]+'| v07 actual30156/hash6c135010… preserves all29976 baseline meshes; brackets_v07 passes240 interfaces/60 continuous slab strips/60 actual200mm seats; panel_roots_v07 roots3660/3660 with glass excluded; all48 routes/public strips pass. Final stock30156/0pairs/0floating; independent all91 images/hash checks and allfive saved-master bridges accepted; exported180fixtures/11taxonomychecks pass. Anchors/welds/capacities remain inferred and unverified.'
    elif line.startswith('R-27 |'):
        line=line.replace('| [ ]','| [x]',1).rsplit('|',1)[0]+'| v07 exact final inventory55 Workbench01–37/41–58,4 selected Cycles12/15/28/40,32 capped drawings=91 images; all independently reviewed and hashed.51 batch copies match canonical bytes; allfive saved masters share measured rendered identity1efe2518… with explicit generated/render bridge. WB53 supplies the usable landing detail; new55–58/capped55–56 show bracket construction.'
    rows.append(line)
path.write_text('\n'.join(rows)+'\n',encoding='utf-8')
(HERE/'builder_handoff_v07.md').write_text(merged+'\n## Builder handoff\n\nGenerator and bracket helper are frozen. `artifact_manifest_v07.json` inventories version artifacts. No further geometry work is required. Coordinator/Runner finish mechanical close-out, broader requirement/rationale updates, viewer inspection and any authorized archival; Builder performed no archive or commit.\n',encoding='utf-8')
print('v07 Builder notes, merged inspection, R27/R40 and handoff finalized.',flush=True)
