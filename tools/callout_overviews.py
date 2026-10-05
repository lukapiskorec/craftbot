"""One exploded sheet per model, in line and inverted highlight variants.

python tools/callout_overviews.py [--only 16] [--slug gpt6]

Reuses the individual-callout renderer. Highlights representative members
of repeated groups, retains every label and quote, and spatially sorts the
numbered callouts to reduce crossings. All fills and edges remain vectors.
"""
import argparse
import hashlib
import html
import inspect
import json
import pickle
from pathlib import Path

import numpy as np

import callout_diagrams as cd
from geometry2d import clip_lin, area
from hidden_lines import _project, EPS
from title_blocks import wrap, SEGOE, MEK
from vector_pdf import A2, FINE, THIN, font_css, print_pdf


def subtract_convex(subject, cutter):
    """Disjoint convex pieces of subject outside a CCW convex cutter."""
    inside, outside = list(subject), []
    for a, b in zip(cutter, list(cutter[1:])+[cutter[0]]):
        ex, ey = b[0]-a[0], b[1]-a[1]
        c, ca, cb = ey*a[0]-ex*a[1], -ey, ex
        piece = clip_lin(inside, -c, -ca, -cb)
        if len(piece) >= 3 and area(piece) > EPS*EPS:
            outside.append(piece)
        inside = clip_lin(inside, c, ca, cb)
        if len(inside) < 3 or area(inside) <= EPS*EPS:
            break
    return outside


def visible_regions(faces, selected, transparent=()):
    """Visible selected face fragments, clipped at actual depth crossings.

    Faces use hidden_lines._project's owner, polygon, plane format. Each
    nearer convex face is subtracted using geometry2d half-plane clipping.
    This keeps black fills behind unselected foreground geometry as well.
    """
    if not faces:
        return []
    owners = np.array([f[0] for f in faces])
    opaque = ~np.isin(owners,list(transparent))
    lows = np.array([f[1].min(0) for f in faces])
    highs = np.array([f[1].max(0) for f in faces])
    planes = np.array([[p[2]+(n[0]*p[0]+n[1]*p[1])/n[2], -n[0]/n[2], -n[1]/n[2]]
                       for _, _, (p,n) in faces])
    regions = []
    for i, (owner, poly, _) in enumerate(faces):
        if owner not in selected:
            continue
        near = np.nonzero(opaque & (owners != owner) & (lows[:,0] < highs[i,0]) & (highs[:,0] > lows[i,0])
                          & (lows[:,1] < highs[i,1]) & (highs[:,1] > lows[i,1]))[0]
        fragments = [poly.tolist()]
        for j in near:
            difference = planes[j]-planes[i]
            difference[0] -= EPS
            cover = clip_lin(faces[j][1].tolist(), *difference)
            if len(cover) < 3 or area(cover) <= EPS*EPS:
                continue
            fragments = [piece for fragment in fragments for piece in subtract_convex(fragment, cover)]
            if not fragments:
                break
        regions.extend(fragments)
    return regions


def selections(members, lines, callouts):
    """One visible anchor and a local representative group for each callout."""
    by_owner = {}
    for owner, line in lines:
        by_owner.setdefault(owner, []).append(line)
    centers = np.array([np.mean(m['verts'], axis=0) for m in members])
    box = cd.bounds(members)
    span = max(box[2]-box[0], box[3]-box[1])
    used, entries = [], []
    for number, callout in enumerate(callouts, 1):
        matched = cd.match_indices(members, callout['match'])
        candidates = [(owner, line) for owner in sorted(matched) for line in by_owner.get(owner, [])]
        revealed = not candidates
        if not candidates:
            focus_ids = sorted(matched)
            candidates = [(focus_ids[owner],line) for owner,line in
                          cd.owner_lines([members[i] for i in focus_ids],cd.RIGHT,cd.UP)]
            if not candidates:
                raise ValueError(f'No drawable geometry for {callout["id"]}')
        def score(candidate):
            _, line = candidate
            midpoint = np.mean(line, axis=0)
            separation = min((np.linalg.norm(midpoint-p)/span for p in used), default=.2)
            length = np.linalg.norm(np.array(line[1])-line[0])/span
            return min(separation,.15)*3 + (midpoint[0]-box[0])/span*.1 + min(length,.03)
        seed, line = max(candidates, key=score)
        anchor = np.mean(line, axis=0)
        used.append(anchor)
        # Complete small sets, local samples for repeated families. Each
        # highlighted member is still an exact match to the authored selector.
        if len(matched) <= 8:
            samples = matched
        else:
            nearest = sorted(matched, key=lambda i: np.linalg.norm(centers[i]-centers[seed]))
            samples = set(nearest[:4]) | {seed}
        entries.append(dict(number=number, callout=callout, matched=matched, selected=samples,
                            anchor=anchor.tolist(), anchor_owner=seed, revealed=revealed))
        if revealed:
            lines.extend((owner,line) for owner,line in candidates if owner in samples)
    return entries


