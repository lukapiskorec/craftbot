# Started from tools/views_template.py. Stable numbered views, append only.
VIEWS=[
    dict(name='01',azim=45,elev=25,hide=[]),
    dict(name='02',azim=135,elev=25,hide=[]),
    dict(name='03',azim=225,elev=25,hide=[]),
    dict(name='04',azim=315,elev=25,hide=[]),
    dict(name='05',azim=270,elev=89.9,hide=[]),
    dict(name='06',azim=270,elev=0,hide=[]), # matched front / entrance
    dict(name='07',azim=0,elev=0,hide=[]), # exterior wave profile
    dict(name='08',azim=225,elev=25,hide=["Facade","Floor","Ceiling","RoofCover"]),
    dict(name='09',azim=225,elev=-30,hide=[]),
    dict(name='10',azim=270,elev=0,hide=[],cut=('y',0)), # simple tall interior
    dict(name='11',azim=270,elev=0,hide=['Facade'],focus=(Vector((0,0,6.5)),2.5)),
    dict(name='12',azim=315,elev=15,hide=['RoofCover','Facade'],focus=(Vector((1.6,-1.5,6.05)),.6)),
    dict(name='13',azim=315,elev=10,hide=['Facade'],focus=(Vector((1.8,-1,3)),.65)),
    dict(name='14',azim=315,elev=20,hide=['Facade','Floor'],focus=(Vector((1.75,-1.5,0)),.65)),
    dict(name='15',azim=270,elev=10,hide=['Facade'],focus=(Vector((0,-1.55,1.15)),1.4)),
    dict(name='16',azim=315,elev=35,hide=[],focus=(Vector((.8,-1,7)),.65)),
    dict(name='17',azim=270,elev=89.9,hide=['RoofCover','Ceiling','Facade'],focus=(Vector((0,0,6.4)),2.5)),
    dict(name='18',azim=270,elev=-89.9,hide=['Floor','Facade']),
    dict(name='19',azim=270,elev=0,hide=['EndBoards'],focus=(Vector((0,0,3)),3.25)),
]
COLORS={
    'Ground':(.57,.44,.29,1),'Floor':(.72,.58,.39,1),'Ceiling':(.76,.64,.46,1),
    'Structure':(.72,.57,.37,1),'ColumnWebs':(.48,.085,.065,1),
    'RoofStructure':(.72,.57,.37,1),'RoofWebs':(.48,.085,.065,1),
    'RoofCover':(.76,.64,.46,1),'Facade':(.48,.085,.065,1),
    'WallSupport':(.48,.085,.065,1),'Entrance':(.72,.57,.37,1),
    'Bracing':(.59,.38,.24,1),
}
RESOLUTION=(1600,1200)
