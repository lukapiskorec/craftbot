"""Entourage for drawing sheets: outlines of people (later trees, symbols) placed on a Sheet at a scale.

An asset is a closed outline in real mm, `(x, height)` with x measured from
the middle of the figure and the height from the ground, stored in
`OUTLINES`. `outline_asset` draws one on a `vector_pdf.Sheet`; `person` is
the first. The outlines are data in this file: the image a figure was traced
from is not kept.

    person(sheet, x, y, 1/10)                     # a 1.75 m visitor at 1:10, feet at (x, y), facing left
    python tools/drawing_assets.py trace figure.png 1750       # print a new outline traced from a silhouette image
    python tools/drawing_assets.py svg person person.svg       # write an asset as an SVG, to look at it

Placing needs only the standard library; `trace` needs Pillow, numpy and scipy.

Provenance: experiment 16 fabrication set, sheets 23 and 24 (the visitor beside the pedestal).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vector_pdf import MEDIUM  # noqa: E402

# name: outline. 'person' is a standing man, 1750 mm tall, facing -x, one foot forward.
OUTLINES = {
    'person': [
        (24, 1749), (33, 1750), (46, 1749), (68, 1744), (83, 1739), (91, 1734), (97, 1728), (101, 1720), (119, 1682), (123, 1667),
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
        (-52, 1682), (-52, 1689), (-59, 1706), (-59, 1711), (-57, 1718), (-52, 1722), (-39, 1726), (-7, 1741), (7, 1746),
    ],
}


def size(name):
    """(width, height) in real mm of an asset."""
    xs, zs = zip(*OUTLINES[name])
    return max(xs)-min(xs), max(zs)-min(zs)


def outline_asset(sheet, name, x, y, scale, mirror=False, fill=1.0, lw=MEDIUM, sink=0.0):
    """Draw the asset `name` on `sheet` at `scale` (1/10 for 1:10) with the middle of its base at (x, y); `mirror` turns it to face +x, `fill` is a grey 0..1 or None, `sink` lowers it by that many mm on the sheet (traced soles are not level)."""
    side = -1 if mirror else 1
    sheet.poly([(x+side*px*scale, y+pz*scale-sink) for px, pz in OUTLINES[name]], fill, lw)


def person(sheet, x, y, scale, mirror=False, fill=1.0, lw=MEDIUM, sink=0.9):
    """A standing visitor 1750 mm tall, feet at (x, y), facing left (-x) unless `mirror`. Paint it after the floor line: the white fill covers the line under the shoes, which `sink` presses 0.9 mm into it."""
    outline_asset(sheet, 'person', x, y, scale, mirror, fill, lw, sink)


def trace(image_path, height, smooth=9, tolerance=0.35):
    """Outline of the largest dark shape of an image (a silhouette on a light or transparent ground) as `(x, height)` in mm, scaled to `height` mm: the boundary pixels are followed, smoothed with a running mean over `smooth` pixels and thinned to `tolerance` pixels (Douglas-Peucker)."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    rgba = np.asarray(Image.open(image_path).convert('RGBA')).astype(float)
    grey = rgba[..., :3].mean(axis=2)*(rgba[..., 3]/255)+255*(1-rgba[..., 3]/255)
    labels, count = ndimage.label(grey < 128)
    largest = 1+np.argmax(ndimage.sum(grey < 128, labels, range(1, count+1)))
    mask = np.pad(ndimage.binary_fill_holes(labels == largest), 1)
    # Moore neighbour tracing from the top-left pixel of the shape.
    rows, cols = np.nonzero(mask)
    start = (rows[0], cols[rows == rows[0]].min())
    around = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]
    path, here, first = [start], start, 0
    while True:
        for k in range(8):
            d = (first+k) % 8
            step = (here[0]+around[d][0], here[1]+around[d][1])
            if mask[step]:
                first, here = (d+5) % 8, step
                break
        if here == start and len(path) > 2:
            break
        path.append(here)
    points = np.array(path, float)
    padded = np.vstack([points[-smooth:], points, points[:smooth]])
    points = np.column_stack([np.convolve(padded[:, c], np.ones(smooth)/smooth, 'same') for c in (0, 1)])[smooth:-smooth]

    def thin(pts):
        a, b = pts[0], pts[-1]
        ab = b-a
        off = np.abs((pts[:, 0]-a[0])*ab[1]-(pts[:, 1]-a[1])*ab[0])/(np.hypot(*ab) or 1)
        i = int(off.argmax())
        return [a, b] if off[i] <= tolerance else thin(pts[:i+1])[:-1]+thin(pts[i:])

    sys.setrecursionlimit(10000)
    half = len(points)//2
    kept = np.array(thin(points[:half+1])[:-1]+thin(np.vstack([points[half:], points[:1]]))[:-1])
    k = height/(points[:, 0].max()-points[:, 0].min())
    middle = (points[:, 1].max()+points[:, 1].min())/2
    return [(round((col-middle)*k), round((points[:, 0].max()-row)*k)) for row, col in kept]


def svg(name):
    """The asset as an SVG document in real mm, black outline and white fill."""
    w, h = size(name)
    left = min(x for x, _ in OUTLINES[name])
    pts = ' '.join(f'{x-left:.0f},{h-z:.0f}' for x, z in OUTLINES[name])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}mm" height="{h:.0f}mm" viewBox="-10 -10 {w+20:.0f} {h+20:.0f}">'
            f'<polygon points="{pts}" fill="white" stroke="black" stroke-width="4" stroke-linejoin="round"/></svg>\n')


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'trace':
        outline = trace(sys.argv[2], float(sys.argv[3]))
        rows = [', '.join(f'({x}, {z})' for x, z in outline[i:i+10]) for i in range(0, len(outline), 10)]
        print('    [\n        ' + ',\n        '.join(rows) + ',\n    ],')
    elif len(sys.argv) == 4 and sys.argv[1] == 'svg':
        with open(sys.argv[3], 'w', encoding='utf-8') as f:
            f.write(svg(sys.argv[2]))
    else:
        sys.exit(__doc__)
