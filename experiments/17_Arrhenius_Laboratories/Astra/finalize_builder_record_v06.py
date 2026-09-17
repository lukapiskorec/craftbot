"""Bind the completed stock gate and independent review to the v06 records."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
raw=(HERE/'render_v06.log').read_bytes()
log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
assert 'OVERLAP CHECK: 29976 members, 0 penetrating pairs (> 1 mm)' in log
assert 'CONTACT CHECK: 29976 members, 0 floating (nothing within 2 mm)' in log
path=HERE/'version_notes.md';s=path.read_text(encoding='utf-8')
s=s.replace('The current standard gate is still running; its result will be recorded below.',
            'The unmodified stock gate passes 29,976 members, zero penetrating pairs and zero floating members, but the missing attachment remains a distinct structural defect.')
s=s.replace("Final corrected-detail confirmation is pending at this entry's initial write.",
            'The independent reviewer confirmed corrected views53/54 and all85 inventoried images; both presentation findings are closed.')
s=s.replace('### Remaining gate and Designer question','### Standard gate and remaining Designer question')
s=s.replace('**Standard diagnostic result: pending the currently running unmodified stock overlap/contact gate on the saved 29,976-mesh master.**',
            '**Standard diagnostic result: 29,976 members, zero penetrating pairs at1mm, zero overlap families, zero floating members at2mm.** The unmodified stock checks completed on saved master hash25c4743bc414e69436a7b18e84e6fc5535ae58651dd41d9913a78b3ee06e6f1a; render_v06.log lines200–202 and the canonical pairs file record the result.')
path.write_text(s,encoding='utf-8')
path=HERE/'inspection_v06.md';s=path.read_text(encoding='utf-8')
s=s.replace('The standard whole-model diagnostic is still running and is not replaced by appearance or the earlier preflight.',
            'The final unmodified whole-model diagnostic passes29,976 members,0 penetrating pairs at1mm,0 overlap families and0 floating at2mm. This does not prove a root for a connected but unsupported facade assembly.')
path.write_text(s,encoding='utf-8')
path=HERE/'builder_handoff_v06.md';s=path.read_text(encoding='utf-8')
s=s[:s.index('## Rendering and review status')]+'''## Final rendering and review status

All **51 Workbench images, four selected Cycles images and 30 capped drawings (85 total)** are independently reviewed and inventoried in `render_evidence_v06.json`. The original49-view Workbench set is retained;53 corrects the occluded landing camera and54 corrects the approach-slab layer presentation. One white-material trial is excluded. All presentation findings are closed.

The unmodified stock gate passes **29,976 members / 0 penetrating pairs at1mm / 0 floating at2mm**, with zero overlap families. `render_v06.log` and the canonical pairs file are actual evidence, not carried preflight claims.

Main Workbench/Cycles saved masters share hash `25c4743bc414e69436a7b18e84e6fc5535ae58651dd41d9913a78b3ee06e6f1a`; the detail master is `eb8c41148a212fc5e40a778760eb1142a3e661c1ba7963af4f7dcc1ea6bc20a9`. All local meshes and primary-support world vertices are exact. The measured transform bridge records only sub4micrometre tread/rail roundoff and all19 rendered tread underside unions pass. No duplicate whole-model checks were run.

Fresh and reused Luna Inspector attempts failed with the runtime thread limit. The Coordinator assigned one independent Designer/reviewer fallback who did not author or read v06 geometry code. All five storey reports, source comparison, presentation and layer reviews are merged in `inspection_v06.md`. Sources01/02/06/07 confirm the requested corrected relationships; the30-panel attachment defect is not waived.

Runner's final metadata rebake moves only the erroneously matched EntranceApproachSlab from fixtures to floors. Current viewer JSON SHA256 `3418977bac8e7bb2913c6d7eef4ee381396477601414db8d4cffdc6956d23a80` has29,976 elements, zero unclassified objects and six taxonomy checks passed. Geometry was not re-exported for that correction.

`version_notes.md` now contains the full v06 entry. Component requirements are refreshed with actual v06 evidence. R22/R30/R32/R34/R38 and final close-out remain open for the CourtSouth repair. **v06 is not converged.** A read-only60-location connector probe and thin-plate/web proposal are available for the independently authorized next version; no v07 geometry exists here.
'''
path.write_text(s,encoding='utf-8')
