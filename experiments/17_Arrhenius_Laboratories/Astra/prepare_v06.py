"""Derive v06 from immutable v05; mechanical edits approved by Coordinator."""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def replace_once(source, old, new):
    assert source.count(old) == 1, old[:100]
    return source.replace(old, new)


destination = HERE/'experiment_17_astra_v06.py'
assert not destination.exists(), 'Never overwrite a prepared or rendered version.'
source = (HERE/'experiment_17_astra_v05.py').read_text(encoding='utf-8').replace('v05', 'v06')
start = source.index('for name,r,z in [(\'South\'')
end = source.index("B('CourtPathEast'", start)
source = source[:start] + '# Concept9: landscape/earth are intentionally unmodeled. Retain paving.\n' + source[end:]
source = replace_once(source, "B('EntranceApproachBase','Foundation',21.,24.,-.90,.30,-.40,-.25)\n", '')
start = source.index('        # Four convex shoulder pieces')
end = source.index('\n# Transverse beams', start)
source = source[:start] + '''        # Concept9: rotate the complete shoulder plan by90deg globally.
        # X is the transverse Beam span; Y is the shorter shoulder depth.
        for sign in (-1,1):
            xa,xb=sorted((x+sign*.3,x+sign*CORBEL_W/2))
            pts=[(xa,top-CORBEL_H*.45),(xb,top-CORBEL_H),(xb,top),(xa,top)] if sign<0 else [(xa,top-CORBEL_H),(xb,top-CORBEL_H*.45),(xb,top),(xa,top)]
            prism_y(f'CorbelWing_{i}_{f}_{sign}','Structure/Corbels',y-CORBEL_D/2,y+CORBEL_D/2,pts)
            ya,yb=sorted((y+sign*.3,y+sign*CORBEL_D/2))
            B(f'CorbelSeat_{i}_{f}_{sign}','Structure/Corbels',x-.3,x+.3,ya,yb,top-CORBEL_H,top)
            # Local integral50mm rear nib restores full shifted y6.35 beam
            # width; its200mm-deep root meets the rotated shoulder face.
            # Column81's first-raised ends instead bear on the core ledges.
            if f==1 and y==6. and x!=45. and not ((x==0. and sign<0) or (x==54. and sign>0)):
                B(f'CorbelNib_{i}_{f}_{sign}','Structure/Corbels',xa,xb,y+.50,y+.55,top-.20,top)
''' + source[end:]
start = source.index('    # Facade ledgers carry panel leaves')
end = source.index('\nfor f in range(6):', start)
source = source[:start] + '    # Longitudinal EdgeBeam strips omitted: facade spandrels are enclosure.\n' + source[end:]
start = source.index('front_beam_cuts=[]')
end = source.index('for i,(a,b) in enumerate(g2.columns(.55,53.45,1.5)):',start)
source = source[:start] + 'front_beam_cuts=[]  # no invented longitudinal beams cut this glazing\n' + source[end:]
source = replace_once(source, "('Column_','CoreWall','InsertColumn','CorbelSeat')", "('Column_','CoreWall','InsertColumn','CorbelSeat','CorbelNib')")
source = replace_once(source, "('Beam_','EdgeBeam','StairHeader'", "('Beam_','StairHeader'")
source = replace_once(source, '    if name==\'EntranceApproachBase\': return 7\n', '')
source = source.replace('# Transverse beams on every station; opening edge beams close load paths.',
                        '# Transverse beams on every station; real opening headers close load paths.')
source = source.replace('# Concept8 support completion preserves the inherited primary geometry.',
                        '# Concept9 regenerates retained support completions against corrected geometry.')
destination.write_text(source, encoding='utf-8')

helper = (HERE/'support_geometry_v05.py').read_text(encoding='utf-8')
helper = helper.replace('Concept 8 support completion after the inherited v04 joinery.',
                        'Concept9 support completion after revised v06 joinery; earth omitted.')
helper = replace_once(helper, "    fitted('CourtSubsoil','Foundation',32.85,35.60,89.50,90.10,-1.25,-.75)\n", '')
start = helper.index("    fitted('TerraceFill'")
end = helper.index('    bpy.context.view_layer.update()',start)
helper = helper[:start] + '    # Earth, prepared subsoil and granular bases are an unmodeled boundary.\n' + helper[end:]
helper = helper.replace('Added concept8 perimeter ledgers, stair waist/seats and contained terrace support.',
                        'Added concept9 perimeter ledgers, stair waist/seats and retained terrace concrete.')
(HERE/'support_geometry_v06.py').write_text(helper, encoding='utf-8')

for name in ('snapshot','check_routes','verify_route_envelopes','check_headroom',
             'check_supports','check_rims','check_south','check_public_routes',
             'structural_followup','draw_plans','draw_support_sections','rasterize_plans','render_interior'):
    target = HERE/f'{name}_v06.py'
    assert not target.exists(), target
    original = (HERE/f'{name}_v05.py').read_text(encoding='utf-8')
    target.write_text(original.replace('v05','v06'), encoding='utf-8')
print('Prepared v06 geometry/support/check copies; dependent checks still require revision.')
