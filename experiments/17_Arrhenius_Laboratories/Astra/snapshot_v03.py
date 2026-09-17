"""Stable geometry identity shared by read-only v03 diagnostics."""
import hashlib
import bpy
def identity():
    digest=hashlib.sha256();count=0
    for obj in sorted((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:o.name):
        count+=1;digest.update(obj.name.encode('utf-8'))
        for vertex in obj.data.vertices:
            p=obj.matrix_world @ vertex.co
            digest.update(('{:.6f},{:.6f},{:.6f};'.format(*p)).encode('ascii'))
    return f'GEOMETRY v03: {count} meshes; SHA256(names/world vertices at1micrometre)={digest.hexdigest()}; loaded {bpy.data.filepath}'
