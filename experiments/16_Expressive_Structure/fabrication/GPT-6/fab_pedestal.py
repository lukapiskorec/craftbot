# The exhibition pedestal sheet of the set: the full model on its pedestal
# as a dimensioned axonometric, the pedestal exploded into its six boards,
# and a side view with a visitor for scale. Four uncut 18 x 400 x 1200 boards are the sides, lapped pinwheel
# fashion; a fifth board gives the top and bottom panels set inside them.
# Called by fab_drawings.py. All numbers are real mm, as on every sheet.
from vector_pdf import THIN, MEDIUM, text_width
from drafting import Drawing, Axo, Y, Z, lollipop, place

BOARD_T, BOARD_W, BOARD_L = 18.0, 400.0, 1200.0
HALF = (BOARD_W+BOARD_T)/2      # half the outer footprint, 209
INNER = HALF-BOARD_T            # half the opening, 191
MAIN, EXPLODED, SIDE = 1/4, 1/10, 1/10      # drawing scales
TOTAL_AT = 190.0                # mm from the pedestal corner to the total height dimension
SPREAD, LIFT, DROP = 140.0, 260.0, 350.0     # mm the sides and the panels move apart in the exploded view, and the two near sides drop to show the far ones

# Outline of a standing visitor facing -x, traced from outputs/person_sample.png:
# (x from the middle of the figure, height) in mm, scaled to 1750 tall.
VISITOR = [(24, 1749), (33, 1750), (46, 1749), (68, 1744), (83, 1739), (91, 1734), (97, 1728), (101, 1720), (119, 1682), (123, 1667),
           (126, 1648), (123, 1623), (119, 1608), (110, 1588), (102, 1571), (94, 1562), (93, 1558), (94, 1551), (109, 1528), (119, 1516),
           (129, 1509), (207, 1471), (227, 1459), (235, 1451), (239, 1445), (247, 1431), (254, 1416), (260, 1397), (265, 1377), (281, 1263),
           (281, 1252), (283, 1235), (283, 1207), (284, 1191), (283, 1167), (284, 1133), (281, 1109), (276, 1080), (271, 1061), (256, 1021),
           (234, 969), (230, 954), (227, 940), (229, 916), (229, 892), (220, 877), (212, 845), (208, 834), (207, 827), (208, 810),
           (207, 794), (209, 764), (209, 725), (211, 709), (211, 648), (209, 631), (208, 605), (216, 572), (213, 554), (214, 548),
           (227, 526), (233, 498), (242, 402), (242, 306), (240, 290), (238, 253), (231, 183), (231, 172), (229, 159), (225, 137),
           (223, 129), (219, 122), (209, 109), (206, 98), (207, 83), (213, 54), (212, 39), (215, 22), (215, 12), (210, 9),
           (201, 7), (192, 7), (142, 2), (118, 2), (102, 0), (83, 2), (72, 2), (31, 7), (25, 9), (22, 12),
           (21, 18), (25, 30), (29, 39), (32, 42), (39, 47), (57, 53), (65, 56), (70, 60), (82, 74), (100, 97),
           (103, 103), (108, 118), (108, 126), (103, 141), (104, 146), (109, 154), (124, 166), (126, 169), (129, 174), (132, 214),
           (136, 231), (136, 240), (129, 271), (126, 292), (126, 314), (132, 351), (135, 378), (135, 391), (130, 415), (129, 437),
           (124, 447), (107, 464), (103, 471), (102, 478), (105, 493), (105, 498), (89, 524), (83, 537), (80, 557), (73, 583),
           (69, 609), (48, 707), (45, 709), (42, 705), (36, 687), (19, 646), (-7, 572), (-9, 563), (-8, 546), (-11, 532),
           (-13, 527), (-18, 522), (-21, 518), (-19, 514), (-12, 502), (-10, 484), (-8, 473), (-7, 467), (-10, 454), (-10, 445),
           (-5, 419), (-4, 395), (-4, 371), (-5, 354), (-5, 279), (-12, 227), (-15, 216), (-22, 196), (-23, 188), (-23, 183),
           (-18, 162), (-18, 140), (-13, 124), (-11, 94), (-6, 61), (-6, 54), (-9, 44), (-8, 36), (-6, 26), (-6, 20),
           (-7, 17), (-10, 14), (-15, 13), (-66, 13), (-83, 11), (-129, 11), (-146, 9), (-210, 9), (-249, 14), (-279, 20),
           (-283, 22), (-284, 28), (-279, 41), (-275, 48), (-269, 53), (-262, 56), (-249, 59), (-210, 58), (-197, 61), (-183, 68),
           (-170, 78), (-145, 106), (-142, 111), (-137, 129), (-131, 146), (-126, 172), (-126, 177), (-129, 199), (-128, 207), (-126, 218),
           (-116, 246), (-116, 257), (-121, 279), (-125, 321), (-127, 356), (-135, 428), (-131, 452), (-137, 474), (-144, 522), (-144, 541),
           (-142, 557), (-144, 576), (-141, 593), (-141, 609), (-140, 620), (-140, 635), (-142, 652), (-142, 661), (-137, 731), (-138, 736),
           (-141, 740), (-155, 751), (-161, 759), (-165, 768), (-168, 785), (-172, 797), (-173, 805), (-171, 814), (-161, 840), (-152, 871),
           (-152, 877), (-155, 890), (-154, 897), (-147, 929), (-144, 951), (-137, 973), (-136, 986), (-129, 1026), (-122, 1087), (-121, 1104),
           (-114, 1124), (-106, 1161), (-107, 1181), (-102, 1237), (-111, 1290), (-113, 1312), (-107, 1331), (-107, 1344), (-109, 1360), (-106, 1386),
           (-103, 1399), (-94, 1423), (-86, 1438), (-81, 1445), (-70, 1454), (-50, 1464), (-17, 1483), (-10, 1489), (-7, 1495), (-9, 1508),
           (-13, 1516), (-20, 1519), (-39, 1520), (-44, 1523), (-48, 1527), (-49, 1532), (-49, 1547), (-53, 1560), (-55, 1569), (-54, 1586),
           (-56, 1590), (-65, 1598), (-66, 1601), (-65, 1608), (-56, 1624), (-55, 1628), (-55, 1634), (-59, 1641), (-61, 1654), (-58, 1667),
           (-52, 1682), (-52, 1689), (-59, 1706), (-59, 1711), (-57, 1718), (-52, 1722), (-39, 1726), (-7, 1741), (7, 1746)]
