# A2 line drawings from members.json (written by fab_model.py): plans,
# elevations, sections, the unrolled roof and 1:1 assembly templates, as
# vector PDF and SVG. Hidden lines of the axis-aligned views are removed by
# painting white-filled faces back to front. The axonometrics use the exact
# hidden-line removal in fab_hlr.py. Needs numpy for the axonometrics only.
#
#   python fab_drawings.py
import os
import math
import zlib
import datetime

from fab_cutlist import load, measure, long_axis, sub, dot, cross, unit
from fab_qr import qr_matrix
from fab_hlr import visible_lines

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pdf')
SVG = os.path.join(HERE, 'svg')      # same sheets, for a quick look in a browser
EXPERIMENT = 'Experiment 16 - Expressive Structure'
VIEWER_URL = 'https://lukapiskorec.github.io/craftbot/?model=models%2F16_Expressive_Structure%2Fgpt6_v02.json'
A2 = (420.0, 594.0)     # mm, portrait
MARGIN, TITLE_H = 10.0, 30.0
THIN, MEDIUM, HEAVY = 0.13, 0.25, 0.45   # line widths, mm
GREY = 0.85
X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]
NEG = lambda a: [-c for c in a]

# Helvetica advance widths per 1000 em, for anchoring text in the PDF.
WIDTHS = {' ': 278, '.': 278, ',': 278, ':': 278, '+': 584, '-': 333, '=': 584, '{': 334, '}': 334,
          'i': 222, 'l': 222, 'j': 222, 't': 278, 'f': 278, 'r': 333, 'm': 833, 'w': 722, 'M': 833, 'W': 944, 'I': 278}


def text_width(s, size):
    return sum(WIDTHS.get(c, 667 if c.isupper() else 556 if c.isdigit() else 530) for c in s)*size/1000


# ---------------------------------------------------------------- canvas
class Sheet:
    """One A2 page in mm, origin bottom-left. Collects polygons, lines and
    text, then writes itself as a PDF page stream or an SVG file."""

    def __init__(self, width, height):
        self.w, self.h, self.ops = width, height, []

    def poly(self, pts, fill=1.0, lw=THIN, dash=False, stroke=0.0):
        self.ops.append(('poly', pts, fill, lw, dash, stroke))

    def line(self, a, b, lw=THIN, dash=False):
        self.ops.append(('poly', [a, b], None, lw, dash, 0.0))

    def circle(self, x, y, r, fill=1.0, lw=THIN):
        self.poly([(x+r*math.cos(i*math.pi/12), y+r*math.sin(i*math.pi/12)) for i in range(24)], fill, lw)

    def text(self, x, y, s, size=2.5, anchor='start'):
        self.ops.append(('text', x, y, s, size, anchor))

    def pdf_stream(self):
        k = 72/25.4
        out = ['1 J 1 j']
        for op in self.ops:
            if op[0] == 'poly':
                _, pts, fill, lw, dash, stroke = op
                out.append(f'{lw*k:.3f} w {stroke:.2f} G ' + ('[2 1.5] 0 d' if dash else '[] 0 d'))
                path = ' '.join(f'{x*k:.2f} {y*k:.2f} {"m" if i == 0 else "l"}' for i, (x, y) in enumerate(pts))
                if len(pts) == 2 or fill is None:
                    out.append(path + (' S' if len(pts) == 2 else ' h S'))
                else:
                    out.append(f'{fill:.2f} g {path} h B')
            else:
                _, x, y, s, size, anchor = op
                width = text_width(s, size)
                x -= {'start': 0, 'middle': width/2, 'end': width}[anchor]
                s = s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                out.append(f'0 g BT /F1 {size*k:.2f} Tf {x*k:.2f} {y*k:.2f} Td ({s}) Tj ET')
        return '\n'.join(out).encode('latin-1')

    def svg(self):
        grey = lambda g: '#%02x%02x%02x' % ((int(g*255),)*3)
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" height="{self.h}mm" '
               f'viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/>']
        for op in self.ops:
            if op[0] == 'poly':
                _, pts, fill, lw, dash, stroke = op
                paint = 'none' if fill is None or len(pts) == 2 else grey(fill)
                d = ' '.join(f'{x:.2f},{self.h-y:.2f}' for x, y in pts)
                tag = 'polyline' if len(pts) == 2 else 'polygon'
                out.append(f'<{tag} points="{d}" fill="{paint}" stroke="{grey(stroke)}" stroke-width="{lw}" '
                           f'stroke-linejoin="round" stroke-linecap="round"{" stroke-dasharray=\"2 1.5\"" if dash else ""}/>')
            else:
                _, x, y, s, size, anchor = op
                out.append(f'<text x="{x:.2f}" y="{self.h-y:.2f}" font-family="Helvetica,Arial" '
                           f'font-size="{size}" text-anchor="{anchor}">{s}</text>')
        return '\n'.join(out+['</svg>'])


