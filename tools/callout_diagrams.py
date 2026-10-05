"""Exploded, vector axonometric sheets for viewer/models/**/*_callouts.json.

python tools/callout_diagrams.py [--only 16] [--slug gpt6]

Uses the latest numeric version of each run, the baked viewer layers, and
the fabrication kit's canvas, font metrics and hidden-line projection.
Outputs callout_diagrams/<run>/ beside the model exports. Source JSON is
never changed. Geometry is in real mm; explosion translates whole layers.
"""
import argparse
from collections import defaultdict
import hashlib
import html
import json
import math
from pathlib import Path
import pickle
import re
import time

import numpy as np

from callouts import glob_re
from hidden_lines import EPS, _project, _inside_interval
from title_blocks import wrap, SEGOE, MEK
from vector_pdf import Sheet, A2, THIN, MEDIUM, FINE, print_pdf, font_css

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'viewer' / 'models'
ORDER = ['foundations', 'frame', 'floors', 'interior', 'cladding int',
         'cladding ext', 'fixtures', 'roof', 'other']
TOWARD = np.array([-1., -1., .8])
TOWARD /= np.linalg.norm(TOWARD)
RIGHT = np.cross([0, 0, 1], TOWARD)
RIGHT /= np.linalg.norm(RIGHT)
UP = np.cross(TOWARD, RIGHT)
CORNERS = np.array([[-1,-1,-1], [1,-1,-1], [1,1,-1], [-1,1,-1],
                    [-1,-1,1], [1,-1,1], [1,1,1], [-1,1,1]])
FACES = [[3,2,1,0], [4,5,6,7], [0,1,5,4], [1,2,6,5], [2,3,7,6], [3,0,4,7]]


def compact_svg(svg):
    """Combine consecutive equal-style line elements without changing order."""
    def compact_run(match):
        paths, commands, previous = [], [], None
        for points, style in re.findall(r'<polyline points="([^"]*)"([^>]*)/>', match.group()):
            if previous is not None and style != previous:
                paths.append(f'<path d="{" ".join(commands)}"{previous}/>')
                commands = []
            a, b = points.split()
            commands.append(f'M{a}L{b}')
            previous = style
        paths.append(f'<path d="{" ".join(commands)}"{previous}/>')
        return '\n'.join(paths)+'\n'
    return re.sub(r'(?:<polyline[^\n]*/>\n?)+', compact_run, svg)


class CalloutSheet(Sheet):
    def svg(self):
        return compact_svg(super().svg())


def decode_model(model):
    """Decode row-major affine boxes and world-space mesh vertices, in mm."""
    if (model.get('format'), model.get('version')) != ('craftbot-model', 1):
        raise ValueError('Unsupported model format')
    members = []
    for row in model['boxes']:
        matrix = np.asarray(row[2:14]).reshape(3, 4)
        verts = (CORNERS @ matrix[:, :3].T + matrix[:, 3])*1000
        faces = [f[:] for f in FACES]
        if np.linalg.det(matrix[:, :3]) < 0:
            faces = [f[::-1] for f in faces]
        members.append(dict(name=row[0], group=model['collections'][row[1]],
                            layer=model['layers'][row[14]], verts=verts.tolist(), faces=faces))
    for mesh in model['meshes']:
        verts = np.asarray(mesh['verts']).reshape(-1, 3)*1000
        # Exported members are convex. Normalize winding like the fabrication
        # exporter, including legacy exports with inward-wound end caps.
        faces = []
        center = verts.mean(axis=0)
        for face in mesh['faces']:
            points = verts[face]
            normal = np.cross(points[1]-points[0], points[2]-points[0])
            faces.append(face[::-1] if np.dot(normal, points.mean(0)-center) < 0 else face[:])
        members.append(dict(name=mesh['name'], group=model['collections'][mesh['collection']],
                            layer=model['layers'][mesh['layer']], verts=verts.tolist(), faces=faces))
    if not members:
        raise ValueError('Empty model')
    return members


