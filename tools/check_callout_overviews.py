"""Validate both overview variants and render paired PDF review images."""
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from pypdf import PdfReader
from fonts import advance
from callouts import resolve
import callout_diagrams as cd


def check(source, render=False):
    slug = source.stem.removesuffix('_callouts')
    folder = source.parent/'callout_diagrams'/slug/'overview'
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    model_path = cd.ROOT/manifest['source']
    assert hashlib.sha256(model_path.read_bytes()).hexdigest()==manifest['source_sha256']
    model = json.loads(model_path.read_text(encoding='utf-8'))
    callouts = json.loads(source.read_text(encoding='utf-8'))['callouts']
    assert len(callouts)==len(manifest['callouts'])
    normalize = lambda s:''.join(s.split())
    for callout,entry in zip(callouts,manifest['callouts']):
        assert callout['id']==entry['id']
        matched = set(resolve(model,callout['match']))
        assert len(matched)==entry['matched_count']
        assert set(entry['selected_names'])<=matched
        assert entry['anchor_name'] in entry['selected_names']
    comparison = PdfReader(folder/'comparison.pdf')
    assert len(comparison.pages)==2
    for page,style in zip(comparison.pages,('lines','inverted')):
        assert not list(page.images)
        tree = ET.parse(folder/(style+'.svg')).getroot()
        assert not tree.findall('.//{*}image')
        text = normalize(' '.join(t.text or '' for t in tree.findall('{*}text')))
        pdf_text = normalize(page.extract_text())
        single = PdfReader(folder/(style+'.pdf'))
        assert len(single.pages)==1
        for callout in callouts:
            for field in ('label','quote'):
                if callout.get(field):
                    assert normalize(callout[field]) in text,(source,style,callout['id'],field)
                    assert normalize(callout[field]) in pdf_text,(source,style,callout['id'],field)
        w,h = map(float,tree.attrib['viewBox'].split()[2:])
        assert abs(float(page.mediabox.width)*25.4/72-w)<.5
        assert abs(float(page.mediabox.height)*25.4/72-h)<.5
        for node in tree.findall('{*}text'):
            x,y,size = [float(node.attrib[k]) for k in ('x','y','font-size')]
            width = advance(node.text or '',size,node.attrib['font-family'].split(',')[0],
                            int(node.attrib.get('font-weight',400)))
            anchor = node.attrib.get('text-anchor','start')
            left = x-(width if anchor=='end' else width/2 if anchor=='middle' else 0)
            assert 10<=left and left+width<=w-10 and 10<=y-size and y<=h-10,(source,style,node.text)
        for node in tree.findall('{*}polygon')+tree.findall('{*}polyline')+tree.findall('{*}path'):
            pairs = (node.attrib['points'].split() if 'points' in node.attrib else
                     re.findall(r'[ML]([-\d.]+,[-\d.]+)',node.attrib['d']))
            for pair in pairs:
                x,y = map(float,pair.split(','))
                assert 10<=x<=w-10 and 10<=y<=h-10,(source,style,pair)
        if style=='inverted':
            assert manifest['face_fragments']>0
            assert any(node.attrib.get('stroke')=='#ffffff' for node in tree.findall('{*}path'))
    if render:
        render_pair(folder,source.parent.name[:2]+'_'+slug)
    return dict(source=source.relative_to(cd.ROOT).as_posix(),callouts=len(callouts),
                orientation=manifest['orientation'],body_size_mm=manifest['body_size_mm'])


def render_pair(folder,tag):
    import pypdfium2 as pdfium
    from PIL import Image,ImageDraw
    pdf = pdfium.PdfDocument(str(folder/'comparison.pdf'))
    previews = []
    for i in range(2):
        page = pdf[i]
        bitmap = page.render(scale=1100/page.get_height())
        previews.append(bitmap.to_pil().convert('RGB'))
        bitmap.close()
        page.close()
    canvas = Image.new('RGB',(sum(p.width for p in previews)+20,1130),'#dedede')
    draw = ImageDraw.Draw(canvas)
    x = 0
    for i,preview in enumerate(previews):
        draw.text((x+8,8),tag+(' / A - dark lines' if i==0 else ' / B - inverted'),fill='black')
        canvas.paste(preview,(x,30))
        x += preview.width+20
    out = cd.ROOT/'outputs'/'callout_overviews_qa'
    out.mkdir(parents=True,exist_ok=True)
    canvas.save(out/(tag+'.png'))
    pdf.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--only',default='')
    args = parser.parse_args()
    records = []
    for path in sorted(cd.MODELS.glob('*/*_callouts.json')):
        if path.parent.name.startswith(args.only):
            record = check(path,args.render)
            records.append(record)
            print(f'{path.parent.name}/{path.stem}: both variants OK',flush=True)
    out = cd.ROOT/'outputs'/'callout_overviews_qa'
    out.mkdir(parents=True,exist_ok=True)
    (out/'report.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(f'{len(records)} models / {2*len(records)} sheets / {sum(r["callouts"] for r in records)} callouts verified')


if __name__=='__main__':
    main()