def write_pdf(path, sheets):
    objects = [None, None, b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>']
    kids = []
    for sheet in sheets:
        stream = zlib.compress(sheet.pdf_stream())
        objects.append(b'<< /Length %d /Filter /FlateDecode >>\nstream\n' % len(stream) + stream + b'\nendstream')
        objects.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Contents %d 0 R '
                       b'/Resources << /Font << /F1 3 0 R >> >> >>' % (sheet.w*72/25.4, sheet.h*72/25.4, len(objects)))
        kids.append(len(objects))
    objects[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[1] = b'<< /Type /Pages /Count %d /Kids [%s] >>' % (len(kids), b' '.join(b'%d 0 R' % k for k in kids))
    body, offsets = b'%PDF-1.4\n', []
    for i, obj in enumerate(objects):
        offsets.append(len(body))
        body += b'%d 0 obj\n' % (i+1) + obj + b'\nendobj\n'
    xref = len(body)
    body += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objects)+1)
    body += b''.join(b'%010d 00000 n \n' % o for o in offsets)
    body += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objects)+1, xref)
    with open(path, 'wb') as f:
        f.write(body)


# ------------------------------------------------------------ projection
def clip_face(pts, d, cut):
    """Part of a 3D polygon with dot(p, d) <= cut, and the points on the plane."""
    out, on_plane = [], []
    for a, b in zip(pts, pts[1:]+pts[:1]):
        da, db = dot(a, d)-cut, dot(b, d)-cut
        if da <= 0:
            out.append(a)
        if da*db < 0:
            t = da/(da-db)
            p = [a[i]+t*(b[i]-a[i]) for i in range(3)]
            out.append(p)
            on_plane.append(p)
    return out, on_plane


def faces_of(member, right, up, toward, cut=None):
    """Front faces of a convex member as (depth, 2D polygon, is_cut)."""
    verts = member['verts']
    polys, cap = [], []
    for face in member['faces']:
        pts = [verts[i] for i in face]
        if cut is not None:
            pts, on_plane = clip_face(pts, toward, cut)
            cap += on_plane
        if len(pts) >= 3:
            polys.append(pts)
    faces = []
    for pts in polys:
        normal = cross(sub(pts[1], pts[0]), sub(pts[2], pts[1]))
        if dot(normal, toward) > 1e-9:
            depth = sum(dot(p, toward) for p in pts)/len(pts)
            faces.append((depth, [(dot(p, right), dot(p, up)) for p in pts], False))
    if len(cap) >= 3:
        flat = [(dot(p, right), dot(p, up)) for p in cap]
        cx, cy = sum(p[0] for p in flat)/len(flat), sum(p[1] for p in flat)/len(flat)
        flat.sort(key=lambda p: math.atan2(p[1]-cy, p[0]-cx))
        faces.append((cut, flat, True))
    return faces


