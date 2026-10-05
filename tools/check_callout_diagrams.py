"""Check every diagram against its source and render PDF contact sheets.

python tools/check_callout_diagrams.py [--render]

Requires the bundled pypdf, Pillow and (for --render) pypdfium2. QA images
and the report go in ignored outputs/callout_diagrams_qa/.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from pypdf import PdfReader

from callouts import resolve
from fonts import advance

ROOT = Path(__file__).resolve().parents[1]


def normalized(text):
    return ''.join(text.split())


def check_set(source, render=False):
    slug = source.stem.removesuffix('_callouts')
    folder = source.parent / 'callout_diagrams' / slug
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    model_path = ROOT / manifest['source']
    model = json.loads(model_path.read_text(encoding='utf-8'))
    assert hashlib.sha256(model_path.read_bytes()).hexdigest() == manifest['source_sha256'], model_path
    callouts = json.loads(source.read_text(encoding='utf-8'))['callouts']
    reader = PdfReader(folder / 'all_callouts.pdf')
    assert len(reader.pages) == len(callouts) == len(manifest['drawings']), source
    assert len(list(folder.glob('*.svg'))) == len(callouts), folder
    for callout, record, page in zip(callouts, manifest['drawings'], reader.pages):
        assert callout['id'] == record['id'], record
        expected = set(resolve(model, callout['match']))
        assert expected == set(record['selected_names']), record['id']
        assert expected and len(expected) == record['selected_count'], record['id']
        tree = ET.parse(folder / record['svg']).getroot()
        assert not tree.findall('.//{*}image'), record['svg']
        assert not list(page.images), record['id']
        svg_text = normalized(' '.join(t.text or '' for t in tree.findall('{*}text')))
        pdf_text = normalized(page.extract_text())
        for field in ('label', 'quote'):
            if callout.get(field):
                for text in (svg_text, pdf_text):
                    assert normalized(callout[field]) in text, (record['id'], field)
        w, h = map(float, tree.attrib['viewBox'].split()[2:])
        assert abs(float(page.mediabox.width)*25.4/72-w) < .5, record['id']
        assert abs(float(page.mediabox.height)*25.4/72-h) < .5, record['id']
        for node in tree.findall('{*}text'):
            x, y, size = [float(node.attrib[k]) for k in ('x', 'y', 'font-size')]
            width = advance(node.text or '', size, node.attrib['font-family'].split(',')[0],
                            int(node.attrib.get('font-weight', 400)))
            anchor = node.attrib.get('text-anchor', 'start')
            left = x-(width if anchor == 'end' else width/2 if anchor == 'middle' else 0)
            assert 10 <= left and left+width <= w-10 and 10 <= y-size and y <= h-10, (record['id'], node.text)
        for node in tree.findall('{*}polyline')+tree.findall('{*}polygon'):
            for pair in node.attrib['points'].split():
                x, y = map(float, pair.split(','))
                assert 10 <= x <= w-10 and 10 <= y <= h-10, (record['id'], pair)
        for node in tree.findall('{*}path'):
            for x, y in re.findall(r'[ML]([-\d.]+),([-\d.]+)', node.attrib['d']):
                assert 10 <= float(x) <= w-10 and 10 <= float(y) <= h-10, record['id']
    if render:
        render_contact(folder / 'all_callouts.pdf', source.parent.name[:2]+'_'+slug)
    return dict(source=str(source.relative_to(ROOT)), pages=len(callouts),
                orientations=sorted({r['orientation'] for r in manifest['drawings']}))


def render_contact(path, tag):
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw

    out = ROOT / 'outputs' / 'callout_diagrams_qa'
    out.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(path))
    contact = Image.new('RGB', (1600, ((len(pdf)+3)//4)*560), '#dedede')
    draw = ImageDraw.Draw(contact)
    for i in range(len(pdf)):
        page = pdf[i]
        bitmap = page.render(scale=400/page.get_width())
        image = bitmap.to_pil().convert('RGB')
        image.thumbnail((390, 530))
        x, y = (i%4)*400+(400-image.width)//2, (i//4)*560
        contact.paste(image, (x, y+22))
        draw.text(((i%4)*400+8, y+5), f'{tag} / {i+1:02}', fill='black')
        bitmap.close()
        page.close()
    contact.save(out / (tag+'_contact.png'))
    pdf.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    records = []
    for source in sorted((ROOT / 'viewer' / 'models').glob('*/*_callouts.json')):
        record = check_set(source, args.render)
        print(f'{source.parent.name}/{source.name}: {record["pages"]} pages OK', flush=True)
        records.append(record)
    out = ROOT / 'outputs' / 'callout_diagrams_qa'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'report.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    print(f'{len(records)} sets / {sum(r["pages"] for r in records)} diagrams verified')


if __name__ == '__main__':
    main()
