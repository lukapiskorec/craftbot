"""The CraftBot agent team organigram as vector lines on a `vector_pdf.Sheet`.

A redrawing of `visuals/craftbot_agent_team_organigram.tex` (TikZ, the
source of the figure): the same boxes, edges, labels and legend at the same
millimetre positions, in Times like the original, so a sheet can carry it at
any width without a raster. Keep the two in step when the team changes.

    organigram(sheet, left, top, width)      # draws it, returns its height on the sheet

Provenance: experiment 16 fabrication set, the newsprint front page.
"""
from fonts import advance

FONT = 'Times New Roman'
# Node: centre (mm, the User box at the origin, y up), width, height, name, role lines, filled black.
NODES = {'user': ((0, 0), 40, 12, 'User', ('brief, review rounds',), False),
         'craftbot': ((0, -33), 68, 18, 'CraftBot', ('orchestrator: brief, scope, phases,', 'design rationale, final report'), True),
         'designer': ((-103, -77), 54, 18, 'Designer', ('concept, requirements,', 'comparison and structural review'), False),
         'builder': ((0, -77), 54, 18, 'Builder', ('versioned Blender scripts,', 'render and check loop'), False),
         'runner': ((103, -77), 54, 18, 'Runner', ('close-out: viewer export,', 'checks, archive'), False),
         'researcher': ((-103, -127), 54, 18, 'Researcher', ('reads the construction', 'manuals, crops figures'), False),
         'inspector': ((0, -127), 54, 18, 'Inspector', ('looks at the renders,', 'reports what is wrong'), False)}
# Spawn edges (filled arrowhead) and report edges (open arrowhead) as polylines, then their labels:
# (point, text, anchor) with anchor 'start' right of the point, 'middle' centred on it, 'above' or 'below' it.
SPAWN = [[(-7, -6), (-7, -24)],
         [(-10, -42), (-10, -68)],
         [(-10, -42), (-10, -54), (-115, -54), (-115, -68)],
         [(-10, -42), (-10, -54), (91, -54), (91, -68)],
         [(-117, -86), (-117, -118)],
         [(-14, -86), (-14, -118)],
         [(-76, -71), (-61, -71), (-61, -121), (-27, -121)]]
REPORT = [[(7, -24), (7, -6)],
          [(10, -68), (10, -42)],
          [(-91, -68), (-91, -33), (-34, -33)],
          [(115, -68), (115, -33), (34, -33)],
          [(-89, -118), (-89, -86)],
          [(14, -118), (14, -86)],
          [(-27, -133), (-51, -133), (-51, -83), (-76, -83)],
          [(27, -72), (76, -72)],
          [(76, -82), (27, -82)]]
LABELS = [((7, -15), 'rationale, final report', 'start'),
          ((10, -63.3), 'scripts, version notes', 'start'),
          ((-60, -33), 'concept, requirements', 'above'),
          ((84, -33), 'close-out reports', 'above'),
          ((-89, -102), 'sources, figure snippets', 'middle'),
          ((14, -102), 'inspection report', 'middle'),
          ((-42, -133), 'comparison round', 'above'),
          ((51.5, -72), 'version rendered', 'above'),
          ((51.5, -82), 'close-out report', 'below')]
LEGEND = (-130, -154)                 # left end of the legend line, under the Researcher
BOUNDS = (-130, -157, 130, 6)         # x0, y0, x1, y1 of the whole figure in its mm
WIDTH, HEIGHT = BOUNDS[2]-BOUNDS[0], BOUNDS[3]-BOUNDS[1]
BOX_LW, SPAWN_LW, REPORT_LW = 0.49, 0.35, 0.25      # TikZ 1.4 pt, 1 pt, 0.7 pt
NAME, ROLE, LABEL = 4.23, 3.18, 2.82                 # mm: \large, \small, \footnotesize at 10 pt