def bounds(members, right=RIGHT, up=UP):
    points = np.concatenate([m['verts'] for m in members]) @ np.stack([right, up]).T
    return (*points.min(0), *points.max(0))


def explode(members, right, up):
    """Rigid vertical translation per viewer layer, with clear projected gaps."""
    present = {m['layer'] for m in members}
    order = [layer for layer in ORDER if layer in present] + sorted(present-set(ORDER))
    original_bounds = bounds(members, right, up)
    gap = (original_bounds[2]-original_bounds[0])*.07
    exploded = [dict(m) for m in members]
    bands, top = [], None
    for layer in order:
        ids = [i for i, m in enumerate(members) if m['layer'] == layer]
        box = bounds([members[i] for i in ids], right, up)
        dz = 0 if top is None else max(0, (top+gap-box[1])/up[2])
        for i in ids:
            exploded[i]['verts'] = (np.asarray(members[i]['verts'])+[0, 0, dz]).tolist()
        box = bounds([exploded[i] for i in ids], right, up)
        bands.append(dict(layer=layer, ids=ids, offset=[0, 0, dz], bounds=box))
        top = box[3]
    return exploded, bands


def owner_lines(members, right, up, transparent=()):
    """Fabrication hidden-line solver with owner IDs and a spatial broad phase.

    The grid only narrows face candidates; clipping and depth tests are the
    existing hidden_lines algorithm. Owner IDs preserve exact callout matches.
    """
    if not members:
        return []
    faces, edges = _project(members, right, up)
    if transparent:
        faces = [face for face in faces if face[0] not in transparent]
    if not faces:
        return [(owner,(tuple(p[:2]),tuple(q[:2]))) for owner,p,q in edges
                if np.linalg.norm(q[:2]-p[:2]) > EPS]
    owners = np.array([f[0] for f in faces])
    lo = np.array([f[1].min(0) for f in faces])
    hi = np.array([f[1].max(0) for f in faces])
    nearest = np.array([max(origin[2]-(normal[0]*(p[0]-origin[0])+normal[1]*(p[1]-origin[1]))/normal[2]
                            for p in poly) for _, poly, (origin, normal) in faces])
    cell = max(np.ptp(np.concatenate([lo, hi]), axis=0))/max(1, min(128, math.sqrt(len(faces)/8)))
    cell = max(cell, EPS)
    grid = defaultdict(list)

    def cells(a, b):
        lower, upper = np.floor(a[:2]/cell).astype(int), np.floor(b[:2]/cell).astype(int)
        for x in range(lower[0], upper[0]+1):
            for y in range(lower[1], upper[1]+1):
                yield x, y

    for i, (a, b) in enumerate(zip(lo, hi)):
        for key in cells(a, b):
            grid[key].append(i)
    lines = []
    for owner, p, q in edges:
        d = q-p
        length = np.hypot(d[0], d[1])
        if length < EPS:
            continue
        box_lo, box_hi = np.minimum(p, q), np.maximum(p, q)
        candidates = np.array(sorted({i for key in cells(box_lo, box_hi) for i in grid.get(key, [])}), dtype=int)
        candidates = candidates[(owners[candidates] != owner)
                                & (lo[candidates, 0] < box_hi[0]) & (hi[candidates, 0] > box_lo[0])
                                & (lo[candidates, 1] < box_hi[1]) & (hi[candidates, 1] > box_lo[1])
                                & (nearest[candidates] > box_lo[2]+EPS)]
        hidden = []
        for i in candidates:
            _, poly, (origin, normal) = faces[i]
            span = _inside_interval(p[:2], d[:2], poly)
            if span is None:
                continue
            mid = p+d*(span[0]+span[1])/2
            depth = origin[2]-(normal[0]*(mid[0]-origin[0])+normal[1]*(mid[1]-origin[1]))/normal[2]
            if depth > mid[2]+EPS:
                hidden.append(span)
        t = 0.
        for a, b in sorted(hidden)+[(1., 1.)]:
            if (a-t)*length > EPS:
                lines.append((owner, (tuple((p+d*t)[:2]), tuple((p+d*a)[:2]))))
            t = max(t, b)
    return lines


