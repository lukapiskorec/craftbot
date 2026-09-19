# Cut list and stick order from members.json (written by fab_model.py).
# Each member is measured along its longest edge direction; pieces are packed
# into 300 mm sticks per profile, first fit, longest first.
#
#   python fab_cutlist.py
import os
import csv
import json
import math
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
KERF = 1.0          # mm lost per cut
SPARE = 0.10        # extra sticks for breakage and miscuts
PRICE = {'3x5': 0.40, '2x10': 0.50}   # EUR per stick, karapori.fi, 2026-09-18
URL = 'https://karapori.fi/products/mantyrima-3-x-3-mm'


def load():
    with open(os.path.join(HERE, 'members.json')) as f:
        return json.load(f)


def sub(a, b): return [a[i]-b[i] for i in range(3)]
def dot(a, b): return sum(a[i]*b[i] for i in range(3))
def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def unit(a):
    n = math.sqrt(dot(a, a))
    return [c/n for c in a]
def extent(verts, axis):
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
    """(length, thickness, face, square) of a member in model mm, measured
    along and across its stock axis."""
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
    return name.split('_')[0]


def pack(lengths, stick):
    """First-fit decreasing; returns the list of sticks, each a list of lengths."""
    sticks = []
    for length in sorted(lengths, reverse=True):
        assert length <= stick, f'piece {length:.1f} mm exceeds the {stick} mm stick'
        for s in sticks:
            if sum(s)+KERF*len(s)+length <= stick:
                s.append(length)
                break
        else:
            sticks.append([length])
    return sticks


def main():
    data = load()
    stick = data['stick_length']
    rows = defaultdict(list)       # (stock, family, length, rip, square) -> names
    lengths = defaultdict(list)
    for m in data['members']:
        length, thickness, face, square = measure(m)
        t, f = (float(x) for x in m['stock'].split('x'))
        assert thickness <= t+0.06, (m['name'], thickness, face)
        assert face <= f*1.04, (m['name'], thickness, face)   # sloped roof boards read slightly wide
        rip = round(face, 1) if face < f-0.25 else None
        rows[(m['stock'], family(m['name']), round(length*2)/2, rip, square)].append(m['name'])
        lengths[m['stock']].append(length)

    with open(os.path.join(HERE, 'cutlist.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['stick', 'part', 'length_mm', 'rip_to_mm', 'ends', 'qty', 'example'])
        for (stock, fam, length, rip, square), names in sorted(rows.items(), key=lambda r: (r[0][0], r[0][1], -r[0][2])):
            w.writerow([stock, fam, f'{length:.1f}', rip or '', 'square' if square else 'angled', len(names), names[0]])

    out = [f'# Stick order, experiment 16 GPT-6 v02 at 1:{data["scale"]}', '',
           f'Mäntyrima 30 cm from {URL}. {len(data["members"])} pieces, frames {data["frames"]}.',
           f'Packing assumes {KERF:.0f} mm per cut. The order adds {SPARE:.0%} spare, rounded up.', '',
           '| Stick | Pieces | Total length m | Sticks packed | Sticks to order | EUR each | EUR |', '|---|---|---|---|---|---|---|']
    total = 0
    for stock, ls in sorted(lengths.items()):
        packed = len(pack(ls, stick))
        order = math.ceil(packed*(1+SPARE))
        total += order*PRICE[stock]
        out.append(f'| {stock} mm | {len(ls)} | {sum(ls)/1000:.1f} | {packed} | **{order}** | {PRICE[stock]:.2f} | {order*PRICE[stock]:.2f} |')
    out += [f'| | | | | | total | **{total:.2f}** |', '', '## Pieces per part', '',
            '| Stick | Part | Pieces | Length range mm |', '|---|---|---|---|']
    parts = defaultdict(list)
    for (stock, fam, length, rip, square), names in rows.items():
        parts[(stock, fam)] += [length]*len(names)
    for (stock, fam), ls in sorted(parts.items()):
        out.append(f'| {stock} | {fam} | {len(ls)} | {min(ls):.1f} to {max(ls):.1f} |')
    out += ['', 'Every piece with its length is in `cutlist.csv`.', '']
    with open(os.path.join(HERE, 'order.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print('\n'.join(out[:12]))


if __name__ == '__main__':
    main()
