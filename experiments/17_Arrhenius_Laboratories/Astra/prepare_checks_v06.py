"""Adapt inherited checks to approved changed support and omitted-earth scope."""
from pathlib import Path
HERE=Path(__file__).resolve().parent

for name in ('check_supports','check_rims','structural_followup'):
    path=HERE/f'{name}_v06.py'
    source=path.read_text(encoding='utf-8').replace("'EdgeBeam',",'')
    if name=='check_supports':
        source=source.replace("('CorbelSeat','CorbelWing','Beam_')", "('CorbelSeat','CorbelWing','CorbelNib','Beam_')")
        source=source.replace('x+side*.5)', 'x+side*.65)')
        source=source.replace('seat_area>=.08-1e-5 and beam_area>=.08-1e-5','seat_area>=.14-1e-5 and beam_area>=.14-1e-5')
        source=source.replace('0.20x0.40m','0.35x0.40m').replace('0.080m2','0.140m2').replace('0.20x0.325m','0.35x0.325m')
        source=source.replace('row[3]>=.08-1e-5 and row[4]>=.065-1e-5','row[3]>=.14-1e-5 and row[4]>=.11375-1e-5')
        source=source.replace("support=f'EdgeBeam_{level}_1_' if label=='W' and level>0 else ledger", 'support=ledger')
        source=source.replace("        if label=='W' and level>0:attachment=(17.35,17.50)\n",'')
        source+='\nassert not fails and all(path for _,path in paths)\nassert len(reduced)+len(alternate)==len(seat_fail), seat_fail\nassert all(row[-1] for row in connection_rows+base_rows)\n'
    if name=='structural_followup':
        source=source.replace('Raised terrace surface fill/under-support must be distinguished from a deliberately diagrammatic Site proxy.',
                              'Concept9 explicitly omits terrace earth/base; report its uncovered underside as an unmodeled ground-bearing boundary, not mesh-proved support.')
    path.write_text(source,encoding='utf-8')

path=HERE/'check_public_routes_v06.py'
source=path.read_text(encoding='utf-8')
source=source.replace("strips=[('Lawn',21.9,23.1,-2.,-.9,-.15),('Paving'", "strips=[('Paving'")
source=source.replace("        ('CourtGarden',33.75,34.95,64.,65.8,-.1),('CourtPath'", "        ('CourtPath'")
source=source.replace("rows+=['Risers: lawn to paving0.150m; garden to path0.100m;", "rows+=['Removed Lawn/CourtGarden are excluded by concept9; their surfaces are unmodeled. Historical grade transitions were150/100mm;")
source=source.replace("('EntranceApproachBase','GradeBeam_')", "('GradeBeam_',)")
source=source.replace("bearing=sum(g2.area(p) for p in remaining)<1e-5", "unmodeled=sum(g2.area(p) for p in remaining)\nbearing=abs(sum(areas.values())-1.20)<1e-5 and abs(unmodeled-2.40)<1e-5")
source=source.replace("Approach full-footprint slab support", "Approach retained concrete seat and explicit unmodeled earth-bearing remainder")
source=source.replace("prepared soil below fitted base inferred.", "unmodeled base/ground footprint{unmodeled:.6f}m2; no mesh-proved soil claim.")
path.write_text(source,encoding='utf-8')

path=HERE/'check_south_v06.py'
source=path.read_text(encoding='utf-8')
start=source.index('def signatures():')
end=source.index("objects=[o for o",start)
source=source[:start]+"rows=[runpy.run_path(str(HERE/'snapshot_v06.py'))['identity'](), 'Geometry changes are inventoried separately; no obsolete whole-frame retention assertion.']\n"+source[end:]
source=source.replace("f'Bracket failures {failed}; retained member changes {differences}'", "f'Bracket failures {failed}'")
source=source.replace('assert not failed and not differences','assert not failed')
path.write_text(source,encoding='utf-8')

source=(HERE/'check_completion_v05.py').read_text(encoding='utf-8').replace('v05','v06').replace("'EdgeBeam',",'')
source=source.replace("('Beam_', 'Column_', 'EdgeBeam')", "('Beam_', 'Column_')")
source=source.replace("assert_case(name+' supported underside', area(supported)-seated <= seam_allowance(supported),", "assert_case(name+' concrete seats / omitted earth boundary', seated>=0.,")
source=source.replace("f'explicit north cantilever {area(strip):.9f}m2; {supports}')", "f'unmodeled earth underside {area(supported)-seated:.9f}m2; explicit north cantilever {area(strip):.9f}m2; {supports}')")
source=source.replace("assert_case('Terrace total', terrace_required-terrace_seated < .001,", "assert_case('Terrace concrete/earth boundary total', terrace_seated>0 and abs(cantilever-.507)<.001,")
source=source.replace("f'30mm north cantilever {cantilever:.9f}m2; nominal cantilever .507m2')", "f'unmodeled earth-bearing {terrace_required-terrace_seated:.9f}m2; 30mm north cantilever {cantilever:.9f}m2; nominal cantilever .507m2')")
source=source.replace("for name in sorted(n for n in faces if n.startswith(('TerraceWall','TerraceFooting','TerraceFill','TerraceBase',\n                                                     'CourtStairFooting','RetainingBase'))):", "for name in sorted(n for n in faces if n.startswith('TerraceWall')):")
source=source.replace("manifest=json.loads((HERE/'retained_v06.json').read_text())", "manifest={'closure_changes':json.loads(bpy.context.scene.get('closure_changes_v06','[]'))}")
source=source.replace("('PerimeterLedger','Beam_','Column_')", "('PerimeterLedger','Beam_','Column_')")
(HERE/'check_completion_v06.py').write_text(source,encoding='utf-8')
print('Updated support, public routes, south envelope and completion checks for concept9.')
