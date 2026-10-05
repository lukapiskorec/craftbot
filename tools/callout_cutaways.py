"""Assembled layer cutaways: one vector A2 sheet per model, all callouts.

python tools/callout_cutaways.py [--only 16] [--slug gpt6]
Whole members are omitted, never translated. Three rear-enclosure depths
are compared; ray tests open actual sightlines with frame removal heavily
penalized. Exact hidden-line removal then verifies every callout anchor.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import html
import inspect
import json
import math
import pickle

import numpy as np

import callout_diagrams as cd
import callout_overviews as overview
from hidden_lines import _project, EPS
from title_blocks import SEGOE
from vector_pdf import FINE, THIN, font_css, print_pdf

# Visual review: the shallow CLT option concealed too many internal levels.
# Keep the rear wall strips and open the front through the full height.
REVIEW_CUTS = {('09','fable'): (.85,'Visual review: open all internal levels'),
               ('16','fable'): (.65,'Visual review: open inner cladding while keeping enclosure context')}
MORE_ENCLOSURE = {('04','fable'),('06','fable'),('07','fable'),('08','fable'),
                  ('11','fable'),('13','fable'),('14','fable'),('16','gpt6')}
HALF_ROOF = {('11','fable'),('13','fable'),('14','fable'),('16','gpt6')}


class CutawaySheet(cd.CalloutSheet):
    """Fabrication canvas with compound fills and translucent glass layers."""
    def vector_layer(self, markup):
        if not hasattr(self,'vector_layers'):
            self.vector_layers = []
        self.vector_layers.append((len(self.ops),markup))

    def glass_tint(self, polygons, opacity):
        self.vector_layer(''.join('<polygon points="'+' '.join(f'{x:.4f},{self.h-y:.4f}' for x,y in poly)+
            f'" fill="black" fill-opacity="{opacity}" stroke="none"/>' for poly in polygons))

    def solid_fill(self, polygons, color='black'):
        # One compound path avoids anti-alias seams between clipped fragments.
        path = ' '.join(' '.join(f'{"M" if i==0 else "L"}{x:.4f},{self.h-y:.4f}'
            for i,(x,y) in enumerate(poly))+'Z' for poly in polygons)
        self.vector_layer(f'<path d="{path}" fill="{color}" stroke="{color}" stroke-width="0.01" stroke-linejoin="round"/>')

    def svg(self):
        if not hasattr(self,'vector_layers'):
            return super().svg()
        fragments,cursor = [],0
        for index,markup in self.vector_layers+[(len(self.ops),'')]:
            block = cd.CalloutSheet(self.w,self.h)
            block.ops = self.ops[cursor:index]
            svg = block.svg().removesuffix('</svg>')
            # Later fragments contribute no SVG root or white background.
            fragments.append(svg if not fragments else svg.split('/>',1)[1])
            fragments.append(markup)
            cursor = index
        return ''.join(fragments)+'</svg>'


class Projection:
    """Spatially indexed front faces and depth-tested point sightlines."""
    def __init__(self, members, right=cd.RIGHT, up=cd.UP):
        self.faces, edges = _project(members,right,up)
        self.edges = defaultdict(list)
        for owner,p,q in edges:
            if np.linalg.norm(q[:2]-p[:2]) > EPS:
                self.edges[owner].append((p,q))
        self.lo = np.array([poly.min(0) for _,poly,_ in self.faces])
        self.hi = np.array([poly.max(0) for _,poly,_ in self.faces])
        self.cell = max(1.,np.ptp(np.concatenate([self.lo,self.hi]),axis=0).max()/64)
        self.grid = defaultdict(list)
        for i,(lo,hi) in enumerate(zip(self.lo,self.hi)):
            a,b = np.floor(lo/self.cell).astype(int),np.floor(hi/self.cell).astype(int)
            for x in range(a[0],b[0]+1):
                for y in range(a[1],b[1]+1):
                    self.grid[x,y].append(i)

    def blockers(self, point, owner):
        blockers = set()
        key = tuple(np.floor(np.array(point[:2])/self.cell).astype(int))
        for i in self.grid.get(key,[]):
            other,poly,(origin,normal) = self.faces[i]
            if other == owner or other in blockers:
                continue
            if np.any(point[:2]<self.lo[i]-EPS) or np.any(point[:2]>self.hi[i]+EPS):
                continue
            depth = origin[2]-np.dot(normal[:2],np.array(point[:2])-origin[:2])/normal[2]
            if depth <= point[2]+EPS:
                continue
            edge = np.roll(poly,-1,axis=0)-poly
            delta = np.array(point[:2])-poly
            if np.all(edge[:,0]*delta[:,1]-edge[:,1]*delta[:,0] >= -1e-7):
                blockers.add(other)
        return blockers


def sample_ids(ids, limit):
    ordered = sorted(ids)
    return [ordered[i] for i in np.linspace(0,len(ordered)-1,min(limit,len(ordered)),dtype=int)]


def choose_targets(members, view, callouts):
    """Find a representative visible edge requiring the least frame removal."""
    frame = {i for i,m in enumerate(members) if m['layer']=='frame'}
    centers = np.array([np.mean(m['verts'],axis=0) for m in members])
    targets,protected,opened = [],set(),set()
    for number,callout in enumerate(callouts,1):
        matched = cd.match_indices(members,callout['match'])
        candidates = []
        for owner in sample_ids(matched-opened,80):
            edges = sorted(view.edges[owner],key=lambda e:-np.linalg.norm(e[1][:2]-e[0][:2]))[:4]
            for p,q in edges:
                for t in (.25,.5,.75):
                    point = p+(q-p)*t
                    blockers = view.blockers(point,owner)-opened
                    if blockers & protected:
                        continue
                    cost = len(blockers&frame)*100000+len(blockers)*10
                    # Prefer a longer exposed edge when removal costs tie.
                    cost -= min(1,np.linalg.norm(q[:2]-p[:2])/1000)
                    candidates.append((cost,owner,point,blockers))
        if not candidates:
            raise ValueError(f'No compatible exposed target for {callout["id"]}')
        _,owner,point,blockers = min(candidates,key=lambda c:c[0])
        protected.add(owner)
        opened |= blockers
        nearest = sorted(matched-opened,key=lambda i:np.linalg.norm(centers[i]-centers[owner]))
        selected = set(nearest[:min(4,len(nearest))])|{owner}
        targets.append(dict(number=number,callout=callout,owner=owner,point=point,
                            matched=matched,selected=selected))
    return targets


def carve(members, view, targets, depth):
    """Retain the skeleton and rear enclosure; open all protected sightlines."""
    centers = np.array([np.mean(m['verts'],axis=0) for m in members])
    xy = (centers[:,:2]-centers[:,:2].min(0))/np.maximum(1,np.ptp(centers[:,:2],axis=0))
    kept = set()
    for i,m in enumerate(members):
        layer = m['layer']
        # A rear L of wall boards, a smaller corner of horizontal finishes.
        rear = max(xy[i]) >= depth if layer in ('cladding int','cladding ext','interior') else min(xy[i]) >= depth
        if layer in ('frame','foundations') or rear:
            kept.add(i)
    kept |= set().union(*(t['selected'] for t in targets))
    protected = {t['owner'] for t in targets}
    blockers = set().union(*(view.blockers(t['point'],t['owner']) for t in targets))
    if blockers & protected:
        raise ValueError('Protected callout targets block one another')
    kept -= blockers
    return kept,set(range(len(members)))-kept


def study(members,view,targets):
    frame = {i for i,m in enumerate(members) if m['layer']=='frame'}
    # CLT exports put their structure in wall/floor layers; audit visibility
    # of those members when there is no dedicated frame layer.
    structure = frame or {i for i,m in enumerate(members) if m['group'].startswith(('Structure/','Core/','Podium/'))}
    probes = []
    for owner in sample_ids(structure or set(range(len(members))),180):
        edges = sorted(view.edges[owner],key=lambda e:-np.linalg.norm(e[1][:2]-e[0][:2]))[:3]
        probes.append((owner,[view.blockers((p+q)/2,owner) for p,q in edges]))
    candidates = []
    nonframe = set(range(len(members)))-frame
    for depth in (.35,.65,.85):
        kept,removed = carve(members,view,targets,depth)
        visible = sum(owner in kept and any(not(blockers&kept) for blockers in rays) for owner,rays in probes)
        fraction = visible/max(1,len(probes))
        retention = len(kept&nonframe)/max(1,len(nonframe))
        candidates.append(dict(depth=depth,kept=kept,removed=removed,
            structure_visibility=fraction,context_retention=retention,
            score=fraction+.18*retention))
    return max(candidates,key=lambda c:c['score']),candidates


def anchor_entries(members,lines,targets,kept):
    by_owner = defaultdict(list)
    for owner,line in lines:
        by_owner[owner].append(line)
    entries = []
    for target in targets:
        owner = target['owner']
        candidates = by_owner[owner]
        if not candidates:
            raise ValueError(f'Cutaway target is still hidden: {target["callout"]["id"]}')
        # Every leader lands on an edge from the actual assembled HLR result.
        line = min(candidates,key=lambda s:np.linalg.norm(np.mean(s,axis=0)-target['point'][:2]))
        selected = target['selected'] & kept & set(by_owner)
        entries.append(dict(number=target['number'],callout=target['callout'],
            matched=target['matched'],selected=selected,anchor=np.mean(line,axis=0).tolist(),
            anchor_owner=owner,revealed=False))
    return entries


def retain_arrhenius_assemblies(members,targets,chosen):
    """Keep the courtyard insert and west stair legible as whole assemblies."""
    kept = set(chosen['kept'])
    kept.update(i for i,m in enumerate(members) if m['group'].startswith('Insert/')
                or (m['group'].startswith('Stairs/') and '_W_' in m['name']))
    targets = [dict(t) for t in targets]
    for target in targets:
        if target['callout']['id'] in ('courtyard-insert','curved-stairs','roof-plant'):
            target['selected'] = set(target['matched'])
            kept |= target['selected']
    # Added context may block an earlier leader. Remove only those additions
    # that intersect its established sightline; the original cut stays valid.
    additions = sorted(kept-chosen['kept'])
    if additions:
        view = Projection([members[i] for i in additions])
        for target in targets:
            kept -= {additions[i] for i in view.blockers(target['point'],-1)}
    chosen = dict(chosen,kept=kept,removed=set(range(len(members)))-kept)
    return targets,chosen


def glass_members(members,experiment):
    if experiment not in ('03','14'):
        return set()
    return {i for i,m in enumerate(members) if 'glass' in m['name'].lower()
            or 'glaz' in m['group'].lower()
            or (experiment=='03' and m['layer']=='fixtures')}


def restore_enclosure(members,targets,kept,roof_fraction):
    """Add coherent rear patches, excluding members blocking leader targets."""
    original = set(kept)
    kept = set(kept)
    pools = defaultdict(set)
    for i,m in enumerate(members):
        if m['layer']=='roof':
            pools['roof',m['group']].add(i)
        elif m['layer'] in ('cladding ext','cladding int'):
            pools[m['layer'],''].add(i)
    potential = sorted(set().union(*pools.values())-kept) if pools else []
    blocked = set()
    if potential:
        view = Projection([members[i] for i in potential])
        for target in targets:
            blocked |= {potential[i] for i in view.blockers(target['point'],-1)}
    centers = np.array([np.mean(m['verts'],axis=0) for m in members])
    for (layer,group),pool in pools.items():
        current = len(kept&pool)
        desired = (max(current,math.ceil(len(pool)*roof_fraction)) if layer=='roof'
                   else min(len(pool),current+math.ceil(len(pool)*.12)))
        candidates = sorted(pool-kept-blocked,key=lambda i:(-sum(centers[i,:2]),i))
        kept.update(candidates[:max(0,desired-current)])
    return kept,kept-original


def restore_reviewed_context(members,targets,kept,model_key):
    """Restore complete fixtures and model-specific enclosure patches in place."""
    required,patches = set(),set()
    for i,m in enumerate(members):
        name,group = m['name'],m['group']
        if model_key==('04','fable') and group=='Stairs':
            required.add(i)
        elif model_key==('16','gpt6'):
            if group=='Entrance':
                required.add(i)
            x,y,z = np.mean(m['verts'],axis=0)
            if group=='Facade/EndBoards' and y<0 and 540<x<1200 and z<3000:
                patches.add(i)
        elif model_key==('14','fable'):
            if group=='New/Ladder' or (group=='New/Guards' and name.startswith(('Guard_','VoidGuard_T_'))):
                required.add(i)
            # Whole boards form coherent patches; no fabricated or moved geometry.
            x,y,z = np.mean(m['verts'],axis=0)
            if ((name.startswith('HHClad_S_') and x>=7200)
                or (name.startswith('HHClad_W_') and y>=2400)
                or (name.startswith('HHRoofBoard_S_') and y>=1100)
                or (name.startswith('Clap_S_') and x>=6000)
                or (name.startswith('Clap_W_') and y>=3000)
                or (group=='Existing/Shed_Roof_Boards' and y>=1400)
                or (group=='Existing/HeadHouse_Floor' and y>=2400)
                or (group=='Existing/Terrace_Deck' and (y>=2400 or y<0))):
                patches.add(i)
    # Enclosure patches must not close established leader sightlines.
    potential = sorted(patches-kept-required)
    if potential:
        view = Projection([members[i] for i in potential])
        for target in targets:
            patches -= {potential[i] for i in view.blockers(target['point'],-1)}
    added = (required|patches)-kept
    return kept|added,added


def white_highlights(members,model_key):
    """The large carport slab is the sole exception to inverted black fills."""
    return {i for i,m in enumerate(members) if model_key==('01','fable') and m['name']=='Slab'}


def reviewed_targets(members,targets,model_key):
    """Keep the room-cladding sample on the wall where its leader lands."""
    reviewed = [dict(target) for target in targets]
    if model_key==('16','gpt6'):
        for target in reviewed:
            if target['callout']['id']=='quiet-room':
                group = members[target['owner']]['group']
                target['selected'] = {i for i in target['selected'] if members[i]['group']==group}
    return reviewed


def make_sheet(members,lines,entries,layout,title,slug,version,counts,style,regions,glass,glass_regions,
               white_ids=(),white_regions=()):
    w,h = layout['w'],layout['h']
    sheet = CutawaySheet(w,h)
    scale = layout['factor']
    ox,oy = layout['offset']
    point = lambda p:(p[0]*scale+ox,p[1]*scale+oy)
    selected = set().union(*(e['selected'] for e in entries))
    white_ids = set(white_ids)
    for owner,line in lines:
        frame = members[owner]['layer']=='frame'
        sheet.poly([point(p) for p in line],None,.13 if frame else .10,stroke=.60 if frame else .80)
    if style=='inverted':
        sheet.solid_fill([[point(p) for p in poly] for poly in regions])
        if white_regions:
            sheet.solid_fill([[point(p) for p in poly] for poly in white_regions],'white')
    for owner,line in lines:
        if owner in selected-glass:
            inverted = style=='inverted' and owner not in white_ids
            sheet.poly([point(p) for p in line],None,.07 if inverted else .24,stroke=1 if inverted else 0)
    if glass:
        sheet.glass_tint([[point(p) for p in poly] for poly in glass_regions['context']],.10)
        sheet.glass_tint([[point(p) for p in poly] for poly in glass_regions['selected']],.35 if style=='inverted' else .10)
        for owner,line in lines:
            if owner in glass:
                highlighted = owner in selected
                sheet.poly([point(p) for p in line],None,.16 if highlighted else .10,
                           stroke=(1 if style=='inverted' else .15) if highlighted else .55)
    column,size = layout['column'],layout['size']
    for row in layout['rows']:
        anchor = point(row['anchor'])
        badge = (column-7,row['top']-1.1)
        route = [anchor,(layout['right']+4,anchor[1]),(column-15,badge[1]),(badge[0]-3,badge[1])]
        for a,b in zip(route,route[1:]):
            sheet.poly([a,b],None,.5,stroke=1)
            sheet.poly([a,b],None,FINE,stroke=.27)
        sheet.circle(*anchor,.75,fill=1 if style=='inverted' else 0,lw=FINE)
        sheet.circle(*badge,3,fill=1,lw=THIN)
        sheet.text(badge[0],badge[1]-.9,f'{row["number"]:02d}',2.4,anchor='middle',font=SEGOE,weight=600)
        y = row['top']
        for label in row['label_lines']:
            sheet.text(column,y,label,size,font=SEGOE)
            y -= size*1.25
        for quote in row['quote_lines']:
            sheet.text(column,y,quote,size,font=SEGOE)
            y -= size*1.3
        sheet.text(column,y-1,f'Section {row["callout"]["section"]} / {len(row["selected"])} highlighted of {len(row["matched"])} matches',2.3,font=SEGOE)
    # Compact retained/total key explains the actual omissions per sheet.
    sheet.text(22,91,'MEMBERS RETAINED / ORIGINAL',2.5,font=SEGOE,weight=600)
    for index,(layer,count) in enumerate(counts.items()):
        x = 22+(index%2)*(layout['right']-22)/2
        y = 85-(index//2)*4.6
        sheet.text(x,y,f'{layer}: {count["kept"]}/{count["total"]}',2.4,font=SEGOE)
    sheet.poly([(10,10),(w-10,10),(w-10,h-10),(10,h-10)],None,THIN)
    sheet.text(18,h-21,'ASSEMBLED CUTAWAY / ALL CALLOUTS',3,font=SEGOE,weight=600)
    sheet.text(w-18,h-21,'C / DARK LINES' if style=='lines' else 'D / BLACK FILL + WHITE EDGES',3,anchor='end',font=SEGOE,weight=600)
    if glass:
        sheet.text(22,58,'Glass translucent; framing remains visible through panes.',2.5,font=SEGOE)
    sheet.line((10,46),(w-10,46),.25)
    cd.paragraph(sheet,title,18,36,w-175,3.2,600)
    sheet.text(18,21,f'{slug} / {version} / {len(entries)} callouts',2.8,font=SEGOE)
    sheet.text(18,15,'Original positions. Whole members omitted to expose selected details.',2.5,font=SEGOE)
    sheet.text(w-154,36,'PARALLEL PROJECTION',2.8,font=SEGOE,weight=600)
    frame = counts.get('frame',dict(kept=0,total=0))
    note = f'Frame retained: {frame["kept"]}/{frame["total"]}' if frame['total'] else 'CLT wall / floor structure'
    sheet.text(w-154,28,note,2.4,font=SEGOE)
    sheet.text(w-154,18,'{protocell:labs}',3.5,font=SEGOE,weight=600)
    sheet.poly([(w-36,18),(w-14,18),(w-14,40),(w-36,40)],fill=0,lw=0)
    sheet.text(w-25,24,'C' if style=='lines' else 'D',9,anchor='middle',font=SEGOE,weight=600,white=True)
    return sheet


def render_file(source):
    slug = source.stem.removesuffix('_callouts')
    model_key = (source.parent.name[:2],slug)
    path = max(source.parent.glob(slug+'_v*.json'),key=lambda p:int(p.stem.rsplit('_v',1)[1]))
    members = cd.decode_model(json.loads(path.read_text(encoding='utf-8')))
    callouts = json.loads(source.read_text(encoding='utf-8'))['callouts']
    cache_dir = cd.ROOT/'outputs'/'callout_cutaways_cache'
    cache_dir.mkdir(parents=True,exist_ok=True)
    code = ''.join(inspect.getsource(fn) for fn in (Projection,sample_ids,choose_targets,carve,study,cd.decode_model,cd.owner_lines,_project))
    key = hashlib.sha256(path.read_bytes()+source.read_bytes()+code.encode()).hexdigest()
    cache = cache_dir/(key+'.pickle')
    if cache.exists():
        targets,chosen,trials,lines = pickle.loads(cache.read_bytes())
    else:
        print('  projecting / selecting sightlines',flush=True)
        view = Projection(members)
        targets = choose_targets(members,view,callouts)
        chosen,trials = study(members,view,targets)
        ids = sorted(chosen['kept'])
        print(f'  exact hidden lines: {len(ids)}/{len(members)} members; rear cut {chosen["depth"]}',flush=True)
        lines = [(ids[owner],line) for owner,line in cd.owner_lines([members[i] for i in ids],cd.RIGHT,cd.UP)]
        cache.write_bytes(pickle.dumps((targets,chosen,trials,lines)))
    reviewed_depth,selection_reason = REVIEW_CUTS.get((source.parent.name[:2],slug),
        (None,'Structure visibility balanced with rear context'))
    if reviewed_depth is not None and chosen['depth'] != reviewed_depth:
        chosen = next(trial for trial in trials if trial['depth']==reviewed_depth)
        ids = sorted(chosen['kept'])
        print(f'  reviewed cut: {reviewed_depth}; {len(ids)} retained members',flush=True)
        lines = [(ids[owner],line) for owner,line in cd.owner_lines([members[i] for i in ids],cd.RIGHT,cd.UP)]
        cache.write_bytes(pickle.dumps((targets,chosen,trials,lines)))
    if source.parent.name.startswith('17_') and slug=='astra':
        review_key = hashlib.sha256((key+inspect.getsource(retain_arrhenius_assemblies)).encode()).hexdigest()
        review_cache = cache_dir/(review_key+'.pickle')
        if review_cache.exists():
            targets,chosen,lines = pickle.loads(review_cache.read_bytes())
        else:
            targets,chosen = retain_arrhenius_assemblies(members,targets,chosen)
            ids = sorted(chosen['kept'])
            print(f'  reviewed assemblies: {len(ids)} retained members',flush=True)
            lines = [(ids[owner],line) for owner,line in cd.owner_lines([members[i] for i in ids],cd.RIGHT,cd.UP)]
            review_cache.write_bytes(pickle.dumps((targets,chosen,lines)))
        selection_reason = 'Visual review: preserve courtyard insert, west stair and plant housings as assemblies'
    kept,added = set(chosen['kept']),set()
    if model_key in MORE_ENCLOSURE:
        kept,added = restore_enclosure(members,targets,kept,.5 if model_key in HALF_ROOF else .3)
        selection_reason += '; additional unhighlighted cladding and roof patches'
    kept,review_added = restore_reviewed_context(members,targets,kept,model_key)
    added |= review_added
    glass = glass_members(members,model_key[0])&kept
    targets = reviewed_targets(members,targets,model_key)
    drawing_code = ''.join(inspect.getsource(fn) for fn in
        (restore_enclosure,glass_members,anchor_entries,overview.visible_regions,overview.subtract_convex))
    drawing_key = hashlib.sha256((key+drawing_code+str(sorted(kept))+str(sorted(glass))+
        str([sorted(t['selected']) for t in targets])).encode()).hexdigest()
    drawing_cache = cache_dir/(drawing_key+'.pickle')
    if drawing_cache.exists():
        lines,entries,regions,glass_regions = pickle.loads(drawing_cache.read_bytes())
    else:
        ids = sorted(kept)
        local_glass = {i for i,owner in enumerate(ids) if owner in glass}
        if added or glass:
            print(f'  restoring {len(added)} context members / {len(glass)} translucent panes',flush=True)
            lines = [(ids[owner],line) for owner,line in cd.owner_lines([members[i] for i in ids],cd.RIGHT,cd.UP,local_glass)]
        entries = anchor_entries(members,lines,targets,kept)
        for entry in entries:
            entry['selected'] -= added
        selected = set().union(*(entry['selected'] for entry in entries))
        local_selected = {i for i,owner in enumerate(ids) if owner in selected}
        print('  clipping vector highlight fills',flush=True)
        faces,_ = _project([members[i] for i in ids],cd.RIGHT,cd.UP)
        regions = overview.visible_regions(faces,local_selected-local_glass,local_glass)
        glass_regions = dict(context=overview.visible_regions(faces,local_glass-local_selected,local_glass),
                             selected=overview.visible_regions(faces,local_glass&local_selected,local_glass))
        drawing_cache.write_bytes(pickle.dumps((lines,entries,regions,glass_regions)))
    white_ids = white_highlights(members,model_key)
    white_regions = []
    if white_ids:
        ids = sorted(kept)
        faces,_ = _project([members[i] for i in ids],cd.RIGHT,cd.UP)
        selected = set().union(*(entry['selected'] for entry in entries))
        regions = overview.visible_regions(faces,{i for i,owner in enumerate(ids) if owner in selected-white_ids})
        white_regions = overview.visible_regions(faces,{i for i,owner in enumerate(ids) if owner in white_ids})
    layout = overview.drawing_layout(cd.bounds([members[i] for i in kept]),entries,heading_delta=0)
    # Reserve the bottom of the drawing column for the omission key.
    box = cd.bounds([members[i] for i in kept])
    layout['factor'] = min((layout['right']-22)/(box[2]-box[0]),(layout['h']-143)/(box[3]-box[1]))
    s = layout['factor']
    layout['offset'] = (22+(layout['right']-22-(box[2]-box[0])*s)/2-box[0]*s,
                        105+(layout['h']-143-(box[3]-box[1])*s)/2-box[1]*s)
    totals = Counter(m['layer'] for m in members)
    counts = {layer:dict(kept=sum(members[i]['layer']==layer for i in kept),total=totals[layer]) for layer in cd.ORDER if layer in totals}
    destination = source.parent/'callout_diagrams'/slug/'cutaway'
    destination.mkdir(parents=True,exist_ok=True)
    sheets = []
    for style,filename in (('lines','cutaway.svg'),('inverted','inverted.svg')):
        sheet = make_sheet(members,lines,entries,layout,source.parent.name.replace('_',' '),slug,path.stem,
                           counts,style,regions,glass,glass_regions,white_ids,white_regions)
        svg = sheet.svg()
        (destination/filename).write_text(svg.replace('>','><style>'+font_css(svg)+'</style>',1),encoding='utf-8')
        sheets.append(sheet)
    print_pdf(str(destination/'cutaway.pdf'),sheets)
    from pypdf import PdfReader, PdfWriter
    pair = PdfReader(destination/'cutaway.pdf')
    for style,page in zip(('lines','inverted'),pair.pages):
        writer = PdfWriter()
        writer.add_page(page)
        writer.write(str(destination/(style+'.pdf')))
        writer.close()
    manifest = dict(source=path.relative_to(cd.ROOT).as_posix(),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        callouts_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        projection='orthographic',translation=[0,0,0],orientation='landscape' if layout['w']>layout['h'] else 'portrait',
        body_size_mm=layout['size'],heading_size_mm=layout['size'],metadata_size_mm=2.3,
        styles=['lines','inverted'],layers=counts,cut_depth=chosen['depth'],
        white_highlight_names=[members[i]['name'] for i in sorted(white_ids)],
        added_context_names=[members[i]['name'] for i in sorted(added)],
        translucent_glass_names=[members[i]['name'] for i in sorted(glass)],
        roof_groups={group:dict(total=sum(m['layer']=='roof' and m['group']==group for m in members),
                               kept=sum(members[i]['layer']=='roof' and members[i]['group']==group for i in kept))
                     for group in sorted({m['group'] for m in members if m['layer']=='roof'})},
        fill_fragments=len(regions),
        selection_reason=selection_reason,
        trials=[{k:v for k,v in trial.items() if k not in ('kept','removed')} for trial in trials],
        removed_names=[m['name'] for i,m in enumerate(members) if i not in kept],
        removed_frame_names=[m['name'] for i,m in enumerate(members) if i not in kept and m['layer']=='frame'],
        callouts=[dict(id=e['callout']['id'],number=e['number'],anchor=e['anchor'],anchor_name=members[e['anchor_owner']]['name'],
                       matched_count=len(e['matched']),selected_names=[members[i]['name'] for i in sorted(e['selected'])],
                       internal_view=False) for e in entries],
        reading_order=[e['number'] for e in layout['rows']])
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'  complete: {len(entries)} callouts; frame {counts.get("frame",{})}',flush=True)


def write_index():
    from pypdf import PdfWriter
    atlas,rows = PdfWriter(),[]
    for path in sorted(cd.MODELS.glob('*/callout_diagrams/*/cutaway/manifest.json')):
        folder = path.parent
        relative = folder.relative_to(cd.MODELS).as_posix()
        label = f'{path.parents[3].name.replace("_"," ")} / {path.parents[1].name}'
        atlas.append(str(folder/'cutaway.pdf'),outline_item=label)
        rows.append(f'<tr><th>{html.escape(label)}</th><td><a href="{relative}/cutaway.svg">Line SVG</a> / '
                    f'<a href="{relative}/lines.pdf">Line PDF</a></td><td><a href="{relative}/inverted.svg">Inverted SVG</a> / '
                    f'<a href="{relative}/inverted.pdf">Inverted PDF</a></td><td><a href="{relative}/cutaway.pdf">Both styles</a></td></tr>')
    atlas.write(str(cd.MODELS/'callout_cutaways.pdf'))
    atlas.close()
    (cd.MODELS/'callout_cutaways.html').write_text('<!doctype html><meta charset="utf-8"><title>Assembled callout cutaways</title>'
        '<style>body{font:16px Segoe UI,sans-serif;max-width:1150px;margin:45px auto;line-height:1.6}'
        'th,td{text-align:left;padding:12px;border-bottom:1px solid #ccc}a{color:#222}</style>'
        '<h1>Assembled cutaways</h1><p><a href="callout_cutaways.pdf">Complete cutaway PDF</a></p>'
        '<p>Two A2 sheets per model: dark lines and black fills with white edges. Selected members are omitted to expose callout details; retained geometry stays in its original position. '
        'The frame is prioritized, with any necessary local omissions reported on each sheet.</p>'
        '<p><a href="callout_overviews.html">Exploded comparison sheets</a></p><table>'+''.join(rows)+'</table>',encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--only',default='')
    parser.add_argument('--slug',default='')
    parser.add_argument('--index-only',action='store_true')
    args = parser.parse_args()
    if not args.index_only:
        for path in sorted(cd.MODELS.glob('*/*_callouts.json')):
            if path.parent.name.startswith(args.only) and (not args.slug or path.stem==args.slug+'_callouts'):
                print(path.relative_to(cd.ROOT),flush=True)
                render_file(path)
    write_index()


if __name__=='__main__':
    main()
