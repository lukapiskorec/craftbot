"""Version existing immutable presentation helpers and add bracket sections."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
for stem in ('render_interior','draw_plans','draw_support_sections','rasterize_plans','check_render_support_bridge'):
    source = (HERE/f'{stem}_v06.py').read_text(encoding='utf-8').replace('v06','v07')
    if stem == 'draw_plans':
        source = source.replace('name.replace("route_","route_v07_")','name.replace("route_","route_v06_")')
    if stem == 'check_render_support_bridge':
        source = source.replace("('CourtStair_','InsertInclineRail_','SouthInclineRail_')", "('CourtStair_','CourtStairHandrail_','InsertInclineRail_','SouthInclineRail_')")
    if stem == 'draw_support_sections':
        source = source.replace('for number,plane,extents,title,notes in sections:', """sections += [
    ('55',21.20,(11.90,12.85,3.20,3.75),'Upper CourtSouth attachment: actual steel and concrete section',
     ['Two discrete connectors per panel; 250mm slab-to-panel gap.',
      'End plates 10mm; web 10mm; all upper pieces 100mm high.',
      'Vertical anchor interfaces 0.010m2; weld interfaces 0.001m2; capacity unverified.']),
    ('56',21.20,(11.90,12.85,-.40,.45),'Ground CourtSouth attachment: continuous stepped web',
     ['Root plate -0.15..0.00m; receiver 0.00..0.15m; web -0.15..0.15m.',
      'Vertical anchor interfaces 0.015m2; weld interfaces 0.0015m2.',
      'Real ground slab bears 200mm on GradeBeam; earth remains unmodeled.']),
]
for number,plane,extents,title,notes in sections:""")
        source = source.replace("if 'Glass' in name:color='#a8d8e2'", "if 'Glass' in name:color='#a8d8e2'\n        if name.startswith('CourtFacadeBracket_'):color='#82afc0'")
        source = source.replace('SVGs41-44/51/52','SVGs41-44/51/52/55/56')
    (HERE/f'{stem}_v07.py').write_text(source,encoding='utf-8')
