"""Build a portable, dependency-free comparison gallery from Cycles settings JSON.

Usage: python tools/render_gallery.py outputs/<study>/fable_v09_settings.json
Optional <stem>_thumb.jpg files beside each render are used for the grid.
"""

import argparse
import html
import json
import sys
from pathlib import Path


def build(manifest_path, thumbnails=False):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cards = []
    by_name = {r["name"]: r for r in manifest["renders"]}
    for render in manifest["renders"]:
        without = by_name.get(render["name"].replace("_with_foundation", "_no_foundation"))
        with_foundation = by_name.get(render["name"].replace("_no_foundation", "_with_foundation"))
        if render["foundation"] != "no_foundation" and without:
            continue
        filename = Path(render["file"]).name
        light = render.get("study", render["name"].removesuffix("_no_foundation")).removeprefix(render["palette"] + "_")
        cards.append(dict(palette=render["palette"], light=light, file=filename, edges=render.get("edges", "none"),
                          without=Path(without["file"]).name if without else None,
                          with_foundation=Path(with_foundation["file"]).name if with_foundation else None,
                          sun=f'{render["sun_rotation"]}° / {render["sun_elevation"]}°',
                          camera=f'{render["camera"]["azimuth"]}° / {render["camera"]["elevation"]}°'))
    title = f'{Path(manifest["experiment"]).stem} · Cycles study'
    first = manifest["renders"][0]
    render_info = (f'{first["resolution"][0]} × {first["resolution"][1]} PNG · '
                   f'Blender {manifest["blender"]} · Cycles / {first["device"]} · '
                   f'{first["samples"]} samples · adaptive sampling + denoising')
    sky_info = " · ".join(f'{key.replace("_", " ")}: {manifest["settings"].get(key, "default")}'
                          for key in ("world_strength", "sun_intensity", "sun_size", "fill_strength", "edge_width"))
    # Escape '<' so a file name cannot terminate the embedded script element.
    payload = json.dumps(cards).replace("<", "\\u003c")
    page = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>TITLE</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eef0f1;color:#25333f;font:15px system-ui,sans-serif}
