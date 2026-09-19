"""Cut list and stick order for a model built from stock sticks.

Reads the members written by `export_members.py` (model millimetres, each
tagged with its stick profile such as '3x5'). Every member is measured along
its longest mesh edge; the pieces of each profile are packed into sticks of
one length, first fit, longest first.

    from cutlist import write_cutlist
    write_cutlist(data, out_dir, title='Stick order, ...', intro='Sticks from ...',
                  prices={'3x5': 0.40, '2x10': 0.50})

writes `cutlist.csv` (every distinct piece) and `order.md` (sticks per
profile with spare and price). Standard library only.

Provenance: experiment 16 fabrication set.
"""
import os
import csv
import math
from collections import defaultdict


def sub(a, b):
    """a - b for 3D vectors given as lists."""
    return [a[i]-b[i] for i in range(3)]


def dot(a, b):
    """Dot product."""
    return sum(a[i]*b[i] for i in range(3))


def cross(a, b):
    """Cross product."""
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def unit(a):
    """a scaled to length 1."""
    n = math.sqrt(dot(a, a))
    return [c/n for c in a]


def extent(verts, axis):
    """Size of a point set along a unit axis."""
    d = [dot(v, axis) for v in verts]
    return max(d)-min(d)


def long_axis(member):
    """Unit vector along the longest mesh edge: the stock axis."""
    verts, best = member['verts'], None
    for face in member['faces']:
        for a, b in zip(face, face[1:]+face[:1]):
            e = sub(verts[b], verts[a])
            if best is None or dot(e, e) > dot(best, best):
                best = e
    return unit(best)


def measure(member):
    """(length, thickness, face, square) of a member in its own units, measured
    along and across its stock axis. `square` is False for angled ends."""
    verts, u = member['verts'], long_axis(member)
    length = extent(verts, u)
    sections = []
    normals = [cross(sub(verts[f[1]], verts[f[0]]), sub(verts[f[2]], verts[f[1]])) for f in member['faces']]
    for c in normals:
        c = unit(c)
        if abs(dot(c, u)) > 0.3:
            continue
        w = sub(c, [dot(c, u)*k for k in u])
        if dot(w, w) < 1e-6:
            continue
        w = unit(w)
        sections.append(sorted((extent(verts, w), extent(verts, cross(u, w)))))
    thickness, face = min(sections, key=lambda s: s[0]*s[1])
    # Square ends: every vertex sits on one of the two end planes.
    d = [dot(v, u) for v in verts]
    square = all(min(abs(x-min(d)), abs(x-max(d))) < 0.05 for x in d)
    return length, thickness, face, square


def family(name):
    """Part family of a member name: the text before the first underscore."""
    return name.split('_')[0]


def pack(lengths, stick, kerf=1.0):
    """First-fit decreasing; returns the list of sticks, each a list of lengths."""
    sticks = []
    for length in sorted(lengths, reverse=True):
        assert length <= stick, f'piece {length:.1f} mm exceeds the {stick} mm stick'
        for s in sticks:
            if sum(s)+kerf*len(s)+length <= stick:
                s.append(length)
                break
        else:
            sticks.append([length])
    return sticks


def write_cutlist(data, out_dir, title, intro, prices, kerf=1.0, spare=0.10):
    """Write cutlist.csv and order.md for `data` (the members.json dict) with `prices` as {profile: EUR per stick} like {'3x5': 0.40}, and return the order as {profile: sticks}.
    Members whose `stock` is None (a slab, a panel) are left out. Asserts
    that every other member fits the section of the stick it is tagged
    with ('3x5' is thickness x face in mm)."""
    stick = data['stick_length']
    rows = defaultdict(list)       # (stock, family, length, rip, square) -> names
    lengths = defaultdict(list)
    for m in data['members']:
        if not m['stock']:
            continue
        length, thickness, face, square = measure(m)
        t, f = (float(x) for x in m['stock'].split('x'))
        # Boards sloped two ways read slightly wide, hence the 4 %.
        assert thickness <= t+0.06 and face <= f*1.04, (
            f"{m['name']} measures {thickness:.1f} x {face:.1f} mm and does not fit the {m['stock']} stick it is tagged with: "
            "fix the tag, or set its stock to None if it is not cut from sticks")
        rip = round(face, 1) if face < f-0.25 else None
        rows[(m['stock'], family(m['name']), round(length*2)/2, rip, square)].append(m['name'])
        lengths[m['stock']].append(length)

    with open(os.path.join(out_dir, 'cutlist.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['stick', 'part', 'length_mm', 'rip_to_mm', 'ends', 'qty', 'example'])
        for (stock, fam, length, rip, square), names in sorted(rows.items(), key=lambda r: (r[0][0], r[0][1], -r[0][2])):
            w.writerow([stock, fam, f'{length:.1f}', rip or '', 'square' if square else 'angled', len(names), names[0]])

    out = [f'# {title}', '', intro,
           f'Packing assumes {kerf:.0f} mm per cut. The order adds {spare:.0%} spare, rounded up.', '',
           '| Stick | Pieces | Total length m | Sticks packed | Sticks to order | EUR each | EUR |', '|---|---|---|---|---|---|---|']
    total, order = 0, {}
    for stock, ls in sorted(lengths.items()):
        packed = len(pack(ls, stick, kerf))
        order[stock] = math.ceil(packed*(1+spare))
        total += order[stock]*prices[stock]
        out.append(f'| {stock} mm | {len(ls)} | {sum(ls)/1000:.1f} | {packed} | **{order[stock]}** | {prices[stock]:.2f} | {order[stock]*prices[stock]:.2f} |')
    out += [f'| | | | | | total | **{total:.2f}** |', '', '## Pieces per part', '',
            '| Stick | Part | Pieces | Length range mm |', '|---|---|---|---|']
    parts = defaultdict(list)
    for (stock, fam, length, rip, square), names in rows.items():
        parts[(stock, fam)] += [length]*len(names)
    for (stock, fam), ls in sorted(parts.items()):
        out.append(f'| {stock} | {fam} | {len(ls)} | {min(ls):.1f} to {max(ls):.1f} |')
    out += ['', 'Every piece with its length is in `cutlist.csv`.', '']
    with open(os.path.join(out_dir, 'order.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    return order
