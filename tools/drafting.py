"""Drafting kit for fabrication sheets: views, sections, labels, title block.

Works on the members of `members.json` (see `export_members.py`), in model
millimetres, and draws on `vector_pdf.Sheet` pages at 1:1 to the model.

- `Drawing` is an axis-aligned view (plan, elevation) or, with `cut`, a
  section. Hidden lines are removed by painting white faces back to front,
  which is exact for axis-aligned views of convex members only.
- `Axo` is an axonometric with exact hidden lines from `hidden_lines.py`.
- `annotate` writes the cut length on each piece and a lollipop beside it
  with the stick profile and the layer code; `depth_layers` numbers the
  layers from the paper up.
- `SheetSet` numbers the sheets, draws the title block picked with `footer`
  from `title_blocks.py` (print check bar, QR code to the viewer) and
  writes the PDFs, printed by headless Chrome, and the SVGs.
- `unroll` lays a folded strip of planar facets flat.

A sheet that does not fit raises: pick the model scale so the largest
template fits the paper.

Provenance: experiment 16 fabrication set.
"""
import os
import math

from vector_pdf import Sheet, print_pdf, A2, THIN, MEDIUM, HEAVY
from title_blocks import FOOTERS, DEFAULT, Block
from cutlist import measure, long_axis, sub, dot, cross, unit
from qr_code import qr_matrix

MARGIN, TITLE_H = 10.0, 32.0     # mm: sheet border, height of the default title block
GREY = 0.85
X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]


def NEG(a):
    """The opposite axis."""
    return [-c for c in a]


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
    """An axis-aligned view of members (plan, elevation, or a section when `cut` is given) with the viewer at cross(right, up).
    `cut` is a position along that viewer axis: everything nearer to the
    viewer than `cut` is removed and the cut faces are shaded, so the
    elevation `X, Z` (viewer at -y) with `cut=-700` is the section at
    y = 700 looking towards +y. `shade` is a function of a member that
    returns True for the members filled grey. Faces are (depth, polygon,
    fill, line width), sorted back to front."""

    def __init__(self, members, right, up, cut=None, shade=None):
        self.right, self.up, self.toward = right, up, cross(right, up)
        self.faces, self.extra = [], []
        for m in members:
            grey = shade is not None and shade(m)
            for depth, pts, is_cut in faces_of(m, right, up, self.toward, cut):
                self.faces.append((depth, pts, 0.7 if is_cut else (GREY if grey else 1.0), HEAVY if is_cut else THIN))
        self.faces.sort(key=lambda f: f[0])

    def bounds(self):
        """(x0, y0, x1, y1) of the drawing."""
        xs = [p[0] for f in self.faces for p in f[1]]
        ys = [p[1] for f in self.faces for p in f[1]]
        return min(xs), min(ys), max(xs), max(ys)

    def paint(self, sheet, ox, oy):
        """Draw on the sheet with the drawing origin at (ox, oy)."""
        for depth, pts, fill, lw in self.faces:
            sheet.poly([(x+ox, y+oy) for x, y in pts], fill, lw)


class Flat:
    """2D outlines that are already on the sheet plane (an unrolled surface).
    Append (0, polygon, fill, line width) to `faces`."""

    def __init__(self):
        self.faces, self.extra = [], []

    bounds, paint = Drawing.bounds, Drawing.paint


class Axo:
    """Axonometric of members with exact hidden lines, drawn at `scale` times model size (pass `scale_text` to the sheet when it is not 1), `toward` pointing from the model to the viewer.
    `point(p)` gives the drawing position of a 3D model point, for tags."""

    def __init__(self, members, scale, toward=(-1, -1, 0.8)):
        from hidden_lines import visible_lines      # numpy only when an axonometric is drawn
        toward = unit(list(toward))
        right = unit(cross(Z, toward))
        up = cross(toward, right)
        self.lines = [[(x*scale, y*scale) for x, y in line] for line in visible_lines(members, right, up)]
        self.point = lambda p: (dot(p, right)*scale, dot(p, up)*scale)      # model point on the drawing
        self.extra = []

    def bounds(self):
        """(x0, y0, x1, y1) of the drawing."""
        xs = [p[0] for line in self.lines for p in line]
        ys = [p[1] for line in self.lines for p in line]
        return min(xs), min(ys), max(xs), max(ys)

    def paint(self, sheet, ox, oy):
        """Draw on the sheet with the drawing origin at (ox, oy)."""
        for a, b in self.lines:
            sheet.line((a[0]+ox, a[1]+oy), (b[0]+ox, b[1]+oy))