def layout_rows(entries, width, top, bottom, heading_delta=.6):
    """Fit full labels/quotes in one column, ordered by target height."""
    ordered = sorted(entries, key=lambda e: (-e['anchor'][1], e['number']))
    for size in (3.2, 3.0, 2.8):
        rows = []
        for entry in ordered:
            callout = entry['callout']
            label = wrap(callout['label'], width, size+heading_delta, SEGOE, 600)
            quote = wrap(callout.get('quote',''), width, size, SEGOE) if callout.get('quote') else []
            height = len(label)*(size+heading_delta)*1.25+len(quote)*size*1.3+5.5
            rows.append(dict(entry, label_lines=label, quote_lines=quote, height=height))
        gap = (top-bottom-sum(r['height'] for r in rows))/max(1,len(rows)-1)
        if gap >= 3:
            y = top
            for row in rows:
                row.update(top=y, bottom=y-row['height'])
                y -= row['height']+gap
            return rows, size
    raise ValueError('Full callout text does not fit an A2 column at 2.8 mm type')


def drawing_layout(box, entries, heading_delta=.6):
    choices = []
    for w,h in (A2, A2[::-1]):
        column = w*.59
        try:
            rows,size = layout_rows(entries,w-column-22,h-45,62,heading_delta)
        except ValueError:
            continue
        right = column-39
        factor = min((right-22)/(box[2]-box[0]), (h-103)/(box[3]-box[1]))
        ox = 22+(right-22-(box[2]-box[0])*factor)/2-box[0]*factor
        oy = 65+(h-103-(box[3]-box[1])*factor)/2-box[1]*factor
        choices.append(dict(w=w,h=h,column=column,rows=rows,size=size,factor=factor,offset=(ox,oy),right=right))
    if not choices:
        raise ValueError('Neither A2 orientation fits the text')
    return max(choices,key=lambda p:p['factor'])


