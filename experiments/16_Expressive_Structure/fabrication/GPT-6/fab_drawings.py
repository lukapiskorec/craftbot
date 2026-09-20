# The A2 sheet set of experiment 16 GPT-6 v02 from members.json (written by
# fab_model.py): which views, which members on each, the frame glue-up
# template and the unrolled roof. The drawing itself is tools/drafting.py.
# Needs numpy for the axonometrics.
#
#   python fab_drawings.py
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'tools')))
from vector_pdf import THIN, MEDIUM, HEAVY
from cutlist import measure
from drafting import (SheetSet, Drawing, Axo, Flat, X, Y, Z, NEG, GREY, in_groups, centre, area, faces_of,
                      depth_layers, annotate, lollipop, add_marks, add_tag, paint_extras, place, unroll)
from fab_cutlist import load
from fab_pedestal import pedestal_sheet

VIEWER_URL = 'https://lukapiskorec.github.io/craftbot/?model=models%2F16_Expressive_Structure%2Fgpt6_v02.json'
STICK_T = 3.0      # mm, thickness of one frame layer (the 3x5 slat on edge)

DATA = load()
SCALE = DATA['scale']
FRAME_AXES = list(zip(DATA['frame_y'], [f'F{j}' for j in DATA['frames']]))
LEVELS = [(metres*1000/SCALE, f'+{metres*1000/SCALE:.0f}') for metres in (0, 1.5, 3, 4.5, 5.25, 6)]


def frame_template(sheets, j, y, members):
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
    add_marks(main, 'level', LEVELS)
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

    sheet = sheets.blank()
    gap = 24
    mx0, my0, mx1, my1 = main.bounds()
    sx0, sy0, sx1, sy1 = side.bounds()
    ox, oy = place((mx0-10, my0, mx1+gap+(sx1-sx0)+6, my1), sheet.w, sheet.h)
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
    sheets.add(f'Frame F{j} template', sheet, note)


def unrolled_roof(sheets, members):
    """Each bay of roof boards is a strip of six planar panels that fold
    along lines parallel to the boards. Every strip is unrolled flat."""
    boards = {}
    for m in in_groups(members, 'RoofBoard'):
        _, j, k, i = m['name'].split('_')
        boards.setdefault(int(j), {}).setdefault(int(k), []).append((int(i), m))
    flat, labels, strips, top = Flat(), [], [], 0.0
    for j in sorted(boards):
        panels = [[m for _, m in sorted(boards[j][k])] for k in sorted(boards[j])]
        # The underside ring of a board: (a,y0) (b,y0) (b,y1) (a,y1).
        strip = unroll([[m['verts'][:4] for m in row] for row in panels])
        low = min(p[1] for facet in strip for pts in facet for p in pts)
        high = max(p[1] for facet in strip for pts in facet for p in pts)
        for k, (row, facet) in enumerate(zip(panels, strip)):
            for i, (m, pts) in enumerate(zip(row, facet)):
                pts = [(x, y-low+top) for x, y in pts]
                flat.faces.append((0, pts, 1.0, THIN))
                labels.append((pts, f'{measure(m)[0]:.1f}', k, i))
        left = min(p[0] for facet in strip for pts in facet for p in pts)
        strips.append((left, top+(high-low)/2, f'Bay F{DATA["frames"][j]}-F{DATA["frames"][j+1]}'))
        top += high-low+18
    sheet = sheets.blank(landscape=True)
    ox, oy = place(flat.bounds(), sheet.w, sheet.h, pad_left=30)
    flat.paint(sheet, ox, oy)
    for pts, text, k, i in labels:
        cx, cy = sum(p[0] for p in pts)/4+ox, sum(p[1] for p in pts)/4+oy
        sheet.text(cx, cy-0.6, text, 1.7, 'middle')
        if i == 0:       # fold line at the start of every panel, and one lollipop per panel
            if k:
                sheet.line((pts[0][0]+ox, pts[0][1]+oy), (pts[3][0]+ox, pts[3][1]+oy), HEAVY)
            lx, ly = cx, pts[0][1]+oy-8
            sheet.line((cx, pts[0][1]+oy+1.5), (lx, ly), THIN)
            lollipop(sheet, lx, ly, '2x10', f'P{k+1}')
    for x, y, label in strips:
        sheet.text(x+ox-6, y+oy-1, label, 2.8, 'end')
    note = ('Roof boards of each bay laid flat, door end at the bottom, -x on the left. Heavy lines: folds between the six planar panels P1 to P6 of a strip. '
            'Numbers: cut length in mm. All boards 2x10, one layer.')
    sheets.add('Roof boards, unrolled', sheet, note)