def unroll(facets):
    """Lay a folded strip flat. `facets` is a list of planar facets in strip
    order; a facet is a list of 3D quads (p0, p1, p2, p3) in order across it,
    with p0-p3 on the fold towards the previous facet and p1-p2 towards the
    next. Returns the same structure in 2D, each facet joined to the last
    along their shared fold line, so lengths and angles are true."""
    out, joint = [], None      # joint: 2D end points of the last fold line
    for quads in facets:
        p0, p1, _, p3 = quads[0]
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
        out.append([[move(local(p)) for p in quad] for quad in quads])
        joint = (out[-1][-1][1], out[-1][-1][2])
    return out


# ----------------------------------------------------------- annotation
def in_groups(members, *prefixes):
    """Members whose collection path or name starts with one of the prefixes."""
    return [m for m in members if m['group'].startswith(prefixes) or m['name'].startswith(prefixes)]


def centre(member, axis):
    """Mid-extent of a member along an axis."""
    values = [dot(v, axis) for v in member['verts']]
    return (min(values)+max(values))/2


def area(pts):
    """Signed area of a 2D polygon."""
    return sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(pts, pts[1:]+pts[:1]))/2


def depth_layers(members, toward):
    """Layer code per member name, L1 lying on the paper (farthest from the viewer) and counting up, for `toward` pointing at the viewer (pass `drawing.toward`)."""
    depth = {m['name']: round(centre(m, toward)*2)/2 for m in members}
    order = sorted(set(depth.values()))
    return {name: f'L{order.index(d)+1}' for name, d in depth.items()}


def covered(point, drawing):
    """How many faces of the drawing cover a 2D point."""
    hits = 0
    for _, pts, _, _ in drawing.faces:
        inside = False
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]+pts[:1]):
            if (y0 > point[1]) != (y1 > point[1]) and point[0] < x0+(point[1]-y0)*(x1-x0)/(y1-y0):
                inside = not inside
        hits += inside
    return hits


def annotate(sheet, drawing, members, layers, ox, oy, min_length=12):
    """Cut length on each piece at least `min_length` long, and beside it a lollipop with stick profile and layer code (`layers` maps member name to code, see `depth_layers`).
    The lollipop goes to the side of the piece with fewer circles and less
    drawing under it. Pieces with the same outline in this view (the plies
    of a layered assembly) are labelled once, with their codes joined as
    'L1+L3'."""
    members, layers = merge_coincident(members, layers, drawing)
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
        pending.append(((px, py), sides[0], m['stock'] or '', layers[m['name']]))
    for (px, py), (cx, cy), stock, layer in pending:
        dx, dy = cx-px, cy-py
        d = math.hypot(dx, dy)
        sheet.line((px+dx/d*1.6+ox, py+dy/d*1.6+oy), (cx+ox, cy+oy), THIN)
    for _, (cx, cy), stock, layer in pending:
        lollipop(sheet, cx+ox, cy+oy, stock, layer)


def merge_coincident(members, layers, drawing):
    """Members to label and their layer codes, with pieces that share one outline in the view reduced to the first and its codes joined ('L2+L4')."""
    groups = {}
    for m in members:
        spans = [f(dot(v, a) for v in m['verts']) for a in (drawing.right, drawing.up) for f in (min, max)]
        axis = long_axis(m)      # two crossed braces share a bounding box but not a direction
        ax, ay = round(dot(axis, drawing.right), 2), round(dot(axis, drawing.up), 2)
        if (ax, ay) < (0, 0):
            ax, ay = -ax, -ay
        groups.setdefault((m['stock'], ax, ay)+tuple(round(s, 1) for s in spans), []).append(m)
    kept = [group[0] for group in groups.values()]
    codes = {group[0]['name']: '+'.join(sorted({layers[m['name']] for m in group})) for group in groups.values()}
    return kept, codes


def lollipop(sheet, x, y, upper, lower):
    """The label circle: two short lines of text, stick profile over layer code."""
    sheet.circle(x, y, 3.3)
    sheet.text(x, y+0.35, upper, 1.5, 'middle')
    sheet.text(x, y-1.45, lower, 1.5, 'middle')


def add_marks(drawing, kind, marks):
    """Reference marks `[(position in drawing mm, label)]` of `kind` 'level' (dashed datum from the left border, for elevations), 'axis_x' (tick under the drawing) or 'axis_y' (tick to its left)."""
    drawing.extra += [(kind, value, label) for value, label in marks]


def add_tag(drawing, anchor, label_at, label):
    """A leader from `anchor` to `label_at` (both 2D drawing points) with the label on its left."""
    drawing.extra.append(('tag', (anchor, label_at), label))


