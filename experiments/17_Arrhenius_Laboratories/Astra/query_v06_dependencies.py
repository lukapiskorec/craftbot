"""Read-only v05 export audit for the v06 design handoff; no scene edits."""
from pathlib import Path
import collections
import json

HERE = Path(__file__).resolve().parent
model = json.loads((HERE.parents[2]/'viewer/models/17_Arrhenius_Laboratories/astra_v05.json').read_text())
objects = {}
for mesh in model['meshes']:
    points = list(zip(*[iter(mesh['verts'])]*3))
    objects[mesh['name']] = (model['collections'][mesh['collection']], points)
for row in model['boxes']:
    matrix = row[2:14]
    points = [tuple(sum(matrix[4*i+j]*p[j] for j in range(3))+matrix[4*i+3] for i in range(3))
              for x in (-1,1) for y in (-1,1) for z in (-1,1) for p in [(x,y,z)]]
    objects[row[0]] = (model['collections'][row[1]], points)

def bounds(points):
    return tuple(round(v,5) for i in range(3) for v in (min(p[i] for p in points),max(p[i] for p in points)))

families = ('EdgeBeam','SiteGround','CourtyardGarden','CourtPathEast','NorthTerrace',
            'CourtSubsoil','TerraceSubsoil','TerraceFill','TerraceBase','EntranceApproachBase',
            'CorbelWing','CorbelSeat','Beam_','StairRim')
print('COUNTS', {prefix:sum(n.startswith(prefix) for n in objects) for prefix in families})
print('FRAME COLLECTIONS', dict(collections.Counter(c for n,(c,p) in objects.items() if 'Frames' in c)))
for name,(collection,points) in sorted(objects.items()):
    b = bounds(points)
    relevant = (name.startswith(('Panel_East_', 'Panel_West_')) and b[2]<6.56 and b[4]<8.01)
    relevant |= name.startswith(('CorbelWing_6_1_', 'CorbelSeat_6_1_', 'Beam_1_1_0_',
                                  'InsertLinkLedger_W_1','InsertLinkDeck_1','SouthInclineRafter_0_',
                                  'SouthInclineRafter_35_','Window_East_1_0','Window_West_1_0'))
    if relevant:
        print(name, collection, b)
print('WEST LINK ATTACHMENT FLOOR')
for name,(collection,points) in sorted(objects.items()):
    if name.startswith('FloorSlab_1_0_'):
        b=bounds(points)
        if b[0]<17.71 and b[1]>17.34 and b[2]<76 and b[3]>74:
            print(name,b)
