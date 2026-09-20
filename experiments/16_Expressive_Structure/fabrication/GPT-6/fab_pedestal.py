# The exhibition pedestal sheets of the set, each with the full model on a
# pedestal as a dimensioned axonometric and a side view with a visitor for
# scale. `pedestal_sheet` is the tall pedestal, also exploded into its six
# boards: four uncut 18 x 400 x 1200 boards are the sides, lapped pinwheel
# fashion; a fifth board gives the top and bottom panels set inside them.
# `platform_sheet` is the low 900 x 900 x 450 pedestal, drawn as one volume,
# with the model at one end and the drawing set lying open in front of it,
# as a spiral-bound booklet or as an accordion. Called by fab_drawings.py.
# All numbers are real mm, as on every sheet.
import math

from vector_pdf import FINE, THIN, MEDIUM, text_width
from drafting import Drawing, Axo, Y, Z, lollipop, place
from drawing_assets import person, size

BOARD_T, BOARD_W, BOARD_L = 18.0, 400.0, 1200.0
HALF = (BOARD_W+BOARD_T)/2      # half the outer footprint, 209
INNER = HALF-BOARD_T            # half the opening, 191
MAIN, EXPLODED, SIDE = 1/4, 1/10, 1/10      # drawing scales
TOTAL_AT = 190.0                # mm from the pedestal corner to the total height dimension
SPREAD, LIFT, DROP = 140.0, 260.0, 350.0     # mm the sides and the panels move apart in the exploded view, and the two near sides drop to show the far ones

VISITOR_GAP = 150.0             # mm from the pedestal face to the visitor's toe
VISITOR_HALF, VISITOR_H = size('person')[0]/2, size('person')[1]      # the visitor of tools/drawing_assets.py
STUB = 5.5                      # mm on the sheet, an extension line: two 2 mm dashes and the 1.5 mm gap
CLEAR = 1.5                     # mm on the sheet between a dimension line and the box of its number
DIM_OFF = 12.0                  # mm on the sheet from the side view to its height dimensions
PLATFORM, PLATFORM_H = 900.0, 450.0      # the low pedestal: square side and height
PLATFORM_AXO, PRINTS = 1/5, 1/15          # drawing scales of the axonometric and of the two print diagrams
SETBACK = 40.0                  # mm from the end of the platform to the model
PAGE_W, PAGE_H, PAGES = 420.0, 594.0, 24      # the drawing set: A2 portrait sheets
SPINE = 10.0                    # mm between the two pages of the open booklet, the spiral
BOOK_GAP = 20.0                 # mm from the model to the booklet
FOLD = 72.0                     # degrees, slope of the accordion panels drawn half unfolded
OPEN_AT = (10, 11)              # sheet numbers of this set shown on the open booklet, left and right page


def board(name, x0, x1, y0, y1, z0, z1):
    ring = [(x1, y1), (x1, y0), (x0, y0), (x0, y1)]
    return {'name': name, 'group': 'Pedestal', 'layer': 'pedestal', 'stock': None,
            'verts': [[x, y, z] for z in (z0, z1) for x, y in ring],
            'faces': [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [4, 0, 3, 7]]}


def moved(member, dx=0.0, dy=0.0, dz=0.0):
    return dict(member, verts=[[x+dx, y+dy, z+dz] for x, y, z in member['verts']])


def scaled(member, k):
    return dict(member, verts=[[x*k, y*k, z*k] for x, y, z in member['verts']])


def pedestal():
    """The six boards as {code: member}. Each side laps the edge of the next."""
    return {'S1': board('Side_1', -HALF, INNER, -HALF, -INNER, 0, BOARD_L),
            'S2': board('Side_2', INNER, HALF, -HALF, INNER, 0, BOARD_L),
            'S3': board('Side_3', -INNER, HALF, INNER, HALF, 0, BOARD_L),
            'S4': board('Side_4', -HALF, -INNER, -INNER, HALF, 0, BOARD_L),
            'T': board('Top', -INNER, INNER, -INNER, INNER, BOARD_L-BOARD_T, BOARD_L),
            'B': board('Bottom', -INNER, INNER, -INNER, INNER, 0, BOARD_T)}