def paint_extras(sheet, drawing, ox, oy):
    """Draw the marks and tags of a drawing placed at (ox, oy)."""
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


# ------------------------------------------------------------ the sheets
def free_area(w, h, pad_left=16):
    """(width, height) in mm that a drawing may fill on a w x h sheet."""
    return w-2*MARGIN-pad_left, h-2*MARGIN-TITLE_H-14


def min_scale(extent_m, paper=A2):
    """Smallest whole model scale (15 for 1:15) at which the plan and both
    elevations of a model with real extents (x, y, z) in metres each fit one
    sheet at 1:1. A view taller than wide goes on a portrait sheet."""
    ex, ey, ez = (e*1000 for e in extent_m)
    need = 0
    for width, height in ((ex, ey), (ex, ez), (ey, ez)):
        free_w, free_h = free_area(*(paper if height > width else paper[::-1]))
        need = max(need, width/free_w, height/free_h)
    return math.ceil(need)


def place(bounds, w, h, pad_left=16):
    """Offsets that centre a bounding box in the free area of a w x h sheet.
    Raises when it does not fit at 1:1."""
    x0, y0, x1, y1 = bounds
    free_w, free_h = free_area(w, h, pad_left)
    assert x1-x0 <= free_w and y1-y0 <= free_h, f'{x1-x0:.0f} x {y1-y0:.0f} mm does not fit the {w:.0f} x {h:.0f} sheet'
    return MARGIN+pad_left+(free_w-(x1-x0))/2-x0, MARGIN+TITLE_H+10+(free_h-(y1-y0))/2-y0


class SheetSet:
    """A numbered set of sheets with one title block. `scale` is the model
    scale (15 for 1:15), `experiment` and `subtitle` go in the title block,
    `viewer_url` becomes the QR code, `studio` is the mark under the check bar,
    `footer` is a key of `title_blocks.FOOTERS` ('a' to 'k')."""

    def __init__(self, scale, experiment, subtitle, viewer_url=None, studio='', paper=A2, footer=DEFAULT):
        assert footer in FOOTERS, f'footer {footer!r} is not one of {" ".join(FOOTERS)}'
        self.footer = footer
        self.scale, self.experiment, self.subtitle = scale, experiment, subtitle
        self.studio, self.paper = studio, paper
        self.qr = qr_matrix(viewer_url) if viewer_url else None
        self.sheets = []      # (title, Sheet)

    def blank(self, landscape=False):
        """An empty sheet of the set's paper."""
        return Sheet(*(self.paper[::-1] if landscape else self.paper))

    def add(self, title, sheet, note='', scale_text=None):
        """Finish a composed sheet with the title block and append it."""
        self.title_block(sheet, len(self.sheets)+1, title, note, scale_text)
        self.sheets.append((title, sheet))

    def view(self, title, drawing, note='', labelled=(), layers=None, scale_text=None):
        """One drawing centred on its own sheet, portrait or landscape to suit,
        with its marks and, for the `labelled` members, lengths and lollipops."""
        x0, y0, x1, y1 = drawing.bounds()
        sheet = self.blank(landscape=(y1-y0) <= (x1-x0))
        ox, oy = place(drawing.bounds(), sheet.w, sheet.h)
        drawing.paint(sheet, ox, oy)
        paint_extras(sheet, drawing, ox, oy)
        if labelled:
            annotate(sheet, drawing, labelled, layers, ox, oy)
        self.add(title, sheet, note, scale_text)

    def title_block(self, sheet, number, title, note, scale_text=None):
        """Border, note line and the title block of the set's `footer`."""
        FOOTERS[self.footer](sheet, Block(number, title, note, self.experiment, self.subtitle, self.scale,
                                          scale_text, self.studio, self.qr))

    def write(self, pdf_dir, svg_dir=None):
        """Write one PDF per sheet plus 00_all_sheets.pdf, and the SVGs when
        `svg_dir` is given. Both folders are emptied first."""
        for folder in filter(None, (pdf_dir, svg_dir)):
            os.makedirs(folder, exist_ok=True)
            for old in os.listdir(folder):
                os.remove(os.path.join(folder, old))
        for i, (title, sheet) in enumerate(self.sheets, 1):
            slug = f'{i:02d}_' + ''.join(c if c.isalnum() else '_' for c in title.lower()).strip('_').replace('__', '_')
            print_pdf(os.path.join(pdf_dir, slug+'.pdf'), [sheet])
            if svg_dir:
                with open(os.path.join(svg_dir, slug+'.svg'), 'w', encoding='utf-8') as f:
                    f.write(sheet.svg())
        print_pdf(os.path.join(pdf_dir, '00_all_sheets.pdf'), [s for _, s in self.sheets])