VISITOR_AT = 645.0              # mm from the pedestal centre to the middle of the visitor
VISITOR_HALF = max(x for x, _ in VISITOR)
STUB = 5.5                      # mm on the sheet, an extension line: two 2 mm dashes and the 1.5 mm gap
CLEAR = 1.5                     # mm on the sheet between a dimension line and the box of its number
VISITOR_DROP = 0.9              # mm on the sheet the traced soles sink into the floor line
DIM_OFF = 12.0                  # mm on the sheet from the side view to its height dimensions


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
        sheet.line((x, y), (x+(mx-x)*reach, y+(my-y)*reach), THIN, dash=True)
        sheet.line((x-1.2, y-1.2), (x+1.2, y+1.2), MEDIUM)
    a, b = on(at(p, length)), on(at(q, length))
    sheet.line(a, b, THIN)
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
    column = max(ex1-ex0, (VISITOR_AT+VISITOR_HALF+HALF)*SIDE+2*DIM_OFF+20)      # the right column: exploded view, board list, side view
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
    side = Drawing([scaled(m, SIDE) for m in list(boards.values())+model], Y, Z)
    sox, soy = ox+reach+10+DIM_OFF+HALF*SIDE, oy+ay0-20
    side.paint(sheet, sox, soy)
    right = sox+(VISITOR_AT+VISITOR_HALF)*SIDE+DIM_OFF
    sheet.line((sox-HALF*SIDE-DIM_OFF-3, soy), (right+3, soy), MEDIUM)
    sheet.poly([(sox+(VISITOR_AT+x)*SIDE, soy+z*SIDE-VISITOR_DROP) for x, z in VISITOR], 1.0, MEDIUM)      # over the floor line
    for height, x in ((top, sox-HALF*SIDE-DIM_OFF), (max(z for _, z in VISITOR), right)):
        sheet.line((x, soy), (x, soy+height*SIDE), THIN)
        for y in (soy, soy+height*SIDE):
            sheet.line((x-1.2, y-1.2), (x+1.2, y+1.2), MEDIUM)
        sheet.text(x+(-2 if x < sox else 2), soy+height*SIDE/2, f'{height:.0f}', 3.2, 'end' if x < sox else 'start')
    sheet.text(ox+reach+column/2, oy+ay0-32, 'Side view 1:10 with a visitor 1.75 m tall', 2.6, 'middle')

    note = (f'Pedestal {2*HALF:.0f} x {2*HALF:.0f} x {BOARD_L:.0f}, with the model {2*HALF:.0f} x {2*HALF:.0f} x {top:.0f}. '
            'Each side laps the edge of the next and is screwed into it; top and bottom panels sit inside the sides, flush with their ends, '
            'and are screwed through the sides. Circles: board section and board code. The bottom panel carries the ballast.')
    sheets.add('Pedestal with model', sheet, note, scale_text='Axonometric 1:4, others 1:10.')
