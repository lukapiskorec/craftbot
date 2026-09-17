"""Focused actual-mesh assertions for user-review corrections, before renders."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import runpy
import sys
import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
import geometry2d as g2
import layers
from craftbot_lib import get_collection

def points(obj):return [obj.matrix_world@v.co for v in obj.data.vertices]
def bounds(obj):
    vertices=points(obj)
    return tuple(v for i in range(3) for v in (min(p[i] for p in vertices),max(p[i] for p in vertices)))
def signature(obj):
    return hashlib.sha256(repr([tuple(round(c,6) for c in p) for p in points(obj)]).encode()).hexdigest()
def path(collection):
    for parent in bpy.data.collections:
        if collection.name in parent.children:
            return path(parent)+'/'+collection.name
    return collection.name

rows=[runpy.run_path(str(HERE/'snapshot_v06.py'))['identity']()]
objects={o.name:o for o in bpy.data.objects if o.type=='MESH'}
forbidden=('EdgeBeam','SiteGround','CourtyardGarden','CourtSubsoil','TerraceSubsoil','TerraceFill','TerraceBase','EntranceApproachBase')
assert not any(n.startswith(forbidden) for n in objects)
rows.append('Forbidden invented beam / ground / earth / granular-base families: 0.')
assert 'CourtPathEast' in objects and any(n.startswith('NorthTerrace') for n in objects)
assert 'EntranceApproachSlab' in objects

wing_cases=0
for name,obj in objects.items():
    if not name.startswith('CorbelWing_'):continue
    _,index,level,sign=name.split('_');shaft=bounds(objects['Column_'+index]);b=bounds(obj)
    cx=(shaft[0]+shaft[1])/2;cy=(shaft[2]+shaft[3])/2
    expected_x=sorted((cx+int(sign)*.30,cx+int(sign)*.65))
    expected=(*expected_x,cy-.50,cy+.50,3.6*int(level)-1.50,3.6*int(level)-.90)
    assert max(abs(a-e) for a,e in zip(b,expected))<2e-5,(name,b,expected)
    wing_cases+=1
assert wing_cases==1250,wing_cases
rows.append(f'{wing_cases} actual chamfered wings: X projection350mm; Y depth1m; original supportZ.')

opaque_hits=[]
for name,obj in objects.items():
    if not name.startswith(('Panel_West_','Panel_East_')):continue
    ps=points(obj)
    if min(p.y for p in ps)>=6. or max(p.y for p in ps)<=.30:continue
    caps=[f for f in obj.data.polygons if abs(f.normal.x)>.999]
    assert caps,name
    poly=[(ps[i].y,ps[i].z) for i in max(caps,key=lambda p:p.area).vertices]
    if g2.signed_area(poly)<0:poly.reverse()
    poly=g2.clip_lin(g2.clip_lin(poly,-.30,1.,0.),6.,-1.,0.)
    poly=g2.clip_lin(poly,8.+.75*5./5.25,-5./5.25,-1.)
    if len(poly)>=3 and g2.area(poly)>1e-5:opaque_hits.append((name,g2.area(poly)))
assert not opaque_hits,opaque_hits
rows.append('Opaque side-panel area within approved below-incline opening: 0m2 (10mm2 area tolerance).')

fixture_rows=[]
fixture_collections={'Facade/TimberFrames','Facade/SteelFrames','Insert/SkylightFrames'}
for name,obj in objects.items():
    collection=path(obj.users_collection[0])
    if collection in fixture_collections or name.startswith('StairRim_'):
        layer=layers.classify('17_Arrhenius_Laboratories',collection,name)
        assert layer=='fixtures',(name,collection,layer)
        fixture_rows.append((name,collection,layer))
for name in ('SouthInclineRafter_31_0','Window_East_5_3_Sill'):
    assert name in objects,name
    assert any(row[0]==name for row in fixture_rows),name
for name,obj in objects.items():
    if name.startswith(('Beam_','Column_','Corbel','RooflightSeatBeam')):
        assert layers.classify('17',path(obj.users_collection[0]),name)=='frame',name
rows.append('Fixtures mapping: '+repr(dict(Counter(c for n,c,l in fixture_rows)))+'; named examples pass; true frame preserved.')
(HERE/'fixture_layers_v06.json').write_text(json.dumps(fixture_rows,indent=2),encoding='utf-8')

# Correspondence is measured, never presumed for refitted families.
frozen=bpy.data.filepath
current={n:signature(o) for n,o in objects.items()}
bpy.ops.wm.open_mainfile(filepath=str(HERE/'preflight_v05.blend'))
prior={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=frozen)
changed=sorted(n for n in current.keys()&prior.keys() if current[n]!=prior[n])
deleted=sorted(prior.keys()-current.keys());added=sorted(current.keys()-prior.keys())
stable_prefixes=('Column_','Beam_','FloorSlab_','FootingPad_','Pedestal_','StairTread_',
                 'StairWaist_','StairLanding','InsertSlab_','EntranceApproachSlab','CourtStair_')
unexpected=[n for n in changed+deleted if n.startswith(stable_prefixes)]
assert not unexpected,unexpected
manifest={'baseline':'preflight_v05.blend','current':'preflight_v06.blend','prior_count':len(prior),'current_count':len(current),
          'unchanged':sum(prior.get(n)==s for n,s in current.items()),'changed':changed,'deleted':deleted,'added':added,
          'fixture_geometry_unchanged':sum(prior.get(n)==current[n] for n,c,l in fixture_rows),
          'fixture_geometry_refitted':[n for n,c,l in fixture_rows if prior.get(n)!=current[n]]}
(HERE/'changes_v06.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
rows.append(f'Measured v05 comparison: {manifest["unchanged"]} unchanged, {len(changed)} changed shared names, {len(deleted)} deleted, {len(added)} added. Primary shafts/beams/slabs/stair walking geometry stable.')
rows.append(f'Fixture geometry unchanged {manifest["fixture_geometry_unchanged"]}; separately inventoried refitted {len(manifest["fixture_geometry_refitted"])}.')
(HERE/'corrections_v06.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('\n'.join(rows),flush=True)