def dimension(sheet, axo, ox, oy, p, q, away, text, anchor):
    """Dimension line for the model points p to q, pushed out along the 3D
    vector `away`, with short dashed extension lines (two dashes towards the model), end ticks and the number
    beside its middle; `anchor` 'start' puts the number right of the line, 'end' left."""
    length = sum(a*a for a in away)**0.5
    at = lambda point, reach: axo.point([c+a*reach/length for c, a in zip(point, away)])
    on = lambda xy: (xy[0]+ox, xy[1]+oy)
    for point in (p, q):
        x, y = on(at(point, length))
        mx, my = on(at(point, 0))
        reach = STUB/((mx-x)**2+(my-y)**2)**0.5
        sheet.line((x, y), (x+(mx-x)*reach, y+(my-y)*reach), FINE, dash=True)
        sheet.line((x-1.2, y-1.2), (x+1.2, y+1.2), THIN)
    a, b = on(at(p, length)), on(at(q, length))
    sheet.line(a, b, FINE)
    # The number sits beside the middle of the line, on the right for 'start' and on the left for 'end', its box CLEAR away
    # from the line measured square to it, so a number beside a sloping line stands as clear as one beside a vertical line.
    nx, ny = b[1]-a[1], a[0]-b[0]
    if (nx < 0) == (anchor == 'start'):
        nx, ny = -nx, -ny
    norm = (nx*nx+ny*ny)**0.5
    nx, ny = nx/norm, ny/norm
    size = 3.2
    width, height = text_width(text, size), 0.72*size
    off = CLEAR+abs(nx)*width/2+abs(ny)*height/2
    sheet.text((a[0]+b[0])/2+nx*off, (a[1]+b[1])/2+ny*off-height/2, text, size, 'middle')


def side_width(half):
    """Width on the sheet of `side_view` for a pedestal `half` deep each side of its centre."""
    return (2*half+VISITOR_GAP+2*VISITOR_HALF)*SIDE+2*DIM_OFF+20


def side_view(sheet, solids, half, top, left, soy):
    """Side view 1:10 seen from +x with the visitor facing the pedestal, its floor line at `soy` and its left end
    (the number of the height dimension) at `left`. `top` is the height of pedestal and model."""
    sox = left+10+DIM_OFF+half*SIDE      # the pedestal centre
    Drawing([scaled(m, SIDE) for m in solids], Y, Z).paint(sheet, sox, soy)
    visitor_at = half+VISITOR_GAP+VISITOR_HALF
    right = sox+(visitor_at+VISITOR_HALF)*SIDE+DIM_OFF
    sheet.line((sox-half*SIDE-DIM_OFF-3, soy), (right+3, soy), MEDIUM)
    person(sheet, sox+visitor_at*SIDE, soy, SIDE)      # over the floor line
    for height, x in ((top, sox-half*SIDE-DIM_OFF), (VISITOR_H, right)):
        sheet.line((x, soy), (x, soy+height*SIDE), FINE)
        for y in (soy, soy+height*SIDE):
            sheet.line((x-1.2, y-1.2), (x+1.2, y+1.2), THIN)
        sheet.text(x+(-2 if x < sox else 2), soy+height*SIDE/2, f'{height:.0f}', 3.2, 'end' if x < sox else 'start')