def match_indices(members, match):
    names = glob_re(match.get('names', '*'))
    collections = glob_re(match['collection']) if match.get('collection') else None
    hits = {i for i, m in enumerate(members) if names.match(m['name'])
            and (collections is None or collections.match(m['group']))}
    if not hits:
        raise ValueError(f'No geometry matches {match}')
    return hits


def page_layout(box):
    """Choose the A2 orientation that makes the exploded view largest."""
    choices = []
    for w, h in (A2, A2[::-1]):
        available = (w-180, h-90)
        scale = min(available[0]/(box[2]-box[0]), available[1]/(box[3]-box[1]))
        choices.append((w, h, scale))
    return max(choices, key=lambda choice: choice[2])


def paragraph(sheet, text, x, y, width, size, weight=400):
    for line in wrap(text, width, size, SEGOE, weight):
        sheet.text(x, y, line, size, font=SEGOE, weight=weight)
        y -= size*1.4
    return y


def paint_lines(sheet, lines, factor, offset, selected=None):
    for owner, line in lines:
        active = selected is None or owner in selected
        sheet.poly([(p[0]*factor+offset[0], p[1]*factor+offset[1]) for p in line],
                   fill=None, lw=MEDIUM if active else THIN, stroke=0 if active else .76)


def make_sheet(members, exploded, bands, lines, callout, number, total, model_path, slug):
    selected = match_indices(members, callout['match'])
    box = bounds(exploded)
    w, h, factor = page_layout(box)
    sheet = CalloutSheet(w, h)
    ox = 20+(w-180-(box[2]-box[0])*factor)/2-box[0]*factor
    oy = 58+(h-90-(box[3]-box[1])*factor)/2-box[1]*factor
    sidebar = w-142
    # A2 border, restrained typography, black sheet number and MEK studio mark
    # follow the fabrication sheets; the scale is this diagram's actual scale.
    sheet.poly([(10,10), (w-10,10), (w-10,h-10), (10,h-10)], None, THIN)
    sheet.line((10,42), (w-10,42), MEDIUM)
    sheet.text(18, h-20, 'EXPLODED AXONOMETRIC / DESIGN CALLOUT', 3, font=MEK)
    sheet.text(w-18, h-20, f'{number:02d} / {total:02d}', 3, anchor='end', font=MEK)
    # Alignment datum lies behind the projected layers.
    datum_x = (box[0]+box[2])/2*factor+ox
    sheet.poly([(datum_x, box[1]*factor+oy), (datum_x, box[3]*factor+oy)],
               None, FINE, True, .8)
    paint_lines(sheet, lines, factor, (ox, oy), selected)
    for i, band in enumerate(bands, 1):
        y = band['bounds'][1]*factor+oy-3
        sheet.text(20, y, f'{i:02d}  {band["layer"].upper()}', 2.4, font=SEGOE)
    y = h-40
    sheet.text(sidebar, y, f'CALLOUT {number:02d}  /  SECTION {callout["section"]}', 2.5, font=MEK)
    y = paragraph(sheet, callout['label'], sidebar, y-9, 120, 4.4, 600)-5
    if callout.get('quote'):
        y = paragraph(sheet, callout['quote'], sidebar, y, 120, 3.1)-7
    y = paragraph(sheet, f'{len(selected):,} matching elements. Heavy black lines identify the selection; pale lines show the rest of the model.',
                  sidebar, y, 120, 2.6)-9
    sheet.line((sidebar,y), (w-22,y), FINE)
    y -= 7
    sheet.text(sidebar, y, 'SELECTED ELEMENTS / AS ASSEMBLED', 2.5, font=MEK)
    # The isolated view exposes internal members hidden inside their own layer.
    focus = [members[i] for i in sorted(selected)]
    detail = owner_lines(focus, RIGHT, UP)
    detail_box = bounds(focus)
    detail_height = min(170, y-113)
    if detail_height < 35:
        raise ValueError(f'Callout text leaves no detail space: {callout["id"]}')
    detail_scale = min(116/max(EPS, detail_box[2]-detail_box[0]), detail_height/max(EPS, detail_box[3]-detail_box[1]))
    dx = sidebar+2+(116-(detail_box[2]-detail_box[0])*detail_scale)/2-detail_box[0]*detail_scale
    dy = y-8-(detail_box[3]*detail_scale)
    paint_lines(sheet, detail, detail_scale, (dx, dy))
    sheet.text(sidebar, y-detail_height-15, f'Detail 1:{1/detail_scale:.0f} / same parallel view', 2.5, font=SEGOE)
    # One numbered leader per affected layer, attached to an actually visible
    # selected segment rather than an empty centroid between matched pieces.
    for band in bands:
        candidates = [line for owner, line in lines if owner in selected and owner in band['ids']]
        if not candidates:
            continue
        a, b = max(candidates, key=lambda line: max(p[0] for p in line))
        anchor = ((a[0]+b[0])/2*factor+ox, (a[1]+b[1])/2*factor+oy)
        label = (w-154, anchor[1])
        sheet.line(anchor, (label[0]-3, label[1]), FINE)
        sheet.circle(*anchor, .65, fill=0, lw=FINE)
        sheet.circle(*label, 3.2, fill=1, lw=THIN)
        sheet.text(label[0], label[1]-1, f'{number:02d}', 2.5, anchor='middle', font=SEGOE)
    title = model_path.parent.name.replace('_', ' ')
    paragraph(sheet, title, 18, 32, w-155, 3.2, 600)
    sheet.text(18, 17, f'{slug} / {model_path.stem} / {callout["id"]}', 2.5, font=SEGOE)
    sheet.text(w-130, 32, f'AXONOMETRIC 1:{1/factor:.0f}', 3, font=SEGOE, weight=600)
    sheet.text(w-130, 25, 'Layer gaps diagrammatic', 2.5, font=SEGOE)
    sheet.text(w-130, 17, '{protocell:labs}', 3.5, font=MEK)
    sheet.poly([(w-36,14), (w-14,14), (w-14,36), (w-36,36)], fill=0, lw=0)
    sheet.text(w-25, 20, f'{number:02d}', 9, anchor='middle', font=SEGOE, weight=600, white=True)
    return sheet, dict(id=callout['id'], selected_count=len(selected),
                      selected_names=[members[i]['name'] for i in sorted(selected)],
                      orientation='landscape' if w>h else 'portrait', scale=1/factor)


