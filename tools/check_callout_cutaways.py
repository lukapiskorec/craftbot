"""Validate assembled cutaway coverage, omissions, vectors, text and bounds."""
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
    folder = source.parent/'callout_diagrams'/slug/'cutaway'
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    model_path = cd.ROOT/manifest['source']
    assert hashlib.sha256(model_path.read_bytes()).hexdigest()==manifest['source_sha256']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['callouts_sha256']
    assert manifest['translation']==[0,0,0]
    model = json.loads(model_path.read_text(encoding='utf-8'))
    members = cd.decode_model(model)
    removed = set(manifest['removed_names'])
    names = {m['name'] for m in members}
    assert removed <= names
    for layer,counts in manifest['layers'].items():
        layer_names = [m['name'] for m in members if m['layer']==layer]
        assert counts==dict(total=len(layer_names),kept=sum(n not in removed for n in layer_names))
    assert manifest['removed_frame_names']==[m['name'] for m in members if m['layer']=='frame' and m['name'] in removed]
    callouts = json.loads(source.read_text(encoding='utf-8'))['callouts']
    assert len(callouts)==len(manifest['callouts'])
    for callout,entry in zip(callouts,manifest['callouts']):
        assert callout['id']==entry['id']
        matched = set(resolve(model,callout['match']))
        assert len(matched)==entry['matched_count']
        assert set(entry['selected_names'])<=matched-removed
        assert entry['anchor_name'] in entry['selected_names']
        assert not entry['internal_view']
        assert not set(entry['selected_names'])&set(manifest['added_context_names'])
    assert manifest['heading_size_mm']==manifest['body_size_mm']
    assert set(manifest['added_context_names'])<=names-removed
    assert set(manifest['translucent_glass_names'])<=names-removed
    import callout_cutaways as cut
    model_key = (source.parent.name[:2],slug)
    assert set(manifest['white_highlight_names'])=={members[i]['name'] for i in cut.white_highlights(members,model_key)}
    if model_key==('04','fable'):
        assert not {m['name'] for m in members if m['group']=='Stairs'}&removed
    if model_key==('16','gpt6'):
        headers = {m['name'] for m in members if m['name'].startswith('EntranceHeader_')}
        assert not headers&removed
        assert not headers&{name for entry in manifest['callouts'] for name in entry['selected_names']}
        room = next(entry for entry in manifest['callouts'] if entry['id']=='quiet-room')
        groups = {m['name']:m['group'] for m in members}
        assert {groups[name] for name in room['selected_names']}=={groups[room['anchor_name']]}
    if model_key==('14','fable'):
        complete = {m['name'] for m in members if m['group']=='New/Ladder'
                    or (m['group']=='New/Guards' and m['name'].startswith(('Guard_','VoidGuard_T_')))}
        assert not complete&removed
    if model_key in cut.HALF_ROOF:
        for group,counts in manifest['roof_groups'].items():
            assert counts['kept']>=counts['total']*.45,(source,group,counts)
    expected_glass = {members[i]['name'] for i in cut.glass_members(members,model_key[0])}-removed
    assert set(manifest['translucent_glass_names'])==expected_glass
    pdf = PdfReader(folder/'cutaway.pdf')
    assert len(pdf.pages)==2
    assert manifest['styles']==['lines','inverted']
    for page,style,filename in zip(pdf.pages,manifest['styles'],('cutaway.svg','inverted.svg')):
        check_page(source,folder,manifest,callouts,page,style,filename,render)
    return dict(source=source.relative_to(cd.ROOT).as_posix(),callouts=len(callouts),
                orientation=manifest['orientation'],layers=manifest['layers'],
                removed_frame_names=manifest['removed_frame_names'],cut_depth=manifest['cut_depth'],
                added_context=len(manifest['added_context_names']),glass_panes=len(expected_glass),
                roof_groups=manifest['roof_groups'])