class Drawing:
    """An axis-aligned orthographic view of members. Faces are (depth,
    polygon, fill, line width), sorted back to front. `shade` picks the
    members filled grey."""

    def __init__(self, members, right, up, cut=None, shade=None):
        self.right, self.up, self.toward = right, up, cross(right, up)
        self.faces, self.extra = [], []
        for m in members:
            grey = shade is not None and shade(m)
            for depth, pts, is_cut in faces_of(m, right, up, self.toward, cut):
                self.faces.append((depth, pts, 0.7 if is_cut else (GREY if grey else 1.0), HEAVY if is_cut else THIN))
        self.faces.sort(key=lambda f: f[0])

    def bounds(self):
        xs = [p[0] for f in self.faces for p in f[1]]
        ys = [p[1] for f in self.faces for p in f[1]]
        return min(xs), min(ys), max(xs), max(ys)

    def paint(self, sheet, ox, oy):
        for depth, pts, fill, lw in self.faces:
            sheet.poly([(x+ox, y+oy) for x, y in pts], fill, lw)


class Axo:
    """Axonometric of members seen from the door side and above, as visible
    line segments at `scale` times model size."""

    def __init__(self, members, scale, toward=(-1, -1, 0.8)):
        toward = unit(list(toward))
        right = unit(cross(Z, toward))
        up = cross(toward, right)
        self.lines = [[(x*scale, y*scale) for x, y in line] for line in visible_lines(members, right, up)]
        self.point = lambda p: (dot(p, right)*scale, dot(p, up)*scale)      # model point on the drawing
        self.extra = []

    def bounds(self):
        xs = [p[0] for line in self.lines for p in line]
        ys = [p[1] for line in self.lines for p in line]
        return min(xs), min(ys), max(xs), max(ys)

    def paint(self, sheet, ox, oy):
        for a, b in self.lines:
            sheet.line((a[0]+ox, a[1]+oy), (b[0]+ox, b[1]+oy))


# ----------------------------------------------------------- annotation
def centre(member, axis):
    values = [dot(v, axis) for v in member['verts']]
    return (min(values)+max(values))/2


def depth_layers(members, toward):
    """Layer code per member name: L1 lies on the paper (farthest from the
    viewer), counting up towards the viewer."""
    depth = {m['name']: round(centre(m, toward)*2)/2 for m in members}
    order = sorted(set(depth.values()))
    return {name: f'L{order.index(d)+1}' for name, d in depth.items()}


def covered(point, drawing):
    hits = 0
    for _, pts, _, _ in drawing.faces:
        inside = False
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]+pts[:1]):
            if (y0 > point[1]) != (y1 > point[1]) and point[0] < x0+(point[1]-y0)*(x1-x0)/(y1-y0):
                inside = not inside
        hits += inside
    return hits