def render_file(callout_path):
    slug = callout_path.stem.removesuffix('_callouts')
    versions = [(int(m.group(1)), p) for p in callout_path.parent.glob(f'{slug}_v*.json')
                if (m := re.fullmatch(re.escape(slug)+r'_v(\d+)', p.stem))]
    model_path = max(versions)[1]
    model = json.loads(model_path.read_text(encoding='utf-8'))
    callouts = json.loads(callout_path.read_text(encoding='utf-8'))['callouts']
    members = decode_model(model)
    for callout in callouts:
        match_indices(members, callout['match'])
    exploded, bands = explode(members, RIGHT, UP)
    cache = ROOT / 'outputs' / 'callout_diagrams_cache'
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(model_path.read_bytes()+Path(__file__).read_bytes()).hexdigest()
    cached = cache / f'{key}.pickle'
    if cached.exists():
        lines = pickle.loads(cached.read_bytes())
    else:
        lines = []
        for band in bands:
            started = time.monotonic()
            local = owner_lines([exploded[i] for i in band['ids']], RIGHT, UP)
            lines.extend((band['ids'][owner], segment) for owner, segment in local)
            print(f'  {band["layer"]}: {len(local):,} lines ({time.monotonic()-started:.1f}s)', flush=True)
        cached.write_bytes(pickle.dumps(lines))
    destination = callout_path.parent / 'callout_diagrams' / slug
    destination.mkdir(parents=True, exist_ok=True)
    sheets, records = [], []
    for i, callout in enumerate(callouts, 1):
        print(f'  {i}/{len(callouts)} {callout["id"]}', flush=True)
        sheet, record = make_sheet(members, exploded, bands, lines, callout, i, len(callouts), model_path, slug)
        filename = f'{i:02d}_{callout["id"]}.svg'
        svg = sheet.svg()
        # Embed the repo's studio typeface for portable standalone SVGs.
        svg = svg.replace('>', '><style>'+font_css(svg)+'</style>', 1)
        (destination / filename).write_text(svg, encoding='utf-8')
        sheets.append(sheet)
        records.append(dict(record, svg=filename))
    print_pdf(str(destination / 'all_callouts.pdf'), sheets)
    manifest = dict(source=str(model_path.relative_to(ROOT)).replace('\\', '/'),
                    callouts=str(callout_path.relative_to(ROOT)).replace('\\', '/'),
                    source_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest(),
                    member_count=len(members), projection=dict(right=RIGHT.tolist(), up=UP.tolist()),
                    layers=[dict(layer=b['layer'], count=len(b['ids']), offset_mm=b['offset']) for b in bands],
                    drawings=records)
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    links = ''.join(f'<li><a href="{r["svg"]}">{i:02d} - {html.escape(c["label"])}</a></li>'
                    for i, (c,r) in enumerate(zip(callouts, records), 1))
    (destination / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Callout diagrams</title>'
        '<style>body{font:16px Segoe UI,sans-serif;max-width:900px;margin:50px auto;line-height:1.8}a{color:#222}</style>'
        f'<h1>{html.escape(model_path.parent.name.replace("_", " "))}</h1><p>{model_path.name}</p>'
        '<p><a href="all_callouts.pdf">Combined PDF</a></p><ol style="list-style:none;padding:0">'+links+'</ol>', encoding='utf-8')
    return destination


