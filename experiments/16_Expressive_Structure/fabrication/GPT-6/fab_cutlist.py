# Cut list and stick order from members.json (written by fab_model.py),
# with tools/cutlist.py. Writes cutlist.csv and order.md here; order.md ends
# with the weight estimates of the model and of the pedestal of fab_pedestal.py.
#
#   python fab_cutlist.py
import os
import sys
import json
import csv
import math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'tools')))
from cutlist import write_cutlist, pack, sub, dot, cross
from fab_pedestal import pedestal

PRICE = {'3x5': 0.40, '2x10': 0.50}   # EUR per stick, karapori.fi, 2026-09-18
URL = 'https://karapori.fi/products/mantyrima-3-x-3-mm'

# Alternative stock: 1 m Bauhaus slats ripped into strips on a small hobby saw.
# stick: (slat, slat width mm, rip width mm, EUR per slat on 2026-09-20, url)
SLATS = {'2x10': ('10 x 70 x 1000', 70, 2, 3.38, 'https://www.bauhaus.fi/hobbylista-maler-manty-puuvalmis-10-x-70-x-1000-mm'),
         '3x5': ('5 x 40 x 1000', 40, 3, 1.88, 'https://www.bauhaus.fi/hobbylista-maler-manty-puuvalmis-5-x-40-x-1000-mm')}
SLAT_LENGTH = 1000
RIP_KERF = 1.0

# Densities in kg/m3 at about 12 % moisture, (low, typical, high). Scots pine for the sticks and a pine
# panel for the pedestal; MDF as the other likely pedestal board.
PINE = (450, 520, 600)
MDF = (700, 750, 800)
BALLAST_KG = 20


def load():
    with open(os.path.join(HERE, 'members.json')) as f:
        return json.load(f)


