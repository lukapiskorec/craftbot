"""Record independently reviewed component passes, retaining structural open gates."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
evidence={
1:'v06 independent ground/five-storey review confirms complete ring, roofs and retained construction with omitted ground; manifest85 images. CourtSouth attachment remains separately open in R22/R34.',
6:'v06 corrections/supports/connections reports verify all rotated profiles and roots; independent source comparison01/06/07 and WB26/45 confirms visible external shoulders.',
7:'v06 supports:866 ordinary .140m2,8 reduced .11375m2,2 independent core-ledger seats;10 nib roots .070m2; independent WB45/46/source comparison. Capacity limitations retained.',
8:'v06 independent elevations/source06/WB26 confirm regular spandrel/window rhythm; facade gravity attachment is separately open in R22/R34.',
9:'v06 south_v06:57 brackets pass, actual ribbon/corbel clearance .180m; source02 comparison and WB12/13/35/36 plus muted Cycles12 confirm projected fascia/ribbon composition.',
10:'v06 zero opaque area below prescribed inclined side opening; independent WB25/47 and source02 plus Cycles12 confirm retained framed incline and open porch.',
11:'v06 public_routes and48 continuous envelopes pass; retained approach1.20m2 actual grade-beam seat +2.40m2 explicitly unmodeled ground. Current plan35/caption and independent ground review pass.',
13:'v06 supports verifies all real150mm ledger seats/200mm attachments; full west ledgers restored without EdgeBeam. INSERT_ACCESS envelopes and independent WB34/48/plan34 pass; anchor capacity inferred.',
14:'v06 completion/public routes and independent ground/support51/53 show retained court stair, terrace and complete retaining-wall union; no modeled terrain remains. R39 separately accepted.',
15:'v06 exact retained stair walking signatures,368 regions minimum2.700m,48 continuous route envelopes pass; gallery CorbelSeat minimum2.0999996185m is within20micrometre seam allowance, separately recorded. Five independent storey reports confirm geometry.',
16:'v06 rim_contacts/supports retain16 real header/beam-to-foundation paths; five storey reports and interior40 confirm curved guards, finite landings and open wells. Fixtures classification preserves structural role.',
23:'v06 structural_followup/priority and supports retain actual four-core x/y diaphragm interfaces,8 core-base unions and real roof ledges; fresh routes/gallery clearances pass. Shear/anchorage capacity remains inferred.',
24:'v06 completion:4,534 ordinary ends pass120mm, all261 prescribed200mm perimeter seats and real roots pass; core/rim/rooflight/insert discontinuities separately checked. Independent support views43/44; buried closure exception remains bounded.',
25:'v06 concept9 ground boundary and completion reports explicitly separate actual concrete, unmodeled earth and30mm terrace cantilever; no soil/base mesh proof or capacity claim inherited.',
27:'v06 render_evidence inventory:51 Workbench01-37/41-54,4 selected Cycles,30 capped drawings=85 images. Independent one-reviewer fallback covers all;53 closes52 occlusion,54 closes50 taxonomy issue. Exact identities linked by measured render bridge.',
33:'v06 actual profiles1,250 wings/1,250 seats, fresh866/8/2 bearing classification and10 nibs pass; independent WB45/46 and source01/06/07 comparison confirm corrected axes.',
35:'v06 corrections asserts zero residual opaque area in approved opening;23 fitted pieces clipped/removed. Independent source02/WB47 confirms open region without invented glass; routes/headroom pass.',
36:'v06 zero forbidden ground/soil/base families;122 removed objects; construction retained. Current export29976 and independent no-ground views pass; completion distinguishes11.399926567m2 terrace concrete from172.690039864m2 unmodeled earth.',
37:'v06 all6,959 requested fixture objects pass complete family mapping; true primary frame retained. Independent49/54 confirms separation. Runner metadata rebake JSON3418977bac8e7bb2913c6d7eef4ee381396477601414db8d4cffdc6956d23a80 has29976 elements/other0/6 checks passed; EntranceApproachSlab floors.'
}
path=HERE/'requirements.md';rows=path.read_text(encoding='utf-8').splitlines()
for i,row in enumerate(rows):
    if not row.startswith('R-'):continue
    number=int(row[2:4])
    if number not in evidence:continue
    fields=row.split(' | ',3);fields[1]=fields[1].replace('[ ]','[x]',1)
    fields[3]=evidence[number]
    rows[i]=' | '.join(fields)
path.write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('Recorded component requirements:',sorted(evidence))