def annotate(sheet, drawing, members, layers, ox, oy, min_length=12):
    """Cut length on each piece; beside it a lollipop with stick profile and
    layer code. The lollipop goes to the emptier side of the piece."""
    x0, y0, x1, y1 = drawing.bounds()
    mid = ((x0+x1)/2, (y0+y1)/2)
    pending = []
    spans = [[f(dot(v, a) for v in m['verts']) for a in (drawing.right, drawing.up) for f in (min, max)] for m in members]
    bars = [(x0, y0, x1, y1) for x0, x1, y0, y1 in spans if x1-x0 > y1-y0]      # pieces lying across
    # Upright pieces first: their rows are fixed, the pieces lying across then
    # pick the side that is clear of the circles already placed.
    upright = lambda span: span[3]-span[2] > span[1]-span[0]
    for m, _ in sorted(zip(members, spans), key=lambda pair: not upright(pair[1])):
        length = measure(m)[0]
        if length < min_length:
            continue
        axis = long_axis(m)
        ax, ay = dot(axis, drawing.right), dot(axis, drawing.up)
        norm = math.hypot(ax, ay) or 1
        ax, ay = ax/norm, ay/norm
        # Upright pieces are labelled off-centre so they clear the rails crossing them.
        rise = max(dot(v, drawing.up) for v in m['verts'])-min(dot(v, drawing.up) for v in m['verts'])
        run = max(dot(v, drawing.right) for v in m['verts'])-min(dot(v, drawing.right) for v in m['verts'])
        px, py = centre(m, drawing.right), centre(m, drawing.up)+(0.15*rise if rise > run else 0)
        if rise > run:       # drop the label and its lollipop below any rail they would sit on
            for bx0, by0, bx1, by1 in bars:
                if bx0 <= px <= bx1 and by0-5 < py < by1+5:
                    py = by0-5
        sheet.text(px+ox, py+oy-0.6, f'{length:.1f}', 1.7, 'middle')
        reach = 9.0
        sides = [(px-ay*reach*s, py+ax*reach*s) for s in (1, -1)]
        crowd = lambda c: sum(math.hypot(c[0]-q[1][0], c[1]-q[1][1]) < 7 for q in pending)
        sides.sort(key=lambda c: (crowd(c), covered(c, drawing), -math.hypot(c[0]-mid[0], c[1]-mid[1])))
        pending.append(((px, py), sides[0], m['stock'], layers[m['name']]))
    for (px, py), (cx, cy), stock, layer in pending:
        dx, dy = cx-px, cy-py
        d = math.hypot(dx, dy)
        sheet.line((px+dx/d*1.6+ox, py+dy/d*1.6+oy), (cx+ox, cy+oy), THIN)
    for _, (cx, cy), stock, layer in pending:
        sheet.circle(cx+ox, cy+oy, 3.3)
        sheet.text(cx+ox, cy+oy+0.35, stock, 1.5, 'middle')
        sheet.text(cx+ox, cy+oy-1.45, layer, 1.5, 'middle')


def add_levels(drawing):
    for metres in (0, 1.5, 3, 4.5, 5.25, 6):
        drawing.extra.append(('level', metres*1000/SCALE, f'+{metres*1000/SCALE:.0f}'))


def add_frame_axes(drawing, kind, sign=1):
    for j, y in zip(DATA['frames'], DATA['frame_y']):
        drawing.extra.append((kind, sign*y, f'F{j}'))


def paint_extras(sheet, drawing, ox, oy):
    x0, y0, x1, y1 = drawing.bounds()
    for kind, value, label in drawing.extra:
        if kind == 'level':       # horizontal datum at the left edge, model mm
            sheet.line((MARGIN+2, value+oy), (x0+ox-3, value+oy), THIN, dash=True)
            sheet.text(MARGIN+2, value+oy+0.8, label, 2.4)
        elif kind == 'axis_x':    # frame axis under the drawing
            sheet.line((value+ox, y0+oy-2), (value+ox, y0+oy-7), THIN)
            sheet.text(value+ox, y0+oy-10.5, label, 2.6, 'middle')
        elif kind == 'axis_y':
            sheet.line((x0+ox-2, value+oy), (x0+ox-7, value+oy), THIN)
            sheet.text(x0+ox-8, value+oy-0.9, label, 2.6, 'end')
        elif kind == 'tag':       # leader from a point on the drawing to a label on its left
            (ax, ay), (bx, by) = value
            sheet.line((ax+ox, ay+oy), (bx+ox, by+oy), THIN)
            sheet.text(bx+ox-1.5, by+oy-1.1, label, 3.2, 'end')


# ------------------------------------------------------------ the sheet
QR = []