def write_slat_order():
    """Put the slat order at the top of order.md: 1 m slats ripped into the two sticks."""
    lengths = {stock: [] for stock in SLATS}
    with open(os.path.join(HERE, 'cutlist.csv')) as f:
        for row in csv.DictReader(f):
            lengths[row['stick']] += [float(row['length_mm'])]*int(row['qty'])
    out = ['## Slat order, Bauhaus', '',
           f'Hobbylista Maler, pine, {SLAT_LENGTH} mm long, ripped into strips with a {RIP_KERF:.0f} mm rip kerf. '
           'Pieces are packed into full-length strips with 1 mm per crosscut. The order adds 10% spare strips, rounded up.', '',
           '| Stick | Slat | Strips per slat | Strips packed | Strips with spare | Slats to order | EUR each | EUR |',
           '|---|---|---|---|---|---|---|---|']
    order, total = {}, 0.0
    for stock, (slat, width, rip, price, url) in SLATS.items():
        per_slat = int((width+RIP_KERF)//(rip+RIP_KERF))
        packed = len(pack(lengths[stock], SLAT_LENGTH, 1.0))
        strips = math.ceil(packed*1.10)
        order[stock] = math.ceil(strips/per_slat)
        total += order[stock]*price
        out.append(f'| {stock} mm | [{slat} mm]({url}) | {per_slat} | {packed} | {strips} | **{order[stock]}** | {price:.2f} | {order[stock]*price:.2f} |')
    out += [f'| | | | | | | total | **{total:.2f}** |', '',
            'Prices of 2026-09-20, on offer until 2026-10-04 (regular 4.50 and 2.50 EUR).', '',
            '## Stick order, Karapori (reference)', '']
    path = os.path.join(HERE, 'order.md')
    with open(path, encoding='utf-8') as f:
        title, _, rest = f.read().partition('\n\n')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(title+'\n\n'+'\n'.join(out)+'\n'+rest)
    return order


def volume(member):
    """Volume in mm3 of a convex member with outward faces: signed tetrahedra from its first vertex."""
    verts, total = member['verts'], 0.0
    for face in member['faces']:
        for i in range(1, len(face)-1):
            a, b, c = (sub(verts[face[k]], verts[0]) for k in (0, i, i+1))
            total += dot(a, cross(b, c))/6
    return total


def write_weights(data):
    """Append the weight estimates of the model and of the pedestal to order.md."""
    litres = lambda members: sum(volume(m) for m in members)/1e6
    kilos = lambda volume_l, density: ' | '.join(f'{volume_l*d/1000:.2f}' if volume_l < 5 else f'{volume_l*d/1000:.1f}' for d in density)
    by_stock = {}
    for m in data['members']:
        by_stock.setdefault(m['stock'], []).append(m)
    model = litres(data['members'])
    out = ['', '## Weight estimates', '',
           'Volumes are measured on the meshes of `members.json` and of the pedestal boards in `fab_pedestal.py`, '
           'as built, without offcuts or spare. Weight is volume times density at about 12 % moisture; the low and high '
           'columns are the usual spread of the material, not a tolerance of the model.', '',
           '### Model', '',
           f'| Part | Pieces | Volume l | kg at {PINE[0]} | kg at {PINE[1]} kg/m3 | kg at {PINE[2]} |', '|---|---|---|---|---|---|']
    for stock, members in sorted(by_stock.items()):
        out.append(f'| {stock} mm sticks, pine | {len(members)} | {litres(members):.3f} | {kilos(litres(members), PINE)} |')
    out += [f'| **model** | {len(data["members"])} | **{model:.3f}** | {kilos(model, PINE)} |', '',
            f'The model weighs about **{model*PINE[1]/1000:.2f} kg**. Glue adds a few per cent, about {model*PINE[1]*0.04:.0f} g at 4 %.', '',
            '### Pedestal', '']
    boards = pedestal()
    sides = litres(m for code, m in boards.items() if code.startswith('S'))
    panels = litres(m for code, m in boards.items() if not code.startswith('S'))
    whole = sides+panels
    out += ['| Boards | Volume l | Pine panel kg | MDF kg |', '|---|---|---|---|',
            f'| 4 sides 18 x 400 x 1200 | {sides:.2f} | {sides*PINE[1]/1000:.1f} | {sides*MDF[1]/1000:.1f} |',
            f'| top and bottom 18 x 382 x 382 | {panels:.2f} | {panels*PINE[1]/1000:.1f} | {panels*MDF[1]/1000:.1f} |',
            f'| **pedestal, empty** | **{whole:.2f}** | **{whole*PINE[1]/1000:.1f}** | **{whole*MDF[1]/1000:.1f}** |',
            f'| with {BALLAST_KG} kg ballast | | {whole*PINE[1]/1000+BALLAST_KG:.1f} | {whole*MDF[1]/1000+BALLAST_KG:.1f} |', '',
            f'Pine panel at {PINE[1]} kg/m3 ({whole*PINE[0]/1000:.1f} to {whole*PINE[2]/1000:.1f} kg over {PINE[0]} to {PINE[2]}), '
            f'MDF at {MDF[1]} kg/m3 ({whole*MDF[0]/1000:.1f} to {whole*MDF[2]/1000:.1f} kg over {MDF[0]} to {MDF[2]}). '
            'Screws add about 0.2 kg. The fifth board is bought whole: its offcut, 18 x 400 x 436 plus two 18 mm strips, is not in these numbers.']
    with open(os.path.join(HERE, 'order.md'), 'a', encoding='utf-8') as f:
        f.write('\n'.join(out)+'\n')
    return model*PINE[1]/1000, whole*PINE[1]/1000


if __name__ == '__main__':
    data = load()
    order = write_cutlist(data, HERE, title=f'Stick order, experiment 16 GPT-6 v02 at 1:{data["scale"]}',
                          intro=f'Mäntyrima 30 cm from {URL}. {len(data["members"])} pieces, frames {data["frames"]}.',
                          prices=PRICE, kerf=1.0, spare=0.10)
    print('Sticks to order:', order)
    print('Slats to order:', write_slat_order())
    print('Model and empty pine pedestal, kg: %.2f and %.1f' % write_weights(data))
