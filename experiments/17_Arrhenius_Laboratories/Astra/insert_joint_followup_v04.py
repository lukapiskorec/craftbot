"""Read-only classification of the 45 insert internal end-strip reservations."""
from pathlib import Path
import runpy,sys
from collections import Counter
HERE=Path(__file__).resolve().parent
sys.argv.append('--priority')
cache=runpy.run_path(str(HERE/'structural_followup_v04.py'))
faces,index,bounds=cache['faces'],cache['index'],cache['bounds']
coverage,area,intersect,overlap=cache['coverage'],cache['area'],cache['intersect'],cache['overlap']
g2=cache['g2']
failed=[r for r in cache['insert_ends'] if not r[-1]]
lines=[cache['lines'][0],'Actual full vertical faces at the 45 internal insert joint planes; no model changes. This is a continuous cast-concrete interface classification, not an independent precast end-seat pass.']
rows=[]
for name,side,y,required_strip,strip_support,passed in failed:
    level=int(name.split('_')[1]);z=3.6*level-.25
    endfaces=[f for f in faces[name] if f[0]==1 and f[1]==side and abs(f[2]-y)<1e-5]
    target_prefix=(f'InsertSlab_{level}_','RooflightSeatBeam','InsertColumn','InsertBeam')
    required=covered=0.;matches=[];bearing_rows=[]
    for axis,sign,plane,poly,bb in endfaces:
        adjacent=[]
        for other,f in index.get((1,-sign,round(y,4)),[]):
            if other==name or not other.startswith(target_prefix) or abs(f[2]-y)>1e-5 or not overlap(bb,f[4]):continue
            common=intersect(poly,f[3]);a=area(common)
            if a>1e-7:
                adjacent.append(common);matches.append((other,a))
        required+=area(poly);covered+=coverage(poly,adjacent)
        # Full 0.40m wide support band beyond the shared joint, over this
        # actual end-face width. Check supporting tops and actual slab or
        # concrete seat-beam feet independently at the same elevation.
        xa,xb=bb[0],bb[1]
        band=g2.rect(xa,xb,y,y+.4)
        lower=[];upper=[];lower_names=[];upper_names=[]
        for other,f in index.get((2,1,round(z,4)),[]):
            if other.startswith(('InsertBeam','InsertColumn')) and abs(f[2]-z)<1e-5 and overlap(cache['bounds2'](band),f[4]):
                if area(intersect(band,f[3]))>1e-7:lower.append(f[3]);lower_names.append(other)
        for other,f in index.get((2,-1,round(z,4)),[]):
            if other.startswith((f'InsertSlab_{level}_','RooflightSeatBeam')) and abs(f[2]-z)<1e-5 and overlap(cache['bounds2'](band),f[4]):
                if area(intersect(band,f[3]))>1e-7:upper.append(f[3]);upper_names.append(other)
        bearing_rows.append((area(band),coverage(band,lower),coverage(band,upper),lower_names,upper_names))
    ok=bool(endfaces) and required-covered<1e-5
    band_ok=all(min(a,b)>=req-1e-5 for req,a,b,_,_ in bearing_rows)
    rows.append((name,level,y,required,covered,ok,band_ok,matches,bearing_rows))
groups=Counter((r[1],r[2]) for r in rows)
lines.append('Grouped (level,joint y): '+repr(dict(sorted(groups.items()))))
lines.append(f'{len(rows)} cases; full concrete end-face coverage failures={sum(not r[5] for r in rows)}; full0.40m beyond-joint band coverage failures={sum(not r[6] for r in rows)}.')
lines.append('Vertical joint area total required/covered: '+repr((sum(r[3] for r in rows),sum(r[4] for r in rows))))
for row in rows:lines.append(repr(row))
lines.append('Actual end faces join adjacent concrete; follow named adjoining slab or rooflight seat beam into the yj..yj+0.40m transverse beam band. Column/base/foundation interfaces remain in structural_followup_v04.txt. A continuous cast RCslab declaration and reinforcement/anchorage remain Designer inference, not capacity proof. No exterior y66/y96 failure belongs to this45-case list.')
output=HERE/'insert_joint_followup_v04.txt';output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines[:5]),flush=True)