def title_block(sheet, number, title, note, scale_text=None):
    w, h = sheet.w, sheet.h
    sheet.poly([(MARGIN, MARGIN), (w-MARGIN, MARGIN), (w-MARGIN, h-MARGIN), (MARGIN, h-MARGIN)], fill=None, lw=MEDIUM)
    sheet.line((MARGIN, MARGIN+TITLE_H), (w-MARGIN, MARGIN+TITLE_H), MEDIUM)
    if note:
        sheet.text(MARGIN+4, MARGIN+TITLE_H+3, note, 2.7)
    sheet.text(MARGIN+4, MARGIN+20.5, f'{number:02d}  {title}', 5)
    sheet.text(MARGIN+4, MARGIN+12, EXPERIMENT, 3.8)
    sheet.text(MARGIN+4, MARGIN+4.5, f'GPT-6 v02, stick model. CraftBot fabrication set, {datetime.date.today().isoformat()}', 2.6)
    # Print check and studio mark, centred.
    bx, by = w/2-50, MARGIN+14.5
    sheet.text(w/2, by+6, f'100 mm in 1:{SCALE} = {100*SCALE/1000:.1f} m in 1:1', 2.8, 'middle')
    sheet.line((bx, by), (bx+100, by), MEDIUM)
    for i in range(11):
        sheet.line((bx+10*i, by), (bx+10*i, by+(3 if i % 5 == 0 else 1.8)), MEDIUM)
    sheet.text(w/2, MARGIN+5, '{protocell:labs}', 3.6, 'middle')
    # QR code to the online viewer, dark modules merged into row runs.
    if not QR:
        QR.extend(qr_matrix(VIEWER_URL))
    n, side = len(QR), 24.0
    cell = side/n
    qx, qy = w-MARGIN-3-side, MARGIN+3
    for r, row in enumerate(QR):
        c = 0
        while c < n:
            run = c
            while run < n and row[run]:
                run += 1
            if run > c:
                y1 = qy+side-r*cell
                sheet.poly([(qx+c*cell, y1), (qx+run*cell, y1), (qx+run*cell, y1-cell), (qx+c*cell, y1-cell)], fill=0.0, lw=0.01)
            c = run+1
    sheet.text(qx-5, MARGIN+20.5, '3D model in CraftBot online viewer', 3.0, 'end')
    sheet.text(qx-5, MARGIN+12, scale_text or f'Scale 1:{SCALE}, drawn 1:1 to the model.', 3.0, 'end')
    sheet.text(qx-5, MARGIN+4.5, 'All numbers on this sheet are model mm.', 2.6, 'end')


def place(bounds, w, h, pad_left=16):
    """Offsets that centre a bounding box in the free area of a sheet."""
    x0, y0, x1, y1 = bounds
    free_w, free_h = w-2*MARGIN-pad_left, h-2*MARGIN-TITLE_H-14
    assert x1-x0 <= free_w and y1-y0 <= free_h, f'{x1-x0:.0f} x {y1-y0:.0f} mm does not fit A2'
    return MARGIN+pad_left+(free_w-(x1-x0))/2-x0, MARGIN+TITLE_H+10+(free_h-(y1-y0))/2-y0


def make_sheet(number, title, drawing, note='', labelled=(), layers=None, scale_text=None):
    x0, y0, x1, y1 = drawing.bounds()
    w, h = A2 if (y1-y0) > (x1-x0) else A2[::-1]
    sheet = Sheet(w, h)
    ox, oy = place(drawing.bounds(), w, h)
    drawing.paint(sheet, ox, oy)
    paint_extras(sheet, drawing, ox, oy)
    if labelled:
        annotate(sheet, drawing, labelled, layers, ox, oy)
    title_block(sheet, number, title, note, scale_text)
    return sheet


# ---------------------------------------------------------------- sheets
def in_groups(members, *prefixes):
    return [m for m in members if m['group'].startswith(prefixes) or m['name'].startswith(prefixes)]


def area(pts):
    return sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(pts, pts[1:]+pts[:1]))/2