def pedestal_sheet(sheets, members):
    boards = pedestal()
    low = min(v[2] for m in members for v in m['verts'])
    model = [moved(m, dz=BOARD_L-low) for m in members]
    span = lambda axis: (min(v[axis] for m in model for v in m['verts']), max(v[axis] for m in model for v in m['verts']))
    (mx0, mx1), (my0, my1), (_, top) = span(0), span(1), span(2)

    main = Axo(list(boards.values())+model, MAIN)
    push = {'S1': (0, -SPREAD, -DROP), 'S2': (SPREAD, 0, 0), 'S3': (0, SPREAD, 0), 'S4': (-SPREAD, 0, -DROP),
            'T': (0, 0, LIFT), 'B': (0, 0, -LIFT-DROP)}
    apart = {code: moved(m, *push[code]) for code, m in boards.items()}
    exploded = Axo(list(apart.values()), EXPLODED)

    sheet = sheets.blank()
    ax0, ay0, ax1, ay1 = main.bounds()
    ex0, ey0, ex1, ey1 = exploded.bounds()
    reach = main.point([HALF+TOTAL_AT, -HALF, 0])[0]+16      # right end of the height dimensions and their numbers
    column = max(ex1-ex0, side_width(HALF))      # the right column: exploded view, board list, side view
    ox, oy = place((ax0-24, ay0-36, reach+column, ay1), sheet.w, sheet.h, pad_left=0)
    main.paint(sheet, ox, oy)

    dim = lambda *args, **kw: dimension(sheet, main, ox, oy, *args, **kw)
    # Pedestal footprint at the floor, model footprint at the pedestal top.
    dim([-HALF, -HALF, 0], [HALF, -HALF, 0], (0, -100, 0), f'{2*HALF:.0f}', 'start')
    dim([-HALF, -HALF, 0], [-HALF, HALF, 0], (-100, 0, 0), f'{2*HALF:.0f}', 'end')
    dim([mx0, my0, BOARD_L], [mx1, my0, BOARD_L], (0, -(my0+HALF+40), 0), f'{mx1-mx0:.0f}', 'start')
    dim([mx0, my0, BOARD_L], [mx0, my1, BOARD_L], (-(mx0+HALF+40), 0, 0), f'{my1-my0:.0f}', 'end')
    # Heights on the right: pedestal and model, then the total.
    corner = [HALF, -HALF]
    dim(corner+[0], corner+[BOARD_L], (90, 0, 0), f'{BOARD_L:.0f}', 'start')
    dim(corner+[BOARD_L], corner+[top], (90, 0, 0), f'{top-BOARD_L:.0f}', 'start')
    dim(corner+[0], corner+[top], (TOTAL_AT, 0, 0), f'{top:.0f}', 'start')
    sheet.text(ox+(ax0+ax1)/2, oy+ay0-20, 'Axonometric 1:4, seen from the door side', 2.6, 'middle')

    # Exploded pedestal at the top of the right column.
    eox = ox+reach+(column-(ex1-ex0))/2-ex0
    eoy = oy+ay1-ey1
    exploded.paint(sheet, eox, eoy)
    for code, m in apart.items():
        # Label the face turned to the viewer: the -y face of S1 and S3, the -x face of S2 and S4, the top of the panels.
        xs, ys, zs = ([v[a] for v in m['verts']] for a in range(3))
        mid = lambda values: (min(values)+max(values))/2
        if code in 'TB':
            spot = [mid(xs), mid(ys), max(zs)]
        elif code in ('S1', 'S3'):
            spot = [mid(xs), min(ys), mid(zs)+(300 if code == 'S3' else 0)]
        else:
            spot = [min(xs), mid(ys), mid(zs)+(300 if code == 'S2' else 0)]
        x, y = exploded.point(spot)
        width = BOARD_W if code.startswith('S') else 2*INNER
        lollipop(sheet, x+eox, y+eoy, f'{BOARD_T:.0f}x{width:.0f}', code)
    sheet.text(eox+(ex0+ex1)/2, eoy+ey0-8, 'Pedestal exploded, 1:10', 2.6, 'middle')

    # Board list under the exploded view.
    tx, ty = ox+reach+(column-100)/2, eoy+ey0-22
    rows = [('S1 to S4', f'side, {BOARD_T:.0f} x {BOARD_W:.0f} x {BOARD_L:.0f}, whole board', '4'),
            ('T', f'top, {BOARD_T:.0f} x {2*INNER:.0f} x {2*INNER:.0f}, cut from board 5', '1'),
            ('B', f'bottom, {BOARD_T:.0f} x {2*INNER:.0f} x {2*INNER:.0f}, cut from board 5', '1')]
    sheet.text(tx, ty, 'Boards', 3.2, weight=600)
    for i, (code, what, count) in enumerate(rows, 1):
        sheet.text(tx, ty-6*i, code, 2.6)
        sheet.text(tx+24, ty-6*i, what, 2.6)
        sheet.text(tx+100, ty-6*i, count, 2.6, 'end')

    # Side view with a visitor, at the foot of the right column.
    side_view(sheet, list(boards.values())+model, HALF, top, ox+reach, oy+ay0-20)
    sheet.text(ox+reach+column/2, oy+ay0-32, 'Side view 1:10 with a visitor 1.75 m tall', 2.6, 'middle')

    note = (f'Pedestal {2*HALF:.0f} x {2*HALF:.0f} x {BOARD_L:.0f}, with the model {2*HALF:.0f} x {2*HALF:.0f} x {top:.0f}. '
            'Each side laps the edge of the next and is screwed into it; top and bottom panels sit inside the sides, flush with their ends, '
            'and are screwed through the sides. Circles: board section and board code. The bottom panel carries the ballast.')
    sheets.add('Pedestal with model', sheet, note, scale_text='Axonometric 1:4, others 1:10.')


