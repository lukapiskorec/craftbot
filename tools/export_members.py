"""Export the mesh members of a Blender scene as members.json for fabrication.

The fabrication tools (`cutlist.py`, `drafting.py`, `hidden_lines.py`) run
without Blender on this file. Every mesh object becomes one member: world
vertices in model millimetres (scene metres x 1000 / scale), faces as vertex
index lists, the collection path as `group`, the viewer layer from
`layers.classify`, and the stick profile from the object's `stock` property
('3x5' = thickness x face in mm; leave it unset for a slab or a panel).

From a script that has just built the scene:

    from export_members import write_members
    write_members(path, scale=15, exp_id='16', stick_length=300, frames=[0, 1, 2])

Or on a saved model (every member then gets the one profile given). Without
`--scale` it only prints the model extent and the smallest scale whose plan
and elevations fit an A2 sheet at 1:1:

    blender --background model.blend --python tools/export_members.py -- members.json
    blender --background model.blend --python tools/export_members.py -- members.json --scale 15 --exp 16 --stock 3x5

The drawings cull back faces, so the export asserts that every face is
wound outwards. Blender's renders do not show an inverted face; this does.

Provenance: experiment 16 fabrication set.
"""
import os
import sys
import json

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layers import classify


def group_path(collection):
    """Collection path 'Parent/Child' of a collection, as the experiment scripts name them."""
    parent = {c.name: p for p in bpy.data.collections for c in p.children}
    path = collection.name
    while collection.name in parent:
        collection = parent[collection.name]
        path = collection.name+'/'+path
    return path


def check_outward(meshes):
    """Assert that every face normal of every (convex) mesh points away from the mesh centre."""
    for o in meshes:
        centre = sum((v.co for v in o.data.vertices), Vector())/len(o.data.vertices)
        for face in o.data.polygons:
            assert face.normal.dot(face.center-centre) > 0, ('face wound inwards', o.name)


def collect_members(scale, exp_id='', default_stock=None):
    """Members of the current scene in model mm at 1:`scale`; `default_stock` tags the meshes that have no `stock` property."""
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    check_outward(meshes)
    k = 1000/scale
    members = []
    for o in meshes:
        stock = o.get('stock', default_stock) or None      # None: not cut from sticks, left out of the cut list
        group = group_path(o.users_collection[0])
        M = o.matrix_world
        members.append({
            'name': o.name,
            'group': group,
            'layer': classify(exp_id, group, o.name),
            'stock': stock,
            'verts': [[round(c*k, 4) for c in (M@v.co)] for v in o.data.vertices],
            'faces': [list(p.vertices) for p in o.data.polygons],
        })
    return members


def write_members(path, scale, exp_id='', stick_length=300, default_stock=None, **extra):
    """Write members.json: scale, stick length, any `extra` keys the drawings need (frame lines, levels) and the members."""
    members = collect_members(scale, exp_id, default_stock)
    with open(path, 'w') as f:
        json.dump({'scale': scale, 'stick_length': stick_length, **extra, 'members': members}, f)
    return members


def scene_extent():
    """Real extents (x, y, z) in metres of all mesh objects in the scene."""
    corners = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
    return tuple(max(c[i] for c in corners)-min(c[i] for c in corners) for i in range(3))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('out')
    parser.add_argument('--scale', type=int, help='15 for a 1:15 model; omit to print the smallest scale that fits A2')
    parser.add_argument('--exp', default='', help='experiment id for the viewer layer rules, e.g. 16')
    parser.add_argument('--stock', help='stick profile for members without a "stock" property, e.g. 3x5')
    parser.add_argument('--stick-length', type=float, default=300)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.scale:
        from drafting import min_scale
        extent = scene_extent()
        print('Model extent %.2f x %.2f x %.2f m: plan and elevations fit A2 at 1:1 from scale 1:%d' % (*extent, min_scale(extent)))
        sys.exit()
    print(f'Wrote {len(write_members(args.out, args.scale, args.exp, args.stick_length, args.stock))} members to {args.out}')
