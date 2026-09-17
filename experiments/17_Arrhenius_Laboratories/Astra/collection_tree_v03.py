"""Read-only collection inventory of the saved frozen model."""
from pathlib import Path
import bpy

lines = []
def walk(collection, indent=''):
    lines.append(indent + collection.name)
    for child in collection.children:
        walk(child, indent + '  ')
for collection in bpy.context.scene.collection.children:
    walk(collection)
output = Path(__file__).with_suffix('.txt')
output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(output.read_text(encoding='utf-8'))