def frame_template(number, j, y, members):
    """One truss frame: the template (all layers as outlines, web layer
    grey), a side view with the layer codes, and an axonometric."""
    frame = [m for m in in_groups(members, 'Structure', 'RoofStructure') if abs(centre(m, Y)-y) < 3*STICK_T]
    offset = lambda m: round((centre(m, Y)-y)/STICK_T)      # -2 .. 2, door side negative
    is_web = lambda m: offset(m) == 0
    # L1 lies on the paper. The template is seen from the door side, so the
    # far strap layer is L1 and the door-side strap layer is L5.
    code = {2: 'L1+L5', 1: 'L2+L4', 0: 'L3'}
    layers = {m['name']: code[abs(offset(m))] for m in frame}

    main = Drawing(frame, X, Z)
    add_levels(main)
    outlines = []
    for m in frame:
        if offset(m) > 0:
            continue      # the two plies share one outline; draw the door-side ply
        pts = max(faces_of(m, X, Z, main.toward), key=lambda f: abs(area(f[1])))[1]
        rank = 0 if is_web(m) else (2 if abs(offset(m)) == 2 else 1)
        outlines.append((rank, pts, GREY if is_web(m) else None, MEDIUM if rank == 1 else THIN))
    main.faces = sorted(outlines, key=lambda o: o[0])

    side = Drawing(frame, Y, Z, shade=is_web)
    axo = Axo(frame, SCALE/40)

    sheet = Sheet(*A2)
    gap = 24
    mx0, my0, mx1, my1 = main.bounds()
    sx0, sy0, sx1, sy1 = side.bounds()
    ox, oy = place((mx0-10, my0, mx1+gap+(sx1-sx0)+6, my1), *A2)
    main.paint(sheet, ox, oy)
    paint_extras(sheet, main, ox, oy)
    annotate(sheet, main, [m for m in frame if offset(m) <= 0], layers, ox, oy)
    # Side view to the right at the same height, layer codes above and below.
    sox = ox+mx1+gap-sx0
    side.paint(sheet, sox, oy)
    for k in range(-2, 3):
        for yy in (sy1+oy+2.5, sy0+oy-4):
            sheet.text(sox+y+k*STICK_T, yy, f'L{3-k}', 1.6, 'middle')
    sheet.text(sox+y, sy1+oy+11, 'Side view', 2.6, 'middle')
    sheet.text(sox+y, sy1+oy+7, 'paper side L1 right', 2.0, 'middle')
    # Axonometric in the room opening.
    ax0, ay0, ax1, ay1 = axo.bounds()
    aox, aoy = ox-(ax0+ax1)/2, oy+3.0*1000/SCALE-(ay0+ay1)/2
    axo.paint(sheet, aox, aoy)
    sheet.text(ox, aoy+ay0-6, 'Axonometric 1:40, seen from the door side', 2.6, 'middle')
    note = ('Glue-up template. Grey: web layer L3, one ply. Heavy outline: chords, plies L2 and L4 on both sides of the webs. '
            'Thin rectangles: 20 mm straps, L1 and L5. Circles: stick profile and layer. L1 lies on the paper.')
    title_block(sheet, number, f'Frame F{j} template', note)
    return sheet


class Flat:
    """2D outlines that are already on the sheet plane (the unrolled roof)."""

    def __init__(self):
        self.faces = []

    bounds, paint = Drawing.bounds, Drawing.paint