def build_sheets():
    members = DATA['members']
    mm = lambda metres: metres*1000/SCALE
    sheets = SheetSet(SCALE, 'Experiment 16 - Expressive Structure', 'GPT-6 v02, stick model',
                      viewer_url=VIEWER_URL, studio='{protocell:labs}')

    def add(title, subset, right, up, cut=None, note='', axes=None, levels=False, labels=False):
        drawing = Drawing(subset, right, up, cut)
        if levels:
            add_marks(drawing, 'level', LEVELS)
        if axes:
            kind, sign = axes
            add_marks(drawing, kind, [(sign*y, label) for y, label in FRAME_AXES])
        layers = depth_layers(subset, drawing.toward) if labels else None
        sheets.view(title, drawing, note, subset if labels else (), layers)

    lollipop_note = ' Numbers: cut length in mm. Circles: stick profile and layer, L1 lies on the paper.'
    ground = in_groups(members, 'Ground', 'Bracing/GroundPlan')
    add('Plan, ground mat', ground, X, Y, axes=('axis_y', 1), labels=True,
        note='Two crossed sleeper layers with sole runners and plan braces. Door end at the bottom.'+lollipop_note)
    add('Plan, section at +80 mm', members, X, Y, cut=mm(1.2), axes=('axis_y', 1),
        note='Horizontal section 80 mm above the floor, looking down. Cut members shaded.')
    roof_frame = in_groups(members, 'RoofStructure', 'Bracing/RoofPlan', 'Ceiling', 'Structure')
    add('Plan, roof framing', roof_frame, X, Y, axes=('axis_y', 1), note='Roof boards removed. Crossed plan braces lie between the lower chords.')
    unrolled_roof(sheets, members)
    add('Elevation, door end', members, X, Z, levels=True)
    add('Elevation, far end', members, NEG(X), Z, levels=True)
    add('Elevation, side plus x', members, Y, Z, levels=True, axes=('axis_x', 1))
    add('Elevation, side minus x', members, NEG(Y), Z, levels=True, axes=('axis_x', -1))
    bay = (DATA['frame_y'][0]+DATA['frame_y'][1])/2
    add('Cross section, first bay', members, NEG(X), Z, cut=bay, levels=True,
        note='Cut midway between F0 and F1, looking towards the door wall from inside, so -x is on the right. Cut members shaded.')
    add('Long section, centre line', members, NEG(Y), Z, cut=mm(0.02), levels=True, axes=('axis_x', -1),
        note='Cut 1.3 mm off the centre line so it passes through boards, not between them. Looking towards -x. Cut members shaded.')
    for j, y in zip(DATA['frames'], DATA['frame_y']):
        frame_template(sheets, j, y, members)
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
        note = 'Every member of the viewer layer' + ('s ' if len(layers) > 1 else ' ') + ' and '.join(f'"{name}"' for name in layers) + '. Seen from the door side.'
        subset = [m for m in members if m['layer'] in layers]
        axo = Axo(subset, SCALE/20)
        # Frame names at the foot of the -x side, on each frame line.
        x_end = min(v[0] for m in subset for v in m['verts'])
        z_low = min(v[2] for m in subset for v in m['verts'])
        for y, label in FRAME_AXES:
            add_tag(axo, axo.point([x_end, y, z_low]), axo.point([x_end-24, y, z_low]), label)
        sheets.view(title, axo, note, scale_text='Axonometric, scale 1:20.')
    pedestal_sheet(sheets, members)
    return sheets


if __name__ == '__main__':
    sheets = build_sheets()
    sheets.write(os.path.join(HERE, 'pdf'), os.path.join(HERE, 'svg'))
    print(f'Wrote {len(sheets.sheets)} A2 sheets to {os.path.join(HERE, "pdf")}')