def make_overview(members,bands,lines,entries,layout,regions,title,slug,version,style):
    w,h = layout['w'],layout['h']
    sheet = cd.CalloutSheet(w,h)
    scale = layout['factor']
    ox,oy = layout['offset']
    point = lambda p:(p[0]*scale+ox,p[1]*scale+oy)
    selected = set().union(*(entry['selected'] for entry in entries))
    # Pale context remains identical between the two comparison sheets.
    for owner,line in lines:
        sheet.poly([point(p) for p in line],None,.10,stroke=.77)
    if style == 'inverted':
        for poly in regions:
            sheet.poly([point(p) for p in poly],fill=0,lw=0,stroke=0)
    for owner,line in lines:
        if owner in selected:
            sheet.poly([point(p) for p in line],None,.05 if style=='inverted' else .22,
                       stroke=1 if style=='inverted' else 0)
    for i,band in enumerate(bands,1):
        sheet.text(20,point((0,band['bounds'][1]))[1]-3,f'{i:02d}  {band["layer"].upper()}',2.3,font=SEGOE)
    column = layout['column']
    size = layout['size']
    # Sorted targets and sorted text rows preserve leader order in the gutter.
    for row in layout['rows']:
        anchor = point(row['anchor'])
        badge = (column-7,row['top']-1.1)
        route = [anchor,(layout['right']+4,anchor[1]),(column-15,badge[1]),(badge[0]-3,badge[1])]
        for a,b in zip(route,route[1:]):
            sheet.poly([a,b],None,.5,stroke=1)
            sheet.poly([a,b],None,FINE,stroke=.27)
        sheet.circle(*anchor,.75,fill=0,lw=FINE)
        sheet.circle(*badge,3,fill=1,lw=THIN)
        sheet.text(badge[0],badge[1]-.9,f'{row["number"]:02d}',2.4,anchor='middle',font=SEGOE,weight=600)
        y = row['top']
        for text in row['label_lines']:
            sheet.text(column,y,text,size+.6,font=SEGOE,weight=600)
            y -= (size+.6)*1.25
        for text in row['quote_lines']:
            sheet.text(column,y,text,size,font=SEGOE)
            y -= size*1.3
        note = ' / internal view through context' if row.get('revealed') else ''
        sheet.text(column,y-1,f'Section {row["callout"]["section"]} / {len(row["selected"])} shown of {len(row["matched"])} matches'+note,2.3,font=SEGOE)
    sheet.poly([(10,10),(w-10,10),(w-10,h-10),(10,h-10)],None,THIN)
    sheet.text(18,h-21,'EXPLODED AXONOMETRIC / ALL CALLOUTS',3,font=MEK)
    variant = 'A / DARK LINES' if style=='lines' else 'B / BLACK FILL + WHITE EDGES'
    sheet.text(w-18,h-21,variant,3,anchor='end',font=MEK)
    sheet.line((10,46),(w-10,46),.25)
    cd.paragraph(sheet,title,18,36,w-175,3.2,600)
    sheet.text(18,21,f'{slug} / {version} / {len(entries)} callouts',2.8,font=SEGOE)
    sheet.text(18,15,'Representative members highlighted; complete callout text retained. Layer gaps diagrammatic.',2.5,font=SEGOE)
    sheet.text(w-154,36,'PARALLEL PROJECTION',2.8,font=SEGOE,weight=600)
    sheet.text(w-154,28,'Original numbers / spatial reading order',2.4,font=SEGOE)
    sheet.text(w-154,18,'{protocell:labs}',3.5,font=MEK)
    sheet.poly([(w-36,18),(w-14,18),(w-14,40),(w-36,40)],fill=0,lw=0)
    sheet.text(w-25,24,'A' if style=='lines' else 'B',9,anchor='middle',font=SEGOE,weight=600,white=True)
    return sheet


def render_file(source):
    slug = source.stem.removesuffix('_callouts')
    path = max(source.parent.glob(slug+'_v*.json'),key=lambda p:int(p.stem.rsplit('_v',1)[1]))
    members = cd.decode_model(json.loads(path.read_text(encoding='utf-8')))
    callouts = json.loads(source.read_text(encoding='utf-8'))['callouts']
    exploded,bands = cd.explode(members,cd.RIGHT,cd.UP)
    cache_dir = cd.ROOT/'outputs'/'callout_overviews_cache'
    cache_dir.mkdir(parents=True,exist_ok=True)
    geometry_code = ''.join(inspect.getsource(fn) for fn in (cd.decode_model,cd.explode,cd.owner_lines,_project))
    key = hashlib.sha256(path.read_bytes()+geometry_code.encode()+cd.RIGHT.tobytes()+cd.UP.tobytes()).hexdigest()
    cache = cache_dir/(key+'.pickle')
    if cache.exists():
        lines = pickle.loads(cache.read_bytes())
    else:
        lines = []
        for band in bands:
            print('  lines: '+band['layer'],flush=True)
            local = cd.owner_lines([exploded[i] for i in band['ids']],cd.RIGHT,cd.UP)
            lines.extend((band['ids'][owner],segment) for owner,segment in local)
        cache.write_bytes(pickle.dumps(lines))
    entries = selections(exploded,lines,callouts)
    selected = set().union(*(e['selected'] for e in entries))
    regions = []
    for band in bands:
        print('  fills: '+band['layer'],flush=True)
        faces,_ = _project([exploded[i] for i in band['ids']],cd.RIGHT,cd.UP)
        local_selected = {i for i,owner in enumerate(band['ids']) if owner in selected}
        regions.extend(visible_regions(faces,local_selected))
    revealed = set().union(*(e['selected'] for e in entries if e['revealed']))
    if revealed:
        # A fully concealed callout is explicitly labelled as an internal
        # view: project its selected members through the pale context.
        faces,_ = _project([exploded[i] for i in sorted(revealed)],cd.RIGHT,cd.UP)
        regions.extend(visible_regions(faces,set(range(len(revealed)))))
    layout = drawing_layout(cd.bounds(exploded),entries)
    destination = source.parent/'callout_diagrams'/slug/'overview'
    destination.mkdir(parents=True,exist_ok=True)
    sheets = []
    for style in ('lines','inverted'):
        sheet = make_overview(exploded,bands,lines,entries,layout,regions,
                              source.parent.name.replace('_',' '),slug,path.stem,style)
        svg = sheet.svg()
        svg = svg.replace('>','><style>'+font_css(svg)+'</style>',1)
        (destination/(style+'.svg')).write_text(svg,encoding='utf-8')
        print_pdf(str(destination/(style+'.pdf')),[sheet])
        sheets.append(sheet)
    print_pdf(str(destination/'comparison.pdf'),sheets)
    manifest = dict(source=path.relative_to(cd.ROOT).as_posix(),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        orientation='landscape' if layout['w']>layout['h'] else 'portrait',body_size_mm=layout['size'],
        scale=1/layout['factor'],face_fragments=len(regions),
        callouts=[dict(id=e['callout']['id'],number=e['number'],anchor=e['anchor'],
                       anchor_name=exploded[e['anchor_owner']]['name'],matched_count=len(e['matched']),
                       internal_view=e['revealed'],
                       selected_names=[exploded[i]['name'] for i in sorted(e['selected'])]) for e in entries],
        reading_order=[e['number'] for e in layout['rows']])
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'  complete: {len(callouts)} callouts / {len(selected)} highlighted members',flush=True)


