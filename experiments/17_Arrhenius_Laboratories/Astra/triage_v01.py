"""Summarize v01 diagnostic pair families without loading the pair list in chat."""
import collections
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tools'))
from triage import families, format_families

hits=[]
for line in (HERE/'experiment_17_astra_v01_blender_pairs.txt').read_text().splitlines()[1:]:
    match=re.match(r'\s*([\d.]+) mm\s+(\S+)\s+x\s+(\S+)',line)
    if match: hits.append((float(match[1])/1000,match[2],match[3]))
summary=format_families(families(hits))
stair_facade=[hit for hit in hits if any(word in hit[1]+hit[2] for word in ('StairTread','StairWaist')) and any(word in hit[1]+hit[2] for word in ('Panel_','Window_','SouthIncline'))]
summary += '\n\nSTAIR/FACADE FAMILIES\n'+format_families(families(stair_facade),20)
(HERE/'triage_v01.txt').write_text(summary+'\n')
print(summary)