def unrolled_roof(number, members):
    """Each bay of roof boards is a strip of six planar panels that fold
    along lines parallel to the boards. Unfold every strip flat, panel by
    panel, each joined to the last along their shared fold line."""
    boards = {}
    for m in in_groups(members, 'RoofBoard'):
        _, j, k, i = m['name'].split('_')
        boards.setdefault(int(j), {}).setdefault(int(k), []).append((int(i), m))
    ring = lambda m: m['verts'][:4]      # underside: (a,y0) (b,y0) (b,y1) (a,y1)
    flat, labels, strips, top = Flat(), [], [], 0.0
    for j in sorted(boards):
        strip, joint = [], None      # joint: 2D end points of the last fold line
        for k in sorted(boards[j]):
            row = [m for _, m in sorted(boards[j][k])]
            p0, p1, _, p3 = ring(row[0])
            u = unit(sub(p1, p0))
            v = unit(cross(cross(sub(p1, p0), sub(p3, p0)), u))
            local = lambda p: (dot(sub(p, p0), u), dot(sub(p, p0), v))
            a1 = local(p3)
            turn, shift = 0.0, (0.0, 0.0)
            if joint:
                turn = math.atan2(joint[1][1]-joint[0][1], joint[1][0]-joint[0][0])-math.atan2(a1[1], a1[0])
                shift = joint[0]
            c, s = math.cos(turn), math.sin(turn)
            move = lambda q: (shift[0]+c*q[0]-s*q[1], shift[1]+s*q[0]+c*q[1])
            for i, m in enumerate(row):
                strip.append(([move(local(p)) for p in ring(m)], m, k, i))
            last = ring(row[-1])
            joint = (move(local(last[1])), move(local(last[2])))
        low = min(p[1] for pts, *_ in strip for p in pts)
        high = max(p[1] for pts, *_ in strip for p in pts)
        for pts, m, k, i in strip:
            pts = [(x, y-low+top) for x, y in pts]
            flat.faces.append((0, pts, 1.0, THIN))
            labels.append((pts, f'{measure(m)[0]:.1f}', k, i))
        left = min(p[0] for pts, *_ in strip for p in pts)
        strips.append((left, top+(high-low)/2, f'Bay F{DATA["frames"][j]}-F{DATA["frames"][j+1]}'))
        top += high-low+18
    w, h = A2[::-1]
    sheet = Sheet(w, h)
    ox, oy = place(flat.bounds(), w, h, pad_left=30)
    flat.paint(sheet, ox, oy)
    for pts, text, k, i in labels:
        cx, cy = sum(p[0] for p in pts)/4+ox, sum(p[1] for p in pts)/4+oy
        sheet.text(cx, cy-0.6, text, 1.7, 'middle')
        if i == 0:       # fold line at the start of every panel, and one lollipop per panel
            if k:
                sheet.line((pts[0][0]+ox, pts[0][1]+oy), (pts[3][0]+ox, pts[3][1]+oy), HEAVY)
            lx, ly = cx, pts[0][1]+oy-8
            sheet.line((cx, pts[0][1]+oy+1.5), (lx, ly), THIN)
            sheet.circle(lx, ly, 3.3)
            sheet.text(lx, ly+0.35, '2x10', 1.5, 'middle')
            sheet.text(lx, ly-1.45, f'P{k+1}', 1.5, 'middle')
    for x, y, label in strips:
        sheet.text(x+ox-6, y+oy-1, label, 2.8, 'end')
    note = ('Roof boards of each bay laid flat, door end at the bottom, -x on the left. Heavy lines: folds between the six planar panels P1 to P6 of a strip. '
            'Numbers: cut length in mm. All boards 2x10, one layer.')
    title_block(sheet, number, 'Roof boards, unrolled', note)
    return sheet