def arrowhead(sheet, tip, from_point, k, filled):
    """A 3 mm arrowhead at `tip` pointing away from `from_point`: TikZ Stealth (filled) or an open Triangle."""
    dx, dy = tip[0]-from_point[0], tip[1]-from_point[1]
    n = (dx*dx+dy*dy)**0.5
    ux, uy = dx/n, dy/n
    px, py = -uy, ux
    tx, ty = tip
    if filled:
        back, notch, half = 3.0*k, 2.2*k, 1.1*k
        pts = [(tx, ty), (tx-ux*back+px*half, ty-uy*back+py*half), (tx-ux*notch, ty-uy*notch), (tx-ux*back-px*half, ty-uy*back-py*half)]
        sheet.poly(pts, fill=0.0, lw=0.01)
    else:
        back, half = 3.0*k, 1.3*k
        pts = [(tx, ty), (tx-ux*back+px*half, ty-uy*back+py*half), (tx-ux*back-px*half, ty-uy*back-py*half)]
        sheet.poly(pts, fill=1.0, lw=REPORT_LW*k)


def organigram(sheet, left, top, width):
    """Draw the figure with its top-left corner at (left, top) on the sheet, `width` mm wide; returns its height."""
    k = width/WIDTH
    at = lambda p: (left+(p[0]-BOUNDS[0])*k, top-(BOUNDS[3]-p[1])*k)
    for edges, lw, filled in ((SPAWN, SPAWN_LW, True), (REPORT, REPORT_LW, False)):
        for path in edges:
            pts = [at(p) for p in path]
            # Stop the line short of the tip so it does not show through the arrowhead.
            (ax, ay), (bx, by) = pts[-2], pts[-1]
            n = ((bx-ax)**2+(by-ay)**2)**0.5
            pts[-1] = (bx-(bx-ax)/n*2.0*k, by-(by-ay)/n*2.0*k)
            for a, b in zip(pts, pts[1:]):
                sheet.line(a, b, lw*k)
            arrowhead(sheet, at(path[-1]), at(path[-2]), k, filled)
    for (cx, cy), w, h, name, roles, filled in NODES.values():
        x0, y0 = at((cx-w/2, cy-h/2))
        sheet.poly([(x0, y0), (x0+w*k, y0), (x0+w*k, y0+h*k), (x0, y0+h*k)], fill=0.0 if filled else 1.0, lw=BOX_LW*k)
        mx = at((cx, 0))[0]
        lines = ((3.4, -1.4, -5.6) if len(roles) == 2 else (1.2, -3.6))
        sheet.text(mx, at((0, cy+lines[0]))[1], name, NAME*k, 'middle', font=FONT, weight=700, white=filled)
        for role, dy in zip(roles, lines[1:]):
            sheet.text(mx, at((0, cy+dy))[1], role, ROLE*k, 'middle', font=FONT, italic=True, white=filled)
    for p, text, anchor in LABELS:
        x, y = at(p)
        w, h, pad = advance(text, LABEL*k, FONT, italic=True), 0.72*LABEL*k, 0.7*k
        if anchor == 'start':
            x, y = x+pad, y-h/2
        elif anchor == 'above':
            x, y = x-w/2, y+pad
        elif anchor == 'below':
            x, y = x-w/2, y-pad-h
        else:
            x, y = x-w/2, y-h/2
        sheet.poly([(x-pad, y-pad), (x+w+pad, y-pad), (x+w+pad, y+h+pad), (x-pad, y+h+pad)], fill=1.0, lw=0.0, stroke=1.0)
        sheet.text(x, y, text, LABEL*k, font=FONT, italic=True)
    lx, ly = at(LEGEND)
    sheet.line((lx, ly), (lx+6*k, ly), SPAWN_LW*k)
    arrowhead(sheet, (lx+8*k, ly), (lx, ly), k, True)
    sheet.text(lx+9*k, ly-0.35*ROLE*k, 'spawns', ROLE*k, font=FONT)
    sheet.line((lx+34*k, ly), (lx+40*k, ly), REPORT_LW*k)
    arrowhead(sheet, (lx+42*k, ly), (lx+34*k, ly), k, False)
    sheet.text(lx+43*k, ly-0.35*ROLE*k, 'reports back', ROLE*k, font=FONT)
    return HEIGHT*k