def check_page(source,folder,manifest,callouts,page,style,filename,render):
    assert not list(page.images)
    tree = ET.parse(folder/filename).getroot()
    assert not tree.findall('.//{*}image')
    assert tree.find('{*}path').attrib['stroke'] in ('#999999','#cccccc')
    normalize = lambda s:''.join(s.split())
    text = normalize(' '.join(t.text or '' for t in tree.findall('{*}text')))
    pdf_text = normalize(page.extract_text())
    for callout in callouts:
        for field in ('label','quote'):
            if callout.get(field):
                assert normalize(callout[field]) in text,(source,callout['id'],field)
                assert normalize(callout[field]) in pdf_text,(source,callout['id'],field)
    w,h = map(float,tree.attrib['viewBox'].split()[2:])
    assert abs(float(page.mediabox.width)*25.4/72-w)<.5
    assert abs(float(page.mediabox.height)*25.4/72-h)<.5
    for node in tree.findall('{*}text'):
        assert node.attrib['font-family'].split(',')[0]=='Segoe UI'
        x,y,size = [float(node.attrib[k]) for k in ('x','y','font-size')]
        width = advance(node.text or '',size,node.attrib['font-family'].split(',')[0],int(node.attrib.get('font-weight',400)))
        anchor = node.attrib.get('text-anchor','start')
        left = x-(width if anchor=='end' else width/2 if anchor=='middle' else 0)
        assert 10<=left and left+width<=w-10 and 10<=y-size and y<=h-10,(source,node.text)
        if abs(x-w*.59)<.02:
            assert int(node.attrib.get('font-weight',400))==400,(source,style,node.text)
            expected = manifest['metadata_size_mm'] if (node.text or '').startswith('Section ') else manifest['body_size_mm']
            assert size==expected,(source,style,node.text,size,expected)
    for node in tree.findall('{*}polygon')+tree.findall('{*}polyline')+tree.findall('{*}path'):
        pairs = (node.attrib['points'].split() if 'points' in node.attrib else re.findall(r'[ML]([-\d.]+,[-\d.]+)',node.attrib['d']))
        for pair in pairs:
            x,y = map(float,pair.split(','))
            assert 10<=x<=w-10 and 10<=y<=h-10,(source,pair)
    if style=='inverted':
        assert manifest['fill_fragments']>0
        assert any(node.attrib.get('stroke')=='#ffffff' for node in tree.findall('{*}path'))
        if manifest['white_highlight_names']:
            assert any(node.attrib.get('fill')=='white' for node in tree.findall('{*}path'))
    if manifest['translucent_glass_names']:
        assert any(0<float(node.attrib.get('fill-opacity','1'))<1 for node in tree.findall('{*}polygon'))
    if render:
        import pypdfium2 as pdfium
        document = pdfium.PdfDocument(str(folder/(style+'.pdf')))
        preview_page = document[0]
        bitmap = preview_page.render(scale=1500/preview_page.get_height())
        out = cd.ROOT/'outputs'/'callout_cutaways_qa'
        out.mkdir(parents=True,exist_ok=True)
        slug = source.stem.removesuffix('_callouts')
        bitmap.to_pil().convert('RGB').save(out/(source.parent.name[:2]+'_'+slug+'_'+style+'.png'))
        bitmap.close()
        preview_page.close()
        document.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--only',default='')
    args = parser.parse_args()
    records = []
    for path in sorted(cd.MODELS.glob('*/*_callouts.json')):
        if path.parent.name.startswith(args.only):
            records.append(check(path,args.render))
            print(f'{path.parent.name}/{path.stem}: OK',flush=True)
    out = cd.ROOT/'outputs'/'callout_cutaways_qa'
    out.mkdir(parents=True,exist_ok=True)
    (out/('report'+args.only+'.json')).write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(f'{2*len(records)} sheets / {sum(r["callouts"] for r in records)} callouts verified in both styles')


if __name__=='__main__':
    main()