header{padding:32px 4vw 20px}h1{font-size:27px;font-weight:550;margin:0 0 12px}
p{line-height:1.6;max-width:1000px}nav{display:flex;flex-wrap:wrap;gap:18px;align-items:center;
position:sticky;top:0;background:#eef0f1f5;padding:16px 4vw;z-index:2;border-bottom:1px solid #ccd2d7}
select,button{padding:8px;border:1px solid #b8c3cb;border-radius:4px;background:white;color:inherit}
main{padding:22px 4vw;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}
article{background:white;border-radius:6px;overflow:hidden}article img{width:100%;display:block}
.caption{padding:14px 16px}.caption b{display:block;margin-bottom:6px}.caption small{color:#5b6974}
footer{padding:10px 4vw 35px}a{color:#345d78}dialog{width:min(96vw,1100px);border:0;padding:12px}
dialog::backdrop{background:#152330c9}dialog img{display:block;width:100%;max-height:83vh;object-fit:contain}
.dialogbar{display:flex;gap:20px;align-items:center;justify-content:space-between}
@media(max-width:850px){main{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:550px){main{grid-template-columns:1fr}}
</style>
<header><h1>TITLE</h1>
<p>Compare material, lighting, edge and foundation variants. Click a render for the full image.</p></header>
<nav><label>Materials <select id="palette"><option value="all">All palettes</option>
<option value="white">White plaster</option><option value="muted">Muted brown</option>
<option value="washed">Pale washed timber</option><option value="weathered">Weathered timber</option></select></label>
<label>Light / view <select id="light"><option value="all">All studies</option>
 </select></label>
<label>Edges <select id="edges"><option value="all">All variants</option></select></label>
<label><input type="checkbox" id="foundation"> Show foundation</label><span id="count"></span></nav>
<main id="grid"></main>
<footer>RENDER_INFO<br>
SKY_INFO<br>
Camera and sun labels are azimuth or rotation / elevation. Click an image to inspect it;
the full-resolution link opens the original PNG. <a href="MANIFEST">Exact settings</a> ·
<a href="README.md">Study notes</a></footer>
<dialog id="viewer"><div class="dialogbar"><b id="caption"></b><a id="original" target="_blank">Full resolution</a>
<button id="close">Close</button></div><img id="large" alt="Selected render"></dialog>
<script>
const cards=PAYLOAD;
const names={white:'White plaster',muted:'Muted brown',washed:'Pale washed timber',weathered:'Weathered timber',
reference:'Reference sun',crosslight:'Crosslight',low_sun:'Lower sun',frame:'Exposed frame',main:'Clad model',
clad_lit:'Clad · fully lit edges',clad_reduced:'Clad · reduced edge light',clad_unlit:'Clad · unlit edges',
frame_lit:'Frame · fully lit edges',frame_reduced:'Frame · reduced edge light',frame_unlit:'Frame · unlit edges',
none:'No edges',bevel:'Dark edges'};
const palette=document.querySelector('#palette'), light=document.querySelector('#light'),
foundation=document.querySelector('#foundation'),grid=document.querySelector('#grid'), viewer=document.querySelector('#viewer');
const edges=document.querySelector('#edges');
for(const [control,key] of [[light,'light'],[edges,'edges']])for(const value of new Set(cards.map(c=>c[key]))){
 const option=document.createElement('option');option.value=value;option.textContent=names[value]||value;control.append(option);
}
if(new Set(cards.map(c=>c.edges)).size>1)grid.style.gridTemplateColumns='repeat(2,minmax(0,1fr))';
function redraw(){
 grid.replaceChildren();
 const selected=cards.filter(c=>(palette.value==='all'||c.palette===palette.value)&&(light.value==='all'||c.light===light.value)&&(edges.value==='all'||c.edges===edges.value));
 document.querySelector('#count').textContent=selected.length+' comparisons';
 for(const c of selected){
  const file=(foundation.checked?c.with_foundation:c.without)||c.file;
  const title=names[c.palette]+' · '+(names[c.light]||c.light)+' · '+names[c.edges];
  const card=document.createElement('article'), a=document.createElement('a'), img=document.createElement('img');
  a.href=file; img.src=file.replace('.png','_thumb.jpg'); img.alt=title; img.loading='lazy';
  img.onerror=()=>{img.onerror=null;img.src=file};a.append(img);
  a.onclick=e=>{e.preventDefault();document.querySelector('#large').src=file;
   document.querySelector('#caption').textContent=title+(foundation.checked?' · Foundation shown':' · Foundation hidden');
   document.querySelector('#original').href=file;viewer.showModal()};
  const caption=document.createElement('div');caption.className='caption';
  const heading=document.createElement('b');heading.textContent=title;
  const settings=document.createElement('small');settings.textContent='Sun '+c.sun+' · Camera '+c.camera;
  caption.append(heading,settings);card.append(a,caption);grid.append(card);
 }
}
for(const control of [palette,light,foundation,edges])control.onchange=redraw;
document.querySelector('#close').onclick=()=>viewer.close();redraw();
</script></html>'''.replace("TITLE", html.escape(title)).replace("PAYLOAD", payload)
    page = page.replace("RENDER_INFO", html.escape(render_info)).replace("MANIFEST", html.escape(manifest_path.name))
    page = page.replace("SKY_INFO", html.escape(sky_info))
    destination = manifest_path.parent / "index.html"
    destination.write_text(page, encoding="utf-8")
    if thumbnails:
        import bpy
        for render in manifest["renders"]:
            source = manifest_path.parent / Path(render["file"]).name
            thumb = source.with_name(source.stem + "_thumb.jpg")
            image = bpy.data.images.load(str(source.resolve()), check_existing=False)
            image.scale(640, max(1, round(image.size[1] * 640 / image.size[0])))
            image.filepath_raw = str(thumb.resolve())
            image.file_format = "JPEG"
            image.save()
            bpy.data.images.remove(image)
    print(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--thumbnails", action="store_true", help="Run inside Blender to generate gallery thumbnails")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
    build(args.manifest, args.thumbnails)