def write_index():
    from pypdf import PdfWriter
    atlas = PdfWriter()
    rows = []
    for path in sorted(cd.MODELS.glob('*/callout_diagrams/*/overview/manifest.json')):
        folder = path.parent
        relative = folder.relative_to(cd.MODELS).as_posix()
        label = f'{path.parents[3].name.replace("_"," ")} / {path.parents[1].name}'
        atlas.append(str(folder/'comparison.pdf'),outline_item=label)
        rows.append(f'<tr><th>{html.escape(label)}</th>'
                    f'<td><a href="{relative}/lines.svg">SVG</a> / <a href="{relative}/lines.pdf">PDF</a></td>'
                    f'<td><a href="{relative}/inverted.svg">SVG</a> / <a href="{relative}/inverted.pdf">PDF</a></td></tr>')
    atlas.write(str(cd.MODELS/'callout_overviews.pdf'))
    atlas.close()
    (cd.MODELS/'callout_overviews.html').write_text('<!doctype html><meta charset="utf-8"><title>Callout overview comparison</title>'
        '<style>body{font:16px Segoe UI,sans-serif;max-width:1150px;margin:45px auto;line-height:1.6}'
        'th,td{text-align:left;padding:12px;border-bottom:1px solid #ccc}a{color:#222}</style>'
        '<h1>All callouts on one sheet</h1><p><a href="callout_overviews.pdf">Complete comparison PDF</a></p>'
        '<p>Each model has two A2 sheets: A uses dark lines; B uses black fills with white edges. '
        'Both highlight representative members and retain every authored label and quote.</p>'
        '<table><tr><th>Model</th><th>A / Dark lines</th><th>B / Inverted</th></tr>'+''.join(rows)+'</table>',encoding='utf-8')
    original_index = cd.MODELS/'callout_diagrams.html'
    if original_index.exists():
        original = original_index.read_text(encoding='utf-8')
        if 'callout_overviews.html' not in original:
            original_index.write_text(original.replace('<ul>',
                '<p><a href="callout_overviews.html">All callouts on one sheet: compare both styles</a></p><ul>',1),encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--only',default='')
    parser.add_argument('--slug',default='')
    parser.add_argument('--index-only',action='store_true')
    args = parser.parse_args()
    if not args.index_only:
        files = [p for p in sorted(cd.MODELS.glob('*/*_callouts.json')) if p.parent.name.startswith(args.only)
                 and (not args.slug or p.stem==args.slug+'_callouts')]
        if not files:
            parser.error('No matching callout files')
        for path in files:
            print(path.relative_to(cd.ROOT),flush=True)
            render_file(path)
    write_index()


if __name__ == '__main__':
    main()
