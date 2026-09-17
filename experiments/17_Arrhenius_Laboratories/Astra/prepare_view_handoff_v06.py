"""Exact view legend and available-image manifest for independent inspection."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
tree=ast.parse((HERE/'views_astra.py').read_text())
views=[]
for node in ast.walk(tree):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='dict':
        name=next((k.value.value for k in node.keywords if k.arg=='name' and isinstance(k.value,ast.Constant)),None)
        if name:views.append((name,ast.unparse(node)))
lines=['# v06 exact view legend','', 'SITE_HIDE=Foundation; SKIN=Facade,Roof,Interior,Insert,Site,Foundation. hide_objects in49/50 uses actual exported layer classifier.','']
lines += ['- '+name+': '+v for name,v in sorted(views)]
files=sorted(HERE.glob('experiment_17_astra_v06_*view_*.png'))+sorted(HERE.glob('plan_v06_*.png'))
manifest=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(HERE/'view_legend_v06.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(HERE/'image_manifest_v06.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Available images:',len(files),[p.name for p in files if '_blender_' in p.name])
