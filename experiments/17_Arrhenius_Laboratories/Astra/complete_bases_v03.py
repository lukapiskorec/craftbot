"""Apply the exact v03 generator function to its completed unrendered snapshot."""
from pathlib import Path
import ast
import runpy
import sys
import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
from craftbot_lib import mesh_prism
identity=runpy.run_path(str(HERE/'snapshot_v03.py'))['identity']
before=identity()
assert '9981f7d19d10d736cab495f33cfb7bf8bee71cbf5f57b90ab873dd73a8b19519' in before,before
tree=ast.parse((HERE/'experiment_17_astra_v03.py').read_text(encoding='utf-8'))
function_names={'B','core_bounds','rect_bounds','subtract_box','complete_core_bases'}
nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in function_names
       or isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CORES' for t in node.targets)]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(HERE/'experiment_17_astra_v03.py'),'exec'))
complete_core_bases()
after=identity();print(before+'\n'+after,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'preflight_v03.blend'))
(HERE/'core_base_completion_v03.txt').write_text(before+'\n'+after+'\nCompletion used exact AST function from the generator; full-source reproduction remains required.\n',encoding='utf-8')