def prism(name, profile, y0, y1):
    """A convex (x, z) profile extruded from y0 to y1, faces wound outwards."""
    if sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(profile, profile[1:]+profile[:1])) > 0:
        profile = profile[::-1]      # clockwise seen from -y, so the side faces below point outwards
    n = len(profile)
    verts = [[x, y, z] for y in (y0, y1) for x, z in profile]
    faces = [list(range(n)), list(range(2*n-1, n-1, -1))]+[[i, n+i, n+(i+1) % n, (i+1) % n] for i in range(n)]
    mid = [sum(v[a] for v in verts)/len(verts) for a in range(3)]
    for k, face in enumerate(faces):
        a, b, c = (verts[j] for j in face[:3])
        u, w = [b[t]-a[t] for t in range(3)], [c[t]-b[t] for t in range(3)]
        normal = [u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0]]
        if sum(normal[t]*(a[t]-mid[t]) for t in range(3)) < 0:
            faces[k] = face[::-1]
    return {'name': name, 'group': 'Prints', 'layer': 'pedestal', 'stock': None, 'verts': verts, 'faces': faces}


def booklet(y0, z0, thick=2.0):
    """The drawing set as an open spiral-bound booklet lying on z0: two portrait pages from y0 back, and the wire loops."""
    inner, outer = SPINE/2, SPINE/2+PAGE_W
    # The reader stands at +y and looks towards -y, so the left page is the one at +x.
    parts = [board('Page_left', inner, outer, y0, y0+PAGE_H, z0, z0+thick),
             board('Page_right', -outer, -inner, y0, y0+PAGE_H, z0, z0+thick)]
    loops = int(PAGE_H//27)
    for k in range(loops):
        y = y0+(PAGE_H-27*(loops-1))/2+27*k
        parts.append(board(f'Loop_{k}', -inner-5, inner+5, y-2, y+2, z0+thick, z0+thick+3))
    return parts


def accordion(turned=4.0, waiting=8.0, panels=4, thick=1.5, trim=4.0):
    """The drawing set as an accordion lying on z = 0: the stack already read on the left, the stack still folded on
    the right, and `panels` sheets between them half unfolded at FOLD degrees."""
    run, rise = PAGE_W*math.cos(math.radians(FOLD)), PAGE_W*math.sin(math.radians(FOLD))
    parts = [board('Stack_read', -PAGE_W, 0, 0, PAGE_H, 0, turned)]
    for k in range(panels):
        (xa, za), (xb, zb) = ((k*run, turned+(rise if k % 2 else 0)), ((k+1)*run, turned+(0 if k % 2 else rise)))
        ux, uz = (xb-xa)/PAGE_W, (zb-za)/PAGE_W
        xa, za, xb, zb = xa+ux*trim, za+uz*trim, xb-ux*trim, zb-uz*trim      # clear of the next panel at the fold
        nx, nz = -uz*thick/2, ux*thick/2
        parts.append(prism(f'Panel_{k}', [(xa+nx, za+nz), (xb+nx, zb+nz), (xb-nx, zb-nz), (xa-nx, za-nz)], 0, PAGE_H))
    parts.append(board('Stack_folded', panels*run, panels*run+PAGE_W, 0, PAGE_H, 0, waiting))
    return parts


def lay_sheet(sheet, source, place_at, scale):
    """Draw the sheet `source` of the set on `sheet` through `place_at`, which maps a point of the source in mm from
    its bottom-left corner to the target: polygons and lines as they are, line widths times `scale`, every text as
    a fine bar of its length, since type this small does not print."""
    for op in source.ops:
        if op[0] == 'poly':
            _, pts, fill, lw, dash, stroke = op
            sheet.poly([place_at(x, y) for x, y in pts], fill, max(lw*scale, 0.03), False, stroke)
        elif not op[6][5]:      # text, but not white text on a black ground
            _, x, y, text, size, anchor = op[:6]
            width = text_width(text, size)
            x -= {'start': 0, 'middle': width/2, 'end': width}[anchor]
            sheet.line(place_at(x, y+0.3*size), place_at(x+width, y+0.3*size), max(0.35*size*scale, 0.03))


def platform_sheet(sheets, members):
    half = PLATFORM/2
    platform = board('Platform', -half, half, -half, half, 0, PLATFORM_H)
    # The model is turned half round and stands at the -y end, its door towards the prints and the visitor at +y.
    turned = [dict(m, verts=[[-x, -y, z] for x, y, z in m['verts']]) for m in members]
    low = min(v[2] for m in turned for v in m['verts'])
    back = min(v[1] for m in turned for v in m['verts'])
    model = [moved(m, dy=-half+SETBACK-back, dz=PLATFORM_H-low) for m in turned]
    span = lambda axis: (min(v[axis] for m in model for v in m['verts']), max(v[axis] for m in model for v in m['verts']))
    (mx0, mx1), (my0, my1), (_, top) = span(0), span(1), span(2)
    book = booklet(my1+BOOK_GAP, PLATFORM_H)
    assert my1+BOOK_GAP+PAGE_H <= half and SPINE/2+PAGE_W <= half, 'the open booklet does not fit the platform'

    toward = (-1, 1, 0.8)      # seen from the door side, which is now +y
    main = Axo([platform]+book+model, PLATFORM_AXO, toward)
    prints = [Axo(booklet(0, 0), PRINTS), Axo(accordion(), PRINTS)]
    sheet = sheets.blank(landscape=True)
    ax0, ay0, ax1, ay1 = main.bounds()
    reach = main.point([-half, -half-TOTAL_AT, 0])[0]+16      # right end of the height dimensions and their numbers
    column = side_width(half)
    side_h = max(top, VISITOR_H)*SIDE
    heights = [a.bounds()[3]-a.bounds()[1] for a in prints]
    stack = 10+side_h+12+sum(h+26 for h in heights)      # side view, then each diagram with its dimensions and two lines of label
    ox, oy = place((ax0-24, ay0-28, reach+24+column, max(ay1, ay0-28+stack)), sheet.w, sheet.h, pad_left=0)
    main.paint(sheet, ox, oy)
    # Two sheets of this set lie on the open booklet, read from +y: bottom edge at the front, left page at +x.
    front, page_top = my1+BOOK_GAP+PAGE_H, PLATFORM_H+2.0
    for number, x_left in zip(OPEN_AT, (SPINE/2+PAGE_W, -SPINE/2)):
        if number <= len(sheets.sheets):
            source = sheets.sheets[number-1][1]
            assert (source.w, source.h) == (PAGE_W, PAGE_H), f'sheet {number} is not A2 portrait'
            on_page = lambda u, v, x_left=x_left: tuple(c+o for c, o in zip(main.point([x_left-u, front-v, page_top]), (ox, oy)))
            lay_sheet(sheet, source, on_page, PLATFORM_AXO)

    dim = lambda *args, **kw: dimension(sheet, main, ox, oy, *args, **kw)
    # Platform footprint at the floor; on its top the model footprint, its setback and the gap to the booklet.
    dim([-half, half, 0], [half, half, 0], (0, 100, 0), f'{PLATFORM:.0f}', 'end')
    dim([-half, half, 0], [-half, -half, 0], (-100, 0, 0), f'{PLATFORM:.0f}', 'start')
    side = [mx0, 0, PLATFORM_H]
    for y0, y1 in ((-half, my0), (my0, my1), (my1, my1+BOOK_GAP)):
        dim([mx0, y0, PLATFORM_H], [mx0, y1, PLATFORM_H], (-60, 0, 0), f'{y1-y0:.0f}', 'start')
    # Heights on the right: platform and model, then the total.
    corner = [-half, -half]
    dim(corner+[0], corner+[PLATFORM_H], (0, -90, 0), f'{PLATFORM_H:.0f}', 'start')
    dim(corner+[PLATFORM_H], corner+[top], (0, -90, 0), f'{top-PLATFORM_H:.0f}', 'start')
    dim(corner+[0], corner+[top], (0, -TOTAL_AT, 0), f'{top:.0f}', 'start')
    # Booklet label in the empty corner above the left edge of the platform.
    lx, ly = ox+ax0-10, oy+main.point([half, half, PLATFORM_H])[1]+42
    sheet.text(lx, ly, 'Booklet', 3.2, weight=600)
    sheet.text(lx, ly-5, f'{PAGES} sheets A2, open {2*PAGE_W+SPINE:.0f} x {PAGE_H:.0f}', 2.6)
    px, py = main.point([SPINE/2+PAGE_W, my1+BOOK_GAP+PAGE_H*0.3, PLATFORM_H+2])      # the outer edge of the left page
    sheet.line((lx+22, ly-7), (px+ox, py+oy), FINE)
    sheet.text(ox+(ax0+ax1)/2, oy+ay0-24, 'Axonometric 1:5, seen from the door side, with the booklet', 2.6, 'middle')

    left = ox+reach+24
    side_view(sheet, [platform]+book+model, half, top, left, oy+ay0-10)
    sheet.text(left+column/2, oy+ay0-24, 'Side view 1:10 with a visitor 1.75 m tall', 2.6, 'middle')

    # The two ways to lay out the prints, above the side view: booklet, then accordion.
    labels = [('Booklet', f'{PAGES} sheets A2 portrait, spiral bound, open {2*PAGE_W+SPINE:.0f} x {PAGE_H:.0f}'),
              ('Accordion', f'{PAGES} sheets A2 joined along the long edge, folded {PAGE_W:.0f} x {PAGE_H:.0f}, {PAGES*PAGE_W/1000:.2f} m unfolded')]
    run = 4*PAGE_W*math.cos(math.radians(FOLD))
    marks = [[([SPINE/2, 0, 0], [SPINE/2+PAGE_W, 0, 0], (0, -90, 0), PAGE_W, 'start'),
              ([-SPINE/2-PAGE_W, 0, 0], [-SPINE/2-PAGE_W, PAGE_H, 0], (-90, 0, 0), PAGE_H, 'end')],
             [([run, 0, 0], [run+PAGE_W, 0, 0], (0, -90, 0), PAGE_W, 'start'),
              ([-PAGE_W, 0, 0], [-PAGE_W, PAGE_H, 0], (-90, 0, 0), PAGE_H, 'end')]]
    y = oy+ay0-10+side_h+12      # foot of the lower diagram
    for axo, (name, what), dims in reversed(list(zip(prints, labels, marks))):
        bx0, by0, bx1, by1 = axo.bounds()
        dox, doy = left+(column-(bx1-bx0))/2-bx0, y+8-by0
        axo.paint(sheet, dox, doy)
        for p0, p1, away, length, anchor in dims:
            dimension(sheet, axo, dox, doy, p0, p1, away, f'{length:.0f}', anchor)
        sheet.text(left+10, doy+by1+10, name, 3.2, weight=600)
        sheet.text(left+10, doy+by1+5, what+f', drawn 1:{1/PRINTS:.0f}', 2.6)
        y = doy+by1+18

    note = (f'Low pedestal {PLATFORM:.0f} x {PLATFORM:.0f} x {PLATFORM_H:.0f}, {top:.0f} high with the model ({mx1-mx0:.0f} x {my1-my0:.0f} in plan), which stands '
            f'{SETBACK:.0f} from the far edge, centred across, its door towards the prints and the visitor. The {PAGES} A2 sheets of this set lie in front of it, open at sheets {OPEN_AT[0]} and {OPEN_AT[1]}, '
            'as a booklet or as an accordion. The pedestal is drawn as one volume; its boards are not designed yet.')
    sheets.add('Low pedestal with model', sheet, note, scale_text='Axonometric 1:5, side view 1:10.')
