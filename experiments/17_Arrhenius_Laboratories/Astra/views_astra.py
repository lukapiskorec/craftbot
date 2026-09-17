# Fixed numbering from tools/views_template.py; the full reference/check set.
SITE_HIDE=['Foundation']
SKIN=['Facade','Roof','Interior','Insert','Site','Foundation']
VIEWS=[
    dict(name='01',azim=45,elev=30,hide=SITE_HIDE),
    dict(name='02',azim=135,elev=30,hide=SITE_HIDE),
    dict(name='03',azim=225,elev=30,hide=SITE_HIDE),
    dict(name='04',azim=315,elev=30,hide=SITE_HIDE),
    dict(name='05',azim=270,elev=89.9,hide=SITE_HIDE),
    dict(name='06',azim=270,elev=0,hide=SITE_HIDE),
    dict(name='07',azim=0,elev=0,hide=SITE_HIDE),
    dict(name='08',azim=90,elev=0,hide=SITE_HIDE),
    dict(name='09',azim=180,elev=0,hide=SITE_HIDE),
    dict(name='10',azim=225,elev=30,hide=["Facade","Roof","Interior","Insert","Site","Foundation","Floors"]),
    dict(name='11',azim=225,elev=-25,hide=['Site','Foundation']),
    # Photo05 south silhouette, Photo02 front corner, Photo06 facade.
    dict(name='12',azim=280,elev=7,hide=SITE_HIDE,focus=(Vector((27,26,10)),38)),
    dict(name='13',azim=230,elev=12,hide=SITE_HIDE,focus=(Vector((10,5,9)),17)),
    dict(name='14',azim=185,elev=8,hide=SITE_HIDE,focus=(Vector((0,40,9)),15)),
    # Photo04 looking north down court; transparent glazing can be judged in Cycles.
    dict(name='15',azim=270,elev=22,hide=SITE_HIDE,focus=(Vector((27,67,7)),29)),
    dict(name='16',azim=0,elev=0,hide=['Site','Foundation'],cut=('x',34.5)),
    dict(name='17',azim=270,elev=0,hide=['Site','Foundation'],cut=('y',61)),
    dict(name='18',azim=180,elev=0,hide=['Facade','Site','Foundation','Interior'],cut=('x',3.65),focus=(Vector((3.65,61,8)),11)),
    dict(name='19',azim=210,elev=20,hide=SKIN+['Floors'],focus=(Vector((9,36,8)),16)),
    dict(name='20',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',1.5)),
    dict(name='21',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',5.1)),
    dict(name='22',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',8.7)),
    dict(name='23',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',12.3)),
    dict(name='24',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',15.9)),
    dict(name='25',azim=180,elev=0,hide=['Site','Foundation'],cut=('x',27),focus=(Vector((27,5,8)),12)),
    dict(name='26',azim=200,elev=15,hide=['Site','Foundation'],focus=(Vector((0,36,7.2)),3.5)),
    dict(name='27',azim=225,elev=-18,hide=['Facade','Roof','Interior','Site','Foundation','Floors'],focus=(Vector((3.65,61,3.4)),4)),
    # Same stair cut as18 with enclosure retained for transmitted daylight.
    dict(name='28',azim=180,elev=0,hide=['Site','Foundation','Interior'],cut=('x',3.65),focus=(Vector((3.65,61,8)),11)),
    dict(name='29',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',15.9),focus=(Vector((5.2,61,14.4)),5.5)),
    dict(name='30',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',5.1),focus=(Vector((9,49,3.6)),12)),
    dict(name='31',azim=0,elev=0,hide=['Foundation'],cut=('x',34.3),focus=(Vector((34.3,73,3)),17)),
    dict(name='32',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',5.1),focus=(Vector((31,109,3.6)),8)),
    dict(name='33',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',5.1),focus=(Vector((42,11,3.6)),7)),
    dict(name='34',azim=270,elev=0,hide=['Site','Foundation'],cut=('y',75),focus=(Vector((18.2,75,3.6)),4)),
    # v04 projected south enclosure: slab/beam and bracket section at x9.
    dict(name='35',azim=180,elev=0,hide=['Site','Foundation','Interior'],cut=('x',9),focus=(Vector((9,.1,13.8)),5.3)),
    dict(name='36',azim=235,elev=12,hide=['Site','Foundation'],focus=(Vector((.7,.3,13.5)),5.4)),
    dict(name='37',azim=270,elev=89.9,hide=SITE_HIDE,cut=('z',1.5),focus=(Vector((22.5,5,0)),7)),
    # v05 real support completion; 38/39 remain presentation trials and
    # 40 remains the selected interior perspective in its dedicated renderer.
    dict(name='41',azim=0,elev=0,hide=['Facade','Roof','Interior'],cut=('x',34.3),focus=(Vector((34.3,93,1.3)),4.8)),
    dict(name='42',azim=0,elev=0,hide=['Facade','Roof','Interior'],cut=('x',34.3),focus=(Vector((34.3,101.5,1.2)),7)),
    dict(name='43',azim=180,elev=0,hide=['Facade','Roof','Interior','Site','Foundation'],cut=('x',12),focus=(Vector((12,113.5,3.2)),1.2)),
    dict(name='44',azim=180,elev=0,hide=['Facade','Roof','Interior','Site','Foundation'],cut=('x',12),focus=(Vector((12,.3,10.4)),1.2)),
]
COLORS={
    'Structure':(.655,.643,.608,1),'Foundation':(.52,.52,.50,1),
    'Floors':(.70,.69,.66,1),'Roof':(.68,.69,.67,1),
    'PrecastPanels':(.70,.69,.66,1),'TimberFrames':(.349,.267,.22,1),
    'Glass':(.28,.37,.38,.25),'InsertGlass':(.28,.37,.38,.25),'SouthMetal':(.718,.729,.714,1),
    'SteelFrames':(.204,.212,.204,1),'Interior':(.74,.73,.70,1),
    'Stairs':(.65,.64,.60,1),'Rails':(.204,.212,.204,1),
    'StairRims':(.204,.212,.204,1),
    'Insert':(.65,.64,.60,1),'SkylightFrames':(.22,.24,.23,1),
    'Site':(.43,.47,.37,1),'SiteStairs':(.62,.61,.57,1),
    'TerraceFill':(.54,.43,.29,1),'TerraceBase':(.62,.57,.45,1),
    'Plant':(.718,.729,.714,1),'PlantLouvres':(.26,.28,.27,1),
    'Entrance':(.349,.267,.22,1),
}
RESOLUTION=(1800,1400)
# v06 source corrections; old camera numbering and definitions stay fixed.
import bpy
import layers
if any(o.name.startswith('CorbelNib_') for o in bpy.data.objects):
    def collection_path(collection):
        for parent in bpy.data.collections:
            if collection.name in parent.children:
                return collection_path(parent)+'/'+collection.name
        return collection.name
    actual_layers={o.name:layers.classify('17',collection_path(o.users_collection[0]),o.name)
                   for o in bpy.data.objects if o.type=='MESH'}
    VIEWS += [
        dict(name='45',azim=220,elev=22,hide=['Facade','Roof','Interior','Insert','Site','Foundation'],focus=(Vector((0,36,6.6)),2.6)),
        dict(name='46',azim=135,elev=-12,hide=['Facade','Roof','Interior','Insert','Site','Foundation','Floors'],focus=(Vector((9,6.35,2.7)),1.3)),
        dict(name='47',azim=220,elev=10,hide=SITE_HIDE,focus=(Vector((.4,3.8,4.8)),6.0)),
        dict(name='48',azim=270,elev=0,hide=['Site','Foundation'],cut=('y',75),focus=(Vector((17.9,75,3.35)),1.8)),
        dict(name='49',azim=225,elev=30,hide=[],hide_objects=[n for n,l in actual_layers.items() if l!='frame']),
        dict(name='50',azim=225,elev=30,hide=[],hide_objects=[n for n,l in actual_layers.items() if l!='fixtures']),
        dict(name='51',azim=270,elev=0,hide=['Facade','Roof','Interior','Floors','Site','Foundation','InsertGlass'],cut=('y',102),focus=(Vector((35.6,102,1.5)),1.8)),
        dict(name='52',azim=225,elev=-15,hide=['Facade','Roof','Interior','Floors','Site','Foundation','InsertGlass'],focus=(Vector((35.1,95.8,2.6)),1.5)),
        # v06 presentation correction: isolate actual landing load-path pieces
        # because the distant insert slab occludes the underside in view52.
        dict(name='53',azim=225,elev=-12,hide=[],
             hide_objects=[n for n in actual_layers if not n.startswith(('CourtLanding','CourtWaist_19','CorbelWing_76_1_-1','Column_76','RetainingWall'))],
             focus=(Vector((35.1,95.8,2.65)),1.5)),
        dict(name='54',azim=225,elev=30,hide=[],hide_objects=[n for n,l in actual_layers.items() if l!='fixtures']),
    ]
# Presentation-only material roles shared by the versioned transmission checks.
if any(o.name.startswith('CourtFacadeBracket_') for o in bpy.data.objects):
    # v07: actual context around one upper/ground bracket, and discrete array.
    bracket_names=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('CourtFacadeBracket_')]
    def bracket_context(f):
        keep=[]
        for o in bpy.data.objects:
            if o.type!='MESH':continue
            if o.name.startswith((f'CourtFacadeBracket_1_{f}_0_',f'Panel_CourtSouth_1_'+('Base' if f==0 else str(f-1)))):
                keep.append(o.name)
            elif o.name.startswith((f'FloorSlab_{f}_','GradeBeam_' if f==0 else f'Beam_{f}_')):
                points=[o.matrix_world@v.co for v in o.data.vertices]
                if min(p.x for p in points)<=21.25 and max(p.x for p in points)>=21.15 and min(p.y for p in points)<=12.30 and max(p.y for p in points)>=12.:
                    keep.append(o.name)
        return [o.name for o in bpy.data.objects if o.type=='MESH' and o.name not in keep]
    VIEWS += [
        dict(name='55',azim=0,elev=0,hide=[],hide_objects=bracket_context(1),cut=('x',21.20),focus=(Vector((21.20,12.30,3.40)),.65)),
        dict(name='56',azim=0,elev=0,hide=[],hide_objects=bracket_context(0),cut=('x',21.20),focus=(Vector((21.20,12.30,0.)),.65)),
        dict(name='57',azim=45,elev=24,hide=[],hide_objects=[o.name for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('CourtFacadeBracket_1_0_0_')],focus=(Vector((21.20,12.425,0.)),.30)),
        dict(name='58',azim=110,elev=15,hide=[],hide_objects=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name not in bracket_names]),
    ]
CYCLES = {'material_roles': {
    **{name: 'concrete' for name in ('Foundation','Columns','Corbels','Beams','Cores',
        'Floors','RoofSlabs','Parapets','PrecastPanels','Treads','Waists','Landings',
        'InsertFloors','InsertStructure','InsertWalls','Retaining','SiteStairs')},
    **{name: 'metal' for name in ('SteelFrames','SouthMetal','StairRims','Rails',
        'SkylightFrames','Plant','PlantLouvres','Drains')},
    'TimberFrames':'timber','Entrance':'timber','Glass':'glass','InsertGlass':'glass',
    'Partitions':'cladding','Site':'cladding',
}}