def write_index():
    from pypdf import PdfWriter

    entries = []
    atlas = PdfWriter()
    for path in sorted(MODELS.glob('*/callout_diagrams/*/manifest.json')):
        manifest = json.loads(path.read_text(encoding='utf-8'))
        relative = path.parent.relative_to(MODELS).as_posix()
        entries.append(f'<li><a href="{relative}/index.html">{html.escape(path.parents[2].name.replace("_", " "))} / '
                       f'{path.parent.name}</a> - {len(manifest["drawings"])} diagrams - '
                       f'<a href="{relative}/all_callouts.pdf">PDF</a></li>')
        atlas.append(str(path.parent / 'all_callouts.pdf'),
                     outline_item=f'{path.parents[2].name} / {path.parent.name}')
    if entries:
        atlas.write(str(MODELS / 'callout_diagrams.pdf'))
    atlas.close()
    overview_link = ('<p><a href="callout_overviews.html">All callouts on one sheet: compare both styles</a></p>'
                     if (MODELS / 'callout_overviews.html').exists() else '')
    (MODELS / 'callout_diagrams.html').write_text('<!doctype html><meta charset="utf-8"><title>CraftBot callout diagrams</title>'
        '<style>body{font:16px Segoe UI,sans-serif;max-width:1050px;margin:50px auto;line-height:2}a{color:#222}</style>'
        '<h1>Exploded callout diagrams</h1><p><a href="callout_diagrams.pdf">Complete PDF atlas</a></p>'
        '<p>A2 vector drawings, latest exported model per run. '
        'Black: selected elements. Pale grey: model context. Layer gaps are diagrammatic.</p>'+overview_link+'<ul>'+''.join(entries)+'</ul>', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--only', default='', help='Experiment folder prefix')
    parser.add_argument('--slug', default='', help='Run slug, e.g. gpt6')
    parser.add_argument('--index-only', action='store_true', help='Rebuild the index and PDF atlas from existing sets')
    args = parser.parse_args()
    if args.index_only:
        write_index()
        return
    files = [p for p in sorted(MODELS.glob('*/*_callouts.json')) if p.parent.name.startswith(args.only)
             and (not args.slug or p.stem == args.slug+'_callouts')]
    if not files:
        parser.error('No matching callout files')
    for path in files:
        print(path.relative_to(ROOT), flush=True)
        render_file(path)
    write_index()


if __name__ == '__main__':
    main()