def build_sheets():
    members = DATA['members']
    mm = lambda metres: metres*1000/SCALE
    sheets, n = [], 0

    def add(title, subset, right, up, cut=None, note='', axes=None, levels=False, labels=False):
        nonlocal n
        n += 1
        drawing = Drawing(subset, right, up, cut)
        if levels: add_levels(drawing)
        if axes: add_frame_axes(drawing, *axes)
        layers = depth_layers(subset, drawing.toward) if labels else None
        sheets.append((title, make_sheet(n, title, drawing, note, subset if labels else (), layers)))

    lollipop_note = ' Numbers: cut length in mm. Circles: stick profile and layer, L1 lies on the paper.'
    ground = in_groups(members, 'Ground', 'Bracing/GroundPlan')
    add('Plan, ground mat', ground, X, Y, axes=('axis_y',), labels=True,
        note='Two crossed sleeper layers with sole runners and plan braces. Door end at the bottom.'+lollipop_note)
    add('Plan, section at +80 mm', members, X, Y, cut=mm(1.2), axes=('axis_y',),
        note='Horizontal section 80 mm above the floor, looking down. Cut members shaded.')
    roof_frame = in_groups(members, 'RoofStructure', 'Bracing/RoofPlan', 'Ceiling', 'Structure')
    add('Plan, roof framing', roof_frame, X, Y, axes=('axis_y',), note='Roof boards removed. Crossed plan braces lie between the lower chords.')
    n += 1
    sheets.append(('Roof boards, unrolled', unrolled_roof(n, members)))
    add('Elevation, door end', members, X, Z, levels=True)
    add('Elevation, far end', members, NEG(X), Z, levels=True)
    add('Elevation, side plus x', members, Y, Z, levels=True, axes=('axis_x',))
    add('Elevation, side minus x', members, NEG(Y), Z, levels=True, axes=('axis_x', -1))
    bay = (DATA['frame_y'][0]+DATA['frame_y'][1])/2
    add('Cross section, first bay', members, X, Z, cut=-bay, levels=True,
        note='Cut midway between F0 and F1, looking away from the door. Cut members shaded.')
    add('Long section, centre line', members, NEG(Y), Z, cut=mm(0.02), levels=True, axes=('axis_x', -1),
        note='Cut 1.3 mm off the centre line so it passes through boards, not between them. Looking towards -x. Cut members shaded.')
    for j, y in zip(DATA['frames'], DATA['frame_y']):
        n += 1
        sheets.append((f'Frame F{j} template', frame_template(n, j, y, members)))
    wall_note = 'Glue-up template seen from outside: boards behind, rails in front.'+lollipop_note
    side = [m for m in in_groups(members, 'SideRail', 'SideBoard') if centre(m, X) > 0]
    add('Side wall template (both sides)', side, Y, Z, levels=True, labels=True, note=wall_note+' Build two, the second mirrored.')
    door = [m for m in in_groups(members, 'EndRail', 'EndBoard', 'Entrance') if centre(m, Y) < 0 and not m['name'].startswith('EntranceBaseSeat')]
    add('Door wall template', door, X, Z, levels=True, labels=True, note=wall_note)
    far = [m for m in in_groups(members, 'EndRail', 'EndBoard') if centre(m, Y) > 0]
    if far:
        add('Far wall template', far, NEG(X), Z, levels=True, labels=True, note=wall_note)
    for title, layers in (('Axonometric, frame layer', ('frame',)),
                          ('Axonometric, cladding and fixtures', ('cladding ext', 'fixtures'))):
        n += 1
        note = 'Every member of the viewer layer' + ('s ' if len(layers) > 1 else ' ') + ' and '.join(f'"{name}"' for name in layers) + '. Seen from the door side.'
        subset = [m for m in members if m['layer'] in layers]
        axo = Axo(subset, SCALE/20)
        # Frame names at the foot of the -x side, on each frame line.
        x_end = min(v[0] for m in subset for v in m['verts'])
        z_low = min(v[2] for m in subset for v in m['verts'])
        for j, y in zip(DATA['frames'], DATA['frame_y']):
            axo.extra.append(('tag', (axo.point([x_end, y, z_low]), axo.point([x_end-24, y, z_low])), f'F{j}'))
        sheets.append((title, make_sheet(n, title, axo, note, scale_text='Axonometric, scale 1:20.')))
    return sheets


if __name__ == '__main__':
    DATA = load()
    SCALE = DATA['scale']
    STICK_T = 3.0
    for folder in (OUT, SVG):
        os.makedirs(folder, exist_ok=True)
        for old in os.listdir(folder):
            os.remove(os.path.join(folder, old))
    sheets = build_sheets()
    for i, (title, sheet) in enumerate(sheets, 1):
        slug = f'{i:02d}_' + ''.join(c if c.isalnum() else '_' for c in title.lower()).strip('_').replace('__', '_')
        write_pdf(os.path.join(OUT, slug+'.pdf'), [sheet])
        with open(os.path.join(SVG, slug+'.svg'), 'w', encoding='utf-8') as f:
            f.write(sheet.svg())
    write_pdf(os.path.join(OUT, '00_all_sheets.pdf'), [s for _, s in sheets])
    print(f'Wrote {len(sheets)} A2 sheets to {OUT}')
